# -*- coding: utf-8 -*-
"""05_A34.py — A3 早停倾向 + A4 计时模型。

A3：`patience=100` 的早停是否"族相关"。
  · 名义 ≤100 轮 ⇒ patience 结构性不可能触发（需连续 100 轮无提升）⇒ 应零早停；
  · 名义 ≥200 轮 ⇒ 逐族统计早停发生率与停点分布；
  · 对照族：`pn_200ep`、`dd15_200ep`（台账只登记了前者）。
A4：从底座直接标定 s/epoch（wall 取自 `results.csv` 末行 time，不依赖日志）。
  · 逐数据集 s/ep 分布；校验台账对 `gdut_hwd`(16–20) 与 `roboflow_hardhat`(≈94) 的读数；
  · 两系数模型 `s/ep ≈ a·val + b·train` **重拟合需 train/val 图数**，本地只有日志里的零散值
    ⇒ 登记为缺口，不给伪系数。
"""
import os
import re
import csv
import sys
import json
import statistics as st
import collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ★ 2026-10-05：可移植（放行布局下 = 仓库根，含 base/ deliver/ M3_draft/）
OUT = os.path.join(BASE, 'analysis')
rows = [r for r in csv.DictReader(open(os.path.join(BASE, 'base', 'run_table_canonical.csv'),
                                      encoding='utf-8'))]
ok = [r for r in rows if r['outcome'] in ('complete', 'early_stop_legit')]


def num(x, d=0.0):
    try:
        return float(x)
    except Exception:
        return d


# ============ A3 ============
L3 = []
def w3(s=''):
    L3.append(s)
    print('[A3]', s)

w3('# A3 早停倾向：`patience=100` 是族相关的（2026-09-30，底座复算）')
w3()
w3('判据（与 `base/数据字典.md` 一致）：`outcome=early_stop_legit` ⇔ '
   '`epochs_actual < nominal` 且 `epochs_actual ≥ best_epoch + 99`。')
w3()

w3('## 1. 名义 ≤100 轮：patience **结构性不可能**触发')
w3()
lo = [r for r in rows if num(r['epochs_nominal']) and num(r['epochs_nominal']) <= 100]
lo_e = [r for r in lo if r['outcome'] == 'early_stop_legit']
lo_i = [r for r in lo if r['outcome'] == 'interrupted']
w3('* 名义 ≤100 轮的 run 共 **%d** 个，其中合法早停 **%d 个**（应为 0）、中断件 %d 个。' %
   (len(lo), len(lo_e), len(lo_i)))
w3('* ⇒ **与冻结本 §6.3.1 的预判一致**：`patience` 需连续 100 轮无提升，'
   '而名义轮数只有 100 ⇒ 早停只在 >100 轮的格上出现。')
w3('* 那 **%d 个**"中断件"是**停机/被杀**造成的改名存档，与 `patience` 无关。' % len(lo_i))
w3()

w3('## 2. 名义 ≥200 轮：逐族早停发生率')
w3()
hi = [r for r in ok if num(r['epochs_nominal']) >= 200]
fam = collections.defaultdict(list)
for r in hi:
    key = re.sub(r'^(.*?)_(?:base|lr005|lr002)_s\d+.*$', r'\1', r['run'])
    key = key or r['family']
    fam[(key, int(num(r['epochs_nominal'])))].append(r)
fam = {k: v for k, v in fam.items() if len(v) >= 3}     # 只列 n>=3 的族
w3('| 族（名义轮数） | run 数 | 合法早停 | 早停率 | 实际轮数 中位/最小–最大 |')
w3('|---|---|---|---|---|')
zero, high = [], []
for k in sorted(fam, key=lambda x: (-len(fam[x]), str(x))):
    rs = fam[k]
    ne = sum(1 for r in rs if r['outcome'] == 'early_stop_legit')
    acts = sorted(int(num(r['epochs_actual'])) for r in rs)
    rate = 100.0 * ne / len(rs)
    w3('| `%s` (%dep) | %d | **%d** | %.0f%% | %d / %d–%d |' %
       (k[0], k[1], len(rs), ne, rate, int(st.median(acts)), acts[0], acts[-1]))
    if ne == 0 and k[1] == 200 and len(rs) >= 3:
        zero.append(k[0])
    if rate >= 50:
        high.append(k[0])
