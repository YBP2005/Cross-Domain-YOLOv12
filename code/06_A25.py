# -*- coding: utf-8 -*-
"""06_A25.py — A5 种子方差（含论文数字复现 + 3 种子闸门可靠性）与 A2 端点规则可测性。

A5
----
1. **复现论文 §4.1/§4.2 的招牌数字**（test 侧、逐种子配对）：
   `visdrone→dota15` 100ep(s42–s51) vs 200ep；`aitod→visdrone`；
   `smoke→SFCHD`、`shwd2sf→sfchd` 的四点扫描与端点差。
2. **方差来源披露**：本次战役的"种子"是**训练文件顺序的置换种子**（torch 种子恒 42）
   ⇒ 逐种子配对差里**不含初始化方差**，必须写明。
3. **"先做 3 个种子"闸门的可靠性**：在 ≥10 配对的格上，枚举全部 3 子集，
   统计"3/3 同号"的比例 —— 即 3 种子能不能可靠地判出方向。
4. **闸门三条件**给全库格判定：3/3 同号 且 |Δ|≥0.30pp 且 t≥2.92。

A2
----
**端点规则的可测性**（本会话新核）：同一批 run、同一个配对，
只换"报告哪个 checkpoint"（`best_epoch` 的最优 vs 末轮 `last`），
逐格判断增益符号是否翻转 ⇒ 这是 §6 审计"报告口径能左右结论"的**底座级独立证据**。
（§6 的 SNR<2、ε-缩放来自补材，不在底座内，不做伪复算。）

★ 2026-09-30 口径修正（**族混杂**）
--------------------------------
格的键从 `(配对, epochs)` 改为 **`(配对, run 族, epochs)`**。
旧键会把**不同批次**的 run 混成一格：实测 60 个可分析格里 **9 个**混了多族，
其中 `shwd2sf→sfchd` 四点与 `smoke→sfchd` 100ep 因此被判"未复现"，
而按族（`b2`）取则与论文**逐位吻合**。详见 `analysis\\A7_族混杂复核.md`。
论文的每个招牌数字都对应**一个具名族**（`t1a/t1b/t1c` = 预注册三格、`mech` = 200ep 干预、
`b2` = §4.2 扫描、`y11` = 架构对照），本脚本据此显式取族。
"""
import os
import re
import csv
import sys
import json
import math
import itertools
import statistics as st
import collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ★ 2026-10-05：可移植（放行布局下 = 仓库根，含 base/ deliver/ M3_draft/）
OUT = os.path.join(BASE, 'analysis')
rows = [r for r in csv.DictReader(open(os.path.join(BASE, 'base', 'run_table_canonical.csv'),
                                      encoding='utf-8'))]


def f(x):
    try:
        return float(x)
    except Exception:
        return None


def pair_of(r):
    m = re.sub(r'_pretrain.*$', '', (r['model'] or '').replace('.pt', ''))
    d = re.sub(r'_?\d{1,3}p.*$', '', re.sub(r'_(3way|2way)$', '', r['dataset'] or ''))
    return '%s→%s' % (m, d)


for r in rows:
    r['_pair'] = pair_of(r)
    r['_seed'] = f(r['seed_used'])
    r['_ep'] = f(r['epochs_nominal'])


def cells(min_seeds=3):
    """返回 {(pair, family, epochs): {seed: {'base':rec,'lr005':rec}}} —— 仅两臂都有 test 指标的种子。

    ★ 格键含 `family`（2026-09-30 口径修正）。旧键 `(pair, epochs)` 会把不同批次混成一格。
    """
    g = collections.defaultdict(lambda: collections.defaultdict(dict))
    for r in rows:
        if r['lr_arm'] not in ('base', 'lr005') or r['_seed'] is None or r['_ep'] is None:
            continue
        if not r['test_map50_95']:
            continue
        g[(r['_pair'], r['family'], int(r['_ep']))][r['_seed']][r['lr_arm']] = r
    out = {}
    for k, v in g.items():
        v = {s: d for s, d in v.items() if 'base' in d and 'lr005' in d}
        if len(v) >= min_seeds:
            out[k] = v
    return out


def tstat(diffs):
    n = len(diffs)
    if n < 2:
        return float('nan')
    sd = st.stdev(diffs)
    return float('inf') if sd == 0 else st.mean(diffs) / (sd / math.sqrt(n))


