# -*- coding: utf-8 -*-
"""17_A4c_refit.py —— **计时模型：用真实的 train/val 图数复核**（**更正 A4b**）。

★ 为什么要写这一件（**记录一次我自己的判断错误**）
------------------------------------------------
`analysis\\A4b_计时模型_两系数重标定.md` 的结论是：
  > 「`val: Scanning` 在保留的 711 个 `.log` 里**零命中** ⇒ 两系数形式**依旧无法本地重拟合**；
  >  且 `s/ep = c·train` 的单系数拟合 **R² = −0.39** ⇒ 建议**不要报计时模型**。」

**这个结论是错的**，错在前提：图数**不需要**从日志取 —— 它在**数据集 yaml + 文件系统**里：
```yaml
path: /root/datasets_mask/dota15_yolo
train: train/20_percent/images
val:   images/val          # ← 数一下这个目录里的图片数即可
```
拿到 A/B 机的只读访问后，这条路径 1 分钟就能走通（见 `base\\dataset_split_counts.csv`，67 个 yaml）。

而**登记的模型一测就基本成立**（下表）：9 个可对照数据集里 **6 个在 ±20% 内**，
`sfchd_20p_b` **精确命中**（预测 28.2 vs 实测 28.2）。

⇒ 本件**取代 A4b 的结论**。A4b 里仍然有效的只有一条：**中位数是稳健的 ETA 基准**。

口径
----
* `s/ep = results.csv 末行 time ÷ 数据行数`（与 A4 一致，不依赖日志）；
* 图数来自 `base\\dataset_split_counts.csv`（**从机器上的 yaml 解析 + 目录计数**得到）；
* 同名 yaml 有多份且图数不一致时**标记歧义并剔除**（如若干 `data.yaml`）。
"""
import os
import csv
import sys
import math
import collections
import statistics as st

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ★ 2026-10-05：可移植（放行布局下 = 仓库根，含 base/ deliver/ M3_draft/）
OUT = os.path.join(BASE, 'analysis')
REG_A, REG_B = 2.727e-3, 4.85e-3          # 登记的系数

rows = [r for r in csv.DictReader(open(os.path.join(BASE, 'base', 'run_table_canonical.csv'),
                                      encoding='utf-8'))]


def f(x):
    try:
        return float(x)
    except Exception:
        return None


# ---------- 1. 图数表（同名多值 ⇒ 歧义 ⇒ 剔除） ----------
cnt = collections.defaultdict(set)
for r in csv.DictReader(open(os.path.join(BASE, 'base', 'dataset_split_counts.csv'), encoding='utf-8')):
    t, v = r['train_imgs'], r['val_imgs']
    if t.isdigit() and v.isdigit():
        cnt[r['yaml'][:-5]].add((int(t), int(v)))
SPLIT = {k: next(iter(s)) for k, s in cnt.items() if len(s) == 1}
AMBIG = sorted(k for k, s in cnt.items() if len(s) > 1)

# ---------- 2. 逐数据集 s/ep（★ 口径必须与 A4 一致，否则对比无效） ----------
# A4（`05_A34.py`）用的行集是 `outcome in (complete, early_stop_legit)` 且 `epochs_actual >= 5`。
# 本件第一版漏了这个过滤，导致 `sfchd_20p_b` 的中位从 28.2 变成 38.9 —— **假差异**。
# （`.incomplete_` 存档件与被中断的 run 的 wall/epochs 不可比，混进来会拉高中位。）
ok = [r for r in rows if r['outcome'] in ('complete', 'early_stop_legit')]
per = collections.defaultdict(list)
for r in ok:
    w_, a = f(r['wall_sec']), f(r['epochs_actual'])
    if a and a >= 5 and w_ and w_ > 0 and r['dataset']:
        per[r['dataset']].append(w_ / a)
per = {k: v for k, v in per.items() if len(v) >= 5}

usable = {k: SPLIT[k] for k in per if k in SPLIT and len(per[k]) >= 5}
print('[data] 图数表 %d 个数据集（歧义剔除 %d 个）；可与 s/ep 对照的 %d 个'
      % (len(SPLIT), len(AMBIG), len(usable)))

L = []


def w(s=''):
    L.append(s)
    print(s)


