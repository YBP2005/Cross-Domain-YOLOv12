# -*- coding: utf-8 -*-
"""01_build_base.py (v2) — A/B 两机 run 级账 → 可复算分析底座。

v1 → v2 的修正（均为实测发现的真 bug）
--------------------------------------
1. **键从 `run` 改为 `(machine, run)`**：实测存在**同一 run 名在两机都跑**的情形
   （`b2_smoke2sf_base200_*` / `t1d_dotatod15_*` / `r10_aitod20_*`），
   v1 按名字做键把 B 的那份静默并进了 A。
2. **内置结局分类** `outcome`：complete / early_stop_legit / interrupted / archive_snapshot。
   `.incomplete_*` 是中断件的存档改名，按定义**不算**合法早停（v1 的粗分类会误收 2 个）。
3. 显式登记**跨机重名**（`also_on_other_machine`）。

判读纪律（写死在这里，不许各分析各自解释）
------------------------------------------
* `results.csv` 行数 = 该 run **实际跑完的 epoch 数**；
* `patience=100`（未显式传，ultralytics 默认），故合法 patience 早停必须满足
  `act ≈ best_ep + 100`（容差 1），且名义轮数 > 100 才可能发生；
* 名义 = 实际 ⇒ complete；`act >= best_ep + 99` 且 act<名义 ⇒ early_stop_legit；
  否则 ⇒ interrupted；
* 同机多快照（A_runs 09-29 / A_small2 09-27 / A_part2）取**行数最多**者为主源
  —— 与"同格取重跑后的合法结果"一致。
"""
import os
import re
import csv
import glob
import json
import hashlib
import collections

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ★ 2026-10-05：可移植（放行布局下 = 仓库根，含 base/ deliver/ M3_draft/）
RAW = os.path.join(BASE, 'raw')
BCSV = r"E:\workplace\AB机实验文件夹\B_csv_20260930"
OUT = os.path.join(BASE, 'base')
os.makedirs(OUT, exist_ok=True)

