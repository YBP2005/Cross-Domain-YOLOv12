# -*- coding: utf-8 -*-
"""28_A11_seed_gate.py —— **A11：种子闸门标定（把 A5 §3 从"感觉"做成"表"）**

## 为什么

`analysis\\A5_种子方差.md` §3 的闸门是全稿可靠性论证的**支点**：
"A6/A9 里大量格只有 3 个配对种子，而 3 种子在边际格判方向只有 20–30% 可靠率" ——
于是那些格的方向**一律不得进正文**。

A5 当年只有少数 ≥10 种子的格可用来标定。**2026-10-01 盘点发现底座里有 48 个格 n≥8**
（含 3 个 n=13、1 个 n=11）。本件用它们把闸门做成**可查表**的定量规则。

## 方法

对每个 n≥8 的格：
1. 算全格的逐种子增益（pp）⇒ 全格均值 / t（作为"真值"）；
2. **枚举全部 3 子集**（C(n,3)），对每个子集算：均值的方向是否与全格一致（`p_dir`）、
   三个种子是否全同号（`p_unan`）；
3. 把 `p_dir` / `p_unan` 与全格的**效应/噪声比**（用 |t| 代理）对上，给出分级阈值。

## 口径

增益 = 逐种子 `(lr005 − base)`，pp，列 `test_map50_95`；格键含 `family`（与 A6/A9/A10 一致）。
"""
import io
import os
import sys
import math
import itertools
import statistics as st
import collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _cells as C

KEY = 'test_map50_95'
MIN_N = 8
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'analysis')
L = []


def w(s=''):
    L.append(s)


def gain_map(G, k):
    a = G.get(k)
    if not a:
        return {}
    o = {}
    for s, by in a.items():
        b = C._pick(by.get('base', []), KEY)
        l = C._pick(by.get('lr005', []), KEY)
        if b is not None and l is not None:
            o[s] = (C.f(l[KEY]) - C.f(b[KEY])) * 100
    return o


