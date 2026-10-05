# -*- coding: utf-8 -*-
"""03_reconcile.py — 底座 vs 既有台账逐项对账。

对账对象
--------
① `§6.3早停按臂台账_20260927.md`：四个已裁定族（vvhr/sgh/cg/srh）+ pn + **未登记的 dd15**
② 两机监视三元组：A `pt2=345 / pt1=0 / _PARTIAL_=10`；B `165 / 0 / 25`
③ `§6.3.2可比性检查_*` 三件裁定（数值层面即 ① 的 |Δ|/max）

口径（写死，与台账一致）
------------------------
* 格 = (族, 臂, seed)；同格多产物 ⇒ 取"合法结果"= 行数最多且 outcome ∈ {complete, early_stop_legit} 者；
  只有中断件时才落到 interrupted。
* `n_early` = 该臂中"所选产物为 early_stop_legit"的格数。
* `Ē` = 该臂三格实际轮数均值（用所选产物）。
* 5.3.a：`|Δ|/max(Ē) > 5%` ⇒ 不可比；5.3.a′：两臂早停比例差 > 0.2 ⇒ 不可比；
  两者都不触发时按 Q3 裁定：PP 空集 ⇒ 可比 + 注明"PP 不可得"。
"""
import os
import re
import csv
import sys
import json
import collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')   # 控制台 GBK 打不出 Ē/Δ

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ★ 2026-10-05：可移植（放行布局下 = 仓库根，含 base/ deliver/ M3_draft/）
OUT = os.path.join(BASE, 'reconcile')
os.makedirs(OUT, exist_ok=True)
rows = list(csv.DictReader(open(os.path.join(BASE, 'base', 'run_table_canonical.csv'),
                                encoding='utf-8')))

# 台账里的权威数字（人工抄自 §6.3 台账，附出处行）
REF = {
    'vvhr_200ep': dict(base=(2, 182.667), lr005=(3, 144.667), ratio=20.80, verdict='P 不可判 (c)', src='台账 §1 / §6.3.2_vvhr200ep'),
    'sgh_200ep':  dict(base=(2, 151.667), lr005=(3, 164.000), ratio=7.52,  verdict='P 不可判 (c)', src='台账 §2 / §6.3.2_sgh200ep'),
    'cg_200ep':   dict(base=(3, 123.333), lr005=(3, 136.333), ratio=9.54,  verdict='P 不可判 (c)', src='台账 §2c / §6.3.2_cg200ep'),
    'srh_200ep':  dict(base=(3, 162.000), lr005=(3, 168.333), ratio=3.76,  verdict='预算可比 + PP 不可得', src='台账 §2b.5/.6 + §3.1 Q3 裁定'),
    'pn_200ep':   dict(base=(0, 200.000), lr005=(0, 200.000), ratio=0.00,  verdict='零早停零中断（仅登记）', src='台账 §2d'),
}


def cell_of(run):
    n = re.sub(r'^_PARTIAL_', '', run)
    n = re.sub(r'\.incomplete_\d+_\d+$', '', n)
    n = re.sub(r'_\d{6}$', '', n)
    return n


fams = collections.defaultdict(lambda: collections.defaultdict(dict))   # fam -> arm -> seed -> [rows]
for r in rows:
    n = cell_of(r['run'])
    m = re.match(r'^(.*)_(base|lr005|lr002)_s(\d+)n$', n)
    if not m:
        continue
    fam, arm, seed = m.group(1), m.group(2), int(m.group(3))
    if not fam.endswith('200ep'):
        continue
    fams[fam][arm][seed] = fams[fam][arm].get(seed, []) + [r]

VALID = ('complete', 'early_stop_legit')


def pick(products):
    v = [p for p in products if p['outcome'] in VALID]
    pool = v if v else products
    return max(pool, key=lambda p: int(p['epochs_actual']))


def arm_stats(fam, arm):
    cells = fams[fam].get(arm, {})
    vals, ne, detail = [], 0, []
    for seed in sorted(cells):
        p = pick(cells[seed])
        act = int(p['epochs_actual'])
        vals.append(act)
        if p['outcome'] == 'early_stop_legit':
            ne += 1
        detail.append(dict(seed=seed, act=act, outcome=p['outcome'],
                           run=p['run'], n_products=len(cells[seed])))
    return dict(n_cells=len(vals), n_early=ne,
                E=(sum(vals) / len(vals)) if vals else None, detail=detail)


lines = []
def w(s=''):
    lines.append(s)
    print(s)


