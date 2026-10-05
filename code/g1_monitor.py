# -*- coding: utf-8 -*-
r"""g1_monitor.py -- G1 云端实验的**异常与空转**监视器（只读，不改云端任何状态）。

判据（每条都有明确阈值）
------------------------
| 检查 | 判据 | 为什么 |
|---|---|---|
| **空转** | 某卡 `memory.used < 500 MiB` 或 `utilization == 0%` 连续 ≥2 次采样 | 用户明确要求"不要让 GPU 空转" |
| **停滞** | 某 run 的 `results.csv` 轮数在 ≥3 次采样（约 15 min）内**没有增长**，且队列进程仍在 | "进程活着但没在训练"是最隐蔽的故障 |
| **降批** | 日志里出现 ultralytics 自行降 batch（`batch=16` 等） | 登记家族"偏离 1"就是它，**违反协议** |
| **OOM** | 日志或 dmesg 出现 out of memory | 同上 |
| **队列死** | `g1_queue.py` 进程消失，但该机仍有未完成的 run | 会话断开会把任务带走（踩过两次） |
| **外部抢占** | 卡上出现**不属于 g1_** 的进程 | B 机曾有过别的项目任务 |
| **磁盘** | overlay 可用 < 20 GB | 写满会让训练中途失败 |

用法
----
    python g1_monitor.py                 # 采样一次并打印报告
    python g1_monitor.py --loop 300      # 每 300 秒采样一次，持续（供子代理用）
    python g1_monitor.py --state <文件>   # 状态文件（默认同目录 _g1_monitor_state.json）

★ 凭据：从 `_cloud_creds.py` 读（该文件**不进任何放行件**；本脚本只读它）。
"""
import io
import os
import sys
import json
import time
import argparse

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# ★★ 2026-10-04：**源码指纹**。教训来自监视子代理：
#   我改了盘上的本文件，但**已在运行的 --loop 循环不会重新加载**（Python 启动时就载入了源码），
#   于是"已修好"实际上没生效，它一直在用旧规则。⇒ 每轮把**源码指纹**打出来，
#   任何人看到指纹与当前文件不符，就知道"跑的是旧代码，需重启"。
SRC_FINGERPRINT = None  # 由 main() 计算


# ★★ 2026-10-04：**B 已停止并归还**（其 40 个 run 的文本产物已于 21:48 取回并 sha256 双验）。
#   而 A 与 B **是同一个 IP**（117.50.190.229，仅端口不同）⇒ 全部 SSH 共用**一份按 IP 计的连接预算**。
#   对一台已死的机器每轮烧最多 4 次失败握手，会直接挤压 A 的可观测性。
#   ⇒ 默认**只监视在跑的机器**。若 B 复活，把下面那条 dict 取消注释即可。
MACHINES = [
    dict(tag='A', host='cpod-1u20pv1vhj4v.podtcp.compshare.cn', port=24581,
         pw_key='A_PW', cells='c3 c4', lanes='base100@0, strat100@1'),
    # dict(tag='B', host='cpod-1uearmsfxbj2.podtcp.compshare.cn', port=25046,
    #      pw_key='B_PW', cells='c1 c2', lanes='base100@0, strat100@1'),
]