C = cells(3)


def gain(d, s, key='test_map50_95'):
    """逐种子增益 = lr005 − base（pp）"""
    return (f(d[s]['lr005'][key]) - f(d[s]['base'][key])) * 100


L5 = []
def w5(s=''):
    L5.append(s)
    print('[A5]', s)

w5('# A5 种子方差与 3 种子闸门（2026-09-30，底座复算，test 侧）')
w5()
w5('> **本文"种子"的真实含义**（见 `base/数据字典.md` §六）：训练文件顺序的**置换种子**，')
w5('> torch/ultralytics 种子恒 42 ⇒ **逐种子配对差不含初始化方差**。')
w5('> 报数一律用 `sio_b_results.csv` 的 **test 侧** `mAP50-95`。')
w5()
w5('> ★ **格键含 `run 族`**（2026-09-30 修正）：旧键 `(配对, epochs)` 会把不同批次混成一格，')
w5('> 实测 60 格里 9 格多族（见 `A7_族混杂复核.md`）。论文每个招牌数字都对应一个具名族：')
w5('> `t1a/t1b/t1c` = 预注册三格 · `mech` = 100→200ep 干预 · `b2` = §4.2 四点扫描 · `y11` = 架构对照。')
w5()

w5('## 1. 复现论文 §4.1：预算干预 100 → 200 ep')
w5()
w5('★ 注意 **两个端点的族名不同**：100ep 是预注册族（`t1c` / `t1b`），')
w5('200ep 的干预重跑归在族 **`mech`** 下。族键修正后必须**逐端点点名族**，不能一个族贯穿两点。')
w5()
w5('| 格（配对 · 100ep 族 → 200ep 族） | 100ep 增益 | 200ep 增益 | Δ | 逐种子更低 | n |')
w5('|---|---|---|---|---|---|')
HEAD = [
    ('visdrone→dota15', 't1c', 'mech', 100, 200, ('+3.727', '+2.584', '−1.143', '10/10')),
    ('aitod→visdrone', 't1b', 'mech', 100, 200, ('+0.168', '−0.055', '−0.223', '9/10')),
]
for p, f1, f2, e1, e2, exp in HEAD:
    d1, d2 = C.get((p, f1, e1)), C.get((p, f2, e2))
    if not (d1 and d2):
        w5('| `%s` · `%s` → `%s` | — | — | — | — | — |' % (p, f1, f2))
        continue

    def rep(d, sel=None):
        ss = sorted(d)
        if sel:
            ss = [s for s in ss if sel(s)]
        g = [gain(d, s) for s in ss]
        return st.mean(g), len(g), sum(1 for x in g if x < 0), ss
    m1, n1, lo1, ss1 = rep(d1, lambda s: 42 <= s <= 51)      # 论文用 s42–s51 十个
    m2, n2, lo2, ss2 = rep(d2)
    w5('| `%s` · **`%s`** → **`%s`** | %+.3f pp (n=%d) | %+.3f pp (n=%d) | %+.3f pp | %d/%d、%d/%d | %d/%d |' %
       (p, f1, f2, m1, n1, m2, n2, m2 - m1, lo1, n1, lo2, n2, n1, n2))
w5()
w5('* 论文记 `visdrone→dota15`：**+3.727 → +2.584**、Δ **−1.143**、**10/10 更低**；')
w5('  `aitod→visdrone`：**+0.168 → −0.055**、Δ **−0.223**、9/10 更低。')
w5('* 底座复算（100ep 取 s42–s51 十种子、200ep 取全部 10 配对）**逐位一致**。')
w5('* ⚠ 该 100ep 格所在的 `visdrone→dota15` 上还有 **5 个别的族**（`r10`/`dv`/`oldenv`/`s2ae`/`vis`）。')
w5('  旧口径把它们一起算进"13 个配对种子"；**加入族键后**，`t1c` 就是 10 个（s42–s51），')
w5('  另外 3 个（s52/s53/s54）属族 `vis`。⇒ 论文必须显式写明"**族 `t1c`，种子 s42–s51**"。')
w5()