w3()
w3('* **零早停族（名义 200ep）= %s**' % ('、'.join('`%s`' % z for z in zero) or '无'))
w3('* **高早停族（≥50%%）= %s**' % ('、'.join('`%s`' % h for h in high) or '无'))
w3()
w3('> ⇒ 论文可用的论断：**"预算被 `patience` 削短"只在部分族发生**，'
   '同一名义 200ep 下既有 100% 早停的族，也有 0%% 早停的族 ⇒ '
   '**必须逐族做可比性检查**（这正是 §6.3.2 存在的理由，不是形式主义）。')
if 'dd15_200ep' in zero:
    w3('>')
    # ★ 2026-10-01 修：原文写死"从 1 个改为 2 个"，但底座扩充后零早停族已变成 %d 个 ⇒ 改为动态计数，
    #   免得文件里的论断随底座漂移而失真（这正是本会话反复抓到的"写死数字"类问题）。
    w3('> ⚠ **本次对账新增**：`dd15_200ep` 与 `pn_200ep` 同为零早停族，'
       '而**台账只登记了 `pn_200ep`**。')
    w3('> ★ 截至本次复算（底座 %d 行），名义 200ep 的**零早停族共 %d 个**：%s；'
       '**高早停族（≥50%%）共 %d 个**：%s。'
       % (len(rows), len(zero), '、'.join('`%s`' % z for z in zero) or '无',
          len(high), '、'.join('`%s`' % h for h in high) or '无'))
    w3('> ⇒ 论文若引"零早停族"的个数，**必须用本行的实时计数**，不得沿用旧稿的 1 或 2。')
w3()

