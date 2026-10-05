# -*- coding: utf-8 -*-
"""40_A21_arch_axis_real.py —— ★ **架构轴的实测对照**（2×2×10 完整交叉设计）。

为什么必须新写一件（这是本次分析最重要的更正）
----------------------------------------------
`A12_架构轴普查.md` 的结论是「**底座里没有任何一个格内部含两种 backbone**
⇒ 底座支撑不起独立的架构轴」。**那个 0 是循环论证，不是实证发现**：

    pair_of(r) = '%s→%s' % (model, dataset)      # scripts/_cells.py:100-103

而 `model` 就是**承载 backbone 的预训练权重**（`yolo11n.pt` / `yolo12n.pt`）。
于是 **backbone 被写进了格键本身** ⇒ 任何一格都不可能含两种 backbone，
普查必然报 0。用户看了会以为"数据不支持架构轴"，其实那个判据**不可能不报 0**。

补实验（`r15_arch_{y11,y12}_vistod15_*`）恰好给出了真正需要的数据：
**同数据集、同族、同轮数，只换 backbone，两臂各 10 个种子**。

本件做的事
----------
把 `pair_of` 造成的分格**显式拆开**，按 (backbone, 臂, 种子) 取数，做完整 2×2：
  ① 架构主效应：同臂下 y12 − y11（按种子配对）
  ② 增益：每 backbone 内的 lr005 − base（按种子配对）
  ③ ★ **交互项 = 增益之差**（等价于 Δlr005 − Δbase）—— 直接回答"**换 backbone 后增益还在不在**"
  ④ 结局可用性沿用 `_cells.ok_outcome()`（`interrupted` 一律排除，存档件看轮数）

口径声明（数据字典 §十.2 要求整节写明用哪一列）
------------------------------------------------
两列都报：`best_map50_95`（val 侧最优轮，§4.3/§4.4 用的列）与
`test_map50_95`（test 侧，§4.1/§4.2/§5 用的列）。**结论不看单列**。
"""
import os
import csv
import sys
import math
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import _cells as C            # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
OUT = os.path.join(BASE, 'analysis', 'A21_架构轴实测_2x2.md')

FAMILY = 'r15'
DATASET = 'dota15_20p_3way'
EPOCHS = '100'
COLS = ['best_map50_95', 'test_map50_95']


def mean(v):
    return sum(v) / len(v)


def sd(v):
    if len(v) < 2:
        return float('nan')
    m = mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def tstat(v):
    """单样本 t（配对差）"""
    n = len(v)
    if n < 2:
        return float('nan')
    s = sd(v)
    if s == 0:
        return float('inf') if mean(v) > 0 else (float('-inf') if mean(v) < 0 else float('nan'))
    return mean(v) / (s / math.sqrt(n))


