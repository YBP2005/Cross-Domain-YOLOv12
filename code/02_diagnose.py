# -*- coding: utf-8 -*-
"""02_diagnose.py — 底座体检：损失标注缺口 / 命名映射 / md5 冲突 / actual≠nominal 分类。

只读 base/ 与 raw/，不改任何数据。
"""
import os
import re
import csv
import collections

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ★ 2026-10-05：可移植（放行布局下 = 仓库根，含 base/ deliver/ M3_draft/）
RAW = os.path.join(BASE, 'raw')
BCSV = r"E:\workplace\AB机实验文件夹\B_csv_20260930"

tab = list(csv.DictReader(open(os.path.join(BASE, 'base', 'run_table_canonical.csv'),
                               encoding='utf-8')))
runs = {r['run'] for r in tab}
by_run = {r['run']: r for r in tab}

# ---------- A. 汇总文件里的名字 vs run 目录名 ----------
summ = {}
for path in [os.path.join(RAW, 'A_aux_20260929', 'sio_b_results.csv'),
             os.path.join(BCSV, 'workspace', 'sio_b_results.csv'),
             os.path.join(RAW, 'A_aux_20260929', 'a5_results.csv'),
             os.path.join(RAW, 'A_aux_20260929', 'a5a_results.csv'),
             os.path.join(RAW, 'A_aux_20260929', 'a5s_results.csv')]:
    if not os.path.isfile(path):
        continue
    for line in open(path, encoding='utf-8', errors='replace'):
        p = line.strip().split(',')
        if len(p) >= 4 and p[0]:
            summ.setdefault(os.path.basename(path), set()).add(p[0])

allsumm = set().union(*summ.values()) if summ else set()
print('=== A. 汇总文件名字覆盖率 ===')
for k, v in summ.items():
    print('  %-24s %4d 个名字，其中 %4d 能在 run 目录里找到' % (k, len(v), len(v & runs)))
miss = allsumm - runs
print('  汇总里有、底座里没有的名字 : %d' % len(miss))
print('  样例:', sorted(miss)[:12])
print('  按前缀:', collections.Counter(re.sub(r'_[0-9].*', '', x) for x in miss).most_common(10))

# ---------- B. 无损失标注的 run ----------
noloss = [r for r in tab if not r['loss']]
print()
print('=== B. 无损失标注的 run：%d 个 ===' % len(noloss))
print('  按机器:', collections.Counter(r['machine'] for r in noloss))
print('  按族(前12):', collections.Counter(r['family'] for r in noloss).most_common(12))
print('  是否 _PARTIAL_/incomplete:',
      collections.Counter((r['flag_partial'], r['flag_incomplete']) for r in noloss))
print('  样例:', [r['run'] for r in noloss[:10]])

# ---------- C. md5 冲突 ----------
prov = collections.defaultdict(dict)
for line in csv.DictReader(open(os.path.join(BASE, 'base', 'provenance.csv'), encoding='utf-8')):
    prov[line['run']][line['source']] = line
conf = []
for run, d in prov.items():
    m = {v['md5_results'] for v in d.values()}
    if len(m) > 1:
        conf.append((run, {k: (v['md5_results'][:8], v['rows']) for k, v in d.items()}))
print()
print('=== C. 来源间 md5 冲突：%d 个 run ===' % len(conf))
for run, d in sorted(conf)[:15]:
    r = by_run.get(run, {})
    print('  %-52s %s  | 底座取 rows=%s actual=%s best_ep=%s' %
          (run, d, r.get('epochs_nominal'), r.get('epochs_actual'), r.get('best_epoch')))

# ---------- D. actual != nominal 分类（act = best_ep + 100）----------
print()
print('=== D. actual != nominal 分类 ===')
legit, inter, weird = [], [], []
for r in tab:
    try:
        nom = int(float(r['epochs_nominal']))
        act = int(float(r['epochs_actual']))
    except Exception:
        continue
    if act == nom:
        continue
    be = r['best_epoch']
    try:
        be = int(float(be))
    except Exception:
        be = None
    if be is None:
        weird.append((r, None))
        continue
    if act >= be + 99:          # 容差 1：best_ep + patience(100)
        legit.append((r, be + 100))
    else:
        inter.append((r, be + 100))

def show(title, lst):
    print('  %-28s %3d 个' % (title, len(lst)))
    for r, acte in lst[:14]:
        print('     %-50s %s nom=%-4s act=%-4s best_ep=%-4s act_expected=%s' %
              (r['run'], r['machine'], r['epochs_nominal'], r['epochs_actual'],
               r['best_epoch'], acte))
show('合法 patience 早停 (act>=best+99)', legit)
show('中断件 (act < best+99)', inter)
if weird:
    print('  best_epoch 解析失败 %d 个' % len(weird))

print()
print('  交集检查：这 122 个里 flag_partial=%d，flag_incomplete=%d' %
      (sum(1 for r, _ in legit + inter if r['flag_partial']),
       sum(1 for r, _ in legit + inter if r['flag_incomplete'])))
print('  ** 重要：act==nominal 但 flag_partial=1 的 run **')
for r in tab:
    if r['flag_partial'] and str(r['epochs_actual']) == str(r['epochs_nominal']):
        print('     ', r['run'], r['machine'], 'act=', r['epochs_actual'], 'nom=', r['epochs_nominal'])
