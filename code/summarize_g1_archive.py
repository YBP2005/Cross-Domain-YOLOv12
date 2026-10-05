# -*- coding: utf-8 -*-
r"""summarize_g1_archive.py —— 从**本地归档**生成逐 run 摘要（不连云端）。

作用：把归档里的 40 个 `results.csv` 压成一张表，使这套数据**离线可核**。
列：run、格、域对、臂、预算、种子、轮数、训练图像数（由 args.yaml 的 data 推）、
    val mAP50-95（末轮）、以及 `data:` 声明（**接线证据**）。

★ 纪律：本件**只用归档里的文件**，不连网、不改云端任何东西。
"""
import io
import os
import re
import csv
import sys
import glob

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARCH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'provenance', 'deliver',
                    'G1_B机run归档_20261003')
PAT = re.compile(r'^(g1_c\d)_([a-z0-9]+)_(base100|strat100)_(10p|50p)_s(\d+)$')
# data 文件名 -> 训练图像数（实测）
NTRAIN = {'dota15_10p.yaml': 141, 'dota15_50p.yaml': 705,
          'aitod_10p.yaml': 1121, 'aitod_50p.yaml': 5607}


def main():
    rows = []
    for d in sorted(glob.glob(os.path.join(ARCH, 'g1_c*'))):
        if not os.path.isdir(d):
            continue
        name = os.path.basename(d)
        m = PAT.match(name)
        if not m:
            continue
        cell, dom, arm, bud, seed = m.groups()
        f = os.path.join(d, 'results.csv')
        data = ''
        ay = os.path.join(d, 'args.yaml')
        if os.path.exists(ay):
            for line in io.open(ay, encoding='utf-8', errors='replace'):
                if line.startswith('data:'):
                    data = os.path.basename(line.split(':', 1)[1].strip())
                    break
        n, last = 0, None
        if os.path.exists(f):
            rr = list(csv.DictReader(io.open(f, encoding='utf-8', errors='replace')))
            n = len(rr)
            if rr:
                last = rr[-1].get('metrics/mAP50-95(B)')
        rows.append(dict(run=name, cell=cell, domain=dom, arm=arm, budget=bud, seed=int(seed),
                         epochs=n, ntrain=NTRAIN.get(data, '?'), data=data,
                         val_map=last))
    outp = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                                        'provenance', 'deliver', 'G1_B机_逐run摘要.csv'))
    with io.open(outp, 'w', encoding='utf-8', newline='\n') as fh:
        w = csv.DictWriter(fh, fieldnames=['run', 'cell', 'domain', 'arm', 'budget', 'seed',
                                           'epochs', 'ntrain', 'data', 'val_map'])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print('逐 run 摘要 %d 行 -> %s' % (len(rows), outp))
    # 一致性小结
    bad = [r for r in rows if r['epochs'] != 100 or not r['data']]
    print('轮数≠100 或缺 data 的 run：%d' % len(bad))
    grp = {}
    for r in rows:
        grp.setdefault((r['cell'], r['arm']), []).append(r)
    print('按格×臂：')
    for k in sorted(grp):
        v = grp[k]
        print('  %s %-9s %2d 个；data=%s；ntrain=%s'
              % (k[0], k[1], len(v), v[0]['data'], v[0]['ntrain']))
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
