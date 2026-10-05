# -*- coding: utf-8 -*-
"""10_A7_family.py —— **族混杂复核**：旧口径的格键缺 `family`，影响面有多大。

背景（本会话发现）：`scripts/06_A25.py` 的 `cells()` 用的格键是 `(pair, epochs)`，
`scripts/04_A1_grid.py` 用的是 `(pair, budget, epochs, loss)` —— **两者都没有把 `family`
（run 名第一段，即"批次"）放进键里**。而底座里同一个 `(pair, dataset, epochs)` 常常
混着多个族（如 `sfchd_20p_b` 上同时有 `b2` / `shwd2sf` / `smoke2sf` / `y11` /
`a5` / `cal*`）。

后果有两类，必须分开说：
  · **数值被平均掉**（`smoke→sfchd` 100ep：族 `b2` 是 +1.666，混入 `smoke2sf` 后变 +1.766）
  · **方向被改掉**（`y11_shwd→sfchd` 100ep：族 `y11` 是 +0.010（t=0.19，无增益），
    混入 `b2` 后变 +0.193（t=2.04，看着"显著"））—— 这一类才是真危险。

本件只做**登记与量化**，不改任何既有产物；`A2`/`A5` 是否按新口径重生成由作者裁定。
"""
import os
import re
import csv
import sys
import math
import collections
import statistics as st

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
    r['_p'] = pair_of(r)
    r['_s'] = f(r['seed_name'])
    r['_e'] = f(r['epochs_nominal'])
    r['_bp'] = (r['budget_pct'] or '').strip()


def tstat(xs):
    n = len(xs)
    if n < 2:
        return float('nan')
    sd = st.stdev(xs)
    return float('inf') if sd == 0 else st.mean(xs) / (sd / math.sqrt(n))


# ---------- 旧口径（复刻 06_A25.cells） ----------
old = collections.defaultdict(lambda: collections.defaultdict(dict))
for r in rows:
    if r['lr_arm'] not in ('base', 'lr005') or r['_s'] is None or r['_e'] is None:
        continue
    if not r['test_map50_95']:
        continue
    old[(r['_p'], int(r['_e']))][r['_s']][r['lr_arm']] = r
OLD = {}
for k, v in old.items():
    v = {s: d for s, d in v.items() if 'base' in d and 'lr005' in d}
    if len(v) >= 3:
        OLD[k] = v


def fam_gains(pair, ep, fam=None, key='test_map50_95'):
    """★ 按族先过滤**再**按种子配对 —— 顺序不能反。

    反了会出错：同一个 seed 在多个族里都有记录时，先按 seed 建索引会把族信息覆盖掉，
    于是"按族取子集"就取空了（本件第一版就栽在这里，产出过 `+nan`）。
    """
    g = collections.defaultdict(dict)
    for r in rows:
        if r['_p'] != pair or r['lr_arm'] not in ('base', 'lr005'):
            continue
        if r['_e'] is None or int(r['_e']) != ep or r['_s'] is None:
            continue
        if fam is not None and r['family'] != fam:
            continue
        if f(r[key]) is None:
            continue
        g[r['_s']][r['lr_arm']] = r
    out = {}
    for s, d in g.items():
        if 'base' in d and 'lr005' in d:
            out[s] = (f(d['lr005'][key]) - f(d['base'][key])) * 100
    return out


def fams_of(pair, ep):
    c = collections.Counter()
    for r in rows:
        if r['_p'] != pair or r['_e'] is None or int(r['_e']) != ep:
            continue
        if r['lr_arm'] not in ('base', 'lr005'):
            continue
        c[r['family']] += 1
    return c


def gains(d, key='test_map50_95'):
    return {s: (f(x['lr005'][key]) - f(x['base'][key])) * 100 for s, x in d.items()}


def fams_in(d):
    c = collections.Counter()
    for s, x in d.items():
        for a in ('base', 'lr005'):
            c[x[a]['family']] += 1
    return c


L = []


