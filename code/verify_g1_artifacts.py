#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""verify_g1_artifacts.py —— 逐 run 核产物**并**核接线（只看产物，不采信 run 名）。

每条 run 检查：
  1. `results.csv` 行数 == 100（轮数齐）；
  2. `args.yaml` 存在，且其 `data:` **等于该格应有的 yaml**（★ 这条正是接线错的报警器）；
  3. `weights/` 非空（至少 `best.pt` 与 `last.pt`）；
  4. 打出一行：`<run 名>|<轮数>|<data 行>|<weights 文件数>|<OK 或 问题>`。

用法（只读，不写任何东西）：
    python3 verify_g1_artifacts.py            # 按格汇总
    python3 verify_g1_artifacts.py --all      # 逐 run 全列
"""
import os
import sys
import glob
import re

CELL_DATA = {
    'c1': '/root/datasets_mask/dota15_yolo/dota15_10p.yaml',
    'c2': '/root/datasets_mask/dota15_yolo/dota15_50p.yaml',
    'c3': '/root/datasets/AI-TOD_yolo/aitod_10p.yaml',
    'c4': '/root/datasets/AI-TOD_yolo/aitod_50p.yaml',
}
CELL_BUDGET = {'c1': '10p', 'c2': '50p', 'c3': '10p', 'c4': '50p'}
PAT = re.compile(r'^g1_(c\d)_([a-z0-9]+)_(base100|strat100)_(10p|50p)_s(\d+)$')
EPOCHS = 100


def main():
    show_all = '--all' in sys.argv
    runs = sorted(d for d in glob.glob('/workspace/runs/g1_c*') if os.path.isdir(d))
    print('本轮 run 目录：%d' % len(runs))
    per_cell, problems = {}, []
    for d in runs:
        b = os.path.basename(d)
        m = PAT.match(b)
        if not m:
            problems.append('%s：名字不符合命名规约' % b)
            continue
        cell, dom, arm, bud, seed = m.groups()
        f = os.path.join(d, 'results.csv')
        rows = (sum(1 for _ in open(f)) - 1) if os.path.exists(f) else -1
        ay = os.path.join(d, 'args.yaml')
        data = ''
        if os.path.exists(ay):
            for line in open(ay):
                if line.startswith('data:'):
                    data = line.split(':', 1)[1].strip()
                    break
        wd = os.path.join(d, 'weights')
        wfiles = sorted(os.listdir(wd)) if os.path.isdir(wd) else []
        has_best = any(x.startswith('best') for x in wfiles)
        has_last = any(x.startswith('last') for x in wfiles)

        bad = []
        if rows != EPOCHS:
            bad.append('轮数 %s≠%d' % (rows, EPOCHS))
        if not data:
            bad.append('args.yaml 无 data 行')
        elif data != CELL_DATA[cell]:
            bad.append('data=%s ≠ 应为 %s' % (os.path.basename(data), os.path.basename(CELL_DATA[cell])))
        if bud != CELL_BUDGET[cell]:
            bad.append('预算名 %s ≠ 该格 %s' % (bud, CELL_BUDGET[cell]))
        if not (has_best and has_last):
            bad.append('weights 缺 best/last（实有 %d 个文件）' % len(wfiles))
        key = (cell, arm)
        per_cell[key] = per_cell.get(key, 0) + 1
        if bad:
            problems.append('%s：%s' % (b, '；'.join(bad)))
        if show_all or bad:
            print('  %-46s %3s 轮 %-46s w=%-3d %s'
                  % (b, rows, os.path.basename(data) or '(无)', len(wfiles),
                     'OK' if not bad else '★' + '；'.join(bad)))
    print()
    print('按格×臂计数：')
    for k in sorted(per_cell):
        print('  %s %-9s %d 个' % (k[0], k[1], per_cell[k]))
    print()
    # ★ 2026-10-04 修：**A/B 机是分工的**（A 只跑 c3/c4，B 只跑 c1/c2）。
    #   原来假定 8 个 (格,臂) 组合都存在 ⇒ 在 B 上报 4 条"c3/c4 计数不符"的**假红**
    #   （本会话第 N 次：判据没考虑部署拓扑）。改为**只核该机实际出现的格**。
    exp = {}
    for (cell, arm), got in per_cell.items():
        exp[(cell, arm)] = 10
    present_cells = sorted(set(c for c, _ in per_cell))
    print('本机出现的格：%s（缺席的格属另一台机，不算问题）' % '、'.join(present_cells))
    for k, v in sorted(exp.items()):
        got = per_cell.get(k, 0)
        if got != v:
            problems.append('计数不符：%s %s 应 %d 实 %d' % (k[0], k[1], v, got))
    if problems:
        print('★ 问题 %d 条：' % len(problems))
        for x in problems:
            print('   · %s' % x)
        return 1
    print('全部通过：轮数齐、data 行与格一致、weights 齐、计数齐。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
