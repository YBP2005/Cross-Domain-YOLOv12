# -*- coding: utf-8 -*-
"""29_A12_arch_axis.py —— **A12：架构轴（把 §4.4 从"一格"扩成"普查"）**

## 为什么

新稿 §4.4 是**全稿最弱的一环**：它只用一个格（`y11_shwd→sfchd`，yolo11n vs yolo12n）说
"第二个架构上方向复制、量级不迁移"。
而 `A9_全域预算轴扫描.md` 的普查里冒出了两个**从没被引用过的架构复制**：
`y11_shwd→sfchd / y11`（−1.277, t=−5.46, 3/3）与 `y26_shwd→sfchd / y26`（−1.170, t=−5.69, 3/3）。
⇒ 本件把架构轴系统化：**同一格上不同 backbone 的增益对照**。

## 口径

* 增益 = 逐种子 `(lr005 − base)`，pp，列 `test_map50_95`；
* **架构取自 `base/run_backbone_map.csv` 的 `backbone` 列，不得按 `family` 或 run 名推断**（A7 §7）；
* `unknown(*)` 的 run 一律排除（不猜）。
"""
import io
import os
import sys
import math
import statistics as st
import collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _cells as C

KEY = 'test_map50_95'
MIN_N = 3
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'analysis')
L = []


def w(s=''):
    L.append(s)


def tstat(v):
    if len(v) < 2:
        return float('nan')
    sd = st.stdev(v)
    return st.mean(v) / (sd / math.sqrt(len(v))) if sd > 0 else float('nan')