def w(s=''):
    L.append(s)
    print(s)


w('# A7 族混杂复核：旧口径的格键缺 `family`（2026-09-30）')
w()
w('> 发现于本会话的 §4.2/§4.3/§4.4 反查（见 `deliver\\§4.2-4.4_未复现断言_候选格反查.md`）。')
w('> **本件只登记与量化，不改任何既有产物。**')
w()
w('## 1. 问题')
w()
w('`scripts\\06_A25.py` 的 `cells()` 用 **`(pair, epochs)`** 做格键，')
w('`scripts\\04_A1_grid.py` 用 **`(pair, budget, epochs, loss)`** —— **两者都不含 `family`**。')
w('而底座里同一格常混着多个族。**族 = run 名第一段 = 批次**（`b2` / `shwd2sf` / `smoke2sf` /')
w('`y11` / `t1c` / `r10` / `g3clean` …），它们**不是同一次实验**。')
w()
w('## 2. 影响面（旧口径 `(pair, epochs)`，n≥3）')
w()
multi = {k: v for k, v in OLD.items() if len(fams_in(v)) > 1}
w('* 旧口径可分析格：**%d** 个' % len(OLD))
w('* 其中**混了多个族**的：**%d** 个（**%.0f%%**）' % (len(multi), 100.0 * len(multi) / max(1, len(OLD))))
w()
w('| 配对 | epochs | 配对种子 | 族数 | 各族（行数） | 旧口径值 | **按族分别算** |')
w('|---|---|---|---|---|---|---|')
for k in sorted(multi, key=lambda x: (-len(multi[x]), str(x))):
    d = multi[k]
    pair, ep = k
    c = fams_of(pair, ep)
    g = gains(d)
    parts = []
    for fam, _ in c.most_common():
        gg = fam_gains(pair, ep, fam)
        if len(gg) >= 2:
            parts.append('`%s` **%+.3f**(n=%d, t=%.2f)' % (fam, st.mean(list(gg.values())),
                                                          len(gg), tstat(list(gg.values()))))
        else:
            parts.append('`%s` —' % fam)
    w('| `%s` | %d | %d | %d | %s | **%+.3f**（t=%.2f） | %s |' %
      (pair, ep, len(d), len(c),
       '、'.join('`%s`(%d)' % (fa, n) for fa, n in c.most_common()),
       st.mean(list(g.values())), tstat(list(g.values())), '；'.join(parts)))
w()
w('## 3. 两类后果（必须分开说）')
w()
w('### 3.1 数值被平均掉 —— 影响 §4.2')
w()
w('| 格 | 论文 | 论文所在的族 | 该族值 | 旧口径（混合）值 | 差 |')
w('|---|---|---|---|---|---|')
for pair, ds, e, fam, paper in (
        ('smoke→sfchd', 'sfchd_20p_b', 100, 'b2', 1.666),
        ('shwd2sf→sfchd', 'sfchd_20p_b', 30, 'b2', 0.812),
        ('shwd2sf→sfchd', 'sfchd_20p_b', 50, 'b2', 0.728),
        ('shwd2sf→sfchd', 'sfchd_20p_b', 100, 'b2', 0.694),
        ('shwd2sf→sfchd', 'sfchd_20p_b', 200, 'b2', 0.794)):
    d = OLD.get((pair, e))
    if not d:
        continue
    gg = fam_gains(pair, e, fam)
    famv = st.mean(list(gg.values())) if len(gg) >= 2 else float('nan')
    oldv = st.mean(list(gains(d).values()))
    w('| `%s` %dep | %+.3f | `%s` | **%+.3f**（n=%d） | %+.3f | 论文与族值差 **%.3f**；族值与旧口径差 **%.3f** |'
      % (pair, e, paper, fam, famv, len(gg), oldv, abs(famv - paper), abs(famv - oldv)))