# 一次采样在远端跑完，只用一条 SSH 连接
REMOTE = r'''python3 - <<"E"
import os, glob, json, subprocess
out = {}
try:
    out['gpu'] = subprocess.run(['nvidia-smi','--query-gpu=index,memory.used,utilization.gpu',
                                 '--format=csv,noheader'], capture_output=True, text=True).stdout.strip().split('\n')
except Exception as e:
    out['gpu'] = ['ERR %s' % e]
try:
    out['procs'] = subprocess.run(['nvidia-smi','--query-compute-apps=pid,used_memory',
                                   '--format=csv,noheader'], capture_output=True, text=True).stdout.strip()
except Exception:
    out['procs'] = ''
out['queue'] = subprocess.run(['bash','-lc','pgrep -af g1_queue.py | grep -v bash | wc -l'],
                              capture_output=True, text=True).stdout.strip()
out['train'] = subprocess.run(['bash','-lc','pgrep -af train_obj.py | grep -v bash | wc -l'],
                              capture_output=True, text=True).stdout.strip()
out['training_names'] = subprocess.run(
    ['bash','-lc','pgrep -af train_obj.py | sed "s/.*--name //;s/ --data.*//" | sort -u'],
    capture_output=True, text=True).stdout.strip().split('\n')
runs = {}
for d in sorted(glob.glob('/workspace/runs/g1_c*')):
    f = os.path.join(d, 'results.csv')
    n = (sum(1 for _ in open(f)) - 1) if os.path.exists(f) else 0
    runs[os.path.basename(d)] = n
out['runs'] = runs
out['oom'] = subprocess.run(['bash','-lc','grep -lci "out of memory" /root/_g1_*.log 2>/dev/null | wc -l'],
                            capture_output=True, text=True).stdout.strip()
out['batch'] = subprocess.run(['bash','-lc','grep -ho "batch=[0-9]*" /root/_g1_*.log 2>/dev/null | sort | uniq -c'],
                              capture_output=True, text=True).stdout.strip().split('\n')
out['disk'] = subprocess.run(['bash','-lc',"df -BG --output=avail / | tail -1 | tr -dc '0-9'"],
                             capture_output=True, text=True).stdout.strip()
out['done'] = subprocess.run(['bash','-lc','wc -l < /root/_g1_done.txt 2>/dev/null || echo 0'],
                             capture_output=True, text=True).stdout.strip()
print('G1MON' + json.dumps(out, ensure_ascii=False))
E'''


def sample(m, pw, timeout=120):
    import paramiko
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for _ in range(4):
        try:
            cli.connect(m['host'], port=m['port'], username='root', password=pw,
                        timeout=40, banner_timeout=90, auth_timeout=40,
                        allow_agent=False, look_for_keys=False)
            break
        except Exception:
            time.sleep(15)
    else:
        return None
    ch = cli.get_transmission if False else cli.get_transport().open_session()
    ch.settimeout(timeout)
    ch.exec_command(REMOTE)
    buf = b''
    try:
        while True:
            d = ch.recv(65536)
            if not d:
                break
            buf += d
    except Exception:
        pass
    cli.close()
    txt = buf.decode('utf-8', 'replace')
    i = txt.find('G1MON')
    if i < 0:
        return None
    try:
        return json.loads(txt[i + 5:].strip().split('\n')[0])
    except Exception:
        return None


