# -*- coding: utf-8 -*-
"""04_A1_grid.py — A1 四轴格完整性审计。

**不按设想，按底座里实际存在什么**。四个维度：
  1. 跨域：`model`（源域预训练权重）→ `dataset`（目标域 data yaml）   ⇒ 配对 (src→tgt)
  2. 标注预算：**从 `dataset` 名里取**（`*_10p/_20p/_30p/_50p`），run 名只作兜底
     —— 实测 1448/1921 行的 run 名里没有预算 token，预算写在 data yaml 名里
  3. 优化预算：`epochs_nominal`
  4. 损失：`loss`（shapeiou / sns / pws / css / jps）
  另测：架构（run 名里的 y11/amod/r16 之类）与 lr 臂（base/lr005/lr002）。

对每个格给出：两臂各自的种子数、**配对种子数**（两臂都有）、是否 ≥3 种子。
输出 `analysis/A1_格完整性.md`。

★ 2026-09-30 口径修正：格的键加入 **`run 族`**（run 名第一段 = 批次）。
旧键 `(配对, 预算, epochs, 损失)` 会把**不同批次**混成一格，虚高"配对种子"数
（实测 60 个可分析格里 9 个多族，见 `analysis\\A7_族混杂复核.md`）。
"""
import os
import re
import csv
import sys
import json
import collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ★ 2026-10-05：可移植（放行布局下 = 仓库根，含 base/ deliver/ M3_draft/）
OUT = os.path.join(BASE, 'analysis')
os.makedirs(OUT, exist_ok=True)
rows = list(csv.DictReader(open(os.path.join(BASE, 'base', 'run_table_canonical.csv'),
                                encoding='utf-8')))


def label_budget(r):
    """标注预算：优先 data yaml 名，其次 run 名。返回 int 或 None。"""
    for s in (r['dataset'], r['data_yaml'], r['run']):
        m = re.search(r'(?:^|[^0-9a-z])(\d{1,3})p(?:[^0-9a-z]|$)', str(s))
        if m:
            v = int(m.group(1))
            if v in (1, 5, 10, 20, 25, 30, 40, 50, 55, 100):
                return v
    return None


def pair(r):
    m = (r['model'] or '').replace('.pt', '')
    m = re.sub(r'_pretrain.*$', '', m) or '(未记预训练)'
    d = r['dataset'] or '(未记数据集)'
    d = re.sub(r'_(3way|2way)$', '', d)
    d = re.sub(r'_?\d{1,3}p.*$', '', d)
    return '%s→%s' % (m, d or '(未记)')


for r in rows:
    r['_lb'] = label_budget(r)
    r['_pair'] = pair(r)
    r['_arch'] = 'y11' if re.search(r'y11|yolo11', r['run'] + r['model']) else (
        'amod' if r['run'].startswith('amod_') or '_amod' in r['run'] else 'y12n')

L = []
def w(s=''):
    L.append(s)
    print(s)

w('# A1 四轴格完整性审计（2026-09-30，数据源 `base/run_table_canonical.csv`）')
w()
w('> 口径：**按底座里实际存在什么**审计，不按设想。')
w('> 标注预算取自 `dataset`（data yaml）名，**不是** run 名 ——')
w('> 实测 1921 行里 **%d 行**的 run 名不含预算 token，预算写在 data yaml 名里。' %
  sum(1 for r in rows if not re.search(r'(?<![0-9a-z])\d{1,3}p(?![0-9a-z])', r['run'])))
w()

w('## 1. 四个维度各自的取值数')
w()
w('| 维度 | 取值 | 说明 |')
w('|---|---|---|')
w('| 源域预训练（跨域轴的一侧） | **%d** | %s |' %
  (len({r['model'] for r in rows}), '、'.join(sorted({(r['model'] or '?').replace('.pt', '') for r in rows}))))
w('| 目标域数据集（另一侧） | **%d** | top: %s |' %
  (len({r['dataset'] for r in rows}),
   '、'.join('%s(%d)' % kv for kv in collections.Counter(r['dataset'] for r in rows).most_common(6))))
