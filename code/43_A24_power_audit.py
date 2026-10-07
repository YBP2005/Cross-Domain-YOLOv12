# -*- coding: utf-8 -*-
"""43_A24_power_audit.py —— **全档案功效审计（选项 B）的生成器 + 守卫**（只读底座，写两件产物）。

为什么有这一件
--------------
`deliver/theory_B_全档案功效审计_20261003.md` 与 `deliver/theory_B_MDE_by_cell.csv` 是 2026-10-03
会话的产物，但**当时没有留下生成脚本**：CSV 是"算过一次就冻结"的，
而正文 §9 的分辨率条目引用它（`43 of 147`、`32 of 73`、`11 of 74`、主格 `12× / 13×`）。
经验 #20/#42：**凡是正文引用的数，必须有一个可执行的检查**；`（已完成 X）` 的 X 必须能被重算。
本件就是那个检查，并且**把 CSV 本身变成可再生的**（而不是不可再生的冻结件）。

口径（与稿内 §4.2 一致，逐字对照）
----------------------------------
配对设计，`n` 个配对种子、逐种子差值（`lr005 − base`，单位 pp）的**种子间样本 SD**（`n−1`）：

    MDE(n, sd) = ( t(0.975, n−1) + t(0.80, n−1) ) * sd / sqrt(n)

`t` 用 `scipy.stats.t.ppf`（本机 scipy 可用）。判据：`|delta| < MDE` ⇒ **功效不足**。
★ 一致性校验（必过）：`n=10, sd=0.3080` ⇒ MDE `= 0.3064`，与稿内 §4.2 的
  `SD 0.308 pp ⇒ MDE 0.306 pp` 对上。

★ 2026-10-04 实测（本件第一次跑就核出来的两件事）
-------------------------------------------------
1. **147 行里每一行都能从底座逐位重算**（`n`、`delta`、`sd` 全部对比；键 = 四列之一，
   实测 **147/147 用的是 `test_map50_95`**，与稿内 §4.2/§6 的口径一致）。
2. **`147` 就是底座里 `test_map50_95` 列上 `n >= 3` 的**全部**格数** ⇒ 正文 §9 的
   `Every cell in the archive was scored` 与 `43 of 147` **口径成立、无需改措辞**。
   ⚠ 这里记一条**已更正的中间结论**：我第一次用 `cell_stats(..., k[2], ...)` 扫底座时
   只数到 **123** 格，并据此写过"147 里多出 24 个旁支格、正文'全档案'过宽"。
   **那是错的**，根因在我自己的扫描循环：`lb=None` 的格被我用 `lb=0` 传进去，
   于是那 24 个 `lb=None` 的格一个都没被数到。修法是**逐格重算时不做 `lb` 替换**
   （本脚本现在就是这么写的）。⇒ 教训与经验 #14 同族：**"数与预期不符"先怀疑自己的扫描代码，
   再怀疑稿子**；而且**错警报必须在原处更正**（经验 #19 §9.4），不能只在别处留新说法。

用法
----
    python scripts/43_A24_power_audit.py            # 重算 + 对比 + 写两件产物
    python scripts/43_A24_power_audit.py --self-test # 阴性对照：故意破坏公式，守卫必须报红
"""
import os
import re
import sys
import csv
import math
import statistics as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import _cells as C  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = C.deliver_dir()       # ★ 布局无关：作者树 deliver/、放行仓 provenance/deliver/

# 稿内引用的四个聚合数（§9 的分辨率条目）。**逐条都要能被算出来**，不许写字面常量。
#   ⚠ 这里的 147 / 43 等是**期望值**，它们是守卫的靶；算出来的值不相等就报红。
EXPECT = dict(rows=147, insufficient=43, n3=73, n3_insuff=32, ngt=74, ngt_insuff=11)

ALPHA = 0.05
POWER = 0.80
KEYS = ['test_map50_95', 'best_map50_95', 'test_map50', 'best_map50']


def _t(p, df):
    """t 分位；scipy 不在时**硬失败**（不许静默退化成常量）。"""
    from scipy.stats import t as _tdist
    return float(_tdist.ppf(p, df))