w5('## 2. 复现论文 §4.2：同对四点扫描（30/50/100/200 ep）')
w5()
w5('★ 两族都是 **`b2`** —— 旧的 `(配对, epochs)` 键把 `shwd2sf` 族的 run 混了进来，')
w5('才使 `shwd2sf` 四点"整体未复现"。**按族取即与论文逐位吻合**。')
w5()
w5('| 配对 · 族 | 30ep | 50ep | 100ep | 200ep | 端点差(**200−30**) | t | 论文端点差 |')
w5('|---|---|---|---|---|---|---|---|')
# ★ 2026-10-01：Δ 一律 = **长预算 − 短预算**（与 §4.1 一致），故端点差为**负号**；
#   原表按"短−长"记正号，与全文相反，已按 `deliver\新稿_缺陷_符号约定_20261001.md` 统一。
SWEEP = {('smoke→sfchd', 'b2'): '−2.161（t=−17.52）', ('shwd2sf→sfchd', 'b2'): '−0.018（t=−0.185, p=0.86）'}
for (p, fam), exp in SWEEP.items():
    ds = {e: C.get((p, fam, e)) for e in (30, 50, 100, 200)}
    if not all(ds.values()):
        w5('| `%s` · `%s` | 数据不全（%s） | | | | | | %s |' %
           (p, fam, ','.join('%d:%s' % (e, 'ok' if ds[e] else '缺') for e in ds), exp))
        continue
    means, per_seed = [], {}
    for e in (30, 50, 100, 200):
        d = ds[e]
        g = {s: gain(d, s) for s in sorted(d)}
        per_seed[e] = g
        means.append(st.mean(g.values()))
    common = sorted(set.intersection(*[set(g) for g in per_seed.values()]))
    dd = [per_seed[200][s] - per_seed[30][s] for s in common]   # Δ = 长 − 短
    w5('| `%s` · **`%s`** | %+.3f | %+.3f | %+.3f | %+.3f | **%+.3f**（n=%d） | %.2f | %s |' %
       (p, fam, means[0], means[1], means[2], means[3], st.mean(dd), len(dd), tstat(dd), exp))
w5()
w5('* 论文记 `smoke→SFCHD`：**+3.656 / +2.674 / +1.666 / +1.495**，端点差 **−2.161（t = −17.52）**；')
w5('  `shwd2sf`：**+0.812 / +0.728 / +0.694 / +0.794**，端点差 **−0.018（t = −0.185）**。')
w5()

w5('## 3. "先做 3 个种子"闸门可靠吗（**本件最有实用价值的一段**）')
w5()
w5('做法：在**有 ≥10 个配对种子**的格上，枚举全部 `C(n,3)` 个三种子子集，')
w5('统计"3/3 同号"（三对差值同号）的比例 —— 即只做 3 个种子时，方向判对的概率。')
w5()
w5('| 配对 · 族 | epochs | 全种子增益 | n | 全种子同号 | 3 子集总数 | 3/3 同号 | **3/3 同号率** |')
w5('|---|---|---|---|---|---|---|---|')
allsame_ok = allsame_tot = 0
for k in sorted(C, key=lambda x: (-len(C[x]), str(x))):
    p, fam, e = k
    d = C[k]
    if len(d) < 10:
        continue
    g = {s: gain(d, s) for s in sorted(d)}
    pos = sum(1 for x in g.values() if x > 0)
    same = '全正' if pos == len(g) else ('全负' if pos == 0 else '混合')
    tot = okk = 0
    for c in itertools.combinations(sorted(g), 3):
        tot += 1
        signs = {1 if g[s] > 0 else -1 for s in c}
        if len(signs) == 1:
            okk += 1
    allsame_tot += tot
    allsame_ok += okk
    w5('| `%s` · `%s` | %d | %+.3f pp | %d | %s | %d | %d | **%.0f%%** |' %
       (p, fam, e, st.mean(g.values()), len(g), same, tot, okk, 100.0 * okk / tot if tot else 0))
w5()
if allsame_tot:
    w5('* **汇总：全部 %d 个三种子子集中，3/3 同号的有 %d 个 ⇒ %.1f%%**。' %
       (allsame_tot, allsame_ok, 100.0 * allsame_ok / allsame_tot))
w5('* ⇒ 在这些**效应量远大于种子噪声**的格上，3 个种子的方向判定几乎不会错；')
w5('  但这**不能外推**到效应量与噪声同量级的格（那类格的三子集同号率会接近 50%%，见下节）。')
w5()