w()
w('### 3.2 ★ 方向被改掉 —— 影响 §4.4（这一类才危险）')
w()
d = OLD.get(('y11_shwd→sfchd', 100))
if d:
    gg_all = gains(d)
    gg_y11 = fam_gains('y11_shwd→sfchd', 100, 'y11')
    gg_b2 = fam_gains('y11_shwd→sfchd', 100, 'b2')
    w('`y11_shwd→sfchd` 100ep：')
    w()
    w('| 口径 | n | 增益(pp) | t | 读出来是什么 |')
    w('|---|---|---|---|---|')
    w('| 旧口径（混 `b2`+`y11`） | %d | **%+.4f** | **%.2f** | "有一个接近显著的正增益" |' %
      (len(gg_all), st.mean(list(gg_all.values())), tstat(list(gg_all.values()))))
    w('| 只看族 `y11`（= 论文的架构对照） | %d | **%+.4f** | **%.2f** | "无增益"（= 论文 §4.4 的结论） |' %
      (len(gg_y11), st.mean(list(gg_y11.values())), tstat(list(gg_y11.values()))))
    w('| 只看族 `b2`（另一批同配对实验） | %d | **%+.4f** | **%.2f** | 参考 |' %
      (len(gg_b2), st.mean(list(gg_b2.values())), tstat(list(gg_b2.values()))))
    w()
    w('⇒ **论文 §4.4 的结论是对的**（这一格在 100ep 无增益），**是旧复算口径把它算成了有增益**。')
    w('   这类"混族改方向"比"混族改数值"严重得多：它会让复核者**以为论文错了**。')
    w()
w('## 4. 逐格后果分类（红/黄）')
w()
red, yellow = [], []
for k, d in multi.items():
    pair, ep = k
    signs = set()
    for fam, _ in fams_of(pair, ep).most_common():
        gg = fam_gains(pair, ep, fam)
        if len(gg) >= 2:
            signs.add(1 if st.mean(list(gg.values())) > 0 else -1)
    if len(signs) > 1:
        red.append(k)
    else:
        yellow.append(k)
w('* **红（各族符号相反 ⇒ 混合会改结论方向）：%d 格**' % len(red))
for k in sorted(red, key=str):
    w('  * `%s` %dep' % k)
w('* **黄（各族同号、只是数值被平均）：%d 格**' % len(yellow))
for k in sorted(yellow, key=str):
    w('  * `%s` %dep' % k)
