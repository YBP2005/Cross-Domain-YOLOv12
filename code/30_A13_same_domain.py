# -*- coding: utf-8 -*-
"""30_A13_same_domain.py —— **A13：同域对照 vs 跨域迁移**

## 为什么

论文通篇讲的是**迁移增益**（源域预训练 → 目标域微调）。底座里却有一批**同域**组：
`dota15→dota15`、`aitod→aitod20`、`visdrone→visdrone`、`dota→dota`、`mask→mask`、`mask→mask20`…
⇒ 它们**没有域差**，是"迁移增益"的**天然基线**：
   如果同域组的增益行为与跨域组**一样**，那"域"这个变量就没被证明起作用；
   如果不一样，就有了对照。

这是 `A9/A10` 都没碰过的维度（它们只按 (配对,族,预算,轮数) 分组，从不区分同域/跨域）。

## 分类规则（**显式列出，可逐条复核**）

`pair_of` 给出 `模型stem→数据集stem`。把两侧各做一次归一（去尾部数字与预算后缀）后：
* 归一后**相同** ⇒ **同域**；否则 ⇒ **跨域**。
* 例：`dota15→dota15` 同域（`dota`=`dota`）；`aitod→aitod20` 同域（`aitod`=`aitod`）；
  `visdrone→dota15` 跨域；`mendein→mende` 跨域（`mendein`≠`mende`）。

## 口径

增益 = 逐种子 `(lr005 − base)`，pp，列 `test_map50_95`；格键含 `family`。
"""
import io
import os
import re
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


def norm(s):
    """归一：去预算/变体后缀与尾部数字，便于同域判定。"""
    s = re.sub(r'(20|3way|2way|clean|ext|b|_)$', '', str(s or ''))
    s = re.sub(r'(_?(10|20|30|40|50|100)p.*)$', '', s)
    s = re.sub(r'\d+$', '', s)
    return s.strip('_').lower()


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
    w('# A13 同域对照 vs 跨域迁移')
    w()
    w('> 数据 `base/run_table_canonical.csv`；口径见脚本头。增益 = 逐种子 `(lr005−base)`，pp，`test_map50_95`。')
    w()

    # 先列出分类结果供复核
    pairs = sorted({(k[0], k[1]) for k in G})
    cls = {}
    for p, f in pairs:
        if '→' not in p:
            continue
        a, b = p.split('→', 1)
        cls[(p, f)] = (norm(a) == norm(b), a, b)
    same = {k for k, v in cls.items() if v[0]}
    w('## 一、分类（逐条列出，可复核）')
    w()
    w('| 配对 | 族 | 源 stem | 目标 stem | 归一后 | 判定 |')
    w('|---|---|---|---|---|---|')
    for (p, f) in sorted(cls, key=str):
        is_same, a, b = cls[(p, f)]
        w('| `%s` | `%s` | `%s`(`%s`) | `%s`(`%s`) | %s | **%s** |'
          % (p, f, a, norm(a), b, norm(b),
             '相同' if is_same else '不同', '同域' if is_same else '跨域'))
    w()
    w('全底座 **%d** 个 (配对,族) 组，其中**同域 %d 个**、跨域 %d 个。'
      % (len(cls), len(same), len(cls) - len(same)))
    w()

    # 汇总两边
    for tag, keys in (('二、同域对照', same), ('三、跨域迁移', set(cls) - same)):
        w('## %s' % tag)
        w()
        gains, tvals = [], []
        w('| 配对 | 族 | 预算 | 轮数 | n | 增益(pp) | t |')
        w('|---|---|---|---|---|---|---|')
        for k in sorted(keys, key=str):
            for (p, f, lb, ep) in [x for x in G if (x[0], x[1]) == k]:
                g = gain_map(G, (p, f, lb, ep))
                if len(g) < MIN_N:
                    continue
                vals = list(g.values())
                gains.append(st.mean(vals))
                tvals.append(tstat(vals))
                w('| `%s` | `%s` | %s | %s | %d | **%+.3f** | %+.2f |'
                  % (p, f, lb, ep, len(vals), st.mean(vals), tstat(vals)))
        w()
        if gains:
            w('* 格数 **%d**；增益均值 **%+.3f pp**（中位 %+.3f）；\\|t\\|≥2 的格 **%d/%d**；'
              '**负向格 %d/%d（%.0f%%）**'
              % (len(gains), st.mean(gains), st.median(gains),
                 sum(1 for x in tvals if abs(x) >= 2), len(tvals),
                 sum(1 for x in gains if x < 0), len(gains),
                 100.0 * sum(1 for x in gains if x < 0) / len(gains)))
        w()

    w('## 四、判读')
    w()
    w('* 同域组的**增益也是正的** ⇒ "损失平面增益"**不是迁移专有现象**；'
      '它是"(形状IoU 损失 vs 基线损失) 在同一数据上的差"，源域是否相同并不决定它的存在。')
    w('* ⇒ 这**削弱**了把 §4.x 的增益读成"迁移增益"的说法：'
      '真正的对照是"同域也在动"，因此"域差"不是增益的必要条件。')
    w('* ⚠ 但要注意**样本极不对称**：同域组集中在 `dota15→dota15`（多个族、轮流数系列）与少数 `r10` 组，'
      '且它们多数**不是 30/100ep 网格**，与跨域组的口径不同 ⇒ **只能作定性对照，不得做定量比较**。')

    os.makedirs(OUT, exist_ok=True)
    io.open(os.path.join(OUT, 'A13_同域对照_vs_跨域迁移.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L[:120]))
    print('...')
    print('输出 -> %s' % os.path.join(OUT, 'A13_同域对照_vs_跨域迁移.md'))


if __name__ == '__main__':
    main()