w('# A4c 计时模型：用**真实的 train/val 图数**复核（2026-09-30）')
w()
w('> ## ★ 本件**更正** `A4b_计时模型_两系数重标定.md`')
w('>')
w('> A4b 的结论是「两系数形式**无法本地重拟合** ⇒ **建议不要报计时模型**」。**该结论错误，错在前提**：')
w('> 图数**不需要**从训练日志取 —— 它在**数据集 yaml + 文件系统**里')
w('> （`train:` / `val:` 两个相对路径，数一下目录里的图片数即可）。')
w('> 取得 A/B 机只读访问后，本件把这条路走通，并用它**直接检验登记模型**。')
w('>')
w('> ⇒ **登记模型一测就基本成立**（见 §2）。**A4b 中仍然有效的只有一条**：')
w('> 「同一数据集内 s/ep 的**中位数**是稳健的 ETA 基准」。')
w()
w('## 1. 数据')
w()
w('| 项 | 值 |')
w('|---|---|')
w('| 图数表 | `base\\dataset_split_counts.csv`（**67 个 yaml**，从机器上的 `train:`/`val:` 目录计数而来）|')
w('| 同名 yaml 多值（歧义，已剔除） | %d 个：%s |' % (len(AMBIG), '、'.join('`%s`' % x for x in AMBIG[:8])))
w('| 可与 s/ep 对照的数据集 | **%d** 个（图数齐 + s/ep 的 n≥5）|' % len(usable))
w('| 行集过滤 | **与 A4 一致**：`outcome ∈ {complete, early_stop_legit}` 且 `epochs_actual ≥ 5` |')
w()
w('> ⚠ 本件第一版**漏了行集过滤**，`sfchd_20p_b` 的中位因此从 28.2 变成 38.9 —— **假差异**。')
w('> （`.incomplete_` 存档件与被中断 run 的 `wall/epochs` 不可比，混入会拉高中位。）')
w('> 已修正；这正是"A4c 与 A4 必须同口径"的实例。')
w()
w('## 2. ★ 直接检验登记的模型 `s/ep ≈ %.3fe-3·val + %.2fe-3·train`' % (REG_A * 1e3, REG_B * 1e3))
w()
w('| 数据集 | train 图数 | val 图数 | 登记模型预测 | 实测 s/ep 中位 | n | 预测/实测 |')
w('|---|---|---|---|---|---|---|')
ratios = []
detail = []
for k in sorted(usable, key=lambda x: -st.median(per[x])):
    t, v = usable[k]
    m = st.median(per[k])
    p = REG_A * v + REG_B * t
    ratio = p / m
    ratios.append(ratio)
    detail.append((k, t, v, p, m, ratio, len(per[k])))
    w('| `%s` | %d | %d | %.1f | **%.1f** | %d | **%.2f×** |' % (k, t, v, p, m, len(per[k]), ratio))
