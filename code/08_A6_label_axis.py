# -*- coding: utf-8 -*-
"""08_A6_label_axis.py —— **A6 标签预算轴**（新稿第二条预算轴的全表 + 逐格体检）。

用户裁定（2026-09-30）："先看完整表再定" ⇒ 本件只**产出可核的表与体检**，
**不**改稿、**不**把标签轴写进正文。

口径（三条都与旧件不同，逐条给出理由）：
  1. **格的键 = (跨域配对, run 族, 数据集变体, epochs)**。
     ★ 加 `family` 是本会话新修的 —— 旧件 `06_A25.py: cells()` 只按 `(pair, epochs)`，
     会把不同批次混成一格（详见 `analysis\\A7_族混杂复核.md`）。
  2. **标注预算取自 dataset 名**（`sfchd_20p_b` 的 `20p`），**不是 run 名** —— 交接件 §4.2 的裁定；
     底座 `budget_pct` 列取自 run 名，1921 行里 1469 行取不到，两者差别本件都登记。
  3. **报数一律 test 侧** `test_map50_95`（`sio_b_results.csv`，driver 用 `split='test'`）。
     为了透明，另附 val 侧 best/last 的对照。

"种子"的真实含义（`base\\数据字典.md` §六）：**训练文件顺序的置换种子**，torch 种子恒 42。
"""
import os
import re
import csv
import sys
import math
import itertools
import collections
import statistics as st

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ★ 2026-10-05：可移植（放行布局下 = 仓库根，含 base/ deliver/ M3_draft/）
OUT = os.path.join(BASE, 'analysis')
rows = [r for r in csv.DictReader(open(os.path.join(BASE, 'base', 'run_table_canonical.csv'),
                                      encoding='utf-8'))]
TIERS = [10, 20, 30, 40, 50]
KEYS = ['test_map50_95', 'best_map50_95', 'last_map50_95']


def f(x):
    try:
        return float(x)
    except Exception:
        return None


def pair_of(r):
    m = re.sub(r'_pretrain.*$', '', (r['model'] or '').replace('.pt', ''))
    d = re.sub(r'_?\d{1,3}p.*$', '', re.sub(r'_(3way|2way)$', '', r['dataset'] or ''))
    return '%s→%s' % (m, d)


def bp_of_dataset(ds):
    m = re.search(r'(\d+)p', ds or '')
    return int(m.group(1)) if m else None


for r in rows:
    r['_p'] = pair_of(r)
    r['_s'] = f(r['seed_name'])
    r['_e'] = f(r['epochs_nominal'])
    r['_bp_ds'] = bp_of_dataset(r['dataset'])
    r['_bp_run'] = int(r['budget_pct']) if (r['budget_pct'] or '').strip().isdigit() else None


def tstat(xs):
    n = len(xs)
    if n < 2:
        return float('nan')
    sd = st.stdev(xs)
    return float('inf') if sd == 0 else st.mean(xs) / (sd / math.sqrt(n))


def cells(key='test_map50_95'):
    """(pair, family, dataset, epochs) -> {seed: gain_pp}"""
    g = collections.defaultdict(lambda: collections.defaultdict(dict))
    for r in rows:
        if r['lr_arm'] not in ('base', 'lr005') or r['_s'] is None or r['_e'] is None:
            continue
        if f(r[key]) is None:
            continue
        g[(r['_p'], r['family'], r['dataset'], int(r['_e']))][r['_s']][r['lr_arm']] = r
    out = {}
    for k, v in g.items():
        v = {s: d for s, d in v.items() if 'base' in d and 'lr005' in d}
        if len(v) >= 3:
            out[k] = v
    return out


C = cells()
GAIN = {k: {s: (f(d[s]['lr005']['test_map50_95']) - f(d[s]['base']['test_map50_95'])) * 100
            for s in d} for k, d in C.items()}

