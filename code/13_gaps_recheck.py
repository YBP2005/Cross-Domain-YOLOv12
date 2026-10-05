# -*- coding: utf-8 -*-
"""13_gaps_recheck.py —— **缺口复核**（157 无损失标注 / 63 有标注无目录）。

两件事：
  1. **63 个"有损失标注但本地没有 run 目录"** —— 逐条尝试用**改名规则**在本地找回
     （`_PARTIAL_*` / `.incomplete_<日期>` / `_oomfix` / 尾缀 `_<hhmmss>`）。若找回，
     这条就不是"取件缺口"而是**命名不一致**；
  2. **157 个"无损失标注"** —— 按族分类，并检查：同一族里**别的 run 有损失标注**时，
     该族是否只用一种损失（若是，则可**推断**该 run 的损失，但必须标注为"推断而非实测"）。
"""
import os
import re
import csv
import sys
import glob
import collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ★ 2026-10-05：可移植（放行布局下 = 仓库根，含 base/ deliver/ M3_draft/）
OUT = os.path.join(BASE, 'analysis')
GAPS = os.path.join(BASE, 'base', '缺口清单.md')
rows = [r for r in csv.DictReader(open(os.path.join(BASE, 'base', 'run_table_canonical.csv'),
                                      encoding='utf-8'))]

# 本地实际存在的 run 目录名（多个来源合并）
local = set()
for d in [os.path.join(BASE, 'raw'), r"E:\workplace\AB机实验文件夹\B_csv_20260930"]:
    if not os.path.isdir(d):
        continue
    for p in glob.glob(os.path.join(d, '**', 'results.csv'), recursive=True):
        local.add(os.path.basename(os.path.dirname(p)))
    for p in glob.glob(os.path.join(d, '**', 'args.yaml'), recursive=True):
        local.add(os.path.basename(os.path.dirname(p)))
print('[local] 本地 run 目录名 %d 个' % len(local))

SUF = re.compile(r'(_PARTIAL_\d+|_PARTIAL_\d{8}|\.incomplete_\d+_\d+|_oomfix|_\d{6})$')


def norm(n):
    prev = None
    while prev != n:
        prev = n
        n = SUF.sub('', n)
    return re.sub(r'^_PARTIAL_', '', n)


LOCAL_NORM = collections.defaultdict(set)
for n in local:
    LOCAL_NORM[norm(n)].add(n)

# ---------- 从缺口清单里取两类 ----------
txt = open(GAPS, encoding='utf-8').read()
m63 = re.search(r'## 有损失标注、但本地没有 run 目录的 \d+ 个[^\n]*\n(.*?)(?:\n## |\Z)', txt, re.S)
miss = re.findall(r'^[*-]\s+`([^`]+)`', m63.group(1), re.M) if m63 else []
print('[gaps] 有标注无目录 %d 个' % len(miss))
m157 = re.search(r'\*\*无损失标注\*\*：(\d+) 个', txt)
n157 = int(m157.group(1)) if m157 else 0

L = []


def w(s=''):
    L.append(s)
    print(s)


w('# A8 缺口复核（2026-09-30）')
w()
w('> 复核 `base\\缺口清单.md` 里的两类缺口，把它们**从"缺口"降为"命名不一致"或"可推断"**，')
w('> 或者**坐实为真缺口**。')
w()
w('## 1. 「有损失标注、但本地没有 run 目录」的 %d 个' % len(miss))
w()
recovered, real = [], []
for n in miss:
    got = LOCAL_NORM.get(norm(n), set()) - {n}
    (recovered if got else real).append((n, sorted(got)))
w('| 结果 | 数 |')
w('|---|---|')
w('| ✅ **本地其实有**（只是被改名：`_PARTIAL_`/`.incomplete_`/`_oomfix`/尾缀时间） | **%d** |' % len(recovered))
w('| ❌ 本地确实没有 | %d |' % len(real))
w()
if recovered:
    w('### 1.1 找回的（**命名不一致，不是取件缺口**）')
    w()
    w('| 清单里的名字 | 本地实际目录 |')
    w('|---|---|')
    for n, g in recovered[:40]:
        w('| `%s` | %s |' % (n, '、'.join('`%s`' % x for x in g)))
    if len(recovered) > 40:
        w('| … 共 %d 条，其余略 | |' % len(recovered))
    w()