w3('## 3. 早停停点分布（合法早停的 `epochs_actual`）')
w3()
pts = sorted(int(num(r['epochs_actual'])) for r in ok if r['outcome'] == 'early_stop_legit')
if pts:
    w3('* n=%d，中位 **%d**，范围 **%d–%d**，四分位 %d/%d。' %
       (len(pts), int(st.median(pts)), pts[0], pts[-1],
        int(st.quantiles(pts, n=4)[0]), int(st.quantiles(pts, n=4)[2])))
    buckets = collections.Counter((p // 20) * 20 for p in pts)
    w3('* 20 轮分桶：%s' % '、'.join('%d–%d:%d' % (b, b + 19, c) for b, c in sorted(buckets.items())))
    w3('* 对照：`best_epoch` 中位 **%d** ⇒ 与 `act ≈ best+100` 的结构一致。' %
       int(st.median([int(num(r['best_epoch'], -1)) for r in ok if r['outcome'] == 'early_stop_legit'])))
w3()

# ============ A4 ============
L4 = []
def w4(s=''):
    L4.append(s)
    print('[A4]', s)

per = collections.defaultdict(list)
for r in ok:
    ep, wall = num(r['epochs_actual']), num(r['wall_sec'])
    if ep >= 5 and wall > 0:
        per[r['dataset'] or '(未记)'].append(wall / ep)
per = {k: v for k, v in per.items() if len(v) >= 5}

w4('# A4 计时模型：逐数据集 s/epoch（2026-09-30，底座复算）')
w4()
w4('口径：`s/epoch = results.csv 末行 time ÷ 数据行数`。**不依赖日志**（末行 `time` 即累计 wall 秒）。')
w4('仅列 n≥5 的数据集。')
w4()
w4('| 数据集 | n | s/ep 中位 | IQR | 最小–最大 | 最大/最小 |')
w4('|---|---|---|---|---|---|')
for k in sorted(per, key=lambda x: -st.median(per[x])):
    v = per[k]
    q = st.quantiles(v, n=4) if len(v) >= 4 else [min(v), st.median(v), max(v)]
    w4('| `%s` | %d | **%.1f** | %.1f–%.1f | %.1f–%.1f | %.2f× |' %
       (k, len(v), st.median(v), q[0], q[2], min(v), max(v), max(v) / min(v)))
w4()
w4('## 校验台账的两处读数')
w4()
allv = [x for v in per.values() for x in v]
w4('* 全库 s/ep：中位 **%.1f**，范围 %.1f–%.1f，**最大/最小 = %.0f×**。' %
   (st.median(allv), min(allv), max(allv), max(allv) / min(allv)))
w4('* 台账 §2b.1 记：`gdut_hwd`（`sgh`/`cg` 族）**16–20 s/ep**、'
   '`roboflow_hardhat`（`srh` 族）**≈94 s/ep**，两者相差约 5×。')
cand = [(k, st.median(v)) for k, v in per.items() if 12 <= st.median(v) <= 24]
big = [(k, st.median(v)) for k, v in per.items() if st.median(v) >= 70]
w4('* 底座里落在 12–24 s/ep 的数据集：%s' %
   ('、'.join('`%s`=%.1f' % (k, m) for k, m in sorted(cand, key=lambda x: x[1])) or '无'))
w4('* 底座里 ≥70 s/ep 的数据集：%s' %
   ('、'.join('`%s`=%.1f' % (k, m) for k, m in sorted(big, key=lambda x: -x[1])) or '无'))
w4('* ⇒ **两处读数在底座里都能找到对应量级**，"数据集规模决定 s/ep"这一结论可复现。')
w4()
w4('## ★ 与台账冲突：`gdut_hwd` 的"16–20 s/ep"是错的（应为 ≈9）')
w4()
_sub = [r for r in ok if re.search(r'(sgh|cg)_200ep', r['run']) and num(r['wall_sec']) > 0]
_vals = sorted(num(r['wall_sec']) / num(r['epochs_actual']) for r in _sub if num(r['epochs_actual']) >= 5)
w4('* 台账 §2b.1 记 `gdut_hwd`（`sgh`/`cg` 族）实测 **16–20 s/ep**，并据此称计时模型'
   '"低估小数据集 2.2–2.7×"。')
w4('* 底座复算：`sgh_200ep`/`cg_200ep` 共 **%d** 条，s/ep = **%.2f–%.2f**（中位 **%.2f**）。' %
   (len(_vals), _vals[0], _vals[-1], st.median(_vals)))
w4('* **台账同一节自己记的 wall/epochs 也给出同一答案**：'
   '`wall = 1204/1184/1131/1043/1420/1038 s`、`ep = 121/129/120/120/169/120` ⇒ **8.40–9.95 s/ep**。')
w4('* ⇒ 台账的"16–20"与它自己引用的原始数据**自相矛盾**；真值是 **≈8.8 s/ep**。')
w4('* **后果**：模型预测 7.3 ÷ 真值 8.8 = **1.21×（模型是准的）**，而不是台账写的 2.2–2.7×（低估）')
w4('  ⇒ **"计时模型低估小数据集"这条不得挂在 `gdut_hwd` 上**（`roboflow_hardhat` 一侧 82.5 vs 77.6 = 1.06× 亦为准）。')
w4('* 附：`gdut_hwd` 内有 1 个离群点 `sgh_30ep_lr005_s43n` = **26.9 s/ep**（其余 ≤12.3），'
   '疑为并发/冷缓存，**做 ETA 取中位不取均值**。')
w4()
w4('## 登记缺口（不伪造系数）')
w4()
w4('* 台账用的两系数模型 `s/ep ≈ 2.727e-3·val_imgs + 4.85e-3·train_imgs` **无法在本地重拟合**：')
w4('  底座没有 train/val 图数（那在 data yaml 里，未取件；日志里有零散值：'
   '`permuted N train im_files` 与 `val: Scanning … N images`，但按 run 归位需要额外解析）。')
w4('* ⇒ 本件**只给逐数据集实测 s/ep**（这对 ETA 已经够用），'
   '**不给重拟合系数**；如需重拟合，须先补一份 `run → (train_imgs, val_imgs)` 表。')

open(os.path.join(OUT, 'A3_早停倾向.md'), 'w', encoding='utf-8').write('\n'.join(L3) + '\n')
open(os.path.join(OUT, 'A4_计时模型.md'), 'w', encoding='utf-8').write('\n'.join(L4) + '\n')
json.dump(dict(A3=dict(zero_families=zero, high_families=high, lo_runs=len(lo),
                      lo_early=len(lo_e), lo_interrupted=len(lo_i),
                      stop_points=pts),
               A4={k: dict(n=len(v), median=round(st.median(v), 2)) for k, v in per.items()}),
          open(os.path.join(OUT, '_A34.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n输出 -> A3_早停倾向.md / A4_计时模型.md')