# 哪些 (pair) 在**同一族**上凑齐五档
bypf = collections.defaultdict(dict)
for (p, fam, ds, e), d in C.items():
    bp = bp_of_dataset(ds)
    if bp is None:
        continue
    bypf[(p, fam)][(bp, e)] = (ds, d)

L = []


def w(s=''):
    L.append(s)
    print(s)


w('# A6 标签预算轴：全表与逐格体检（2026-09-30）')
w()
w('> **本件是"看表"件，不是"定级"件**（用户裁定：先看完整表再定）。')
w('> 它回答一个问题：**标签预算轴在底座里能不能作为结果报出来，以及它的形状是什么。**')
w('> 所有数字可由 `scripts\\08_A6_label_axis.py` 重跑；底座 = `base\\run_table_canonical.csv`。')
w()
w('## 0. 口径（三条，都与旧件不同）')
w()
w('| # | 口径 | 说明 |')
w('|---|---|---|')
w('| 1 | 格的键 = **(配对, run 族, 数据集变体, epochs)** | ★ 本会话新修的 `family` 维度；旧件 `06_A25.py` 只按 `(pair, epochs)`，会混批（见 `A7_族混杂复核.md`）|')
w('| 2 | **标注预算取自 dataset 名**（`sfchd_20p_b` 的 `20p`），不是 run 名 | 交接件 §4.2 的裁定；底座 `budget_pct` 列取自 run 名，两者差别见 §1 |')
w('| 3 | 报数一律 **test 侧** `test_map50_95` | `sio_b_results.csv`（driver `split="test"`）；另附 val 侧 best/last 对照 |')
w()
w('"种子" = **训练文件顺序的置换种子**（`args.yaml: seed` 恒 42）；逐种子配对差不含初始化方差。')
w('增益 = **逐种子 (lr005 − base)**，单位 pp。')
w()
w('## 1. 覆盖度体检')
w()

# 所有候选 (pair, family) 组
groups = {}
for (p, fam), dd in bypf.items():
    tiers = sorted({bp for bp, e in dd})
    eps = sorted({e for bp, e in dd})
    if len(tiers) >= 4 and set(eps) >= {30, 100}:
        groups[(p, fam)] = dd

sel = set()
for (p, fam), dd in groups.items():
    for (bp, e), (ds, d) in dd.items():
        sel.update(id(d[s][a]) for s in d for a in ('base', 'lr005'))
selrows = [r for r in rows if id(r) in sel]

w('* 满足"**同族 × ≥4 档预算 × 含 {30ep,100ep}**"的 **(配对, 族)** 组：**%d** 个' % len(groups))
w('* 涉及两臂 run：**%d** 条' % len(selrows))
w()
if selrows:
    w('| 体检验项 | 实测 | 判读 |')
    w('|---|---|---|')
    sa = collections.Counter(r['seed_args'] for r in selrows)
    w('| `seed_args`（torch 种子） | %s | %s |' %
      (dict(sa), '✅ 恒 42 ⇒ 确为置换种子' if set(sa) == {'42'} else '⚠ 有非 42'))
    sk = collections.Counter(r['seed_kind'] for r in selrows)
    w('| `seed_kind` | %s | %s |' % (dict(sk), '✅ 全 shuffle' if set(sk) == {'shuffle'} else '⚠ 混有非 shuffle'))
    oc = collections.Counter(r['outcome'] for r in selrows)
    w('| `outcome` | %s | %s |' %
      (dict(oc), '✅ 全 complete' if set(oc) == {'complete'} else '⚠ 含非 complete'))
    mc = collections.Counter(r['machine'] for r in selrows)
    w('| 机器 | %s | 见下"同机性" |' % dict(mc))
    w('| `seed_name` | %s | 配对种子集 |' % dict(collections.Counter(r['seed_name'] for r in selrows)))
    w('| `dup_test_line=1` | %d 条 | %s |' %
      (sum(1 for r in selrows if r['dup_test_line'] == '1'),
       '⚠ 报数须写明"多读数取哪一次"' if any(r['dup_test_line'] == '1' for r in selrows) else '无'))
    w('| `has_weights_A` | %s | 权重库存 |' % dict(collections.Counter(r['has_weights_A'] for r in selrows)))
    w()
    # 同机性
    bad = []
    for k, d in C.items():
        if not any(id(d[s][a]) in sel for s in d for a in ('base', 'lr005')):
            continue
        ms = set()
        for s in d:
            ms.add(d[s]['base']['machine'])
            ms.add(d[s]['lr005']['machine'])
        if len(ms) > 1:
            bad.append((k, sorted(ms), len(d)))
    w('* **同机性**：可分析格中，两臂/逐种子**跨机**的格 = **%d** 个' % len(bad))
    for k, ms, n in bad:
        w('  * `%s` / 族 `%s` / `%s` / %dep：机器 %s，n=%d' % (k[0], k[1], k[2], k[3], ms, n))
    if not bad:
        w('  * ✅ 全部同机 ⇒ 无跨机混淆')
    w()
    # 预算口径分歧
    diff = [r for r in selrows if r['_bp_ds'] != r['_bp_run']]
    w('* **预算口径分歧**（dataset 名 vs run 名）：%d / %d 条不一致 ⇒ %s' %
      (len(diff), len(selrows),
       '✅ 本集合内两口径一致' if not diff else '⚠ 须显式声明用哪个'))
    w()