if real:
    w('### 1.2 仍缺的 %d 个（逐条）' % len(real))
    w()
    fam = collections.Counter(re.split(r'[_\d]', n)[0] for n, _ in real)
    w('按前缀（族）：%s' % '、'.join('`%s`(%d)' % kv for kv in fam.most_common()))
    w()
    for n, _ in real:
        w('* `%s`' % n)
    w()

# ---------- 157 无损失标注 ----------
nloss = [r for r in rows if not r['loss']]
w('## 2. 「无损失标注」的 %d 个' % len(nloss))
w()
w('### 2.1 按族分布')
w()
famc = collections.Counter(r['family'] for r in nloss)
w('| 族 | 个数 | 该族总 run | 占比 |')
w('|---|---|---|---|')
tot_fam = collections.Counter(r['family'] for r in rows)
for f, n in famc.most_common():
    w('| `%s` | %d | %d | %.0f%% |' % (f, n, tot_fam[f], 100.0 * n / tot_fam[f]))
w()
w('### 2.2 能否**推断**损失？（同族是否只用一种损失）')
w()
w('规则：若同族的**其他** run 在 `sio_b_results.csv` 里只有**一种**损失值，则该 run 的损失')
w('可**推断**为该值 —— 但必须标注"**推断，非实测**"，不得当作实测进入分析。')
w()
inferable = []
ambig = []
noev = []
for r in nloss:
    sib = [x['loss'] for x in rows if x['family'] == r['family'] and x['loss']]
    s = set(sib)
    if len(s) == 1:
        inferable.append((r['run'], list(s)[0], len(sib)))
    elif len(s) > 1:
        ambig.append((r['run'], sorted(s)))
    else:
        noev.append(r['run'])
w('| 情形 | 数 | 可推断性 |')
w('|---|---|---|')
w('| 同族只有**一种**损失 | **%d** | ✅ 可推断（须标注） |' % len(inferable))
w('| 同族有**多种**损失 | %d | ❌ 不可推断 |' % len(ambig))
w('| 同族**无任何**损失标注 | %d | ❌ 无依据 |' % len(noev))
w()
if inferable:
    ic = collections.Counter(x[1] for x in inferable)
    w('可推断的损失取值分布：%s' % '、'.join('`%s`(%d)' % kv for kv in ic.most_common()))
    w()
    w('样例（前 12 条）：')
    w()
    w('| run | 推断损失 | 同族有实测的 run 数 |')
    w('|---|---|---|')
    for n, l, k in inferable[:12]:
        w('| `%s` | `%s` | %d |' % (n, l, k))
    w()
if ambig:
    w('不可推断（同族混多种损失）的样例：')
    w()
    for n, s in ambig[:8]:
        w('* `%s`：族内出现 %s' % (n, s))
    w()

w('## 3. 结论与处置')
w()
w('| 缺口 | 原登记 | 复核后 |')
w('|---|---|---|')
w('| 有损失标注无本地目录 | %d 个"取件缺口" | **%d 个是命名不一致（本地其实有）**、%d 个仍缺 |'
  % (len(miss), len(recovered), len(real)))
w('| 无损失标注 | %d 个"无法进入损失轴分析" | 其中 **%d 个可推断**（须标注"推断"）、%d 个不可推断、%d 个无依据 |'
  % (len(nloss), len(inferable), len(ambig), len(noev)))
w()
w('**处置建议**：')
w()
w('1. 第 1 类：把"本地其实有"的 %d 条从缺口清单移入"命名不一致"一节，并给出对照表；' % len(recovered))
w('   仍缺的 %d 条保留为真缺口（多半在云盘的 `P1part1.tar`）。' % len(real))
w('2. 第 2 类：可推断的 %d 条**只作探索性**，在稿中必须写"损失由同族单一取值推断"，' % len(inferable))
w('   不得与实测损失混列；A1 §3"损失轴撑不起独立轴"的结论**不因这批推断而改变**')
w('   （非 `shapeiou` 的实测实体仍只有 89 条）。')
w()

open(os.path.join(OUT, 'A8_缺口复核.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n输出 -> %s' % os.path.join(OUT, 'A8_缺口复核.md'))