def mde_of(n, sd, lam=1.0):
    """MDE = (t(1-α/2,n-1) + t(power,n-1)) · sd/√n。

    `lam` 只给 `--self-test` 用：`lam != 1` 就是"故意算错"，守卫必须因此报红。
    """
    if n < 2 or sd is None:
        return None
    se = sd / math.sqrt(n)
    return (_t(1 - ALPHA / 2, n - 1) + _t(POWER, n - 1)) * se * lam


def cell_stats(G, pair, fam, lb, ep, key, min_n=3):
    """重算一个格：`(n, delta, sd)`；不唯一或种子不足返回 `None`。"""
    ks = [k for k in G if k[0] == pair and k[1] == fam and k[3] == int(ep)
          and (lb is None or k[2] == lb)]
    if len(ks) != 1:
        return None
    dd = {}
    for s, arms in G[ks[0]].items():
        rec = {}
        for a in ('base', 'lr005'):
            r = C._pick(arms.get(a, []), key)
            if r is not None:
                rec[a] = r
        if len(rec) == 2:
            dd[s] = rec
    if len(dd) < min_n:
        return None
    vals = [(C.f(dd[s]['lr005'][key]) - C.f(dd[s]['base'][key])) * 100 for s in sorted(dd)]
    sd = st.stdev(vals) if len(vals) > 1 else 0.0
    return dict(n=len(vals), delta=st.mean(vals), sd=sd,
                t=(st.mean(vals) / (sd / math.sqrt(len(vals)))) if len(vals) > 1 and sd > 0 else float('nan'))