def main():
    rows, G = C.load()
    bb = C.load_backbone()
    w('# A12 架构轴普查')
    w()
    w('> 数据 `base/run_table_canonical.csv` + `base/run_backbone_map.csv`。')
    w('> 架构**按 `backbone` 列**取，不按 `family`/run 名推断（见 `A7_族混杂复核.md` §7）。')
    w('> 增益 = 逐种子 `(lr005−base)`，pp，`test_map50_95`。')
    w()

    # (pair, lb, ep) -> backbone -> {seed: gain}
    ax = collections.defaultdict(lambda: collections.defaultdict(dict))
    for k in G:
        p, f, lb, ep = k
        for s, by in G[k].items():
            b = C._pick(by.get('base', []), KEY)
            l = C._pick(by.get('lr005', []), KEY)
            if b is None or l is None:
                continue
            back = bb.get(b['run']) or bb.get(l['run']) or ''
            if not back or back.startswith('unknown'):
                continue
            ax[(p, lb, ep)][back][s] = (C.f(l[KEY]) - C.f(b[KEY])) * 100

    multi = []
    for k, v in ax.items():
        keep = {b: d for b, d in v.items() if len(d) >= MIN_N}
        if len(keep) >= 2:
            multi.append((k, keep))
    w('同格上**至少两种 backbone、各 ≥%d 个配对种子**的格：**%d** 个。' % (MIN_N, len(multi)))
    w()

    w('## 一、同格多架构对照')
    w()
    w('| 配对 | 预算 | 轮数 | 架构 | n | 增益(pp) | t | 两架构之差 |')
    w('|---|---|---|---|---|---|---|---|')
    detail = []
    for k, keep in sorted(multi, key=str):
        backs = sorted(keep, key=lambda b: -st.mean(list(keep[b].values())))
        m = {b: st.mean(list(keep[b].values())) for b in backs}
        for i, b in enumerate(backs):
            vals = list(keep[b].values())
            if i == 0:
                diff = ''
            else:
                d = m[b] - m[backs[0]]
                diff = '**%+.3f** vs `%s`' % (d, backs[0])
            w('| `%s` | %s | %s | `%s` | %d | **%+.3f** | %+.2f | %s |'
              % (k[0], k[1], k[2], b, len(vals), st.mean(vals), tstat(vals), diff))
        detail.append((k, keep, m, backs))
    w()

    w('## 二、在同一格上按 `backbone` 分组的增益（跨全部格汇总）')
    w()
    agg = collections.defaultdict(list)
    for k, keep, m, backs in detail:
        for b, v in keep.items():
            agg[b].append(st.mean(list(v.values())))
    w('| backbone | 参与格数 | 增益均值(pp) | 中位 | 最小 | 最大 |')
    w('|---|---|---|---|---|---|')
    for b in sorted(agg, key=lambda x: -len(agg[x])):
        v = agg[b]
        w('| `%s` | %d | %+.3f | %+.3f | %+.3f | %+.3f |'
          % (b, len(v), st.mean(v), st.median(v), min(v), max(v)))
    w()

    w('## 三、§4.4 的那一格（`y11_shwd→sfchd`）逐架构')
    w()
    hit = [d for d in detail if d[0][0] == 'y11_shwd→sfchd']
    if not hit:
        w('（本底座里没有该配对的同格多架构数据）')
    else:
        for k, keep, m, backs in hit:
            w('* **预算 %s / %s**：%s' % (k[1], k[2],
              '；'.join('`%s` n=%d **%+.3f**（t=%+.2f）' % (b, len(keep[b]), m[b], tstat(list(keep[b].values())))
                        for b in backs)))
    w()

    w('## 判读')
    w()
    # 不设 n 门槛，先看"格内有没有混架构"这件事本身
    mixed_cells = 0
    for k, v in ax.items():
        if len(v) >= 2:
            mixed_cells += 1
    w('* **格内混架构的格数（不设种子门槛）= %d**' % mixed_cells)
    if mixed_cells == 0:
        w('* ⇒ 在**本普查的口径**（格键 = `_cells.pair_of()`）下，没有任何一格内部含两种 backbone。')
        w('* ⚠⚠ **但这个 0 是"定义保证的"，不是实证发现** —— 2026-10-02 发现：')
        w('  `pair_of(r)` = `model→dataset`，而 **`model` 就是承载 backbone 的预训练权重**')
        w('  ⇒ **backbone 被写进了格键** ⇒ 普查**不可能**报出非 0。')
        w('  ⇒ 照这一段读会以为"数据不支持架构轴"，那是**判据的假象**。')
        w('* **正确做法**：把 backbone 从格键里显式拆出来，按 (backbone, 臂, 种子) 取数 ——')
        w('  见 `analysis\\A21_架构轴实测_2x2.md`（生成器 `scripts\\40_A21_arch_axis_real.py`）。')
        w('  补实验给出了**同数据/同族/同轮数、只换 backbone** 的 2×2×10，')
        w('  增益 `yolo11n` **+7.57 pp**、`yolo12n` **+8.66 pp**（`best_map50_95`，各 **10/10** 正号）')
        w('  ⇒ **架构轴是可测的。**')
        w('* 仍然成立的部分：稿内 §4.4 原说的"第二个架构"（`y11_shwd→sfchd`）**确实**是')
        w('  **另一个配对**（架构与数据配对混淆）—— 这一点没变，见 `A7_族混杂复核.md` §7。')
    w()
    w('> ⚠ **措辞纪律（2026-10-02 修订）**：')
    w('>  · **不得**再写"底座支撑不起独立的架构轴"（那是 `pair_of` 的循环造成的假象）；')
    w('>  · §4.4 **可以**写成"**同数据、同族、同轮数，只换 backbone，增益在两列上都复现**"，')
    w('>   但**必须**同时声明边界：**只有一个数据集（`dota15_20p_3way`）、只有一个轮数（100ep）**，')
    w('>   且种子是 **data-order 置换种子（torch seed 固定 42）**，不是 10 次独立训练。')
    w('>  · **不得**由本条外推成"跨架构普遍"。')
    w()
    if multi:
        w('* 同格多架构（各 ≥%d 种子）的格：%d 个。' % (MIN_N, len(multi)))

    os.makedirs(OUT, exist_ok=True)
    io.open(os.path.join(OUT, 'A12_架构轴普查.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    print()
    print('输出 -> %s' % os.path.join(OUT, 'A12_架构轴普查.md'))


if __name__ == '__main__':
    main()
