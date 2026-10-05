#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""pack_g1_runs.py —— 在本机把 G1 的**本案** run 打包成一个归档（供取回）。

★ 为什么需要这一件：云机用完要**归还**，而 run 的文本产物必须**先取回**才能复算与归档。
  本脚本**只读** run 目录，把下列内容打进一个 tar.gz：
    · 每个本案 run 的 `results.csv`（逐 epoch 指标）与 `args.yaml`（协议指纹）；
    · 每 run 的 lane 日志 `/root/_g1_<run>.log`（若存在且 < 2 MB）；
    · `/root/_g1_done.txt`、`/root/_g1_timing.csv`；
    · 各 run 的 `weights/` **只记文件名与大小**（不打包权重，权重 MB 级且非必需）。

★ "本案 run" 的判据：名字匹配 `g1_c<N>_...` —— 这条**必须**存在，否则会把 9 月 19 日
  旧原型的 `g1_aitod20_*` 也打进来（那批与 G1 无关，实测有 10 个）。

用法：
    python3 pack_g1_runs.py                 # 打包到 /root/g1_archive_<host>.tar.gz
    python3 pack_g1_runs.py --out /root/x.tar.gz
"""
import io
import os
import re
import sys
import glob
import json
import tarfile
import hashlib
import socket

RUNS = '/workspace/runs'
PAT = re.compile(r'^g1_c\d_[a-z0-9]+_(base100|strat100)_(10p|50p)_s\d+$')


def main():
    out = '/root/g1_archive_%s.tar.gz' % socket.gethostname()
    if '--out' in sys.argv:
        out = sys.argv[sys.argv.index('--out') + 1]

    runs = sorted(d for d in glob.glob(os.path.join(RUNS, 'g1_c*'))
                  if os.path.isdir(d) and PAT.match(os.path.basename(d)))
    print('本案 run 目录：%d' % len(runs))
    manifest = []
    staged = []

    # 权重清单（只记名字与大小）
    for d in runs:
        for sub in ('results.csv', 'args.yaml'):
            p = os.path.join(d, sub)
            if os.path.exists(p):
                staged.append((p, '%s/%s' % (os.path.basename(d), sub)))
        wd = os.path.join(d, 'weights')
        if os.path.isdir(wd):
            for w in sorted(os.listdir(wd)):
                wp = os.path.join(wd, w)
                manifest.append('%s/weights/%s\t%d' % (os.path.basename(d), w,
                                                       os.path.getsize(wp)))
        lg = '/root/_g1_%s.log' % os.path.basename(d)
        if os.path.exists(lg) and os.path.getsize(lg) < 2 * 1024 * 1024:
            staged.append((lg, 'logs/%s.log' % os.path.basename(d)))
    for extra in ('/root/_g1_done.txt', '/root/_g1_timing.csv',
                  '/root/_g1_done.txt.bak_wiring'):
        if os.path.exists(extra):
            staged.append((extra, 'accounting/%s' % os.path.basename(extra)))

    print('待打包文件：%d（权重清单 %d 行，权重本体不打包）' % (len(staged), len(manifest)))

    with tarfile.open(out, 'w:gz') as tf:
        for src, arc in staged:
            tf.add(src, arcname=arc)
        # 权重清单与一个自述
        import tempfile
        d = tempfile.mkdtemp()
        mf = os.path.join(d, 'WEIGHTS_INVENTORY.tsv')
        io.open(mf, 'w', encoding='utf-8', newline='\n').write(
            'run/weight\tbytes\n' + '\n'.join(manifest) + '\n')
        tf.add(mf, arcname='WEIGHTS_INVENTORY.tsv')
        note = os.path.join(d, 'README.txt')
        io.open(note, 'w', encoding='utf-8', newline='\n').write(
            'G1 run archive\n'
            'host: %s\n'
            'runs (本案, 名字匹配 g1_c<N>_...): %d\n'
            'contents: per-run results.csv + args.yaml + lane log; '
            'accounting files; weights inventory (weights NOT included).\n'
            'excluded on purpose: old prototype runs named g1_aitod20_* (unrelated).\n'
            % (socket.gethostname(), len(runs)))
        tf.add(note, arcname='README.txt')

    h = hashlib.sha256(open(out, 'rb').read()).hexdigest()
    print('打包完成 -> %s' % out)
    print('字节数 %d' % os.path.getsize(out))
    print('sha256 %s' % h)
    print('G1PACK %s %d %s' % (out, os.path.getsize(out), h))
    return 0


if __name__ == '__main__':
    sys.exit(main())
