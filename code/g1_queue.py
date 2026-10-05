#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""g1_queue.py — G1 队列：**单卡单 run、顺序、断点续跑、逐 run 记时**。

设计要点（每条都有来由，不是风格问题）
--------------------------------------
1. **单卡单 run（顺序）**：登记家族的"偏离 1"已证明两泳道会触发 CUDA OOM，
   并迫使 ultralytics **私自把 batch 从 32 降到 16**（违反协议）⇒ G1 一开始就单跑。
2. **断点续跑**：每个 run 完成即在 `_g1_done.txt` 记一行；重跑本脚本会**跳过已完成的**。
   判"完成"的判据 = 权重目录存在 **且** `results.csv` 行数 ≥ epochs。
3. **`_PARTIAL_` 命名**：历史遗留（`/workspace/runs/_PARTIAL_cg_200ep_*`）说明被打断的 run
   会留下残缺目录。本脚本若发现以 `_PARTIAL_` 开头的目录，**不算完成**，会重跑。
4. **逐 run 记时**：把每个 run 的墙钟写进 `_g1_timing.csv`，
   用于把方案里"≈48 GPU·h"从**外推**换成**实测**。
5. **命名严格**（判读脚本按名字解析）：
       g1_c<格>_<域对>_<臂>_<预算>_s<种子>
   例：g1_c3_d15toaitod_base100_10p_s42
6. **B 机要避开 GPU 0**（那儿有别的项目的任务）⇒ 用 `--device 1`。

用法
----
    # A 机（跑 C3+C4：dota15→aitod）
    /root/yolo_env/bin/python /root/g1_queue.py --cells c3 c4 --device 0

    # B 机（跑 C1+C2：dota15→dota15；避开 GPU 0）
    /root/miniconda3/envs/yolo/bin/python /root/g1_queue.py --cells c1 c2 --device 1

    # 只试跑一个（记时用）—— 注意：**没有 --budgets 这个开关**了（预算由格绑定）
    ... --cells c3 --arms base100 --seeds 42