def analyse(m, d, prev, stall_marks):
    """返回 (问题列表, 备注列表)。问题 = 需要人介入的。"""
    bad, note = [], []
    if d is None:
        return ['**连不上**（SSH 失败）'], note

    # 1) GPU 空转
    #   ★ 2026-10-04 修：**memv<500 不能凭单次采样就升级为报警**。
    #     实测（监视子代理 round 21）：B 机 GPU 1 瞬时 4 MiB 是 **run 边界的空档**
    #     （上一 run 于 18:09:42 收尾 → 下一 run 18:11:31 开始训练，约 **1.8 min**：
    #      teardown + 数据集扫描 + 建模，期间**没有 CUDA 上下文**，显存自然回到 ~0）。
    #     那是**正常**的，约占 25 min 周期的 7%。而原判据单次即报 ⇒
    #     **每个 run 边界都会产生一条幽灵报警**（B 剩 ~16 run、A 剩 ~35 run ⇒ 几十条）。
    #   ⇒ 改为与利用率同款：**连续两次**才升级；单次只作备注。
    for line in d.get('gpu', []):
        try:
            idx, mem, util = [x.strip() for x in line.split(',')]
            memv = int(mem.split()[0])
        except Exception:
            continue
        # ★★ 2026-10-04 修（监视子代理第 3 次报出）：**完工豁免**。
        #   机器跑完 40/40 后卡本来就该是空的，但空转计数仍会每轮 +1
        #   ⇒ **每轮重复报一次"空转"**，纯噪声（实测 round 42：B 队列 0/训练 0/已建 40/已完成 40）。
        #   判据：`done >= 40 and queue == 0` ⇒ **完工态**，压制空转升级；
        #   但**仍有未完成 run 的机器**照常升级 —— 那才是真该报的。
        _total = len(d.get('runs', {}))
        _done = int(d.get('done') or 0)
        _finished = (_done >= 40 and d.get('queue', '0') == '0')
        key = 'gpu_idle_%s' % idx
        if memv < 500 and _finished:
            stall_marks[key] = 0
            note.append('GPU %s 空（%d MiB）—— **完工态**（已完成 %d/40、队列 0），不判空转'
                        % (idx, memv, _done))
            continue
        if memv < 500:
            stall_marks[key] = stall_marks.get(key, 0) + 1
            if stall_marks[key] >= 2:
                bad.append('空转：GPU %s 连续 %d 次只占 %d MiB（无任务）—— 单次是 run 边界空档，'
                           '**连续两次才判空转**' % (idx, stall_marks[key], memv))
            else:
                note.append('GPU %s 本次只占 %d MiB —— 疑为 run 边界空档（约 1–2 min，正常）；'
                            '连续两次才升级为报警' % (idx, memv))
        else:
            stall_marks[key] = 0
            if util.rstrip('%') == '0':
                note.append('GPU %s 利用率 0%%（可能处于 run 之间的加载/扫描，需连续两次才判停滞）' % idx)

    # 2) 外部进程
    procs = d.get('procs', '')
    if procs and d.get('queue', '0') == '0' and d.get('train', '0') == '0':
        bad.append('卡上有进程但**没有 g1 队列/训练**：%s（疑外部抢占）' % procs[:120])

    # 3) 队列死
    total = len(d.get('runs', {}))
    done = int(d.get('done') or 0)
    if d.get('queue', '0') == '0' and total < 40 and done < 40:
        bad.append('**队列进程消失**：已建 %d/40、已完成 %d/40 ⇒ 任务被打断（会话断开会把任务带走）'
                   % (total, done))

    # 4) 降批 / OOM
    for b in d.get('batch', []):
        b = b.strip()
        if b and 'batch=32' not in b:
            bad.append('**降批**：%s（协议要求 batch=32）' % b)
    if d.get('oom') not in ('0', '', None):
        bad.append('日志里出现 out of memory：%s 个文件' % d.get('oom'))

    # 5) 停滞
    runs = d.get('runs', {})
    if prev:
        stuck = []
        for k, v in runs.items():
            pv = prev.get(k)
            if pv is not None and v == pv and v < 100:
                stall_marks[k] = stall_marks.get(k, 0) + 1
                if stall_marks[k] >= 3:
                    stuck.append('%s（%d 轮，连续 %d 次无增长）' % (k, v, stall_marks[k]))
            else:
                stall_marks[k] = 0
        if stuck:
            bad.append('**停滞**：%s' % '；'.join(stuck))

    # 6) 磁盘
    try:
        avail = int(d.get('disk') or '999')
        if avail < 20:
            bad.append('磁盘可写空间仅 %d GB' % avail)
    except Exception:
        pass

    note.append('队列 %s ｜ 训练 %s ｜ 已建 %d/40 ｜ 已完成 %s/40 ｜ 日志OOM %s ｜ 盘余 %s GB'
                % (d.get('queue'), d.get('train'), total, done, d.get('oom'), d.get('disk')))
    return bad, note


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--loop', type=int, default=0, help='每 N 秒采样一次并持续（0=只采样一次）')
    ap.add_argument('--state', default=os.path.join(HERE, '_g1_monitor_state.json'))
    a = ap.parse_args()

    try:
        import _cloud_creds as C
    except Exception:
        print('缺 `_cloud_creds.py`（需 A_PW / B_PW）'); return 2

    state = {}
    if os.path.exists(a.state):
        try:
            state = json.load(io.open(a.state, encoding='utf-8'))
        except Exception:
            state = {}
    prev = state.get('runs', {})
    stall = state.get('stall', {})
    round_no = state.get('round', 0)

    while True:
        round_no += 1
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        global SRC_FINGERPRINT
        if SRC_FINGERPRINT is None:
            import hashlib
            SRC_FINGERPRINT = hashlib.md5(
                io.open(os.path.abspath(__file__), 'rb').read()).hexdigest()[:10]
        print('本进程源码指纹 %s（与盘上文件不符即说明**跑的是旧代码**，需重启）' % SRC_FINGERPRINT)
        print('=' * 74)
        print('第 %d 次采样  %s' % (round_no, ts))
        allbad = []
        runs_now = {}
        for m in MACHINES:
            pw = getattr(C, m['pw_key'], None)
            d = sample(m, pw) if pw else None
            bad, note = analyse(m, d, prev.get(m['tag']), stall.setdefault(m['tag'], {}))
            print('--- %s 机（%s）---' % (m['tag'], m['lanes']))
            for n in note:
                print('    · ' + n)
            for b in bad:
                print('    ★★★ ' + b)
            allbad += ['%s: %s' % (m['tag'], b) for b in bad]
            if d:
                runs_now[m['tag']] = d.get('runs', {})
            else:
                # ★★ 2026-10-04 修（监视子代理报出）：采样失败时**不能把该机从 runs 里丢掉**。
                #   原逻辑只在 `d` 为真时写 runs_now[tag] ⇒ 失败那一轮该机在状态文件里**消失**
                #   ⇒ 下一轮 `prev.get(tag)` 是 None、`if prev:` 为假 ⇒ **该机的停滞比较被跳过一轮**。
                #   实测（round 34）：B 机连不上，状态里 `B present_in_state` = False。
                #   ★ 该缺陷是**保守**的（不会产生假阳性，只是停滞升级可能晚一轮），但既然要"能报就报"，
                #     就该把上一轮的 runs **原样带过去**，让下一轮的比较**仍有基准**。
                #   （带过去是安全的：如果那一轮真的停了，下一轮的成功采样会看到轮数没涨，
                #     停滞计数照常 +1，不会因为"带了旧值"而漏报。）
                carried = prev.get(m['tag'])
                if carried:
                    runs_now[m['tag']] = carried
                    print('    · 本机采样失败 ⇒ 沿用上一轮 runs 作基准（%d 个 run），'
                          '以免下一轮跳过停滞比较' % len(carried))
        print('-' * 74)
        if allbad:
            print('本轮发现 %d 个问题：' % len(allbad))
            for b in allbad:
                print('  ★ ' + b)
        else:
            print('本轮无异常、无空转。')

        io.open(a.state, 'w', encoding='utf-8', newline='\n').write(
            json.dumps(dict(round=round_no, ts=ts, runs=runs_now, stall=stall,
                            last_bad=allbad), ensure_ascii=False, indent=1))
        # ★★ 2026-10-04 修（监视子代理第 4 次报出，**最严重的一次**）：
        #   `prev` 原来只在 `while True:` **之前**读一次、循环内**从不重新赋值**
        #   ⇒ 每一轮的"上一轮"永远是**循环启动时的快照** ⇒ 停滞判据形同虚设。
        #   因为 `v == pv` 只可能在"当前轮数恰好等于启动时的轮数"成立：
        #     · 启动时就已停滞的 run（一直等于启动值）⇒ **能报**；
        #     · **启动后才停滞的 run**（先涨到 70 再停）⇒ 永远不等于启动值 ⇒ 计数每轮被清零 ⇒ **永不报**。
        #   而"进程活着但不再训练"恰恰是**后者**——所以这条缺陷把停滞检测变成了死代码。
        #   证据（子代理提供）：本地合成复现；且 round 43 的承载行打印"沿用上一轮 runs（37 个 run）"，
        #   而真实上一轮（42）是 **40** —— 37 正是它循环启动时（20:51）B 的数，**陈旧基准泄漏到了输出里**。
        #   ⇒ 修法：每轮写盘后 `prev = runs_now`，让比较真正是"相邻两轮"。
        #     （副作用是预期的、正确的：run 被从头重跑时轮数下降 ⇒ 计数清零，那本该清零。）
        prev = dict(runs_now)
        if not a.loop:
            break
        time.sleep(a.loop)
    return 0


if __name__ == '__main__':
    sys.exit(main())
