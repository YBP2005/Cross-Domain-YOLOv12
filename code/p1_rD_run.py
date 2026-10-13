#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""p1_rD_run.py — 在 **A 机本地**跑 99 个端点的点态 r_D 读数（评测，不训练）。

为什么是"本地"驱动：本机到 A 机的 SSH 在 detach 场景下会让远端 Python 撞断管而被杀。
把编排也放到 A 上，就只有一条短连接（启动 + 轮询），进程本身不依赖连接存活。

每个端点（= 一个已训 `best.pt`）跑一次 `theory_read_endpoint.py`，它已记录
`gradT_at_T_norm`（分子）、`spec_norm`、`delta_norm`、以及新加的 `theta_norm`。
于是点态 r_D = gradT_at_T_norm / (spec_norm * rho * theta_norm)。

用法（在 A 机上）：
    python3 p1_rD_run.py --rows /workspace/_rD_rows.csv --out /workspace/p1_rD \
        --gpus 0,1 --lanes-per-gpu 2 --rho 0.001
"""
import argparse
import csv
import os
import queue
import subprocess
import threading
import time

PY = '/root/yolo_env/bin/python'
SCRIPT = '/workspace/theory_read_endpoint.py'
WEIGHTS = '/workspace/weights'
RUNROOT = '/workspace/runs'


def resolve_yaml(name):
    """把表里记录的 yaml 文件名解析成实际路径。"""
    if not name:
        return ''
    if os.path.isabs(name) and os.path.exists(name):
        return name
    # ★ 2026-10-13：原先只搜这两处，导致 sfchd 全域（92/180 行、55/99 run）被判 skip：
    #   其 yaml 在 /root/ 与 /root/xcal/ 下。搜索根必须包含它们。
    for root in ('/root/datasets_mask', '/root/datasets', '/root', '/root/xcal', '/workspace'):
        for dirpath, _dirs, files in os.walk(root):
            if name in files:
                return os.path.join(dirpath, name)
    return ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rows', required=True, help='逐端点表（含 tag/data/src_data/split）')
    ap.add_argument('--out', default='/workspace/p1_rD')
    ap.add_argument('--gpus', default='0,1')
    ap.add_argument('--lanes-per-gpu', type=int, default=2)
    ap.add_argument('--rho', type=float, default=0.001)
    ap.add_argument('--batch', type=int, default=4)
    ap.add_argument('--nbatches', type=int, default=4)
    ap.add_argument('--lanczos', type=int, default=20)
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    rows = list(csv.DictReader(open(args.rows, encoding='utf-8')))
    if args.limit:
        rows = rows[:args.limit]
    tasks = []
    for r in rows:
        tag = (r.get('tag') or '').strip()
        parts = tag.split('__')
        if len(parts) < 3:
            continue
        src = parts[0].replace('_pretrain', '')
        run = parts[2]
        src_pt = os.path.join(WEIGHTS, src + '_pretrain.pt')
        tgt_pt = os.path.join(RUNROOT, run, 'weights', 'best.pt')
        tyaml = resolve_yaml(r.get('data', ''))
        syaml = resolve_yaml(r.get('src_data', '')) or tyaml
        if not (os.path.exists(src_pt) and os.path.exists(tgt_pt) and tyaml):
            tasks.append((tag, None, 'skip src=%s tgt=%s yaml=%s' % (os.path.exists(src_pt), os.path.exists(tgt_pt), bool(tyaml))))
            continue
        tasks.append((tag, dict(src_pt=src_pt, tgt_pt=tgt_pt, tyaml=tyaml, syaml=syaml,
                                split=r.get('split') or 'test', run=run), 'ok'))

    q = queue.Queue()
    for t in tasks:
        q.put(t)
    lock, done = threading.Lock(), [0]
    total = q.qsize()

    def worker(gpu, wid):
        while True:
            try:
                tag, info, st = q.get_nowait()
            except queue.Empty:
                return
            if info is None:
                with lock:
                    done[0] += 1
                    print('[%d/%d] %s -> %s' % (done[0], total, tag, st), flush=True)
                continue
            out = os.path.join(args.out, 'reads_%s.csv' % info['run'])
            cmd = ('cd /workspace && CUDA_VISIBLE_DEVICES=%d %s %s --tag "%s" --src %s --tgt %s '
                   '--data %s --src-data %s --split %s --batch %d --nbatches %d --lanczos %d --out %s'
                   % (gpu, PY, SCRIPT, tag, info['src_pt'], info['tgt_pt'], info['tyaml'],
                      info['syaml'], info['split'], args.batch, args.nbatches, args.lanczos, out))
            logp = os.path.join(args.out, 'err_%s_gpu%d_%d.log' % (info['run'], gpu, wid))
            with open(logp, 'w') as lf:
                r = subprocess.run(cmd, shell=True, stdout=lf, stderr=lf)
            with lock:
                done[0] += 1
                print('[%d/%d] gpu%d %s -> %s' % (done[0], total, gpu, tag, 'ok' if r.returncode == 0 else 'FAIL rc=%d' % r.returncode), flush=True)

    ts = []
    for gp in [int(x) for x in args.gpus.split(',')]:
        for w in range(args.lanes_per_gpu):
            t = threading.Thread(target=worker, args=(gp, w), daemon=True)
            t.start(); ts.append(t)
    for t in ts:
        t.join()
    print('rD DONE %d tasks (rho=%g)' % (total, args.rho))


if __name__ == '__main__':
    main()