先 `--dry-run` 看它要跑什么、跳什么，再正式跑。
"""
import io
import os
import sys
import csv
import time
import argparse
import subprocess

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT = '/workspace/runs'                 # train_obj.py 的 PROJECT（固定）
W = '/workspace/weights'
RUNNER = '/workspace/train_obj.py'
DONE = '/root/_g1_done.txt'
TIMING = '/root/_g1_timing.csv'
EPOCHS = 100

# 格定义（与方案 §1 一致）。python/data/domain 全在这里，**不散落在命令里**。
# ★★ 2026-10-04 修接线错：**预算由「格」绑定，不再作为一个独立因子去乘**。
#   事故：原来 `queue = [(c, arm, b, s) for c in cells for b in budgets ...]`
#         —— `CELLS[cell]['data']` 决定用哪个 yaml，而 `--budgets` **只进 run 名字**、不影响取数，
#         两者相乘 ⇒ 每个格被跑两遍（一遍挂 `10p` 名、一遍挂 `50p` 名），**总量从 80 翻到 160**。
#         实测：`g1_c1_..._50p_s42` 与 `g1_c1_..._10p_s42` 的 args.yaml 里 data 都是 `dota15_10p.yaml`，
#         且 100 行 mAP50-95 **逐行完全相同** ⇒ 确认是重复。
#   ⇒ 现在每个格**自带预算**，一一对应，`--budgets` 已删除。
CELLS = {
    'c1': dict(domain='d15tod15',  budget='10p', data='/root/datasets_mask/dota15_yolo/dota15_10p.yaml',
               pretrain=W + '/dota15_pretrain.pt', machine='B'),
    'c2': dict(domain='d15tod15',  budget='50p', data='/root/datasets_mask/dota15_yolo/dota15_50p.yaml',
               pretrain=W + '/dota15_pretrain.pt', machine='B'),
    'c3': dict(domain='d15toaitod', budget='10p', data='/root/datasets/AI-TOD_yolo/aitod_10p.yaml',
               pretrain=W + '/dota15_pretrain.pt', machine='A'),
    'c4': dict(domain='d15toaitod', budget='50p', data='/root/datasets/AI-TOD_yolo/aitod_50p.yaml',
               pretrain=W + '/dota15_pretrain.pt', machine='A'),
}
ARMS = {'base100': None, 'strat100': 0.005}      # 臂 -> lr（None = 用默认 0.001）
SEEDS = list(range(42, 52))                      # 42..51，十枚


def run_name(cell, arm, seed):
    """★ 预算取自**格自己**（CELLS[cell]['budget']），不再由调用方传 —— 这是防复发的关键。"""
    return 'g1_%s_%s_%s_%s_s%d' % (cell, CELLS[cell]['domain'], arm, CELLS[cell]['budget'], seed)


def is_done(name):
    """完成判据：权重目录在 **且** results.csv 行数 ≥ epochs。`_PARTIAL_` 前缀视为未完成。"""
    for d in (os.path.join(PROJECT, name), os.path.join(PROJECT, '_PARTIAL_' + name)):
        pass
    d = os.path.join(PROJECT, name)
    if not os.path.isdir(d):
        return False
    csvp = os.path.join(d, 'results.csv')
    if not os.path.exists(csvp):
        return False
    try:
        with io.open(csvp, encoding='utf-8', errors='replace') as fh:
            n = sum(1 for _ in fh)
        return n >= EPOCHS
    except Exception:
        return False


def has_partial(name):
    d = os.path.join(PROJECT, '_PARTIAL_' + name)
    return os.path.isdir(d)


def load_done():
    if not os.path.exists(DONE):
        return set()
    with io.open(DONE, encoding='utf-8', errors='replace') as fh:
        return set(l.strip() for l in fh if l.strip())


def append(path, line):
    with io.open(path, 'a', encoding='utf-8', newline='\n') as fh:
        fh.write(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cells', nargs='+', required=True, choices=sorted(CELLS))
    ap.add_argument('--device', default='0', help='CUDA_VISIBLE_DEVICES 的值（B 机用 1）')
    ap.add_argument('--arms', nargs='+', default=sorted(ARMS), choices=sorted(ARMS))
    ap.add_argument('--seeds', nargs='+', type=int, default=SEEDS)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--timeout', type=int, default=6 * 3600, help='单 run 超时（秒），默认 6h')
    a = ap.parse_args()

    python = sys.executable
    # ★ 不变式：**同一域对内**每个预算恰好绑一个格。
    #   ⚠ 第一版写成"全局预算唯一" ⇒ 立刻报"预算 10p 同时绑到 c1 与 c3" —— 那是**假红**：
    #     c1(dota15,10p) 与 c3(aitod,10p) **本来就该共用** 10p 这个标签（两个域对各自两档）。
    seen = {}
    for c in CELLS:
        key = (CELLS[c]['domain'], CELLS[c]['budget'])
        if key in seen:
            sys.stderr.write('★ 不变式破坏：域对 %s 的预算 %s 同时绑到 %s 与 %s\n'
                             % (key[0], key[1], seen[key], c))
            return 4
        seen[key] = c
    queue = [(c, arm, CELLS[c]['budget'], s)
             for c in a.cells for arm in a.arms for s in a.seeds]
    print('=' * 70)
    print('G1 队列：%d 个 run ｜ device=%s ｜ python=%s' % (len(queue), a.device, python))
    print('=' * 70)

    done = load_done()
    if not os.path.exists(TIMING):
        append(TIMING, 'run,cell,arm,budget,seed,seconds,rc\n')

    todo, skip = [], []
    for c, arm, b, s in queue:
        nm = run_name(c, arm, s)
        if nm in done and is_done(nm):
            skip.append((nm, 'done'))
        elif is_done(nm):
            skip.append((nm, 'results.csv 完整'))
            append(DONE, nm + '\n')
        else:
            todo.append((c, arm, b, s, nm, '重跑(_PARTIAL_ 残留)' if has_partial(nm) else 'new'))

    print('要跑 %d ｜ 跳过 %d' % (len(todo), len(skip)))
    for nm, why in skip:
        print('  [跳过] %-44s %s' % (nm, why))
    for c, arm, b, s, nm, why in todo:
        print('  [跑]   %-44s %s' % (nm, why))

    if a.dry_run:
        print('\ndry-run 结束（未执行）。去掉 --dry-run 即开始。')
        return 0
    if not todo:
        print('\n全部已完成。')
        return 0

    os.makedirs(PROJECT, exist_ok=True)
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(a.device), PYTHONIOENCODING='utf-8')
    t_all = time.time()
    for k, (c, arm, b, s, nm, why) in enumerate(todo, 1):
        cmd = [python, RUNNER, '--loss', 'shapeiou', '--epochs', str(EPOCHS),
               '--name', nm, '--data', CELLS[c]['data'], '--pretrain', CELLS[c]['pretrain'],
               '--shuffle-seed', str(s)]
        lr = ARMS[arm]
        if lr is not None:
            cmd += ['--lr', str(lr)]
        log = '/root/_g1_%s.log' % nm
        print('\n[%d/%d] %s  (%s, dev=%s)' % (k, len(todo), nm, why, a.device))
        print('        ' + ' '.join(cmd))
        t0 = time.time()
        try:
            with io.open(log, 'w', encoding='utf-8', newline='\n') as fh:
                rc = subprocess.call(cmd, env=env, stdout=fh, stderr=subprocess.STDOUT,
                                     timeout=a.timeout)
        except subprocess.TimeoutExpired:
            rc = 'TIMEOUT'
        dt = time.time() - t0
        print('        用时 %.1f s（%.2f h），rc=%s，日志 %s' % (dt, dt / 3600, rc, log))
        append(TIMING, '%s,%s,%s,%s,%d,%.1f,%s\n' % (nm, c, arm, b, s, dt, rc))
        if rc == 0 and is_done(nm):
            append(DONE, nm + '\n')
        else:
            print('        ⚠ 未判为完成（rc=%s，或 results.csv 行数不足 %d）⇒ 下次重跑本脚本会再试'
                  % (rc, EPOCHS))

    el = time.time() - t_all
    print('\n' + '=' * 70)
    print('队列结束：%d 个 run，总用时 %.2f h（%.1f s）' % (len(todo), el / 3600, el))
    print('逐 run 记时 -> %s' % TIMING)
    print('完成清单   -> %s' % DONE)
    # 用实测外推全盘（方案 §6 的外推换成实测）
    try:
        with io.open(TIMING, encoding='utf-8', errors='replace') as fh:
            rows = [r for r in csv.DictReader(fh) if r.get('seconds')]
        secs = [float(r['seconds']) for r in rows if r['rc'] == '0']
        if secs:
            avg = sum(secs) / len(secs)
            print('实测单 run 均值 %.1f s（%.2f h，n=%d）⇒ 40 run/机 ≈ %.1f h'
                  % (avg, avg / 3600, len(secs), avg * 40 / 3600))
    except Exception as e:
        print('(记时汇总失败：%s)' % e)
    print('=' * 70)
    return 0


if __name__ == '__main__':
    sys.exit(main())