w('| **跨域配对** `src→tgt` | **%d** | %s |' %
  (len({r['_pair'] for r in rows}),
   '、'.join('%s(%d)' % kv for kv in collections.Counter(r['_pair'] for r in rows).most_common(6))))
w('| 标注预算 %% | **%d** | %s |' %
  (len({r['_lb'] for r in rows if r['_lb']}),
   '、'.join('%s%%(%d)' % (k, v) for k, v in sorted(collections.Counter(r['_lb'] for r in rows if r['_lb']).items()))))
w('| 优化预算 epochs | **%d** | %s |' %
  (len({r['epochs_nominal'] for r in rows}),
   '、'.join('%sep(%d)' % kv for kv in collections.Counter(r['epochs_nominal'] for r in rows).most_common(8))))
w('| 损失 | **%d** | %s |' %
  (len({r['loss'] for r in rows if r['loss']}),
   '、'.join('%s(%d)' % kv for kv in collections.Counter(r['loss'] for r in rows).most_common())))
w('| lr 臂 | **%d** | %s |' %
  (len({r['lr_arm'] for r in rows}),
   '、'.join('%s(%d)' % kv for kv in collections.Counter(r['lr_arm'] for r in rows).most_common())))
w()

# ---------- 2. 核心格：(配对, 标注预算, epochs) × 两臂种子 ----------
grid = collections.defaultdict(lambda: collections.defaultdict(set))     # key -> arm -> {seed}
lossmix = collections.defaultdict(set)
for r in rows:
    if r['lr_arm'] not in ('base', 'lr005'):
        continue
    try:
        seed = int(float(r['seed_used']))
    except Exception:
        continue
    key = (r['_pair'], r['family'], r['_lb'], r['epochs_nominal'], r['loss'] or '?')
    grid[key][r['lr_arm']].add(seed)
    lossmix[key].add(r['loss'] or '?')

w('## 2. 核心格：(跨域配对, **run 族**, 标注预算, epochs, 损失) —— 两臂 × 种子')
w()
w('**判据**：需两臂各 ≥3 配对种子（"种子先做 3 个"）；`配对种子` = 两臂**都有**的种子数。')
w('**族**= run 名第一段 = 批次；同一 `(配对,预算,epochs,损失)` 下不同族**不是同一次实验**。')
w()
w('| 配对 | 族 | 标注预算 | epochs | 损失 | base 种子 | lr005 种子 | **配对种子** | 判定 |')
w('|---|---|---|---|---|---|---|---|---|')
ok, weak, single = 0, [], []
for key in sorted(grid, key=lambda k: (-len(grid[k].get('base', set()) & grid[k].get('lr005', set())), str(k))):
    p, fam, lb, ep, ls = key
    b, l = grid[key].get('base', set()), grid[key].get('lr005', set())
    both = b & l
    if len(both) >= 3:
        v = '✅ 可配对'
        ok += 1
    elif len(both) >= 1:
        v = '⚠ 配对种子 %d 个（<3）' % len(both)
        weak.append(key)
    else:
        v = '❌ 无配对种子'
        single.append(key)
    w('| `%s` | `%s` | %s | %s | %s | %d | %d | **%d** | %s |' %
      (p, fam, ('%d%%' % lb) if lb else '—', ep, ls, len(b), len(l), len(both), v))
w()
w('* **可配对（≥3 种子）的核心格 = %d 个**；配对不足 %d 个；无配对 %d 个。' %
  (ok, len(weak), len(single)))
w()

# ---------- 3. 损失轴的格 ----------
w('## 3. 损失轴：非 `shapeiou` 的格（这是"损失平面"轴的全部实体）')
w()
nl = [r for r in rows if r['loss'] and r['loss'] != 'shapeiou']
w('* 非 `shapeiou` 的运行共 **%d 条**（占 %.1f%%）：%s' %
  (len(nl), 100.0 * len(nl) / len(rows),
   '、'.join('%s(%d)' % kv for kv in collections.Counter(r['loss'] for r in nl).most_common())))
