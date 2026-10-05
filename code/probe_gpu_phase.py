#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""probe_gpu_phase.py —— 多次采样 GPU 利用率，判"某卡长期空转"是**常态**还是**采样巧合**。

为什么需要：单次采样看到 GPU0 = 2%、GPU1 = 65%，这可能是
  (a) **相位差**：两条 lane 各自在"训练/扫描/评估"之间循环，恰好一条在低占用段；
  (b) **常态失衡**：一条 lane 长期喂不满。
两者对估时的影响完全不同 ⇒ 必须**多次采样**才分得开。

采样内容（只读）：每 `--every` 秒取一次
  · `nvidia-smi` 的每卡利用率与显存；
  · `train_obj.py` 进程数与当前 run 名；
  · 训练进程的 `rchar` 增量（判是否在**读数据**）。

用法：python3 probe_gpu_phase.py --n 8 --every 30
"""
import re
import sys
import time
import subprocess

N, EVERY = 8, 30
if '--n' in sys.argv:
    N = int(sys.argv[sys.argv.index('--n') + 1])
if '--every' in sys.argv:
    EVERY = int(sys.argv[sys.argv.index('--every') + 1])


def sh(c):
    return subprocess.run(['bash', '-lc', c], capture_output=True, text=True).stdout


def gpu():
    out = sh('nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader')
    r = {}
    for l in out.strip().split('\n'):
        f = [x.strip() for x in l.split(',')]
        if len(f) >= 2:
            r[f[0]] = f[1]
    return r


def rc():
    tot = 0
    for p in sh('pgrep -f train_obj.py').split():
        try:
            t = open('/proc/%s/io' % p).read()
            m = re.search(r'rchar:\s*(\d+)', t)
            if m:
                tot += int(m.group(1))
        except Exception:
            pass
    return tot


def names():
    out = sh('pgrep -af train_obj.py | sed "s/.*--name //;s/ --data.*//" | sort -u')
    return [x for x in out.strip().split('\n') if x]


print('采样 %d 次，每 %d 秒一次（共约 %.0f 分钟）' % (N, EVERY, N * EVERY / 60.0))
print('%-6s %-8s %-8s %-10s %s' % ('t', 'GPU0', 'GPU1', '读(MB/s)', '在跑的 run'))
print('-' * 78)
prev_rc, prev_t = rc(), time.time()
rows = []
for i in range(N):
    g = gpu()
    n = names()
    print('%-6.0fs %-8s %-8s %-10s %s'
          % (i * EVERY, g.get('0', '?'), g.get('1', '?'), '—',
             (' | '.join(n))[:44] if n else '（无训练进程）'))
    if i < N - 1:
        time.sleep(EVERY)
        cur_rc, cur_t = rc(), time.time()
        dt = cur_t - prev_t
        mb = (cur_rc - prev_rc) / 1e6
        prev_rc, prev_t = cur_rc, cur_t
        rows.append((g.get('0'), g.get('1'), mb / dt if dt else 0))
print()
if rows:
    g0 = [int(x[0].rstrip('%')) for x in rows if x[0] and x[0].endswith('%')]
    g1 = [int(x[1].rstrip('%')) for x in rows if x[1] and x[1].endswith('%')]
    rd = [x[2] for x in rows]
    if g0:
        print('GPU0 利用率：min %d%% / 中位 %d%% / max %d%%' % (min(g0), sorted(g0)[len(g0)//2], max(g0)))
    if g1:
        print('GPU1 利用率：min %d%% / 中位 %d%% / max %d%%' % (min(g1), sorted(g1)[len(g1)//2], max(g1)))
    print('读吞吐：中位 %.2f MB/s（>50 MB/s 说明在真读盘，≈0 说明走页缓存）'
          % sorted(rd)[len(rd)//2])
    print()
    print('判读：若**两卡都会周期性掉到低位** ⇒ 相位差（正常）；'
          '若**同一张卡持续低** ⇒ 常态失衡（值得查 CPU/worker）。')
