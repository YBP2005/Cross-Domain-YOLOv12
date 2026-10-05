# -*- coding: utf-8 -*-
"""36_A20_loss_contrast.py —— **损失轴的实测对照**（回答"要不要重跑"）。

背景（2026-10-01）：
  `A15` 报"同格含两种非空 loss 的格 = 0"，据此把损失轴列为**不可识别**。
  但那个 0 是**管线看不见**造成的：换损失的 run 名形如 `{族}_{loss}_{轮数}`，
  其 `lr_arm` **为空** ⇒ 进不了 `_cells` 的格图（格图只收 `base`/`lr005` 两臂）。
  ⇒ 正确问法不是"有没有两种 loss"，而是"**同一格、同一臂、同一种子下有没有两种 loss**"。

本件做三件事：
  ① 用**数据驱动**的方式把换损失 run 归臂（比对该格的 `base`/`lr005` 臂的 `lr0`）；
  ② 在 **(配对, 族, 轮数, 种子, 预训练权重)** 这一粒度上找 loss 对照；
  ③ 分开报两类量，因为它们回答不同问题：
     · **base 臂的损失效应** = `loss-base` − `shapeiou-base`（**现有数据可算**）
     · **对增益的损失效应** = 需要 `loss-lr005` 与 `loss-base` 同时存在（**现有数据几乎不可算**）

产出：`analysis/A20_损失轴实测对照.md`
"""
import os
import re
import sys
import collections
import statistics as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import _cells as C            # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'analysis', 'A20_损失轴实测对照.md')
SEEDPAT = re.compile(r'_s(\d+)(n?)$')

rows, _ = C.load()
L = []


def w(s=''):
    L.append(s)


def seedof(r):
    m = SEEDPAT.search(r['run'])
    return int(m.group(1)) if m else None


# ---------- ① 数据驱动地归臂 ----------
# 每个 (配对, 族, 轮数) 下：shapeiou 的 base / lr005 各自的 lr0 是"臂的指纹"。
# 换损失 run 若 lr0 等于某臂的指纹，就归到那一臂。
armprint = collections.defaultdict(lambda: {'base': set(), 'lr005': set()})
for r in rows:
    if (r.get('loss') or '').strip() != 'shapeiou':
        continue
    if r['lr_arm'] not in ('base', 'lr005') or not C.f(r['epochs_nominal']):
        continue
    k = (C.pair_of(r), r['family'], int(C.f(r['epochs_nominal'])))
    if r['lr0']:
        armprint[k][r['lr_arm']].add(r['lr0'])

alt_by_cell = collections.defaultdict(list)
for r in rows:
    lo = (r.get('loss') or '').strip()
    if not lo or lo == 'shapeiou' or not C.f(r['epochs_nominal']):
        continue
    k = (C.pair_of(r), r['family'], int(C.f(r['epochs_nominal'])))
    pr = armprint.get(k, {'base': set(), 'lr005': set()})
    arm = None
    if r['lr0'] and r['lr0'] in pr['base'] and r['lr0'] not in pr['lr005']:
        arm = 'base'
    elif r['lr0'] and r['lr0'] in pr['lr005'] and r['lr0'] not in pr['base']:
        arm = 'lr005'
    alt_by_cell[k].append((r, arm))

# ---------- ②③ 逐 (格, 种子, 预训练) 找对照 ----------
pairs_found = []
unassigned = []
for k, vs in sorted(alt_by_cell.items(), key=lambda x: str(x[0])):
    pair, fam, ep = k
    for r, arm in vs:
        if arm is None:
            unassigned.append((k, r['loss'], r['lr0']))
            continue
        sd = seedof(r)
        if sd is None:
            continue                     # 无种子后缀 ⇒ 不可配对（当真种子用会造假）
        mates = [x for x in rows
                 if C.pair_of(x) == pair and x['family'] == fam
                 and C.f(x['epochs_nominal']) and int(C.f(x['epochs_nominal'])) == ep
                 and x['lr_arm'] == arm and (x.get('loss') or '').strip() == 'shapeiou'
                 and seedof(x) == sd and x['model'] == r['model']]
        if not mates:
            continue
        try:
            dv = C.f(r['test_map50_95'])
            dm = C.f(mates[0]['test_map50_95'])
        except Exception:
            dv = dm = None
        pairs_found.append(dict(k=k, arm=arm, loss=r['loss'], seed=sd, model=r['model'],
                                alt=dv, base=dm, run=r['run'], base_arm=mates[0]['run']))