w('# 对账报告：分析底座 vs 既有台账（2026-09-30）')
w()
w('> 底座：`base/run_table_canonical.csv`（1921 行，(机器,run) 为键），')
w('> 由 `scripts/01_build_base.py` 从原始 `results.csv`/`args.yaml` 复算，')
w('> **不复用任何台账里的数字**。本件只核"台账说的对不对"。')
w()

# ---------- ① 族级 ----------
w('## ① 四个已裁定族 + pn：逐格复算 vs 台账')
w()
w('| 族 | 臂 | 台账 n_early | 底座 n_early | 台账 Ē | 底座 Ē | 逐格实际轮数（底座，取合法产物） | 判定 |')
w('|---|---|---|---|---|---|---|---|')
allfam = sorted(fams)
verdict_rows = []
for fam in allfam:
    for arm in ('base', 'lr005'):
        st = arm_stats(fam, arm)
        if not st['n_cells']:
            continue
        ref = REF.get(fam, {}).get(arm)
        ref_ne, ref_E = (ref if ref else (None, None))
        acts = '/'.join(str(d['act']) for d in st['detail'])
        if ref_ne is None:
            ok = '— 台账未登记'
        elif int(ref_ne) == st['n_early'] and abs(ref_E - st['E']) < 0.01:
            ok = '✅ 一致'
        else:
            ok = '❌ 不一致'
        w('| `%s` | %s | %s | **%d** | %s | **%.3f** | %s | %s |' %
          (fam, arm, ('—' if ref_ne is None else ref_ne),
           st['n_early'], ('—' if ref_E is None else '%.3f' % ref_E), st['E'], acts, ok))
        verdict_rows.append((fam, arm, ref_ne, st['n_early'], ref_E, st['E'], ok))

w()
w('### 5.3.a 复算（`|Δ|/max(Ē)`，阈值 5%）与裁定')
w()
w('| 族 | Ē_base | Ē_lr005 | Δ | 台账 \\|Δ\\|/max | 底座 \\|Δ\\|/max | 5.3.a | 台账裁定 | 一致？ |')
w('|---|---|---|---|---|---|---|---|---|')
fam_verdict = {}
for fam in allfam:
    b, l = arm_stats(fam, 'base'), arm_stats(fam, 'lr005')
    if not (b['E'] and l['E']):
        continue
    d = b['E'] - l['E']
    ratio = abs(d) / max(b['E'], l['E']) * 100
    if ratio > 5:
        v = '两臂预算不可比 ⇒ `P 不可判 (c)`'
    else:
        a1 = abs(b['n_early'] / max(b['n_cells'], 1) - l['n_early'] / max(l['n_cells'], 1)) > 0.2
        v = ('两臂预算不可比 ⇒ `P 不可判 (c)`' if a1 else
             '预算可比 ⇒ 报 ITT' + ('（PP 不可得）' if (b['n_early'] == b['n_cells'] and l['n_early'] == l['n_cells']) else ' + PP'))
    fam_verdict[fam] = v
    ref = REF.get(fam, {})
    rr = ref.get('ratio')
    same = ('—' if rr is None else ('✅' if abs(rr - ratio) < 0.02 else '❌'))
    w('| `%s` | %.3f | %.3f | %+.3f | %s | **%.2f %%** | %s | %s | %s |' %
      (fam, b['E'], l['E'], d, ('—' if rr is None else '%.2f %%' % rr), ratio,
       ('触发' if ratio > 5 else '不触发'),
       ref.get('verdict', '— 台账未登记'), same))

w()
w('### ★ 结论 1：台账未登记但存在的 200ep 族')
w()
unreg = [f for f in allfam if f not in REF]
if unreg:
    for f in unreg:
        b, l = arm_stats(f, 'base'), arm_stats(f, 'lr005')
        w('* **`%s`**：base n_early=%d/%d（Ē=%.1f）、lr005 n_early=%d/%d（Ē=%.1f）' %
          (f, b['n_early'], b['n_cells'], b['E'] or -1, l['n_early'], l['n_cells'], l['E'] or -1))
        if (b['n_early'] >= 3 or l['n_early'] >= 3):
            w('  ⇒ ⚠ **任一臂 ≥3 早停 ⇒ 按 §6.3 第 5 条本应强制触发 §6.3.2，但台账中无此族**')
else:
    w('* 无')

# ---------- ② 制度性计数 ----------
w()
w('## ② 制度性计数对账（两台机器的检查点不变量）')
w()