w('## 2. 全表：**族 × 5 档标签 × {30,100}ep**（test 侧，逐种子配对）')
w()
w('只列 §1 里满足"同族 ≥4 档"的组。`n` = 两臂都有的置换种子数；`符号` = 逐种子增益的符号一致性。')
w()
for (p, fam), dd in sorted(groups.items()):
    tiers = sorted({bp for bp, e in dd})
    eps = sorted({e for bp, e in dd})
    w('### `%s`　族 `%s`' % (p, fam))
    w()
    w('| 标签预算 | ' + ' | '.join('%dep 增益 (n)' % e for e in eps) + ' | 说明 |')
    w('|---|' + '---|' * len(eps) + '---|')
    for bp in tiers:
        cs = []
        for e in eps:
            if (bp, e) not in dd:
                cs.append('—')
                continue
            ds, d = dd[(bp, e)]
            g = {s: (f(d[s]['lr005']['test_map50_95']) - f(d[s]['base']['test_map50_95'])) * 100
                 for s in d}
            cs.append('**%+.3f** (%d)' % (st.mean(list(g.values())), len(g)))
        note = ''
        if (bp, 30) in dd and (bp, 100) in dd:
            g30 = {s: (f(dd[(bp, 30)][1][s]['lr005']['test_map50_95'])
                       - f(dd[(bp, 30)][1][s]['base']['test_map50_95'])) * 100 for s in dd[(bp, 30)][1]}
            g100 = {s: (f(dd[(bp, 100)][1][s]['lr005']['test_map50_95'])
                        - f(dd[(bp, 100)][1][s]['base']['test_map50_95'])) * 100 for s in dd[(bp, 100)][1]}
            common = sorted(set(g30) & set(g100))
            if common:
                dd_ = [g100[s] - g30[s] for s in common]
                note = '100ep − 30ep = **%+.3f**（t=%.2f）' % (st.mean(dd_), tstat(dd_))
        w('| %d%% | %s | %s |' % (bp, ' | '.join(cs), note))
    w()
    # 逐格符号
    w('逐格符号一致性（test 侧，逐种子）：')
    w()
    w('| 预算 | ep | n | 增益(pp) | t | 全正/全负/混合 | 逐种子 |')
    w('|---|---|---|---|---|---|---|')
    for bp in tiers:
        for e in eps:
            if (bp, e) not in dd:
                continue
            ds, d = dd[(bp, e)]
            g = {s: (f(d[s]['lr005']['test_map50_95']) - f(d[s]['base']['test_map50_95'])) * 100
                 for s in d}
            vals = list(g.values())
            sign = '全正' if all(v > 0 for v in vals) else ('全负' if all(v < 0 for v in vals) else '混合')
            w('| %d%% | %d | %d | %+.3f | %.2f | %s | %s |' %
              (bp, e, len(vals), st.mean(vals), tstat(vals), sign,
               '、'.join('%+.2f' % g[s] for s in sorted(g))))
    w()