# 汇总到 (格, 臂, loss)
grp = collections.defaultdict(list)
for p in pairs_found:
    grp[(p['k'], p['arm'], p['loss'])].append(p)

w('# A20 损失轴的**实测对照**（回答"损失轴要不要重跑"）')
w()
w('> 数据 = `base/run_table_canonical.csv`（**%d 行**）。' % len(rows))
w('> 口径：`lr005 − base` 是论文的"增益"；**损失轴**问的是"换损失后这个增益还在不在"。')
w('> ★ 本件只做**可复算**的部分，并把不可算的部分**明确标成缺件**，不估算。')
w()

w('## 一、为什么 `A15` 说"0 格"——那是**管线看不见**，不是数据没有')
w()
w('换损失的 run 名形如 `{族}_{loss}_{轮数}`（如 `dota15_css_100ep`），其 `lr_arm` **为空**：')
w()
w('```')
w('run                          lr_arm   loss    lr0')
for r in [x for x in rows if (x.get('loss') or '').strip() not in ('', 'shapeiou')][:4]:
    w('%-28s %-8s %-7s %s' % (r['run'][:28], repr(r['lr_arm']), r['loss'], r['lr0']))
w('```')
w()
w('`_cells.load()` 的格图**只收 `base` / `lr005` 两臂** ⇒ 这些 run 一个都进不去，')
w('于是"同格两种非空 loss 的格 = 0"。**这个 0 是口径造成的，不是事实。**')
w()
w('★ 归臂是**可判定的**：每个 (配对, 族, 轮数) 下，`base` 臂的 `lr0` 与 `lr005` 臂的 `lr0`')
w('是两枚指纹；换损失 run 的 `lr0` 落在那一边，就属于那一臂。实测：')
w()
w('| 归臂结果 | 条数 |')
w('|---|---|')
w('| 归到 **`base`** 臂（`lr0` 与 base 指纹一致） | **%d** |'
  % sum(1 for v in alt_by_cell.values() for _, a in v if a == 'base'))
w('| 归到 **`lr005`** 臂 | **%d** |'
  % sum(1 for v in alt_by_cell.values() for _, a in v if a == 'lr005'))
w('| **归不上**（该格没有 shapeiou 两臂可作指纹） | **%d** |' % len(unassigned))
w()
if unassigned:
    w('归不上的（这些格**没有** shapeiou 两臂，故无法判定换损失跑属于哪一臂）：')
    w()
    for k, lo, lr0 in unassigned:
        w('* `%s` / `%s` / %sep —— loss=`%s`, lr0=`%s`' % (k[0], k[1], k[2], lo, lr0))
    w()

w('## 二、★ **base 臂的损失效应** —— 现有数据**可算**')
w()
w('量 = `loss-base` − `shapeiou-base`，在 **(配对, 族, 轮数, 种子, 预训练权重)** 全部相同的条件下配对。')
w('（预训练权重必须相同：`model` 不同就是"换了预训练"，那是另一个干预。）')
w()
w('| 配对 | 族 | 轮数 | 臂 | 损失 | n | 换损失均值 | shapeiou 均值 | **损失效应(pp)** | t |')
w('|---|---|---|---|---|---|---|---|---|---|')
reportable = []
for k, arm, lo in sorted(grp, key=lambda x: str(x)):
    g = grp[(k, arm, lo)]
    dv = [C.f(p['alt']) * 100 for p in g if C.f(p['alt']) is not None]
    bv = [C.f(p['base']) * 100 for p in g if C.f(p['base']) is not None]
    if len(dv) < 2 or len(dv) != len(bv):
        continue
    d = [a - b for a, b in zip(dv, bv)]
    m = st.mean(d)
    sd = st.stdev(d)
    t = m / (sd / (len(d) ** 0.5)) if sd > 0 else float('nan')
    ok = (len(d) >= 10) or (len(d) >= 5 and (all(x < 0 for x in d) or all(x > 0 for x in d))) or abs(t) >= 4
    w('| `%s` | `%s` | %s | `%s` | `%s` | %d | %+.3f | %+.3f | **%+.3f** | %+.2f |'
      % (k[0], k[1], k[2], arm, lo, len(d), st.mean(dv), st.mean(bv), m, t))
    reportable.append((k, arm, lo, len(d), m, t, ok))