def main():
    rows, G = C.load()
    w('# A11 种子闸门标定')
    w()
    w('> 数据 `base/run_table_canonical.csv`；口径见脚本头。')
    w('> 目的：把 `A5_种子方差.md` §3 的"3 种子判不准方向"从定性说法做成**可查表的阈值**。')
    w()

    cells = []
    for k in G:
        g = gain_map(G, k)
        if len(g) >= MIN_N:
            cells.append((k, g))
    w('底座里 **n≥%d** 的格共 **%d** 个**（A5 当年只有少数几个）**。' % (MIN_N, len(cells)))
    w()

    w('| 格（配对/族/预算/轮数） | n | 全格均值(pp) | 全格 t | 3子集方向正确率 | 3子集全同号率 |')
    w('|---|---|---|---|---|---|')
    recs = []
    for k, g in sorted(cells, key=lambda x: -len(x[1])):
        vals = list(g.values())
        n = len(vals)
        mu = st.mean(vals)
        sd = st.stdev(vals) if n > 1 else 0.0
        t = mu / (sd / math.sqrt(n)) if sd > 0 else float('nan')
        subs = list(itertools.combinations(vals, 3))
        pdir = sum(1 for s in subs if (st.mean(s) > 0) == (mu > 0)) / len(subs)
        pun = sum(1 for s in subs if all(x > 0 for x in s) or all(x < 0 for x in s)) / len(subs)
        recs.append(dict(k=k, n=n, mu=mu, t=t, pdir=pdir, pun=pun))
        w('| `%s`/`%s` %s %s | %d | **%+.3f** | %+.2f | **%.0f%%** | **%.0f%%** |'
          % (k[0], k[1], k[2], k[3], n, mu, t, 100 * pdir, 100 * pun))
    w()

    w('## 分级：按全格 |t| 分箱（这就是闸门的可查表形式）')
    w()
    bins = [(0, 2), (2, 4), (4, 8), (8, 1e9)]
    w('| 全格 \\|t\\| | 格数 | 3子集方向正确率（中位） | 方向正确率=100% 的格 | 3子集全同号率（中位） |')
    w('|---|---|---|---|---|')
    for lo, hi in bins:
        sel = [r for r in recs if lo <= abs(r['t']) < hi]
        if not sel:
            w('| %s | 0 | — | — | — |' % ('≥8' if hi > 1e8 else '%g–%g' % (lo, hi)))
            continue
        med = st.median([r['pdir'] for r in sel])
        perfect = sum(1 for r in sel if r['pdir'] >= 0.999)
        medun = st.median([r['pun'] for r in sel])
        w('| %s | %d | **%.0f%%** | %d/%d | **%.0f%%** |'
          % ('≥8' if hi > 1e8 else '%g–%g' % (lo, hi), len(sel), 100 * med, perfect, len(sel), 100 * medun))
    w()

    w('## ★ 可用形式：按 **3 子集自身的 |t|** 分箱')
    w()
    w('> 上一节按**全格 t** 分箱 —— 但那个 t 对"只有 3 个种子的格"是**未知的**，无法直接套用。')
    w('> 本节改成：对每个 3 子集算**它自己的** `t₃`，再看它的方向是否与全格一致。')
    w('> **这才是能直接用在 A6/A9 那些 n=3 条目上的规则。**')
    w()
    triples = []
    for k, g in cells:
        vals = list(g.values())
        mu = st.mean(vals)
        for s in itertools.combinations(vals, 3):
            m3 = st.mean(s)
            sd3 = st.stdev(s)
            t3 = m3 / (sd3 / math.sqrt(3)) if sd3 > 0 else float('nan')
            triples.append((abs(t3), (m3 > 0) == (mu > 0), all(x > 0 for x in s) or all(x < 0 for x in s)))
    tb = [(0, 2), (2, 4), (4, 8), (8, 1e9)]
    w('| 该 3 子集自身的 \\|t₃\\| | 子集数 | **方向正确率** | 三个种子全同号占比 |')
    w('|---|---|---|---|')
    for lo_, hi_ in tb:
        sel = [x for x in triples if lo_ <= x[0] < hi_]
        if not sel:
            continue
        w('| %s | %d | **%.0f%%** | %.0f%% |'
          % ('≥8' if hi_ > 1e8 else '%g–%g' % (lo_, hi_), len(sel),
             100.0 * sum(1 for x in sel if x[1]) / len(sel),
             100.0 * sum(1 for x in sel if x[2]) / len(sel)))
    w()
    w('⇒ **操作规则**：一个 n=3 的格，先算它自己的 `|t₃|`：')
    w('  * `|t₃| ≥ 4` ⇒ 方向**基本可信**（本底座实测正确率见上表）；')
    w('  * `|t₃| < 2` ⇒ 方向**不可信**，只能报"均值+区间"；')
    w('  ⚠ 这是**经验校准**（来自本底座的 45 个 n≥8 格、数千个 3 子集），不是理论保证。')
    w()
    w('### ⚠★ 必须写明的**选择偏差**（否则上表会被误用）')
    w()
    w('* 上表的"真值"是那 **48 个 n≥8 格**给出的，而**这些格大多效应量很大**'
      '（|t|≥4 的有 35/48）—— 它们是"被反复测量过"的格，不是任意格的随机样本。')
    w('* ⇒ `|t₃|<2` 那一箱的 **86%** 是**乐观上界**：真值大的时候，即使 3 子集很噪声，'
      '也大概率落在正确一侧。**而我们真正担心的是"真实效应本身就小"的格** —— '
      '对那类格，`|t₃|` 小就意味着方向基本靠猜。')
    w('* **上一节（按全格 |t| 分箱）才是对小效应格的正确读数**：'
      '全格 `|t|<2` 时 3 子集方向正确率中位只有 **66%**、全同号率只有 **25%**。')
    w('* ⇒ **两条一起用**：')
    w('  1. 若已知该格（或同族同量级的格）**真实效应小** ⇒ 用"全格 |t|"那一节，**`|t|<2` 一律不报方向**；')
    w('  2. 若只有一个 n=3 的格、想快速筛 ⇒ 用 `|t₃|`，但要知道它是**乐观**的，'
      '`|t₃|<2` 时**不得**仅凭 86% 就去报方向。')
    w()

    w('## ★ 顶档补充：n=13 的三个格（2026-10-01 新增）')
    w()
    w('底座里有 **3 个 n=13 的格** —— 比 n=10 更能压窄统计量，也是闸门的最强证据层：')
    w()
    w('| 格 | n | 均值(pp) | t | 3子集方向正确率 | 3子集全同号率 | 10子集方向正确率 |')
    w('|---|---|---|---|---|---|---|')
    _big = [(k, gain_map(G, k)) for k in G if len(gain_map(G, k)) >= 13]
    for k, g in sorted(_big, key=str):
        vals = list(g.values()); n = len(vals)
        mu = st.mean(vals); sd = st.stdev(vals)
        t_ = mu / (sd / math.sqrt(n)) if sd > 0 else float('nan')
        s3 = list(itertools.combinations(vals, 3))
        p3 = sum(1 for s in s3 if (st.mean(s) > 0) == (mu > 0)) / len(s3)
        u3 = sum(1 for s in s3 if all(x > 0 for x in s) or all(x < 0 for x in s)) / len(s3)
        s10 = list(itertools.combinations(vals, 10))
        p10 = sum(1 for s in s10 if (st.mean(s) > 0) == (mu > 0)) / len(s10) if s10 else float('nan')
        w('| `%s`/`%s` %s %s | %d | **%+.3f** | %+.2f | **%.0f%%** | **%.0f%%** | **%.1f%%** |'
          % (k[0], k[1], k[2], k[3], n, mu, t_, 100 * p3, 100 * u3, 100 * p10))
    w()
    w('* ⇒ **`|t|` 在 3.4–4.7 这一带时：3 子集的"均值方向"正确率已到 99–100%，'
      '但"三个种子全同号"只有 58–77%** —— '
      '⇒ **判方向要看均值，不能要求逐种子全同号**；后者是过严的判据。')
    w('* ★ **对 §4.3 的直接佐证**：`mask→mende20/r10`（n=13）给 **−1.170（t=−3.39）**，'
      '而 §4.3 最终选定的是 `mask→mende`/族 `t2`（n=10，−1.4275）。'
      '**当年被排除的那个候选族同向、同量级** ⇒ **§4.3 的结论不依赖"选了哪个候选族"**，'
      '这消掉了 §4.3 最后一点选择自由度。')
    w()

    w('## 判读')
    w()
    lo = [r for r in recs if abs(r['t']) < 2]
    hi = [r for r in recs if abs(r['t']) >= 4]
    if lo:
        w('* **\\|t\\|<2 的格（效应不比种子噪声大）**：%d 个，3 子集方向正确率中位 **%.0f%%**、'
          '全同号率中位 **%.0f%%** ⇒ **3 个种子基本判不出方向**。'
          % (len(lo), 100 * st.median([r['pdir'] for r in lo]), 100 * st.median([r['pun'] for r in lo])))
    if hi:
        w('* **\\|t\\|≥4 的格**：%d 个，3 子集方向正确率中位 **%.0f%%**、全同号率中位 **%.0f%%** ⇒ '
          '**效应量压过噪声时，3 个种子也能判准方向**。'
          % (len(hi), 100 * st.median([r['pdir'] for r in hi]), 100 * st.median([r['pun'] for r in hi])))
    w('* ⇒ 与 `A5` §3 的结论**同向**，但现在有了**可查的阈值**：')
    w('  **报告任何 n≤3 的格之前，先看它的 |t|**：|t| 小的格只能报"均值+区间"，**不得报方向**。')
    w()
    w('> ⚠ 本件只标定"**种子噪声**对方向判定"的影响；它**不**回答"该不该加种子"以外的问题，')
    w('> 也**不**把任何 n≤3 的格变成可信 —— 恰恰相反，它给了"不可信"一个量化依据。')

    os.makedirs(OUT, exist_ok=True)
    io.open(os.path.join(OUT, 'A11_种子闸门标定.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    print()
    print('输出 -> %s' % os.path.join(OUT, 'A11_种子闸门标定.md'))


if __name__ == '__main__':
    main()