w('## 3. 标签轴的端点差（10% → 50%）')
w()
w('| 配对 | 族 | ep | 10%% 增益 | 50%% 增益 | 端点差(50−10) | t | 形状 |')
w('|---|---|---|---|---|---|---|---|')
for (p, fam), dd in sorted(groups.items()):
    tiers = sorted({bp for bp, e in dd})
    if 10 not in tiers or 50 not in tiers:
        continue
    for e in sorted({e for bp, e in dd}):
        if (10, e) not in dd or (50, e) not in dd:
            continue
        _, d10 = dd[(10, e)]
        _, d50 = dd[(50, e)]
        g10 = {s: (f(d10[s]['lr005']['test_map50_95']) - f(d10[s]['base']['test_map50_95'])) * 100 for s in d10}
        g50 = {s: (f(d50[s]['lr005']['test_map50_95']) - f(d50[s]['base']['test_map50_95'])) * 100 for s in d50}
        common = sorted(set(g10) & set(g50))
        dv = [g50[s] - g10[s] for s in common]
        means = []
        for bp in TIERS:
            if (bp, e) in dd:
                _, d = dd[(bp, e)]
                gg = [(f(d[s]['lr005']['test_map50_95']) - f(d[s]['base']['test_map50_95'])) * 100 for s in d]
                means.append(st.mean(gg))
        shape = '—'
        if len(means) >= 4:
            inc = all(means[i] <= means[i + 1] for i in range(len(means) - 1))
            dec = all(means[i] >= means[i + 1] for i in range(len(means) - 1))
            shape = '**单调递增**' if inc else ('**单调递减**' if dec else '非单调')
        w('| `%s` | `%s` | %d | %+.3f | %+.3f | **%+.3f** | %.2f | %s |' %
          (p, fam, e, st.mean(list(g10.values())), st.mean(list(g50.values())),
           st.mean(dv), tstat(dv), shape))
w()

w('## 4. 两条预算轴的对照（**本表最能说明"两轴不是一回事"**）')
w()
w('对同一个 (配对, 族)，把两条轴各自的端点差并排放：')
w()
w('* **标签轴**：10% → 50%（标签从少到多）')
w('* **轮数轴**：30ep → 100ep')
w()
w('> ⚠★ **读数前必看：本表的两个数是"在对侧轴上取平均"后的汇总。**')
w('> * **标签轴** = 30ep 与 100ep **两条切片**端点差的均值；')
w('> * **轮数轴** = 5 档预算上端点差的均值。')
w('>')
w('> ⇒ 它们**与 §3 的逐 ep 端点差不相等**。实例（`s2df`，T2 补到 n=10 后）：')
w('> 标签轴在 30ep 是 **−10.714**、在 100ep 是 **−2.391**，本表给二者均值 **−6.553**；')
w('> 轮数轴在 5 档上是 −9.758 / −7.169 / −3.341 / −2.699 / −1.435，本表给均值 **−4.880**。')
w('>')
w('> ⚠ **取平均会掩盖对侧轴上的符号变化** —— 而"两轴是否反号"恰恰最怕这个：')
w('> 若某一档/某一轮数上符号与其余相反，均值会把它抹平。')
w('> ⇒ **本表是速览，不是判据。** 判断"反号"必须看**切片级**读数：')
w('> `scripts/22_s2ae_grid.py`（可传 `配对 族` 参数）的 §二（标签轴逐 ep）与 §三（轮数轴逐预算）。')
w()
w('| 配对 | 族 | 标签轴端点差(50%−10%) | 轮数轴端点差(100ep−30ep) | 两轴同号？ |')
w('|---|---|---|---|---|')
for (p, fam), dd in sorted(groups.items()):
    lab = []
    for e in (30, 100):
        if (10, e) in dd and (50, e) in dd:
            _, d10, _, d50 = dd[(10, e)][1], dd[(10, e)][1], dd[(50, e)][1], dd[(50, e)][1]
            g10 = {s: (f(d10[s]['lr005']['test_map50_95']) - f(d10[s]['base']['test_map50_95'])) * 100 for s in d10}
            g50 = {s: (f(d50[s]['lr005']['test_map50_95']) - f(d50[s]['base']['test_map50_95'])) * 100 for s in d50}
            common = sorted(set(g10) & set(g50))
            if common:
                lab.append(st.mean([g50[s] - g10[s] for s in common]))
    epd = []
    for bp in TIERS:
        if (bp, 30) in dd and (bp, 100) in dd:
            d30, d100 = dd[(bp, 30)][1], dd[(bp, 100)][1]
            g30 = {s: (f(d30[s]['lr005']['test_map50_95']) - f(d30[s]['base']['test_map50_95'])) * 100 for s in d30}
            g100 = {s: (f(d100[s]['lr005']['test_map50_95']) - f(d100[s]['base']['test_map50_95'])) * 100 for s in d100}
            common = sorted(set(g30) & set(g100))
            if common:
                epd.append(st.mean([g100[s] - g30[s] for s in common]))
    if not lab or not epd:
        continue
    L_ = st.mean(lab)
    E_ = st.mean(epd)
    same = '✅ 同号' if (L_ > 0) == (E_ > 0) else '❌ **反号**'
    w('| `%s` | `%s` | %+.3f | %+.3f | %s |' % (p, fam, L_, E_, same))