# _PARTIAL_ 计数：A 用完整目录清单，B 用底座 + 已知无 csv 的那一个
alist = os.path.join(r"E:\workplace\AB机实验文件夹\P1newruns", 'A_runs_mtime_order.txt')
A_dirs = [l.strip() for l in open(alist, encoding='utf-8')] if os.path.isfile(alist) else []
A_part = [d for d in A_dirs if d.startswith('_PARTIAL_')]
B_part = [r['run'] for r in rows if r['machine'] == 'B' and r['run'].startswith('_PARTIAL_')]
B_part_extra = ['_PARTIAL_xcal_B_s42n_050157']          # 已知无 results.csv 者
w('| 量 | 监视/台账值 | 底座复算 | 一致？ | 说明 |')
w('|---|---|---|---|---|')
w('| A `_PARTIAL_` 目录数 | 10 | **%d** | %s | 源：A 机 828 目录全清单 |' %
  (len(A_part), '✅' if len(A_part) == 10 else '❌'))
w('| B `_PARTIAL_` 目录数 | 25 | **%d**（含 1 个无 csv） | %s | 源：底座 %d + 已知无 csv 1 个 |' %
  (len(B_part) + 1, '✅' if len(B_part) + 1 == 25 else '❌', len(B_part)))
w('| A 目录总数 | 828 | **%d** | %s | 源：A_runs_mtime_order.txt |' %
  (len(A_dirs), '✅' if len(A_dirs) == 828 else '❌'))

# pt2 / pt1：A 机权重库存（B 无库存，不可核）
inv = r"D:\p1_pickup_20260930\A\a1_weight_inventory.tsv"
if os.path.isfile(inv):
    cnt = collections.Counter()
    for line in open(inv, encoding='utf-8', errors='replace'):
        # 格式：size \t mtime \t /workspace/runs/<run>/weights/<f>.pt
        toks = [t for t in line.rstrip('\n').split('\t') if t]
        if not toks:
            continue
        p = toks[-1]
        if not p.endswith('.pt'):
            continue
        m = re.search(r'runs/(?:detect/)?([^/]+)/', p)
        if m:
            cnt[m.group(1)] += 1
    pt2 = sum(1 for v in cnt.values() if v == 2)
    pt1 = sum(1 for v in cnt.values() if v == 1)
    dist = collections.Counter(v if v <= 3 else 4 for v in cnt.values())
    w('| A `pt2`（恰好 best+last 的目录） | 345 | **%d** | %s | 源：a1_weight_inventory.tsv（9308 个 .pt 路径） |' %
      (pt2, '✅' if pt2 == 345 else '❌'))
    w('| A `pt1`（恰好 1 个 .pt） | 0 | **%d** | %s | 同上 |' % (pt1, '✅' if pt1 == 0 else '❌'))
    w('| B `pt2` | 165 | — | ⚠ **本地不可核** | B 无权重库存（只取了 csv/yaml） |')
    w('| B `pt1` | 0 | — | ⚠ **本地不可核** | 同上 |')
    w()
    w('> A 机库存：**%d 个 run 名有 `.pt`**、共 9308 个权重文件；' % len(cnt))
    w('> 每个目录的 `.pt` 数分布：1 个 %d、2 个 %d、3 个 %d、≥4 个 %d。' %
      (dist.get(1, 0), dist.get(2, 0), dist.get(3, 0), dist.get(4, 0)))
    w('> ⇒ "`pt1` 恒 0" 的含义是**没有任何目录只剩 1 个权重**（best 与 last 同生同灭），')
    w('> 这正是"A 机排空全程没有任何目录从 2 个 `.pt` 掉出"这个护栏的底账。')

# ---------- ③ 与三份裁定件的数值一致性 ----------
w()
w('## ③ 与三份 `§6.3.2可比性检查_*` 的数值一致性')
w()
for fam, f in [('vvhr_200ep', '§6.3.2可比性检查_vvhr200ep_20260927.md'),
               ('sgh_200ep', '§6.3.2可比性检查_sgh200ep_20260928.md'),
               ('cg_200ep', '§6.3.2可比性检查_cg200ep_20260928.md')]:
    ref = REF[fam]
    b, l = arm_stats(fam, 'base'), arm_stats(fam, 'lr005')
    ratio = abs(b['E'] - l['E']) / max(b['E'], l['E']) * 100
    w('* `%s`（→ `%s`）：裁定件记 `|Δ|/max = %.2f %%`，底座复算 **%.2f %%** ⇒ %s；裁定 **%s**' %
      (fam, f, ref['ratio'], ratio, '✅ 一致' if abs(ref['ratio'] - ratio) < 0.02 else '❌ 不一致',
       ref['verdict']))

json.dump(dict(families={f: {a: arm_stats(f, a) for a in ('base', 'lr005')} for f in allfam},
               verdicts=fam_verdict, unregistered=unreg),
          open(os.path.join(OUT, '_reconcile.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, default=str)
open(os.path.join(OUT, '对账报告.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n输出 ->', os.path.join(OUT, '对账报告.md'))