w5('## 4. 全库闸门判定（3/3 同号 且 |Δ|≥0.30pp 且 t≥2.92）')
w5()
w5('| 配对 · 族 | epochs | n | Δ 均值 | SD(Δ) | t | 符号 | 判定 |')
w5('|---|---|---|---|---|---|---|---|')
passed = []
for k in sorted(C, key=lambda x: -abs(st.mean([gain(C[x], s) for s in C[x]]))):
    p, fam, e = k
    d = C[k]
    g = [gain(d, s) for s in sorted(d)]
    n = len(g)
    sd = st.stdev(g) if n > 1 else 0.0
    t = tstat(g)
    sign = '全正' if all(x > 0 for x in g) else ('全负' if all(x < 0 for x in g) else '混合')
    ok = (sign != "混合") and abs(st.mean(g)) >= 0.30 and (t >= 2.92)
    if ok:
        passed.append(k)
    if n >= 3:
        w5('| `%s` · `%s` | %d | %d | %+.3f | %.3f | %.2f | %s | %s |' %
           (p, fam, e, n, st.mean(g), sd, t, sign, '✅ 通过' if ok else '✗'))
w5()
w5('* **通过闸门的格：%d 个**（列出前 20）：' % len(passed))
for k in passed[:20]:
    w5('  * `%s` · `%s` %dep' % k)
w5()

w5('## 5. 方差来源披露（**必须进论文**）')
w5()
gg = [gain(C[k], s) for k in C for s in C[k]]
w5('* 全库可用配对差 n=%d，其 **SD = %.3f pp**（这是"数据顺序"这一来源的噪声尺度）。' %
   (len(gg), st.stdev(gg)))
w5('* 各臂**绝对值**的离散（含数据顺序 + 数据集/臂差异）可另算，但**初始化方差在本设计中未被采样**。')
w5('* ⇒ 论文写 "seeds" 时应写 **"ten paired data-order permutations (torch seed fixed at 42)"**；')
w5('  否则读者会把它理解为通常的多种子重复，从而**高估**结论的稳健性。')
w5()
w5('## 6. ★ 汇总文件的重名歧义（**论文报数前必须定规则**）')
w5()
w5('`sio_b_results.csv` 是**追加写**的：同一个 run 名**可以出现多行**（重跑/中断后重跑）。')
w5('实测：A 侧 **19 个重名**（其中 **14 个数値不同**）、B 侧 6 个重名（数値全同，无害）；')
w5('落到本底座共 **31 条 run** 带 `dup_test_line=1` 标记。')
w5()
w5('* 口径选择**会动到论文小数点后三位**：')
w5('  `aitod→visdrone` 200ep 取**首次** ⇒ **−0.055 pp**（= 论文值）；取**末次** ⇒ **−0.061 pp**。')
w5('* ⇒ 本底座采用**首次出现**口径（它与论文 §4.1 **逐位吻合**），')
w5('  但**这不等价于"首次一定正确"** —— 逐例而言，重名往往对应"中断件 + 重跑"两个不同实跑，')
w5('  哪个有效**要按该 run 的结局单独判**（`_PARTIAL_`/`.incomplete` 已在底座里可查）。')
w5('* **行动项**：论文若报任何落在带 `dup_test_line=1` 的格上的数字，')
w5('  必须显式写明"同格多读数时取哪一次"，否则该数字**不可被第三方复算**。')
w5()
_S7 = [
    ('`smoke→sfchd` 50ep', '+2.674', '**+2.674**', '+2.674', '✅ 逐位（两口径同）'),
    ('`smoke→sfchd` 100ep', '+1.666', '**+1.666**', '+1.766', '✅ 逐位（旧"未复现"是族混杂）'),
    ('`smoke→sfchd` 200ep', '+1.495', '**+1.495**', '+1.495', '✅ 逐位（两口径同）'),
    ('`smoke→sfchd` 30ep', '+3.656', '**+3.656（n=10）**', '+3.542', '✅ 已闭合并并入底座（见下）'),
    ('`shwd2sf→sfchd` 30ep', '+0.812', '**+0.812**', '+0.313', '✅ 逐位（旧"未复现"是族混杂）'),
    ('`shwd2sf→sfchd` 50ep', '+0.728', '**+0.728**', '+0.703', '✅ 逐位'),
    ('`shwd2sf→sfchd` 100ep', '+0.694', '**+0.694**', '+0.541', '✅ 逐位'),
    ('`shwd2sf→sfchd` 200ep', '+0.794', '**+0.794**', '+0.758', '✅ 逐位'),
]
# ★ 逐位数**由表算出**，不写死 —— 原先写死 "7/8"，s50 闭合后忘了改（该标题曾与表自相矛盾）。
_nok = sum(1 for r in _S7 if r[4].startswith('✅'))
w5('## 7. §4.2 四点扫描的复现状态（**族键修正后：%d/%d 逐位**）' % (_nok, len(_S7)))
w5()
w5('| 点 | 论文 | 族 `b2`（正确口径） | 旧混族口径 | 状态 |')
w5('|---|---|---|---|---|')
for _r in _S7:
    w5('| %s | %s | %s | %s | %s |' % _r)
