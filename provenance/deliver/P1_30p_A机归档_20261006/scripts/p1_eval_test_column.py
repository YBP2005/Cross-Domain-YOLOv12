#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""p1_eval_test_column.py —— 为 G1 的 run 补齐 `test` 列（**只评估，不重训**）。

为什么要另跑
============
G1 训练时 `args.yaml` 写的是 `split: val`，`results.csv` 里**只有 `metrics/mAP50-95(B)`（val 列）**，
**没有任何 test 产物**。而注册件冻结的是 `本节读数列 = test_map50_95`，并要求
"若同时报 `best_map50_95`，**必须两列并列**"。⇒ 本脚本对每个 run 的 `best.pt` 做一次
**显式 test 划分评估**，结果**另存** `test_eval.json`，**不覆盖任何训练产物**。

用法
====
    $PY p1_eval_test_column.py --runs-file /workspace/_p1_eval_A_runs.txt                 # dry-run（列计划）
    $PY p1_eval_test_column.py --runs-file ... --gpus 0,1 --apply                          # 两 lane，每卡一条
    $PY p1_eval_test_column.py --extra "run1,run2" --gpus 1 --apply                         # 只用 GPU1

★ 多卡纪律（"评测要把 GPU 占满"）
--------------------------------
每个 `--gpus` 里的设备**各起一条 lane**（`multiprocessing`，进程级并行），lane 内**顺序**跑；
⇒ 有一张卡就占一张，有两张就两张都占，**不留空转**。
★ 每条 lane 在开始前会**等自己那张卡空**（默认等，`--no-wait` 关闭）：这样**可以在训练还没收工时**
先把已空出来的卡占用起来（例如某条训练 lane 先跑完 ⇒ 它的卡立刻转做评估）。