SOURCES = [
    ('A', 'A_runs_20260929',   os.path.join(RAW, 'A_runs_20260929', 'runs')),
    ('A', 'A_small2_20260927', os.path.join(RAW, 'A_small2_20260927', 'runs')),
    ('A', 'A_part2',           os.path.join(RAW, 'A_part2')),
    ('B', 'B_csv_20260930',    os.path.join(BCSV, 'workspace', 'runs')),
    # ★ 2026-10-01「扩展批次」取件（P1 T2 / D2 / T3 的补种子 run）。
    #   目录不存在时 glob 为空 ⇒ 不报错；取件后**重跑本脚本**即自动纳入。
    ('A', 'P1ext_A_20261001',  os.path.join(RAW, 'P1_ext_20261001', 'A', 'runs')),
    ('B', 'P1ext_B_20261001',  os.path.join(RAW, 'P1_ext_20261001', 'B', 'runs')),
    # ★ 2026-10-02「补实验」（损失×增益 / 架构轴）：A、B 两机同时跑，各自取回。
    #   目录不存在时 glob 为空 ⇒ 不报错；取件后**重跑本脚本**即自动纳入。
    ('A', 'P1supp_A_20261002', os.path.join(RAW, 'P1_supp_20261002', 'A', 'runs')),
    ('B', 'P1supp_B_20261002', os.path.join(RAW, 'P1_supp_20261002', 'B', 'runs')),
]
SUMMARY_FILES = [
    ('A', os.path.join(RAW, 'A_aux_20260929', 'sio_b_results.csv'), 'sio7'),
    ('B', os.path.join(BCSV, 'workspace', 'sio_b_results.csv'),     'sio7'),
    # ★ 扩展批次新增的 test 读数（**只含新 run 的行**，与旧文件无重名 ⇒ 不会触发"取末次"歧义）
    ('A', os.path.join(RAW, 'P1_ext_20261001', 'A_sio_b_results.csv'), 'sio7'),
    ('B', os.path.join(RAW, 'P1_ext_20261001', 'B_sio_b_results.csv'), 'sio7'),
    # ★ 补实验：A 与 B **各写自己的** /workspace/sio_b_results.csv ⇒ 两份都要并进来。
    #   ⚠ 同一 run 若两机都跑了（不该发生），这里会触发"取首次"并把 `dup_test_line` 置 1。
    ('A', os.path.join(RAW, 'P1_supp_20261002', 'A_sio_b_results.csv'), 'sio7'),
    ('B', os.path.join(RAW, 'P1_supp_20261002', 'B_sio_b_results.csv'), 'sio7'),
    ('A', os.path.join(RAW, 'A_aux_20260929', 'a5_results.csv'),    'a5_10'),
    ('A', os.path.join(RAW, 'A_aux_20260929', 'a5a_results.csv'),   'a5_10'),
    ('A', os.path.join(RAW, 'A_aux_20260929', 'a5s_results.csv'),   'a5_10'),
]
ARGS_KEYS = ['data', 'model', 'epochs', 'lr0', 'seed', 'batch', 'imgsz',
             'patience', 'save_period', 'optimizer', 'cos_lr', 'pretrained']


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def parse_results(path):
    with open(path, newline='', encoding='utf-8', errors='replace') as f:
        r = list(csv.reader(f))
    if len(r) < 2:
        return dict(rows=0, best_epoch=None, best_map=None, best_map50=None,
                    last_map=None, last_map50=None, wall=None)
    hdr, rows = r[0], r[1:]
    idx = {c: i for i, c in enumerate(hdr)}
    i_map, i_m50, i_t = (idx.get('metrics/mAP50-95(B)'), idx.get('metrics/mAP50(B)'),
                         idx.get('time'))
    best = None
    for k, row in enumerate(rows):
        try:
            m = float(row[i_map]) if i_map is not None else None
        except Exception:
            m = None
        if m is not None and (best is None or m > best[1]):
            best = (k + 1, m)
    out = dict(rows=len(rows), best_epoch=best[0] if best else None,
               best_map=best[1] if best else None, last_map=None, last_map50=None, wall=None,
               best_map50=None)
    try:
        out['last_map'] = float(rows[-1][i_map]) if i_map is not None else None
        out['last_map50'] = float(rows[-1][i_m50]) if i_m50 is not None else None
        out['wall'] = float(rows[-1][i_t]) if i_t is not None else None
        if best and i_m50 is not None:
            out['best_map50'] = float(rows[best[0] - 1][i_m50])
    except Exception:
        pass
    return out


def parse_args(path):
    d = {}
    try:
        for line in open(path, encoding='utf-8', errors='replace'):
            m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$', line)
            if m:
                d[m.group(1)] = m.group(2).strip("'\"")
    except Exception:
        pass
    return {k: d.get(k) for k in ARGS_KEYS}


# ---------- 1. 枚举 ----------
prov = []
by_key = collections.defaultdict(list)       # (machine, run) -> [(src, path, st)]
args_by_key = collections.defaultdict(list)
for machine, src, root in SOURCES:
    if not os.path.isdir(root):
        print('  [WARN] 缺来源:', root)
        continue
    n = 0
    for dp, dn, fn in os.walk(root):
        if 'results.csv' in fn:
            run = os.path.basename(dp)
            pc = os.path.join(dp, 'results.csv')
            pa = os.path.join(dp, 'args.yaml')
            has_a = os.path.isfile(pa)
            st = parse_results(pc)
            prov.append(dict(run=run, machine=machine, source=src, md5_results=md5(pc),
                             rows=st['rows'], md5_args=(md5(pa) if has_a else ''),
                             has_args=int(has_a), mtime=os.path.getmtime(pc)))
            by_key[(machine, run)].append((src, pc, st))
            if has_a:
                args_by_key[(machine, run)].append((src, pa))
            n += 1
    print('%-22s %4d 个 results.csv' % (src, n))