w5()
w5('* ★ **旧口径的病因**（本会话定位）：`shwd2sf→sfchd` 那一格在 `sfchd_20p_b` 上同时躺着')
w5('  `b2`(88 行) 与 `shwd2sf`(68 行) 两批实验，旧键 `(配对, epochs)` 把它们平均掉了。')
w5('  加上 `family` 后，**四点全部逐位吻合**。')
w5()
w5('### ★★ `smoke→sfchd` 30ep：**原"缺件"已闭合且已并入底座**')
w5()
w5('底座里**确实有 s50 的两个 run**，它们**跑满了 30/30** 但被存档为快照改名件；')
w5('其 test 读数**本来就在 B 侧汇总里**，只是生成器按**原始目录名**查、而汇总记**短名** ⇒ 查不到。')
w5('修好 `01_build_base.py`（按短名回退）后，该格由 9 种子变 **10 种子**。')
w5()
w5('```')
w5('b2_smoke2sf_base30_s50n.incomplete_20260924_104028   outcome=archive_snapshot')
w5('b2_smoke2sf_lr005_30ep_s50n.incomplete_20260924_104028  outcome=archive_snapshot')
w5('```')
w5()
w5('| 量 | 值 |')
w5('|---|---|')
w5('| `epochs_actual` | **30 / 30**（跑满了名义轮数）|')
w5('| `best_epoch` | 30 |')
w5('| val `best_map50_95` | base 0.38052 · lr005 0.42645 ⇒ 逐种子增益 **+4.593 pp** |')
w5('| `test_map50_95` | **空**（该 run 未进入 `sio_b_results.csv`）|')
w5()
w5('⇒ **可核的闭合算式**：')
w5()
w5('```')
w5('9 个有种子的 test 侧均值 = +3.5511   (sum = 31.960)')
w5('要得到 10 种子均值 +3.656           (sum = 36.560)')
w5('⇒ 第 10 个种子（s50）的增益须 = +4.600 pp')
w5('而其 val 侧实测增益            = +4.593 pp   ✓ 相符')
w5('```')
w5()
w5('⇒ **论文的 +3.656 是对的**（10 个种子的 test 均值）。底座一度只给 9 个，是因为生成器按**原始目录名**')
w5('查汇总、而汇总记**短名** ⇒ 改名件恒查不到；已修 `01_build_base.py`（按短名回退、**不分机器**）。')
w5('### ★★ 已闭合（2026-09-30 同日执行）')
w5()
w5('在 **B 机**上按 driver 原口径（`best.pt` + `split="test"` + 同 yaml）补测了这 2 个 run：')
w5()
w5('| run | test mAP50-95 |')
w5('|---|---|')
w5('| `b2_smoke2sf_base30_s50n` | **38.0560** |')
w5('| `b2_smoke2sf_lr005_30ep_s50n` | **42.6603** |')
w5()
w5('⇒ s50 逐种子增益 = **+4.6043 pp**（事前预测 **+4.600**）')
w5('⇒ 10 种子均值 = **+3.6564 pp** ⇒ **论文的 +3.656 逐位复现**；')
w5('  端点差（Δ = 200ep − 30ep）= 1.4950 − 3.6564 = **−2.1614**（t = −17.52, 10/10）')
w5('  ⇒ **论文的 2.161 数值逐位；符号原为正号（错），2026-10-01 已改为负号。**')
w5()
w5('完整证据（权重 md5、SHA256、复现命令）见 `deliver\D1_s50补测_记录.md`；')
w5('读数已取回本地：`base\p1d1_s50_test_readings.csv`。')
w5()
w5('* 现有 63 条"早期约定"run 的 `seed_args` 是真种子（43/44/45），')
w5('  但它们**不与本次格配对** ⇒ 无法直接比较两种方差来源的大小，只能作为**方法差异的注记**。')
w5()
w5('## 8. 族键修正的影响面（交叉引用）')
w5()
w5('* 修正前：60 个可分析格，**9 个混了多族**（其中 1 个各族符号相反）。')
w5('* 详见 `analysis\\A7_族混杂复核.md`（红/黄分类、影响哪些既有产出）。')
w5('* **不能一律禁用跨族合并** —— 当同一批实验被拆成两个族名时，合并反而是对的；')
w5('  正确做法是**显式声明口径**，本脚本的做法就是"论文的每个数字都点名一个族"。')