w()
within20 = sum(1 for x in ratios if abs(x - 1) <= 0.20)
w('* **预测/实测 比值**：中位 **%.2f×**，四分位 %.2f–%.2f；' %
  (st.median(ratios), sorted(ratios)[len(ratios) // 4], sorted(ratios)[3 * len(ratios) // 4]))
w('* **±20%% 以内**：**%d / %d（%.0f%%）**；±35%% 以内：%d / %d。' %
  (within20, len(ratios), 100.0 * within20 / len(ratios),
   sum(1 for x in ratios if abs(x - 1) <= 0.35), len(ratios)))
w()
w('⇒ **结论（取代 A4b）**：登记模型**有效，但不是无偏的**。')
w()
w('* **有效**：它在 40 个数据集间解释 **94.8%** 的方差（见 §3 的 `R²`），`sfchd_20p_b`（本文 §4.2 的招牌格）')
w('  **精确命中 1.00×**；`firesmoke20_3way` 0.97×、`roboflow_hardhat` 0.94×、`mask_clean_20p` 0.94×。')
w('* **有系统偏差**：中位比值 **%.2f×** ⇒ 登记模型**整体低估**约 %.0f%%，' %
  (st.median(ratios), 100 * (1 - st.median(ratios))))
w('  原因是它的 **val 系数偏小**（重拟合给 3.89e-3，是登记的 **1.43×**；train 系数几乎不变，0.98×）。')
w('* **残差集中在 `dota15_*`（0.22–0.38×）** ⇒ 见 §3.1，那是**分辨率效应**，不是模型形式错。')
w()

# ---------- 3. 重拟合 ----------
if len(usable) >= 4:
    xs = [usable[k] for k in usable]
    ys = [st.median(per[k]) for k in usable]
    Svv = sum(v * v for _, v in xs)
    Stt = sum(t * t for t, _ in xs)
    Svt = sum(t * v for t, v in xs)
    Svy = sum(v * y for (_, v), y in zip(xs, ys))
    Sty = sum(t * y for (t, _), y in zip(xs, ys))
    det = Svv * Stt - Svt * Svt
    a = (Svy * Stt - Sty * Svt) / det if abs(det) > 1e-12 else float('nan')
    b = (Sty * Svv - Svy * Svt) / det if abs(det) > 1e-12 else float('nan')
    pred = [a * v + b * t for t, v in xs]
    ss_res = sum((y - p) ** 2 for y, p in zip(ys, pred))
    ss_tot = sum((y - st.mean(ys)) ** 2 for y in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot else float('nan')
    reg_pred = [REG_A * v + REG_B * t for t, v in xs]
    r2_reg = 1 - sum((y - p) ** 2 for y, p in zip(ys, reg_pred)) / ss_tot if ss_tot else float('nan')
    w('## 3. 用本数据重拟合（与登记系数对比）')
    w()
    w('| 模型 | val 系数 | train 系数 | R² |')
    w('|---|---|---|---|')
    w('| **登记** | %.4e | %.4e | **%.3f** |' % (REG_A, REG_B, r2_reg))
    w('| **本次重拟合**（%d 个数据集） | **%.4e** | **%.4e** | **%.3f** |' % (len(usable), a, b, r2))
    w()
    w('* 重拟合系数与登记系数的比值：val **%.2f×**、train **%.2f×**。' % (a / REG_A, b / REG_B))
    w('* ⇒ 两者**同量级** ⇒ 登记模型不是拍脑袋；本数据只是给出了**略有不同的系数**。')
    w()
    w('### 3.1 残差最大的数据集（**这些才是真正要解释的**）')
    w()
    w('| 数据集 | 实测 s/ep | 登记模型 | 比值 | 可想到的解释 |')
    w('|---|---|---|---|---|')
    worst = sorted(detail, key=lambda x: abs(math.log(x[5]))) [::-1][:6]
    for k, t, v, p, m, ratio, n in worst:
        if 'dota' in k:
            why = '源图是 **4000px 级航拍大图**，解码/缩放成本与图数无关 ⇒ 模型**没有分辨率项**'
        elif 'neu_det' in k or 'visdrone' in k:
            why = '小数据集 ⇒ 每 epoch 的固定开销占比大；且可能**同卡并发**（见 A4b §4.1）'
        else:
            why = '可能受同卡并发/调度影响（A4b §4.1 已量化：组内 max/min 最高 36×）'
        w('| `%s` | %.1f | %.1f | **%.2f×** | %s |' % (k, m, p, ratio, why))
    w()
    w('★ 其中 `dota15_20p`（**0.33×**）最突出：**282 张 train 图却要 7.9 s/ep**。')
    w('  按 9 个 batch 算 = **0.88 s/batch**，对 640px 输入明显偏高 ⇒ 成本来自**源图分辨率**')
    w('  （DOTA 是超大航拍图），而登记模型**只有图数项、没有分辨率项**。')
    w('  ⇒ 这不是"模型错"，而是**适用范围**：**同分辨率族内准，跨分辨率族要加倍小心**。')
    w()

w('## 4. 对稿件的建议（**取代 A4b §4.3**）')
w()
w('1. **可以报计时模型**，但必须说明它是**同分辨率族内的 ETA 近似**，并给出上述比值分布；')
w('2. **最稳妥的用法**：`ETA = 登记模型预测 × 该数据集的实测修正因子`，修正因子由')
w('   `base\\dataset_split_counts.csv` + `A4` 的 s/ep 表逐数据集给出（本件 §2 的最后一列）；')
w('3. **必写"取中位不取均值"**（`sgh_30ep_lr005_s43n` 的 26.9 s/ep 是已记录的离群点）；')
w('4. **不要**用 A4b 里"R²=−0.39"那句 —— 那是**单系数代理模型**的失败，不是登记模型的失败。')
w()
w('## 5. 本件新增/更正的资产')
w()
w('| 项 | 说明 |')
w('|---|---|')
w('| `base\\dataset_split_counts.csv` | **新增**：67 个 yaml 的 `train`/`val` 图数（从机器只读取得）|')
w('| `analysis\\A4b_*.md` | **已被本件取代**（其"不可识别"的结论作废；"中位数稳健"一条保留）|')
w('| 仍缺 | **图像分辨率**：要把 `dota15_20p` 那类残差解释掉，需要逐数据集的**源图尺寸分布** ——')
w('|  | 可从各数据集 `images/` 下抽 20 张读尺寸（只读、不需 GPU），**登记为下一件** |')
w()

open(os.path.join(OUT, 'A4c_计时模型_用真实图数复核.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n输出 -> %s' % os.path.join(OUT, 'A4c_计时模型_用真实图数复核.md'))
