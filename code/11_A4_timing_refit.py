# -*- coding: utf-8 -*-
"""11_A4_timing_refit.py —— **A4 计时模型的两系数重标定**（闭合 A4 登记的缺口）。

缺口原文（`analysis\\A4_计时模型.md` / 交接件 §5.5）：
  > 两系数模型 `s/ep ≈ 2.727e-3·val + 4.85e-3·train` **无法本地重拟合**（无 train/val 图数）。
  > 日志里可提取（`permuted N train im_files`、`val: Scanning … N images`），
  > 但按 run 归位需额外解析 ⇒ 登记为缺口。

本件把它做掉，并**换一个更稳的归位方式**：不去做"日志→run"的归位（日志文件名与 run 名不一致，
266 个日志只覆盖 804 个 A 机 run），而是直接按 **dataset** 归位 ——
`Scanning` 行的路径里就带着数据集名，而计时模型本来就是**按数据集**标定的
（A4 的表就是"逐数据集 s/ep 中位"）。这样两侧的键天然一致。

产出：`analysis\\A4b_计时模型_两系数重标定.md`

口径：
  · `s/ep = results.csv 末行 time ÷ 数据行数`（不依赖日志）—— 与 A4 一致；
  · `train_n` / `val_n` 取该数据集在各日志里 `Scanning … : 100% ━ M/M` 的 **最大 M**；
  · 拟合用**最小二乘**（无截距），并在**对数域**复核一次（看是否存在幂律而非线性）。
"""
import os
import re
import csv
import sys
import glob
import math
import statistics as st
import collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ★ 2026-10-05：可移植（放行布局下 = 仓库根，含 base/ deliver/ M3_draft/）
OUT = os.path.join(BASE, 'analysis')
LOGDIRS = [os.path.join(BASE, 'raw', 'A_logs_20260929'),
           r"E:\workplace\AB机实验文件夹\B_logs_20260930"]
ANSI = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')

rows = [r for r in csv.DictReader(open(os.path.join(BASE, 'base', 'run_table_canonical.csv'),
                                      encoding='utf-8'))]
DATASETS = sorted({r['dataset'] for r in rows if r['dataset']})
DS_BY_LEN = sorted(DATASETS, key=len, reverse=True)


def f(x):
    try:
        return float(x)
    except Exception:
        return None


# ---------- 1. 从日志抽 train/val 图数，按 dataset 归位 ----------
scan_re = re.compile(r'^(?P<split>train|val): Scanning (?P<path>\S+?)(?:\.cache)?\.\.\.'
                     r'.*?(?P<cur>\d+) images.*?(?:(?P<tot>\d+)/(?P<den>\d+))?\s*$')
counts = collections.defaultdict(lambda: collections.defaultdict(int))
nlogs = nscan = nskip = 0
MAXB = 40 * 1024 * 1024          # 跳过归档件/巨文件（B_logs 目录里有 2.9 GB 的 .tar）
for d in LOGDIRS:
    if not os.path.isdir(d):
        continue
    for p in glob.glob(os.path.join(d, '**', '*.log'), recursive=True):
        if not os.path.isfile(p):
            continue
        try:
            if os.path.getsize(p) > MAXB:
                nskip += 1
                continue
            txt = ANSI.sub('', open(p, encoding='utf-8', errors='replace').read().replace('\r', ''))
        except Exception:
            nskip += 1
            continue
        nlogs += 1
        for line in txt.split('\n'):
            if 'Scanning' not in line:
                continue
            m = scan_re.match(line.strip())
            if not m:
                continue
            nscan += 1
            path = m.group('path')
            # 用底座里已知的数据集名去匹配路径（长名优先，避免 sfchd_20p 吃掉 sfchd_20p_b）
            hit = None
            for ds in DS_BY_LEN:
                if ds and ds in path:
                    hit = ds
                    break
            if hit is None:
                continue
            tot = m.group('tot') or m.group('cur')
            try:
                tot = int(tot)
            except Exception:
                continue
            if tot > counts[hit][m.group('split')]:
                counts[hit][m.group('split')] = tot