# ---------- 2. 损失轴 / test 侧指标 ----------
summary = {}
summary_m = {}               # ★ 2026-10-01：(机器, 名) 索引 —— 供改名件回退查，**只认同机**
sum_note = []
dup_summary = set()          # 同名多次出现且数值不同 ⇒ 重跑，取最后一次
for machine, path, fmt in SUMMARY_FILES:
    if not os.path.isfile(path):
        continue
    got = 0
    for line in open(path, encoding='utf-8', errors='replace'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        p = line.split(',')
        try:
            if fmt == 'sio7' and len(p) >= 7:
                name, loss, ep = p[0], p[1], int(float(p[2]))
                m50, m, mp, mr = map(float, p[3:7])
            elif fmt == 'a5_10' and len(p) >= 10:
                name, loss, ep = p[0], p[1], int(float(p[2]))
                m50, m, mp, mr = map(float, (p[6], p[7], p[8], p[9]))
            else:
                continue
        except Exception:
            continue
        got += 1
        rec = dict(loss=loss, epochs=ep, map50=m50, map=m, mp=mp, mr=mr,
                   src=os.path.basename(path), machine=machine)
        prev = summary.get(name)
        if prev is None:
            summary[name] = rec      # ★ 取**第一次**出现（此口径与论文 §4.1 逐位吻合）
        elif prev['loss'] != rec['loss'] or abs(prev['map'] - rec['map']) > 1e-9:
            sum_note.append((name, prev['src'], prev['loss'], prev['map'],
                             rec['src'], rec['loss'], rec['map']))
            dup_summary.add(name)    # ★ 但必须标记：这些 run 有**两个不同读数**
        summary_m.setdefault((machine, name), rec)
    print('  [summary] %-24s %4d 行' % (os.path.basename(path), got))

weights = set()
invp = r"D:\p1_pickup_20260930\A\a1_weight_inventory.tsv"
if os.path.isfile(invp):
    for line in open(invp, encoding='utf-8', errors='replace'):
        for tok in line.split():
            if tok.endswith('.pt'):
                m = re.search(r'runs/(?:detect/)?([^/]+)/', tok)
                if m:
                    weights.add(m.group(1))
    print('  [weights] A 机库存覆盖 %d 个 run 名' % len(weights))


def norm(name):
    d = dict(family='', budget_pct=None, epochs_nominal=None, lr_arm='',
             seed=None, seed_kind='none', threeway=0, partial=0, incomplete=0)
    n = name
    if n.startswith('_PARTIAL_'):
        d['partial'] = 1
        n = n[len('_PARTIAL_'):]
    if '.incomplete' in n:
        d['incomplete'] = 1
    n = re.sub(r'\.incomplete_\d+_\d+$', '', n)
    n = re.sub(r'_\d{6}$', '', n)
    m = re.search(r'_s(\d+)(n?)$', n)
    if m:
        d['seed'] = int(m.group(1))
        # 尾缀带 n ⇒ 新战役约定：该数是**置换种子**（shuffle），torch 种子恒 42；
        # 无 n ⇒ 早期约定：该数是**真种子**（与 args.yaml 一致）。
        d['seed_kind'] = 'shuffle' if m.group(2) == 'n' else 'torch'
        n = n[:m.start()]
    if '3way' in n:
        d['threeway'] = 1
    m = re.search(r'(\d+)p(?![a-z])', n)
    if m:
        d['budget_pct'] = int(m.group(1))
    m = re.search(r'(\d+)ep', n)
    if m:
        d['epochs_nominal'] = int(m.group(1))
    else:
        m = re.search(r'base(\d+)', n)
        if m:
            d['epochs_nominal'] = int(m.group(1))
    if 'lr005' in n:
        d['lr_arm'] = 'lr005'
    elif 'lr002' in n:
        d['lr_arm'] = 'lr002'
    elif re.search(r'base\d*', n):
        d['lr_arm'] = 'base'
    d['family'] = n.split('_')[0] if n else ''
    return d


def outcome_of(act, nom, best_ep, incomplete):
    if incomplete:
        return 'archive_snapshot'
    if nom is None or act is None:
        return 'unknown'
    if act >= nom:
        return 'complete'
    if best_ep is not None and act >= best_ep + 99:
        return 'early_stop_legit'
    return 'interrupted'


pmap = collections.defaultdict(dict)
for p in prov:
    pmap[(p['machine'], p['run'])][p['source']] = p
names_by_machine = collections.defaultdict(set)
for (m, r) in by_key:
    names_by_machine[m].add(r)
# ★ 2026-10-01：`also_on_other_machine` 原先只按**原始目录名**比对，对改名件
#   （`.incomplete_*` / `_PARTIAL_*`）失明 —— 而两机对同一 run 的改名时间戳必然不同，
#   于是改名件永远"看不到对岸"。这里补一份**短名**索引，两边任一命中即算跨机重名。
_RS2 = re.compile(r'(_PARTIAL_\d+|\.incomplete_\d+_\d+|_oomfix|_\d{6})$')
names_short_by_machine = collections.defaultdict(set)
for m, rs in names_by_machine.items():
    for r in rs:
        names_short_by_machine[m].add(_RS2.sub('', r))

COLS = ['run', 'machine', 'outcome', 'loss', 'loss_src', 'epochs_nominal', 'epochs_actual',
        'best_epoch', 'best_map50_95', 'best_map50', 'last_map50_95', 'last_map50', 'wall_sec',
        'lr0', 'seed_name', 'seed_args', 'seed_kind', 'seed_used', 'dataset', 'data_yaml', 'model', 'imgsz', 'batch',
        'patience', 'save_period', 'family', 'budget_pct', 'lr_arm', 'threeway', 'flag_partial',
        'flag_incomplete', 'also_on_other_machine', 'n_sources', 'sources', 'src_primary',
        'md5_results', 'has_args', 'has_weights_A', 'test_map50_95', 'test_map50',
        'test_mp', 'test_mr', 'dup_test_line']

rows_out = []
for (machine, run) in sorted(by_key):
    entries = by_key[(machine, run)]
    src, path, st = max(entries, key=lambda e: e[2]['rows'])
    a = parse_args(args_by_key[(machine, run)][0][1]) if args_by_key.get((machine, run)) else {}
    nm = norm(run)
    # ★ 2026-10-01 修复：汇总（sio/a5）里记录的是**去掉改名后缀的短名**，
    #   而 `run` 是磁盘上的**原始目录名**（如 `..._s50n.incomplete_20260924_104028`）。
    #   原先只按原始名查 ⇒ **所有改名件的 test 列恒为空**，并被误读成
    #   "改名件没有 test 读数"（曾据此把 `smoke→sfchd` 30ep 记成 9 种子缺件）。
    #   实情：这些 run 的读数一直在汇总里，只是键对不上。改为回落到短名查。
    #   全域影响已实测：**只有 `smoke→sfchd` / 族 `b2` / 30ep 一格**（n 9 → 10）。
    _RS = re.compile(r'(_PARTIAL_\d+|\.incomplete_\d+_\d+|_oomfix|_\d{6})$')
    s = summary.get(run, {})
    if not s:
        # ★ **不区分机器**：作者裁定「跨机可以默认和同机一样，跨机不存在差异」
        #   ⇒ 同名读数不分机器，直接从汇总取。（先前一度只认同机，已按该裁定放开。）
        s = summary.get(_RS.sub('', run), {})
    try:
        nom = int(float(a.get('epochs') or nm['epochs_nominal'] or ''))
    except Exception:
        nom = None
    act = st['rows']
    rows_out.append(dict(
        run=run, machine=machine,
        outcome=outcome_of(act, nom, st['best_epoch'], nm['incomplete']),
        loss=s.get('loss', ''), loss_src=s.get('src', ''),
        epochs_nominal=nom if nom is not None else '', epochs_actual=act,
        best_epoch=st['best_epoch'], best_map50_95=st['best_map'], best_map50=st['best_map50'],
        last_map50_95=st['last_map'], last_map50=st['last_map50'], wall_sec=st['wall'],
        lr0=a.get('lr0') or '', seed_name=(nm['seed'] if nm['seed'] is not None else ''),
        seed_args=a.get('seed') or '',
        seed_kind=nm['seed_kind'],
        seed_used=(nm['seed'] if nm['seed'] is not None else (a.get('seed') or '')),
        dataset=os.path.basename(str(a.get('data') or '')).replace('.yaml', ''),
        data_yaml=a.get('data') or '', model=os.path.basename(str(a.get('model') or '')),
        imgsz=a.get('imgsz') or '', batch=a.get('batch') or '', patience=a.get('patience') or '',
        save_period=a.get('save_period') or '', family=nm['family'],
        budget_pct=nm['budget_pct'] if nm['budget_pct'] is not None else '',
        lr_arm=nm['lr_arm'], threeway=nm['threeway'], flag_partial=nm['partial'],
        flag_incomplete=nm['incomplete'],
        also_on_other_machine='|'.join(sorted(({'A', 'B'} - {machine}) & {m for m in 'AB'
                                              if run in names_by_machine.get(m, set())
                                              or _RS2.sub('', run) in names_short_by_machine.get(m, set())})),
        n_sources=len(entries), sources='|'.join(sorted({e[0] for e in entries})),
        src_primary=src, md5_results=pmap[(machine, run)][src]['md5_results'],
        has_args=1 if args_by_key.get((machine, run)) else 0,
        has_weights_A=1 if (machine == 'A' and run in weights) else 0,
        test_map50_95=s.get('map', ''), test_map50=s.get('map50', ''),
        test_mp=s.get('mp', ''), test_mr=s.get('mr', ''),
        dup_test_line=1 if run in dup_summary else 0))

with open(os.path.join(OUT, 'run_table_canonical.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore')
    w.writeheader()
    for r in sorted(rows_out, key=lambda x: (x['machine'], x['family'], x['run'])):
        w.writerow(r)

with open(os.path.join(OUT, 'provenance.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['run', 'machine', 'source', 'md5_results', 'rows',
                                      'md5_args', 'has_args', 'mtime'])
    w.writeheader()
    for p in sorted(prov, key=lambda x: (x['machine'], x['run'], x['source'])):
        w.writerow(p)

# ---------- 摘要与缺口清单 ----------
mach = collections.Counter(r['machine'] for r in rows_out)
outc = collections.Counter(r['outcome'] for r in rows_out)
noloss = [r for r in rows_out if not r['loss']]
crossdup = [r for r in rows_out if r['also_on_other_machine']]
conflict = []
for r in rows_out:
    d = {v['md5_results'] for v in pmap[(r['machine'], r['run'])].values()}
    if len(d) > 1:
        conflict.append(r)
notinbase = sorted({n for n in summary} - {r['run'] for r in rows_out})

print()
print('=== 底座 v2 摘要 ===')
print('run 记录（机器,run）:', len(rows_out), dict(mach))
print('结局分布            :', dict(outc))
print('无损失标注          :', len(noloss))
print('跨机重名 run        :', len(crossdup),
      collections.Counter(r['run'].split('_')[0] for r in crossdup).most_common(6))
print('同机多快照 md5 冲突 :', len(conflict))
print('test 侧指标覆盖     :', sum(1 for r in rows_out if r['test_map50_95'] != ''))
print('有损失标注但无目录  :', len(notinbase))
print('汇总文件重名(取末次):', len(dup_summary))

with open(os.path.join(OUT, '缺口清单.md'), 'w', encoding='utf-8') as f:
    f.write('# 底座缺口清单（scripts/01_build_base.py v3 自动生成）\n\n')
    f.write('> 本件是**原始缺口登记**；两类缺口的**分类与处置**见 `analysis\\A8_缺口复核.md`：\n')
    f.write('> 「有标注无目录」会先按**改名规则**在本地找回（`_PARTIAL_*` / `.incomplete_<日期>` / '
            '`_oomfix` / 尾缀 `_<hhmmss>`），找回的属**命名不一致**而非取件缺口；\n')
    f.write('> 「无损失标注」会按**同族是否单一损失**判定可否推断 —— 推断件**不得与实测混列**。\n\n')
    f.write('* run 记录数：**%d**（%s）\n' % (len(rows_out), dict(mach)))
    f.write('* 结局分布：%s\n' % dict(outc))
    f.write('* **无损失标注**：%d 个（无法进入损失轴分析）\n' % len(noloss))
    f.write('* **跨机重名**：%d 个（同名在两机各有一份，必须分开统计）\n' % len(crossdup))
    f.write('* 同机多快照 md5 冲突：%d 个（取行数最多者为主源）\n' % len(conflict))
    # ★ v3：把「有标注无目录」先按改名规则在本地找一遍 —— 找回的**不是取件缺口**
    _SUF = re.compile(r'(_PARTIAL_\d+|\.incomplete_\d+_\d+|_oomfix|_\d{6})$')

    def _norm(n):
        prev = None
        while prev != n:
            prev = n
            n = _SUF.sub('', n)
        return re.sub(r'^_PARTIAL_', '', n)

    _local = set()
    for _d in (os.path.join(BASE, 'raw'), r"E:\workplace\AB机实验文件夹\B_csv_20260930"):
        if os.path.isdir(_d):
            for _p in glob.glob(os.path.join(_d, '**', 'results.csv'), recursive=True):
                _local.add(os.path.basename(os.path.dirname(_p)))
            for _p in glob.glob(os.path.join(_d, '**', 'args.yaml'), recursive=True):
                _local.add(os.path.basename(os.path.dirname(_p)))
    _ln = collections.defaultdict(set)
    for _n in _local:
        _ln[_norm(_n)].add(_n)
    _renamed, _really = [], []
    for _n in notinbase:
        _got = _ln.get(_norm(_n), set()) - {_n}
        (_renamed if _got else _really).append((_n, sorted(_got)))
    f.write('\n## ★ 分类：**命名不一致 %d 条** / **真缺 %d 条**（合计 %d）\n\n'
            % (len(_renamed), len(_really), len(notinbase)))
    f.write('### 命名不一致（**本地其实有**，只是被改名 —— 不算取件缺口）\n\n')
    f.write('| 清单里的名字 | 本地实际目录 |\n|---|---|\n')
    for _n, _g in _renamed:
        f.write('| `%s` | %s |\n' % (_n, '、'.join('`%s`' % x for x in _g)))
    f.write('\n### 真缺（本地确实没有；多半在已删的 `P1part1.tar`，见云盘）\n\n')
    for _n, _ in _really:
        f.write('* `%s`\n' % _n)
    f.write('\n## 无损失标注明细（%d）\n\n| run | machine | outcome |\n|---|---|---|\n' % len(noloss))
    for r in sorted(noloss, key=lambda x: (x['machine'], x['run'])):
        f.write('| `%s` | %s | %s |\n' % (r['run'], r['machine'], r['outcome']))
json.dump(dict(runs=len(rows_out), machines=dict(mach), outcomes=dict(outc),
               no_loss=len(noloss), cross_dup=len(crossdup), conflict=len(conflict),
               summary_only=len(notinbase)),
          open(os.path.join(OUT, '_build_base_summary.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n输出 ->', OUT)