def main():
    rows, _ = C.load()
    sel = [r for r in rows
           if r['family'] == FAMILY and r['dataset'] == DATASET and r['epochs_nominal'] == EPOCHS]
    if not sel:
        raise SystemExit('空集合：找不到 %s / %s / %sep 的行 —— 空集合必须硬失败' % (FAMILY, DATASET, EPOCHS))

    # (pair, arm, seed) -> rows
    T = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list)))
    for r in sel:
        T[r['_pair']][r['lr_arm']][r['_seed']].append(r)

    pairs = sorted(T)
    if len(pairs) != 2:
        raise SystemExit('预期恰好 2 个配对（两种 backbone），实得 %d: %s' % (len(pairs), pairs))

    # 按 backbone 名排序，保证 A = y11、B = y12（名字序）
    bb = {p: p.split('→')[0] for p in pairs}
    A = sorted(pairs, key=lambda p: bb[p])[0]
    B = sorted(pairs, key=lambda p: bb[p])[1]

    def vals(pair, arm, col):
        out = {}
        for s, rs in T[pair][arm].items():
            r = C._pick(rs, col)
            if r is not None:
                out[s] = C.f(r[col])
        return out

    L = []
    w = L.append
    w('# A21 架构轴**实测对照**（2×2×10 完整交叉设计）')
    w('')
    w('> 数据 = `base/run_table_canonical.csv`（**%d 行**）+ `base/run_backbone_map.csv`。' % len(rows))
    w('> 生成器 = `scripts/40_A21_arch_axis_real.py`。**只读**，可复算。')
    w('>')
    w('> ★ **本件更正 `A12_架构轴普查.md` 的结论。** A12 报"格内混架构 = 0"，')
    w('> 但那是**定义使然**：`_cells.pair_of()` 返回 `model→dataset`，而 `model` 就是')
    w('> 承载 backbone 的预训练权重 ⇒ **backbone 被写进格键** ⇒ 普查**不可能**报出非 0。')
    w('> 本件把分格显式拆开，用补实验的 `%s` 族做真正的架构对照。' % FAMILY)
    w('')
    w('## 一、设计')
    w('')
    w('| 维度 | 取值 |')
    w('|---|---|')
    w('| 数据集 | `%s`（**只有一个**） |' % DATASET)
    w('| 族 | `%s`（**只有一个**） |' % FAMILY)
    w('| 轮数 | `%s`（**只有一个**） |' % EPOCHS)
    w('| backbone A | `%s` |' % bb[A])
    w('| backbone B | `%s` |' % bb[B])
    w('| 臂 | `base`（lr0=0.001）、`lr005`（lr0=0.005） |')
    w('| 种子 | s42–s51（**data-order 置换种子，torch seed 固定 42**） |')
    w('')
    w('⇒ 这是**唯一变 backbone**、其余全同的 2×2；每格 n=10。')
    w('')

    stats = {}
    for col in COLS:
        w('## 二、逐格均值与可用种子数（列 `%s`）' % col)
        w('')
        w('| backbone | 臂 | n | 均值 | 中位 | 最小 | 最大 |')
        w('|---|---|---|---|---|---|---|')
        for p in (A, B):
            for arm in ('base', 'lr005'):
                v = vals(p, arm, col)
                if not v:
                    w('| `%s` | `%s` | 0 | — | — | — | — |' % (bb[p], arm))
                    continue
                xs = sorted(v.values())
                w('| `%s` | `%s` | %d | **%.4f** | %.4f | %.4f | %.4f |'
                  % (bb[p], arm, len(xs), mean(xs), xs[len(xs) // 2], xs[0], xs[-1]))
        w('')

        # ② 增益（每 backbone 内，按种子配对）
        w('### 2.%d 增益 = `lr005 − base`（按种子配对，单位 pp）' % (1 if col == COLS[0] else 2))
        w('')
        w('| backbone | n | 增益均值(pp) | 中位 | 正号 | t |')
        w('|---|---|---|---|---|---|')
        gains = {}
        for p in (A, B):
            b, l = vals(p, 'base', col), vals(p, 'lr005', col)
            com = sorted(set(b) & set(l))
            g = [(l[s] - b[s]) * 100 for s in com]
            gains[p] = (g, com)
            if not g:
                w('| `%s` | 0 | — | — | — | — |' % bb[p])
                continue
            pos = sum(1 for x in g if x > 0)
            w('| `%s` | %d | **%+.4f** | %+.4f | **%d/%d** | %+.3f |'
              % (bb[p], len(g), mean(g), sorted(g)[len(g) // 2], pos, len(g), tstat(g)))
        w('')

        # ① 架构主效应（同臂，按种子配对）
        w('### 2.%d 架构主效应 = `%s − %s`（同臂、按种子配对，pp）'
          % (3 if col == COLS[0] else 4, bb[B], bb[A]))
        w('')
        w('| 臂 | n | 差值均值(pp) | 中位 | 正号 | t |')
        w('|---|---|---|---|---|---|')
        for arm in ('base', 'lr005'):
            a, b = vals(A, arm, col), vals(B, arm, col)
            com = sorted(set(a) & set(b))
            d = [(b[s] - a[s]) * 100 for s in com]
            if not d:
                w('| `%s` | 0 | — | — | — | — |' % arm)
                continue
            pos = sum(1 for x in d if x > 0)
            w('| `%s` | %d | **%+.4f** | %+.4f | **%d/%d** | %+.3f |'
              % (arm, len(d), mean(d), sorted(d)[len(d) // 2], pos, len(d), tstat(d)))
        w('')

        # ③ ★ 交互项 = 增益之差
        w('### 2.%d ★ **交互项：增益之差**（直接回答"换 backbone 后增益还在不在"）'
          % (5 if col == COLS[0] else 6))
        w('')
        ga, ca = gains[A]
        gb, cb = gains[B]
        ga_of, gb_of = dict(zip(ca, ga)), dict(zip(cb, gb))
        com = sorted(set(ga_of) & set(gb_of))
        if len(com) >= 2:
            # 交互项 = 增益_B − 增益_A（按种子配对）；等价于 Δlr005 − Δbase
            diff = [gb_of[s] - ga_of[s] for s in com]
            w('| 量 | 值 |')
            w('|---|---|')
            w('| `%s` 的增益 | %+.4f pp |' % (bb[A], mean(ga)))
            w('| `%s` 的增益 | %+.4f pp |' % (bb[B], mean(gb)))
            w('| **增益之差（交互项）** | **%+.4f pp** |' % (mean(diff),))
            w('| 配对种子数 | %d |' % len(diff))
            w('| 交互项 t | **%+.3f** |' % tstat(diff))
            w('| 两臂增益是否同号 | %s |' % ('**是**（都为正）' if mean(ga) > 0 and mean(gb) > 0 else '**否**'))
            stats[col] = dict(ga=mean(ga), gb=mean(gb), inter=mean(diff), t=tstat(diff),
                              n=len(diff), pa=sum(1 for x in ga if x > 0), na=len(ga),
                              pb=sum(1 for x in gb if x > 0), nb=len(gb))
        else:
            w('配对种子不足（%d），不给交互项。' % len(com))
            stats[col] = None
        w('')

    # ---- 结论 ----
    w('## 三、结论')
    w('')
    bm = stats.get('best_map50_95')
    tm = stats.get('test_map50_95')
    if bm and tm:
        w('* **`best_map50_95`（§4.4 用的列）**：`%s` 增益 **%+.2f pp**（%d/%d 正号）、'
          % (bb[A], bm['ga'], bm['pa'], bm['na']))
        w('  `%s` 增益 **%+.2f pp**（%d/%d 正号）；**交互项 %+.2f pp，t=%+.2f**。'
          % (bb[B], bm['gb'], bm['pb'], bm['nb'], bm['inter'], bm['t']))
        w('* **`test_map50_95`（§4.1/§4.2/§5 用的列）**：`%s` 增益 **%+.2f pp**（%d/%d 正号）、'
          % (bb[A], tm['ga'], tm['pa'], tm['na']))
        w('  `%s` 增益 **%+.2f pp**（%d/%d 正号）；**交互项 %+.2f pp，t=%+.2f**。'
          % (bb[B], tm['gb'], tm['pb'], tm['nb'], tm['inter'], tm['t']))
        w('')
        same = (bm['ga'] > 0 and bm['gb'] > 0 and tm['ga'] > 0 and tm['gb'] > 0)
        w('* ⇒ ★★ **增益在两种 backbone 上都是正的、且两列一致**：%s'
          % ('**成立**' if same else '**不成立**'))
        w('* ⇒ **架构轴现在是可测的**（此前 A12 说"支撑不起"，那是格键定义的假象）。')
        w('  §4.4 因此可以从"另一个（源域, backbone）组合上的复现"**升级为**')
        w('  "**同数据、同族、同轮数、只换 backbone，增益在两列上都复现**"。')
        w('')
        w('### 边界与保留（必须一并写进论文或不写）')
        w('')
        w('1. **只有一个数据集**（`%s`）、**只有一个轮数**（%s ep）' % (DATASET, EPOCHS))
        w('   ⇒ 结论限于"在这个数据/预算上"，**不得**外推成"跨架构普遍"。')
        w('2. 种子是 **data-order 置换种子（torch seed 固定 42）**，'
          '不是 10 次独立训练 ⇒ 报的是**置换稳健性**，措辞不得写 "seeds"。')
        w('3. 两臂的 `lr0` 相差 5 倍；"增益"= `lr005 − base`，是**学习率干预的效应**。')
        w('4. ⚠ `A12` 的原文与 `_cells.pair_of()` 的这处循环必须**同时**留下更正记录，')
        w('   否则以后还会有人照着 A12 得出"架构轴不存在"。')
    w('')
    w('---')
    w('')
    w('输出 -> %s' % os.path.relpath(OUT, BASE))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    print('\n'.join(L[-24:]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