w()
n_ok = sum(1 for x in reportable if x[6])
w('* 可算的 (格, 臂, 损失) 组：**%d**；其中**过论文自己的种子闸门**（n≥10 / n≥5 且全同号 / |t|≥4）：**%d**。'
  % (len(reportable), n_ok))
w('* 逐条目数普遍很小（2–6），**按论文自己的闸门大多不可报方向** —— 这一点必须照实说。')
w()

w('## 三、★★ **对"增益"的损失效应** —— 补实验后**首次可算**')
w()
w('论文的因变量是**增益** `lr005 − base`。"换损失后增益还在不在"需要')
w('**四条腿**同时存在：`shapeiou-base` / `shapeiou-lr005` / `{loss}-base` / `{loss}-lr005`。')
w()
# ★ 动态判定（2026-10-02）：补实验补的正是 `{loss}-lr005` 腿，
#   所以这一节**必须算**，不能像第一版那样写死"格不存在"。写死过一次，就过期了一次。
four = []
for k, vs in alt_by_cell.items():
    pr = armprint.get(k, {'base': set(), 'lr005': set()})
    if not (pr['base'] and pr['lr005']):
        continue
    byl = collections.defaultdict(set)
    for r, a in vs:
        if a:
            byl[(r.get('loss') or '').strip()].add(a)
    for lo, arms in byl.items():
        if {'base', 'lr005'} <= arms:
            four.append((k, lo))
four.sort(key=lambda x: str(x))
w('实测：换损失的 run 归到 **`lr005` 臂的有 %d 条**（第一版是 0 —— 补实验前确实没有这一腿）。'
  % sum(1 for v in alt_by_cell.values() for _, a in v if a == 'lr005'))
w()
w('**四条腿齐备的 (格, 损失)：%d 个**' % len(four))
w()
for k, lo in four:
    w('  * `%s` / 族 `%s` / %dep / 损失 `%s`' % (k[0], k[1], k[2], lo))
w()
if four:
    w('⇒ ★ **"损失对增益的效应"现在可算** —— 此前本节写"格不存在"，那是**补实验之前**的事实。')
    w('⇒ 逐组增益、损失对增益的幅度与 t、符号一致性，见 `analysis\\A22_损失对增益_实测.md`'
      '（生成器 `scripts\\41_A22_loss_on_gain.py`）。')
else:
    w('⇒ **"损失对增益的效应"仍不可识别** —— 是格不存在，不是统计功效不足。')
w()
w('## 四、结论：需不需要重跑？')
w()
w('| 轴 | 现状 | 要重跑吗 |')
w('|---|---|---|')
w('| **base 臂的损失效应** | 可算 **%d** 组（过闸门 %d 组） | ❌ **不用**（可直接进补充材料） |'
  % (len(reportable), n_ok))
if four:
    w('| **损失对增益的效应** | **四腿齐备 %d 组**（已可算） | ❌ **不用再补**；见 `A22` |' % len(four))
else:
    w('| **损失对增益的效应** | 缺 `{loss}-lr005` 臂 | ✅ **要**：在已有 `{loss}-base` 的格上各补 lr005 臂 |')
w()
w('> **最小实验设计（若还要补）**：挑 `n≥3` 的干净格（本件第二节里 n≥3 的那几组），')
w('> 每格补 `{loss}-lr005` 的同样种子 —— 即"换损失跑一遍 lr005 臂"。')
w('> 每格需要 **`n` 个 run**（`n` = 该格已有种子的个数），不是乘积。')
w()

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('输出 -> %s' % OUT)
print('可算 (格,臂,损失) 组 %d；过闸门 %d；归不上臂 %d' % (len(reportable), n_ok, len(unassigned)))