def main(self_test=False):
    fails = []
    rows, G = C.load()

    # ---------- 1) 从底座重建 CSV ----------
    pub_path = os.path.join(OUT, 'theory_B_MDE_by_cell.csv')
    pub = list(csv.DictReader(open(pub_path, encoding='utf-8')))
    rebuilt, mism = [], []
    for p in pub:
        lb = int(p['lb']) if p['lb'] not in ('', 'None') else None
        ep, n = int(p['ep']), int(p['n'])
        hit = None
        for key in KEYS:
            r = cell_stats(G, p['pair'], p['family'], lb, ep, key, min_n=n)
            if r and r['n'] == n and abs(r['delta'] - float(p['delta'])) < 0.005:
                hit = (key, r)
                break
        if hit is None:
            mism.append((p['pair'], p['family'], p['lb'], p['ep'], 'n/delta 无法从底座重算'))
            continue
        key, r = hit
        if abs(r['sd'] - float(p['sd'])) > 1e-6:
            mism.append((p['pair'], p['family'], p['lb'], p['ep'],
                         'sd 对不上：底 %.6f vs CSV %s' % (r['sd'], p['sd'])))
            continue
        lam = 0.5 if self_test else 1.0        # 阴性对照：把公式算错一半
        m = mde_of(n, r['sd'], lam=lam)
        rebuilt.append(dict(pair=p['pair'], family=p['family'],
                            lb='' if p['lb'] in ('', 'None') else p['lb'], ep=ep, n=n,
                            delta=r['delta'], sd=r['sd'], mde=m,
                            resolvable=str(abs(r['delta']) >= m), t=r['t'],
                            key=key))

    if len(rebuilt) != len(pub):
        fails.append('重建行数 %d != 已发布 %d' % (len(rebuilt), len(pub)))
    if mism:
        fails.append('%d 行无法逐位重算，前三条：%s' % (len(mism), mism[:3]))

    # ---------- 2) 聚合数（稿内 §9 引用的四个） ----------
    n_rows = len(rebuilt) if rebuilt else len(pub)
    insuff = [r for r in rebuilt if r['resolvable'] == 'False']
    n3 = [r for r in rebuilt if r['n'] == 3]
    ngt = [r for r in rebuilt if r['n'] > 3]
    agg = dict(rows=n_rows, insufficient=len(insuff),
               n3=len(n3), n3_insuff=sum(1 for r in n3 if r['resolvable'] == 'False'),
               ngt=len(ngt), ngt_insuff=sum(1 for r in ngt if r['resolvable'] == 'False'))
    for k, want in EXPECT.items():
        if agg[k] != want:
            fails.append('聚合量 %s = %d，稿内引用为 %d' % (k, agg[k], want))

    # ---------- 3) 一致性校验（与 §4.2 的 0.306 口径对撞） ----------
    chk = mde_of(10, 0.3080)
    if not (abs(chk - 0.3064) < 0.001):
        fails.append('口径校验失败：n=10/sd=0.3080 ⇒ MDE=%.4f（应为 0.3064）' % chk)

    # ---------- 4) 头部结论的比值（正文 §9 写 12× 与 13×） ----------
    heads = {}
    for r in rebuilt:
        if r['pair'] == 'visdrone→dota15' and r['family'] in ('t1c', 'mech') and r['lb'] == '20':
            heads[r['family']] = abs(r['delta']) / r['mde']
    for fam, lo in (('t1c', 12.0), ('mech', 12.0)):
        if fam not in heads or heads[fam] < lo:
            fails.append('主格 %s 的 |Δ|/MDE = %s，应 >= %.0f（正文 §9 写 12× 与 13×）'
                         % (fam, heads.get(fam), lo))

    # ---------- 5) 覆盖口径：CSV 的 147 是不是"底座里全部可算格" ----------
    avail = set()
    for k in G:
        r = cell_stats(G, k[0], k[1], k[2], k[3], 'test_map50_95', min_n=3)
        if r:
            avail.add(k)
    pub_keys = {(r['pair'], r['family'],
                 None if r['lb'] == '' else int(r['lb']), int(r['ep'])) for r in pub}
    miss = sorted(avail - pub_keys)
    extra = sorted(pub_keys - avail)

    # ---------- 报告 ----------
    lines = []
    A = lines.append
    A('# 选项 B（全档案功效审计）—— **重算与覆盖口径**（2026-10-04）')
    A('')
    A('> 由 `scripts/43_A24_power_audit.py` 生成。**只读底座**；产物 = 本件 + 重算后的逐格 CSV。')
    A('> 口径：`MDE(n,sd) = (t(0.975,n-1) + t(0.80,n-1)) · sd/√n`，`|Δ| < MDE ⇒ 功效不足`。')
    A('')
    A('## 一、逐格重建（这是"147 行可复算"的证明）')
    A('')
    A('| 项 | 值 |')
    A('|---|---|')
    A('| 已发布行数 | **%d** |' % len(pub))
    A('| **从底座逐位重算成功** | **%d** |' % len(rebuilt))
    A('| 其中用 `test_map50_95` 列 | **%d** |' % sum(1 for r in rebuilt if r['key'] == 'test_map50_95'))
    A('| 对不上的行 | **%d** |' % len(mism))
    A('')
    A('## 二、稿内 §9 引用的四个聚合数')
    A('')
    A('| 量 | 重算值 | 稿内引用 | 判定 |')
    A('|---|---|---|---|')
    for k, label in (('rows', '可算格总数'), ('insufficient', '`|Δ| < MDE`（功效不足）'),
                     ('n3', '`n = 3` 的格'), ('n3_insuff', '↳ 其中功效不足'),
                     ('ngt', '`n > 3` 的格'), ('ngt_insuff', '↳ 其中功效不足')):
        A('| %s | **%d** | %d | %s |' % (label, agg[k], EXPECT[k],
                                          '✅' if agg[k] == EXPECT[k] else '❌'))
    A('')
    A('> 口径校验：`n = 10, sd = 0.3080 ⇒ MDE = %.4f`（稿内 §4.2 写 0.306）%s'
      % (chk, '✅' if abs(chk - 0.3064) < 0.001 else '❌'))
    A('> 头部比值：`t1c` **%.2f×**、`mech` **%.2f×** 各自 MDE（稿内 §9 写 12× 与 13×）'
      % (heads.get('t1c', float('nan')), heads.get('mech', float('nan'))))
    A('')
    A('## 三、覆盖口径：`147` 是不是"底座里的全部可算格"')
    A('')
    A('| 项 | 值 |')
    A('|---|---|')
    A('| 底座里 `test_map50_95` 上 `n >= 3` 的 `(配对,族,预算,轮数)` 格 | **%d** |' % len(avail))
    A('| CSV 的行数 | **%d** |' % len(pub))
    A('| **未进 CSV 的格** | **%d** |' % len(miss))
    A('| CSV 里不属于上述集合的行 | **%d** |' % len(extra))
    A('')
    A('⇒ **两者相等**：`147` 不是"登记子集"，而是底座在该列上 `n >= 3` 的**全部**格。'
      '正文 §9 的 `Every cell in the archive was scored`、`43 of 147`、`32 of 73`、`11 of 74` '
      '**口径成立**（%s）。' % ('✅' if not miss and not extra else '❌ 有差异，见下表'))
    A('')
    if miss:
        A('未进 CSV 的格：')
        A('')
        for k in miss[:30]:
            A('* `%s` · 族 `%s` · lb=%s · %s ep' % (k[0], k[1], k[2], k[3]))
        A('')
    if extra:
        A('CSV 里多出的行：')
        A('')
        for k in extra[:30]:
            A('* `%s` · 族 `%s` · lb=%s · %s ep' % (k[0], k[1], k[2], k[3]))
        A('')
    A('> **已更正的中间结论（留档，不删）**：本件第一版把扫描循环里 `lb=None` 的格按 `lb=0` 传入，'
      '只数到 **123** 格，于是写过"147 里多出 24 个旁支格、正文\'全档案\'过宽"。'
      '**那是错的**：那 24 个格就是 `lb=None` 的格本身。'
      '⇒ 教训同经验 #14/#19 §9.4：**数与预期不符先怀疑自己的扫描代码**，'
      '且**错警报必须在原处更正**，不能只在别处留新说法。')
    A('')
    A('---')
    A('')
    A('## 附：逐格表（重算值）')
    A('')
    A('| pair | family | lb | ep | n | delta | sd | mde | resolvable | t | key |')
    A('|---|---|---|---|---|---|---|---|---|---|---|')
    for r in sorted(rebuilt, key=lambda x: (-x['n'], x['pair'])):
        A('| %s | %s | %s | %d | %d | %.4f | %.6f | %.6f | %s | %.4f | %s |'
          % (r['pair'], r['family'], r['lb'], r['ep'], r['n'], r['delta'],
             r['sd'], r['mde'], r['resolvable'], r['t'], r['key']))
    A('')

    with open(os.path.join(OUT, 'theory_B_全档案功效审计_复算_20261004.md'), 'w',
              encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')

    # 逐格 CSV：只在**完全重建成功**时重写（先校验、后落盘，经验 #19）。
    # ⚠ `--self-test`（阴性对照）**一律不写盘** —— 否则阴性对照会把产物破坏掉，
    #   那是"工具纪律"里最贵的一类事故（脚本第一次跑就改了被测件）。
    if not fails and rebuilt and not self_test:
        with open(pub_path, 'w', encoding='utf-8', newline='') as fh:
            wr = csv.writer(fh)
            wr.writerow(['pair', 'family', 'lb', 'ep', 'n', 'delta', 'sd', 'mde', 'resolvable', 't'])
            for r in rebuilt:
                wr.writerow([r['pair'], r['family'], r['lb'], r['ep'], r['n'],
                             '%.15g' % r['delta'], '%.15g' % r['sd'], '%.15g' % r['mde'],
                             r['resolvable'], '%.15g' % r['t']])

    print('已发布行 %d / 重建 %d / 对不上 %d' % (len(pub), len(rebuilt), len(mism)))
    print('聚合：%s' % agg)
    print('覆盖：底座可算 %d 格；CSV 含 %d 行（未登记 %d，旁支 %d）'
          % (len(avail), len(pub), len(miss), len(extra)))
    print('口径校验 MDE(10, 0.3080) = %.4f' % chk)
    if fails:
        print('\n❌ 失败 %d 条：' % len(fails))
        for f in fails:
            print('  · %s' % f)
        return 1
    print('\n✅ 全绿：147 行逐位可重算，聚合数四项与稿内一致。')
    print('输出 -> %s' % os.path.join(OUT, 'theory_B_全档案功效审计_复算_20261004.md'))
    return 0


if __name__ == '__main__':
    sys.exit(main(self_test='--self-test' in sys.argv))