w('* 它们分布在 **%d 个 (配对,预算,epochs) 格**上、**%d 个种子**：' %
  (len({(r['_pair'], r['_lb'], r['epochs_nominal']) for r in nl}), len({r['seed_used'] for r in nl})))
w()
lg = collections.defaultdict(lambda: collections.defaultdict(list))
for r in nl:
    lg[(r['_pair'], r['_lb'], r['epochs_nominal'])][r['loss']].append((r['seed_used'], r['run']))
w('| 配对 | 预算 | epochs | 各损失 × 种子 |')
w('|---|---|---|---|')
for k in sorted(lg, key=str):
    p, lb, ep = k
    cells = '；'.join('%s: %s' % (ls, ','.join(str(s) for s, _ in sorted(v)))
                      for ls, v in sorted(lg[k].items()))
    w('| `%s` | %s | %s | %s |' % (p, ('%d%%' % lb) if lb else '—', ep, cells))
w()
w('> ⇒ 损失轴**不是**一条与预算轴并列的独立轴：它的实体量级小一个数量级，')
w('> 且几乎不与 `base/lr005` 两臂交叉（见 §2 表内损失列全为 `shapeiou` 的行）。')
w('> 这与料清单 B2"损失先验（三种）/结构模块（11 个）**无 ≥+0.4 pp 的增益**、单跑/臂"一致。')
w()

# ---------- 4. 架构轴 ----------
w('## 4. 架构维度（`y12n` / `y11` / `amod`）')
w()
ac = collections.Counter(r['_arch'] for r in rows)
w('| 架构 | run 数 | 跨域配对 | epochs | 说明 |')
w('|---|---|---|---|---|')
for a, n in ac.most_common():
    sub = [r for r in rows if r['_arch'] == a]
    w('| `%s` | %d | %d | %s | |' %
      (a, n, len({r['_pair'] for r in sub}),
       '、'.join('%s(%d)' % kv for kv in collections.Counter(r['epochs_nominal'] for r in sub).most_common(5))))
w()
w('> ⚠ 架构是**从 run 名推断**的（`y11`/`amod` 字面 token），底座的 `model` 列只记**预训练权重**，')
w('> 不记 backbone ⇒ **架构轴的完整审计需要补一份"run→backbone"映射**，否则只能给下界。')
w()

# ---------- 5. 缺口 ----------
w('## 5. 缺口清单')
w()
w('1. **标注预算 token 不在 run 名里**：只能从 `dataset` 反解；`dataset` 为空的 %d 行无法定预算。' %
  sum(1 for r in rows if not r['dataset']))
w('2. **配对种子 <3 的格 %d 个**、**无配对种子的格 %d 个**（逐格见 §2 表）。' % (len(weak), len(single)))
w('3. **架构轴缺映射**（见 §4 说明）—— 这是 A1 唯一无法从现有底座闭合的维度。')
w('4. **损失轴 %d 条几乎全为单跑/单臂**（料清单已标"无增益"）⇒ 该轴只可作探索性证据。' % len(nl))
w('5. **无损失标注 157 行**（见 `base/缺口清单.md`），无法进入按损失的分类。')
w('6. **族混杂**（2026-09-30 修正）：旧口径的格键不含 `family`，会把不同批次混成一格、')
w('   虚高"配对种子"数。本脚本已修（键含 `run 族`）；影响面见 `analysis\\A7_族混杂复核.md`。')

json.dump(dict(pairs=len({r['_pair'] for r in rows}),
               budgets=sorted({r['_lb'] for r in rows if r['_lb']}),
               grid_ok=ok, grid_weak=len(weak), grid_none=len(single),
               loss_nondefault=len(nl), arch=dict(ac)),
          open(os.path.join(OUT, '_A1.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(OUT, 'A1_格完整性.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n输出 ->', os.path.join(OUT, 'A1_格完整性.md'))