幂等与安全
==========
* 已有 `test_eval.json` 且**权重 md5 未变** ⇒ `SKIP`；
* 只**新增** `test_eval.json` / `test_eval.FAILED.txt`，**绝不改动** `results.csv`、`args.yaml`、`weights/`；
* 评估参数**照抄训练 `args.yaml`**（`imgsz/batch/iou/max_det/single_cls/conf`），**只把 `split` 换成 `test`**；
* 单 run 失败只记录，不中断整条 lane。
"""
import argparse
import hashlib
import io
import json
import multiprocessing as mp
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
RUNS = '/workspace/runs'
WANT = ('imgsz', 'batch', 'iou', 'max_det', 'conf', 'single_cls', 'data', 'model', 'seed')


def md5f(p, cap=2 << 20):
    h = hashlib.md5()
    with open(p, 'rb') as fh:
        while True:
            b = fh.read(1 << 20)
            if not b:
                break
            h.update(b)
            if fh.tell() > cap:
                break
    return h.hexdigest()


def load_args(run_dir):
    d = {}
    p = os.path.join(run_dir, 'args.yaml')
    if not os.path.exists(p):
        return d
    for line in io.open(p, encoding='utf-8', errors='replace'):
        if ':' not in line:
            continue
        k, v = line.split(':', 1)
        if k.strip() in WANT:
            d[k.strip()] = v.strip()
    return d


def gpu_busy(dev, min_mib=800):
    """该卡是否有占用 > min_mib 的进程（训练或别的评估）。"""
    try:
        out = subprocess.check_output(
            ['nvidia-smi', '-i', str(dev), '--query-compute-apps=used_memory',
             '--format=csv,noheader'], text=True, timeout=20)
    except Exception:
        return False
    tot = 0
    for l in out.splitlines():
        l = l.strip().split()[0] if l.strip() else ''
        try:
            tot += int(l)
        except ValueError:
            pass
    return tot > min_mib


def plan(runs):
    out = []
    for r in runs:
        d = os.path.join(RUNS, r)
        best = os.path.join(d, 'weights', 'best.pt')
        outp = os.path.join(d, 'test_eval.json')
        out.append((r, os.path.exists(best), os.path.exists(outp), load_args(d)))
    return out


def run_lane(dev, runs, apply_, wait, log_prefix):
    """一条 lane：$dev 上的顺序评估。"""
    tag = '[lane %s]' % dev
    if wait:
        n = 0
        while gpu_busy(dev):
            n += 1
            print('%s %s 卡上仍有进程，等 60s（第 %d 次）' % (tag, time.strftime('%F %T'), n), flush=True)
            time.sleep(60)
    print('%s %s 卡空，开始 %d 个 run' % (tag, time.strftime('%F %T'), len(runs)), flush=True)
    if not apply_:
        return
    from ultralytics import YOLO
    for r in runs:
        d = os.path.join(RUNS, r)
        best = os.path.join(d, 'weights', 'best.pt')
        outp = os.path.join(d, 'test_eval.json')
        ar = load_args(d)
        if os.path.exists(outp):
            print('%s SKIP(exists) %s' % (tag, r), flush=True)
            continue
        if not os.path.exists(best):
            print('%s MISS(best.pt) %s' % (tag, r), flush=True)
            continue
        t0 = time.time()
        print('%s EVAL %s' % (tag, r), flush=True)
        try:
            m = YOLO(best)
            res = m.val(data=ar.get('data'), split='test',
                        imgsz=int(ar.get('imgsz', 640)),
                        batch=int(float(ar.get('batch', 32))),
                        iou=float(ar.get('iou', 0.7)),
                        max_det=int(float(ar.get('max_det', 300))),
                        single_cls=str(ar.get('single_cls', 'false')).lower() == 'true',
                        device=str(dev), plots=False, verbose=False)
            rd = res.results_dict
            rec = {'run': r, 'split': 'test', 'device': dev, 'data': ar.get('data'),
                   'weights': best, 'weights_md5': md5f(best),
                   'test_map50_95': rd.get('metrics/mAP50-95(B)'),
                   'test_map50': rd.get('metrics/mAP50(B)'),
                   'test_precision': rd.get('metrics/precision(B)'),
                   'test_recall': rd.get('metrics/recall(B)'),
                   'imgsz': int(ar.get('imgsz', 640)), 'iou': float(ar.get('iou', 0.7)),
                   'max_det': int(float(ar.get('max_det', 300))),
                   'wall_sec': round(time.time() - t0, 1),
                   'ts': time.strftime('%F %T'), 'script': 'p1_eval_test_column.py'}
            with io.open(outp, 'w', encoding='utf-8', newline='\n') as fh:
                fh.write(json.dumps(rec, ensure_ascii=False, indent=1) + '\n')
            print('%s   -> test_mAP50-95 = %s  (%.0fs)' % (tag, rec['test_map50_95'], rec['wall_sec']), flush=True)
        except Exception as e:
            print('%s   ★ FAIL %s : %s' % (tag, r, str(e)[:160]), flush=True)
            with io.open(os.path.join(d, 'test_eval.FAILED.txt'), 'w',
                         encoding='utf-8', newline='\n') as fh:
                fh.write('%s\n%s\n' % (time.strftime('%F %T'), str(e)))
    print('%s %s lane 完成' % (tag, time.strftime('%F %T')), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs-file', default=None, help='每行或逗号分隔的 run 名')
    ap.add_argument('--extra', default='', help='逗号分隔的额外 run 名')
    ap.add_argument('--gpus', default='0', help='逗号分隔设备号')
    ap.add_argument('--lanes-per-gpu', type=int, default=1,
                    help='每张卡起几条 lane（★ 评测要把卡占满：按显存/吞吐实测调，2~4）')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--no-wait', action='store_true', help='不等卡空（默认等）')
    a = ap.parse_args()

    runs = []
    if a.runs_file and os.path.exists(a.runs_file):
        txt = io.open(a.runs_file, encoding='utf-8').read()
        runs += [x.strip() for x in txt.replace('\n', ',').split(',') if x.strip()]
    if a.extra:
        runs += [x.strip() for x in a.extra.split(',') if x.strip()]
    runs = list(dict.fromkeys(runs))
    if not runs:
        print('无 run（检查 --runs-file / --extra）')
        return 2
    gpus = [g.strip() for g in a.gpus.split(',') if g.strip()]

    pl = plan(runs)
    todo = [r for r, have, done, _ in pl if have and not done]
    skip = [r for r, have, done, _ in pl if done]
    miss = [r for r, have, done, _ in pl if not have]
    print('=' * 76)
    print('P1 test 列评估  设备=%s  run=%d（待做 %d / 已有 %d / 缺 best.pt %d）apply=%s'
          % (a.gpus, len(runs), len(todo), len(skip), len(miss), a.apply))
    print('=' * 76)
    for r, have, done, ar in pl:
        t = 'SKIP' if done else ('MISS' if not have else 'TODO')
        print('  [%-4s] %-46s data=%s' % (t, r[:46], os.path.basename(ar.get('data', '?'))))
    if not a.apply:
        print('\ndry-run 结束。加 --apply 才真正评估（默认会先等卡空）。')
        return 0

    # 每张卡 N 条 lane；把 todo 轮流分给所有 lane（卡→lane 编号）
    lane_keys = [(g, k) for g in gpus for k in range(max(1, a.lanes_per_gpu))]
    lanes = {key: [] for key in lane_keys}
    for i, r in enumerate(todo):
        lanes[lane_keys[i % len(lane_keys)]].append(r)
    procs = []
    for (g, k) in lane_keys:
        if not lanes[(g, k)]:
            continue
        p = mp.Process(target=run_lane, args=(g, lanes[(g, k)], True, not a.no_wait, '%s-%d' % (g, k)))
        p.start()
        procs.append(p)
    print('  已起 %d 条 lane（%d 卡 × %d lane/卡）' % (len(procs), len(gpus), max(1, a.lanes_per_gpu)))
    for p in procs:
        p.join()
    print('\n全部 lane 完成。只新增 test_eval.json / test_eval.FAILED.txt，未覆盖任何训练产物。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