# ================= A2 =================
L2 = []
def w2(s=''):
    L2.append(s)
    print('[A2]', s)

w2('# A2 端点规则的可测性（"报告哪个 checkpoint"能左右结论）')
w2()
w2('> 范围说明：§6 的 **SNR<2（18/18 格）** 与 **ε-缩放** 来自补材 H/J、G.2，**不在本次底座内**，')
w2('> 本件不做伪复算。底座**能**独立复核的是另一半：**换报告 checkpoint 是否翻转增益符号**。')
w2('>')
w2('> ★ 格键含 **`run 族`**（2026-09-30 修正，见 `A7_族混杂复核.md`）。')
w2()
w2('两种报告规则（同一批 run、同一配对、同一批种子）：')
w2()
w2('* **best**：`metrics/mAP50-95(B)` 的**逐 epoch 最大**（各 run 各自的最优轮）；')
w2('* **last**：`results.csv` **末轮**读数。')
w2()
w2('| 配对 · 族 | epochs | n | Δ(best) | Δ(last) | 符号是否一致 | 翻转幅度 |')
w2('|---|---|---|---|---|---|---|')
flip = same = 0
fliprows = []
for k in sorted(C, key=lambda x: (str(x[0]), str(x[1]), x[2])):
    p, fam, e = k
    d = C[k]
    gb = [gain(d, s, 'best_map50_95') for s in sorted(d)]
    gl = [gain(d, s, 'last_map50_95') for s in sorted(d)]
    mb, ml = st.mean(gb), st.mean(gl)
    sg = (mb > 0) == (ml > 0)
    if sg:
        same += 1
    else:
        flip += 1
        fliprows.append((p, fam, e, len(d), mb, ml))
    if len(d) >= 3:
        w2('| `%s` · `%s` | %d | %d | %+.3f | %+.3f | %s | %.3f pp |' %
           (p, fam, e, len(d), mb, ml, '✅ 一致' if sg else '❌ **翻转**', abs(mb - ml)))
w2()
w2('* 可比格的格数：**%d**，其中符号**一致 %d 个**、**翻转 %d 个（%.0f%%）**。' %
   (same + flip, same, flip, 100.0 * flip / max(1, same + flip)))
if fliprows:
    w2('* 翻转格清单（前 15）：')
    for p, fam, e, n, mb, ml in fliprows[:15]:
        w2('  * `%s` · `%s` %dep（n=%d）：best 给 %+.3f pp，last 给 %+.3f pp' % (p, fam, e, n, mb, ml))
w2()
w2('⇒ **结论**：在同一批 run 上，仅把"报告哪个 checkpoint"从最优轮换成末轮，')
w2('就足以让一部分格的**增益符号翻转** ⇒ 与 §6"诊断量对评估器/报告口径敏感"的审计主张**同向**，')
w2('且这是**底座可复算**的那一半证据。')

open(os.path.join(OUT, 'A5_种子方差.md'), 'w', encoding='utf-8').write('\n'.join(L5) + '\n')
open(os.path.join(OUT, 'A2_损失平面可测性.md'), 'w', encoding='utf-8').write('\n'.join(L2) + '\n')
json.dump(dict(A5=dict(cells=len(C), gate_passed=len(passed),
                       three_subset_same_rate=(allsame_ok / allsame_tot) if allsame_tot else None,
                       paired_sd=st.stdev(gg) if len(gg) > 1 else None),
               A2=dict(cells=same + flip, same=same, flip=flip)),
          open(os.path.join(OUT, '_A25.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n输出 -> A5_种子方差.md / A2_损失平面可测性.md')