w()

w('## 5. 可靠性：n=3 的置换种子能判准方向吗')
w()
w('本轴每格只有 **3 个配对置换种子**。据 `A5_种子方差.md` §3 的闸门：')
w('在 ≥10 配对种子的格上枚举全部 3 子集，**效应量远大于噪声的格 ⇒ 3/3 同号率 100%**；')
w('**混合符号的格 ⇒ 20–30%**。⇒ 下表直接给"逐种子是否全同号"，这是可读的可靠性代理。')
w()
allc = allsame = 0
for (p, fam), dd in sorted(groups.items()):
    for (bp, e), (ds, d) in sorted(dd.items()):
        g = [(f(d[s]['lr005']['test_map50_95']) - f(d[s]['base']['test_map50_95'])) * 100 for s in d]
        allc += 1
        if all(v > 0 for v in g) or all(v < 0 for v in g):
            allsame += 1
w('* 本轴可分析格共 **%d** 个；其中**逐种子全同号**的 **%d** 个（**%.0f%%**）。' %
  (allc, allsame, 100.0 * allsame / max(1, allc)))
w('* ⇒ 与 A5 的规律一致：**效应大的格方向可信，边际格不可信**。')
w('  凡逐种子"混合"的格（见 §2 逐格表），在稿里只能报**均值+区间**，不得报"方向"。')
w()

w('## 6. 缺口与注意')
w()
w('1. **跨机格**：见 §1 的同机性清单；跨机格的两臂若不同机，不可直接报（论文的既有纪律是"两臂同机"）。')
w('2. **重名读数**：`dup_test_line=1` 的 run 须显式声明"多读数取哪一次"（底座取首次）。')
w('3. **预算口径**：本表用 **dataset 名**。底座 `budget_pct` 列用 **run 名**；两者在 §1 已核。')
w('4. **"种子"措辞**：稿里必须写 *paired data-order permutations (torch seed fixed at 42)*，不得写 "seeds"。')
w('5. **未纳入本表的族**：只有 1 档或 2–3 档预算的配对（如 `smoke→sfchd` 的 `b2` 族只有 20% 一档）')
w('   ⇒ 它们是**单点**，不能构成标签轴的曲线。')
w()

open(os.path.join(OUT, 'A6_标签预算轴.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n输出 -> %s' % os.path.join(OUT, 'A6_标签预算轴.md'))