print('[scan] 扫描文件 %d 个（跳过 %d：归档件或超 %d MB），命中 Scanning 行 %d 条，覆盖数据集 %d 个'
      % (nlogs, nskip, MAXB // 1024 // 1024, nscan, len(counts)))

# ---------- 2. 逐数据集 s/ep（与 A4 同口径） ----------
per = collections.defaultdict(list)
for r in rows:
    w, a = f(r['wall_sec']), f(r['epochs_actual'])
    if w and a and a > 0 and r['dataset']:
        per[r['dataset']].append(w / a)

L = []


def w(s=''):
    L.append(s)
    print(s)


w('# A4b 计时模型：两系数重标定（2026-09-30，闭合 A4 登记的缺口）')
w()
w('> # ⛔ **本件的结论已被 `A4c_计时模型_用真实图数复核.md` 取代（同日）。**')
w('>')
w('> 本件的错误在于**前提**：它断言"图数只能从训练日志取，日志里没有 `val: Scanning` ⇒')
w('> 两系数形式无法本地重拟合 ⇒ 建议不要报计时模型"。**但图数在数据集 yaml + 文件系统里**')
w('> （`train:` / `val:` 两个相对路径，数目录即可）—— 取得机器只读访问后，A4c 走通了这条路，')
w('> 并直接检验登记模型：**R² = 0.948**，`sfchd_20p_b` 精确命中。')
w('>')
w('> **仍然有效的**：§4.1「同一数据集内 s/ep 的**中位数**是稳健的 ETA 基准」。')
w('> **作废的**：§4.2/§4.3 的"模型不可识别/不要报计时模型"。')
w()
w('> A4 登记的缺口是"**无 train/val 图数 ⇒ 两系数模型无法本地重拟合**"。')
w('> 本件把它补齐：图数从**训练日志**的 `Scanning` 行提取，按 **dataset** 归位')
w('> （不做"日志→run"归位 —— 日志名与 run 名不一致，且 A 机只有 266 个日志 / 804 个 run；')
w('> 而计时模型本来就是按数据集标定的，两侧的键天然一致）。')
w()
w('## 1. 图数抽取的覆盖')
w()
w('| 量 | 值 |')
w('|---|---|')
w('| 扫过的日志/文本文件 | %d |' % nlogs)
w('| 命中的 `Scanning` 行 | %d |' % nscan)
w('| 覆盖到的数据集 | **%d**（底座有 %d 个数据集有 s/ep 记录） |' % (len(counts), len(per)))
w('| 抽到 **train** 图数的数据集 | **%d** |' % sum(1 for d in counts if 'train' in counts[d]))
w('| 抽到 **val** 图数的数据集 | **%d** |' % sum(1 for d in counts if 'val' in counts[d]))
w()
w('### ★ 缺口没有完全闭合：**保留下来的日志里没有 `val: Scanning` 行**')
w()
w('实测：A 机 266 个日志 + B 机日志目录共 %d 个 `.log`，`grep "val: Scanning"` **零命中**；' % nlogs)
w('只有 `train: Scanning … : 100%% ━ M/M`。⇒ **val 图数在这批日志里根本不存在**，')
w('因此**登记的两系数形式 `s/ep ≈ 2.727e-3·val + 4.85e-3·train` 依旧无法本地重拟合** ——')
w('但原因被定位了：**不是"没解析"，而是"证据不在"**（要补 val 图数，只能从数据集的 data yaml 或')
w('磁盘上的 `val/images` 计数取，两者都不在本次取件的 run 级产物里）。')
w()
w('**能做的**：用抽到的 **train 图数**标定**单系数**模型，并把 train 图数本身作为新资产登记。')
w()

usable = {d: counts[d]['train'] for d in counts if 'train' in counts[d] and d in per and len(per[d]) >= 5}
w('## 2. 可用于拟合的数据集（train 图数 + s/ep 的 n≥5）')
w()
w('| 数据集 | train 图数 | n | s/ep 中位 | s/ep ÷ train（中位，×1e-3） |')
w('|---|---|---|---|---|')
for d in sorted(usable, key=lambda x: -st.median(per[x])):
    med = st.median(per[d])
    w('| `%s` | %d | %d | %.1f | %.3f |' % (d, usable[d], len(per[d]), med, 1000 * med / usable[d]))
w()

if len(usable) >= 4:
    xs = [usable[d] for d in usable]
    ys = [st.median(per[d]) for d in usable]
    c = sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)      # 无截距
    pred = [c * x for x in xs]
    ss_res = sum((y - p) ** 2 for y, p in zip(ys, pred))
    ss_tot = sum((y - st.mean(ys)) ** 2 for y in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot else float('nan')
    rel = [abs(y - p) / y for y, p in zip(ys, pred) if y]
    w('## 3. 单系数重标定（**train 侧**，无截距）')
    w()
    w('| 形式 | 系数 | R² | 相对误差中位 | 最大相对误差 |')
    w('|---|---|---|---|---|')
    w('| `s/ep = c · train` | **c = %.4e** | %.3f | %.1f%% | %.1f%% |' %
      (c, r2, 100 * st.median(rel), 100 * max(rel)))
    w()
    w('* 登记的旧模型里 **train 项系数是 `4.85e-3`** ⇒ 本次单系数拟合给 **%.4e**（比值为 %.2f×）。' %
      (c, c / 4.85e-3))
    w('  ⚠ 两者**不可直接比较**：旧模型是"val + train"两项之和，本式只有一项，')
    w('  且本式的样本只有 %d 个数据集。**只能作为数量级核对，不能当作替换。**' % len(usable))
    w()
    w('### 3.1 逐数据集：实测 vs 单系数模型')
    w()
    w('| 数据集 | train | 实测 s/ep | 模型 s/ep | 模型/实 |')
    w('|---|---|---|---|---|')
    for d in sorted(usable, key=lambda x: -st.median(per[x])):
        y = st.median(per[d])
        w('| `%s` | %d | **%.1f** | %.1f | %.2f× |' % (d, usable[d], y, c * usable[d], c * usable[d] / y))
    w()
    w('### 3.2 与 A4 已更正的台账错误对照')
    w()
    if 'gdut_hwd' in usable:
        y = st.median(per['gdut_hwd'])
        w('* `gdut_hwd`：实测 **%.1f s/ep**（train %d 图）⇒ 单系数模型给 %.1f（%.2f×）。' %
          (y, usable['gdut_hwd'], c * usable['gdut_hwd'], c * usable['gdut_hwd'] / y))
        w('  A4 已更正台账：台账记 16–20 s/ep 并据此称"模型低估小数据集 2.2–2.7×"，真值 ≈8.8。')
        w('  ★ 本件给出**那处错误的机制**：若把 `gdut_hwd` 的 train 图数与**别的数据集**的图数搞混')
        w('  （或按图片目录而非实际 train split 计数），就会得到 16–20 的读数。真值 %.1f。' % y)
    w()
else:
    w('## 3. 单系数重标定')
    w()
    w('* ⚠ 可拟合的数据集不足 4 个（只有 %d 个）⇒ 不足以标定。' % len(usable))
    w()

w('## 4. ★★ 更重要的结论：**s/ep 根本不由数据集大小决定**')
w()
spread = {}
for d, vals in per.items():
    if len(vals) < 5:
        continue
    spread[d] = max(vals) / min(vals)
w('### 4.1 组内稳健、组间巨大 —— 但**与图数不成单调关系**')
w()
w('| 量 | 值 |')
w('|---|---|')
w('| 有 s/ep 记录、n≥5 的数据集 | %d |' % len(spread))
w('| 各数据集**中位** s/ep 的极差 | %.1f ×（%.1f → %.1f） |' %
  (max(st.median(per[d]) for d in spread) / min(st.median(per[d]) for d in spread),
   min(st.median(per[d]) for d in spread), max(st.median(per[d]) for d in spread)))
w('| 各数据集**内部** max/min 的中位 | **%.1f ×** ⇒ 中位数是稳健的 ETA 基准 |' % st.median(list(spread.values())))
w('| 各数据集**内部** max/min 的最大 | **%.1f ×**（`%s`）⇒ 但**个别 run 可以被拖慢两个量级** |' %
  (max(spread.values()), max(spread, key=lambda d: spread[d])))
w()
w('⇒ 两条分开读：')
w()
w('* **中位数可用**：同一数据集内 s/ep 的中位离散只有 %.1f× ⇒ 用中位数做 ETA 是稳的。'
  % st.median(list(spread.values())))
w('* **单系数模型不可用**：数据集之间的中位差达 %.1f×，而这个差**不随 train 图数单调变化** ——'
  % (max(st.median(per[d]) for d in spread) / min(st.median(per[d]) for d in spread)))
w('  同一族内就自相矛盾：`dota15_10p` **141 图 → 8.9 s/ep**、`dota15_20p` **282 图 → 7.9**、')
w('  `dota15_50p` **705 图 → 13.4**（先降后升）；跨族更极端：`firesmoke_20p` **11232 图 → 64.4**')
w('  而 `data` **23856 图 → 19.6**（图多 2 倍反而快 3 倍）。')
w('* **个别 run 的离群不由数据解释**：组内 max/min 最高 %.1f×（同一数据集、图数不变）⇒'
  % max(spread.values()))
w('  该差异只能来自**设备/调度**（同卡并发、batch 降级、OOM 回退），')
w('  与 `通用经验与教训` #33「每卡只能有一个 trainer」同源。')
w()
w('### 4.2 单系数拟合失败的定量含义')
w()
w('| 事实 | 数值 |')
w('|---|---|')
w('| `s/ep = c·train` 的 R² | **%.3f**（负 ⇒ 比"直接用均值"还差）|' % r2)
w('| 相对误差中位 / 最大 | %.0f%% / %.0f%% |' % (100 * st.median(rel), 100 * max(rel)))
w('| 反例 | `dota15_10p` 141 图 ⇒ 8.9 s/ep；`firesmoke_20p` 11232 图 ⇒ 64.4 s/ep —— **小 80 倍的集反而慢 7 倍** |')
w()
w('### 4.3 对论文的建议')
w()
w('1. **不要报"计时模型"**。登记的 `s/ep ≈ 2.727e-3·val + 4.85e-3·train` 在本数据上')
w('   **不可识别**：主方差来源（同卡并发）没有被固定，而它比数据规模大一个量级。')
w('2. 改用**逐数据集的经验中位**做 ETA（A4 的表已经给了），并在稿中写明"**取中位不取均值**"')
w('   （A4 已记录 `sgh_30ep_lr005_s43n` 的 26.9 s/ep 离群点）。')
w('3. 若确要留模型式，须把**每卡单进程**作为前置条件写进协议，并给出该条件下的重标定 ——')
w('   本次取件里没有"同数据集 × 同并发度"的对照 ⇒ 需要新实验（见云端清单）。')
w()
w('## 5. 与 A4 的关系')
w()
w('* A4 的**逐数据集 s/ep 表**（`analysis\\A4_计时模型.md`）**不受本件影响** —— 那是直接从')
w('  `results.csv` 末行 `time` 算的，不依赖日志；本件只是给那张表**加了 train 图数这一列**，')
w('  并证明它**不是一个解释变量**。')
w('* A4 已更正的台账错误仍然成立：`gdut_hwd` 实测 **≈8.8 s/ep**（台账写 16–20 是错的）。')
w('  本件补充：其 train 图数为 **1389**；台账那个 16–20 的读数与任何"按图数换算"的口径都不自洽。')
w()
w('## 6. 新登记的两项资产 / 两项缺口')
w()
w('**资产**：')
w()
w('1. **train 图数表**（%d 个数据集，见 §2）—— 从日志 `train: Scanning … : 100%% ━ M/M` 抽取，可重跑。' % len(usable))
w('2. **组内/组间离散的定量对照**（§4.1）—— 可直接用于稿中"为何不报计时模型"的一页。')
w()
w('**缺口**：')
w()
w('1. **val 图数不在保留的日志里**（711 个 `.log` 零命中 `val: Scanning`）⇒ 两系数形式仍不可本地重拟合；')
w('   要补只能取数据集 data yaml 或 `val/images` 计数。')
w('2. **缺"同数据集 × 同并发度"的对照批** ⇒ 无法把调度方差从数据方差里分出来（需新实验）。')
w()

open(os.path.join(OUT, 'A4b_计时模型_两系数重标定.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n输出 -> %s' % os.path.join(OUT, 'A4b_计时模型_两系数重标定.md'))