w()
w('## 5. 影响哪些既有产出（**状态截至 2026-09-30 本会话收口**）')
w()
w('> ★ 下表右列是**处置状态**；带 ✅ 的已在**本会话内执行完毕**。')
w()
w('| 产出 | 影响 | 处置状态 |')
w('|---|---|---|')
w('| `analysis\\A5_种子方差.md` §1 | `visdrone→dota15` 100ep 的"13 个配对种子"= 族 `t1c` 的 s42–s51 + 族 `vis` 的 s52/s53/s54 | ✅ **已改**：现写明"族 `t1c`，种子 s42–s51"，并列出同格另外 5 个族 |')
w('| `analysis\\A5_种子方差.md` §2 | `shwd2sf` 四点旧值 +0.313/+0.703/+0.541/+0.758 ⇒ 族 `b2` 值 **+0.812/+0.728/+0.694/+0.794** | ✅ **已改**：按族 `b2` 重算，四点**与论文逐位吻合** |')
w('| `analysis\\A5_种子方差.md` §7 | 同上 | ✅ **已改**：标题按表计算为"族键修正后 **8/8** 逐位"；`smoke→sfchd` 30ep 的 s50 曾记为缺件，现**已闭合并并入底座**（生成器按短名回退后读数回到表内） |')
w('| `analysis\\A2_损失平面可测性.md` | 端点翻转判定建在同一批混合格上 | ✅ **已重算**：格数 63→**88**，翻转 7 个（8%），每条都带族名 |')
w('| `deliver\\claims_to_evidence.md` #10–#13 | `shwd2sf` 四点 | ✅ **已改判**：❌未复现 → **✅逐位**（口径：族 `b2`）|')
w('| `deliver\\claims_to_evidence.md` #8 | `smoke→sfchd` 100ep | ✅ **已改判**：❌未复现 → **✅逐位**（口径：族 `b2`）|')
w('| `deliver\\claims_to_evidence.md` #6 | `smoke→sfchd` 30ep | ✅ **已定案**：⚠（缺 s50 的 test 读数）。s50 的 val 侧增益 +4.593，与"10 种子要到 +3.656 需 +4.600"相符 |')
w('| `deliver\\claims_to_evidence.md` #15 | YOLO11n 100ep 旧为 +0.1930(t=2.04) | ✅ **已改判**：族 `y11` + 列 `best_map50_95` ⇒ **−0.0050（t=−0.099）逐位**；30ep 亦逐位 |')
w('| `deliver\\claims_to_evidence.md` #14 | `mask→mendeley` | ✅ **已闭合**：§4.3 采 **`t2`**（`mende_20p` · 100ep · 列 `best_map50_95` · s42–s51）；`r10` n=13 作第二批次独立佐证 |')
w('| `analysis\\A1_格完整性.md` §2 | "配对种子"数同样缺 `family`、虚高 | ✅ **已改**：格键含族；可配对核心格 **126 → 148** |')
w()
w('### 5.1 汇总（本会话收口后）')
w()
w('| 状态 | 修正前 | 修正后 |')
w('|---|---|---|')
w('| ✅逐位 | 10 | **17** |')
w('| ⚠口径待定 | 5 | **7** |')
w('| ❌未复现 | **8** | **0** |')
w('| ⛔不可核 | 6 | 6 |')
w()
w('⇒ **8 条"未复现"全部闭合**：6 条是族混杂、1 条是"未写明指标列"（§4.4 用 val 侧 `best_map50_95`）、')
w('1 条是"缺件的 test 读数"（`smoke→sfchd` 30ep 的 s50，且已给出可核算式）。')
w()
w('### 5.2 附带发现：**同一节内也可能换列**')
w()
w('§4.4 的 YOLO11n 两点用的是 **val 侧 `best_map50_95`**，而 §4.1/§4.2/§5 用 **test 侧 `test_map50_95`**。')
w('这两列在同一格上可以差很多（`shwd2sf→sfchd20` · 族 `r10` · 100ep · n=13：test **+0.628** / best **−0.307** —— **换列即翻号**）。')
w('论文正文只说 "Gains are percentage points of mAP50-95"，**没有写明是哪一列 / 哪一侧** ⇒')
w('这是投稿前必须统一或显式披露的口径问题。')
w()
w('## 6. 已执行的修法')
w()
w('1. `06_A25.py`：`cells()` 格键 `(pair, epochs)` → **`(pair, family, epochs)`**；')
w('   §1/§2 显式点名声明的族（§4.1 两端点的族名**不同**：100ep `t1c`/`t1b`，200ep `mech`）；')
w('   闸门表与 A2 表都加族列；新增 §7.1（s50 缺件定案）与 §8（影响面交叉引用）。')
w('2. `04_A1_grid.py`：格键加 `family`；§2 表加族列；§5 新增"族混杂"缺口条。')
w('3. `07_claims.py`：`cell()` 加 `fam` 与 `key` 两个维度；新增 `FAM` 映射表（论文每个数字点名一个族）；')
w('   修正"同一 (种子,臂) 多行时取到空读数存档件"的取值 bug（改为 `_pick`：先丢空读数、再按结局优先级）。')
w('4. **保留"跨族合并"作为第二种口径并显式标注** —— 它在"同一实验被分到两个族名"时反而是对的，')
w('   所以**不能一律禁用，只能显式声明**。')
w()
w('> 备份：`_bak_familyfix_20260930_200748\\`（改动前的 3 个脚本 + 4 个产出）。')
w()

open(os.path.join(OUT, 'A7_族混杂复核.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n输出 -> %s' % os.path.join(OUT, 'A7_族混杂复核.md'))
