# -*- coding: utf-8 -*-
"""_cells.py —— **格的唯一解析器**（单一实现，供 `07_claims.py` 与 `14_verify_claims.py` 共用）。

为什么要单独抽出来：本会话发现的整个 bug 类（族混杂、取到空读数存档件、未写明指标列）
都源于**同一个格解析逻辑被两处各写一遍**。按「数字只有一处」的纪律，解析只能有一份。

口径（三条，逐条都有实测依据；详见 `base\\数据字典.md` §七/§十）：
  1. **格的键 = (跨域配对, run 族, 标注预算%, epochs)** —— 旧键缺 `family`，会把不同批次混成一格；
  2. **可指定指标列** `key` —— 底座有 6 个可选列；论文 §4.4 用 val 侧 `best_map50_95`，
     其余各节用 test 侧 `test_map50_95`，不写明就无法复现；
  3. **同一 (种子, 臂) 多行时**：先扔掉该列无读数的行，再按结局优先级取（`complete` 最优）。

`标注预算%` 默认取自 **dataset 名**（交接件裁定）；`lb=None` 表示不按预算过滤。
"""
import os
import re
import csv
import collections

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE, 'base', 'run_table_canonical.csv')

COLS = ['test_map50_95', 'test_map50', 'best_map50_95', 'best_map50', 'last_map50_95', 'last_map50']
PREF = {'complete': 0, 'early_stop_legit': 1, 'interrupted': 2, 'archive_snapshot': 3}

# 论文每个招牌数字对应的**具名 run 族**（2026-09-30 由反查确定，逐位吻合）
FAM = {
    ('visdrone→dota15', 100): 't1c',     # §4.1 / §5 T1-c
    ('visdrone→dota15', 200): 'mech',
    ('aitod→visdrone', 100): 't1b',      # §4.1 / §5 T1-b
    ('aitod→visdrone', 200): 'mech',
    ('dota15→aitod', 100): 't1a',        # §5 T1-a
    ('smoke→sfchd', 30): 'b2', ('smoke→sfchd', 50): 'b2',
    ('smoke→sfchd', 100): 'b2', ('smoke→sfchd', 200): 'b2',
    ('shwd2sf→sfchd', 30): 'b2', ('shwd2sf→sfchd', 50): 'b2',
    ('shwd2sf→sfchd', 100): 'b2', ('shwd2sf→sfchd', 200): 'b2',
}

BB_PATH = os.path.join(BASE, 'base', 'run_backbone_map.csv')


def load_backbone():
    """`run -> backbone`（见 `base/run_backbone_map.csv`，覆盖率 ~98%）。"""
    if not os.path.exists(BB_PATH):
        return {}
    return {r['run']: r['backbone'] for r in csv.DictReader(open(BB_PATH, encoding='utf-8'))}


def arch_cell(G, pair, ep, backbone, key='test_map50_95', lb=None, seeds=None, min_n=3, BB=None):
    """★ 按 **backbone** 圈定架构对照 —— **不能用 `family`**。

    `family` 是 **run 名的第一段 = 批次**，不是架构。实测：
      · `b2_y11_sf_base100_s45n` 的 `family` = **`b2`**，而它正是 §4.4 的架构对照 run
        ⇒ 按 `family='y11'` 取会**漏掉 7 个种子**，把 100ep 从 **n=10 缩到 n=3**；
      · 反过来，`b2` 族里混着 yolo12n 与 yolo11n 两种架构（见 `A7_族混杂复核.md`）。
    ⇒ 架构轴的正确键是 `base/run_backbone_map.csv` 的 `backbone` 列。
    """
    BB = load_backbone() if BB is None else BB
    acc = collections.defaultdict(dict)
    for k in G:
        if k[0] != pair or k[3] != ep or (lb is not None and k[2] != lb):
            continue
        for s, arms in G[k].items():
            for a, rs in arms.items():
                hit = [r for r in rs if BB.get(r['run']) == backbone]
                if hit:
                    acc[s].setdefault(a, []).extend(hit)
    dd = {}
    for s, arms in acc.items():
        rec = {}
        for a in ('base', 'lr005'):
            r = _pick(arms.get(a, []), key)
            if r is not None:
                rec[a] = r
        if len(rec) == 2:
            dd[s] = rec
    if seeds:
        dd = {s: v for s, v in dd.items() if seeds(s)}
    if len(dd) < min_n:
        return None
    g = [((f(dd[s]['lr005'][key]) - f(dd[s]['base'][key])) * 100, s) for s in sorted(dd)]
    vals = [x for x, _ in g]
    import math
    import statistics as st
    sd = st.stdev(vals) if len(vals) > 1 else 0.0
    return dict(k=(pair, 'backbone:%s' % backbone, ep), fam='backbone:%s' % backbone, key=key,
                n=len(vals), mean=st.mean(vals), sd=sd,
                t=(st.mean(vals) / (sd / math.sqrt(len(vals)))) if len(vals) > 1 and sd > 0 else float('nan'),
                per_seed={s: v for v, s in g},
                ds=sorted({dd[s][a]['dataset'] for s in dd for a in ('base', 'lr005')}))


def f(x):
    try:
        return float(x)
    except Exception:
        return None


def pair_of(r):
    m = re.sub(r'_pretrain.*$', '', (r['model'] or '').replace('.pt', ''))
    d = re.sub(r'_(3way|2way)$', '', re.sub(r'_?\d{1,3}p.*$', '', r['dataset'] or ''))
    return '%s→%s' % (m, d)


def budget_of(r):
    """标注预算取 dataset 名（交接件裁定），run 名兜底。"""
    for s in (r['dataset'], r['data_yaml'], r['run']):
        m = re.search(r'(?<![0-9a-z])(\d{1,3})p(?![0-9a-z])', str(s))
        if m and int(m.group(1)) in (10, 20, 30, 40, 50, 100):
            return int(m.group(1))
    return None


def load():
    rows = list(csv.DictReader(open(CSV_PATH, encoding='utf-8')))
    for r in rows:
        r['_pair'] = pair_of(r)
        r['_seed'] = f(r['seed_used'])
        r['_ep'] = f(r['epochs_nominal'])
        r['_lb'] = budget_of(r)
    G = collections.defaultdict(lambda: collections.defaultdict(dict))
    for r in rows:
        if r['lr_arm'] in ('base', 'lr005') and r['_seed'] is not None and r['_ep']:
            G[(r['_pair'], r['family'], r['_lb'], int(r['_ep']))] \
                .setdefault(int(r['_seed']), {}).setdefault(r['lr_arm'], []).append(r)
    return rows, G


def ok_outcome(r):
    """★ 该行的结局是否**可用于配对**（2026-10-01 新增，堵一个真实口子）。

    背景：`_pick` 原先只要求"该列非空"，而**列是有偏向的**：
      · `test_map50_95` 由 driver 跑完 eval 后写进 `sio_b_results.csv`
        ⇒ 中断件**自然没有**这一列 ⇒ 旧逻辑对 test 侧恰好安全；
      · `best_map50_95` 来自 run 自己的 `results.csv`（val 侧最优轮）
        ⇒ **中断件照样有这一列** ⇒ 旧逻辑会把 92/100 的截断读数当完整件用。
    实测（`mask→mende`/族 `t2`/100ep，即 §4.3 的格）：
      · `key='test_map50_95'` → n=7，s49 被正确排除；
      · `key='best_map50_95'` → n=8，**s49 = `interrupted 92/100` 与 `93/100` 被算进去**，
        均值从 −1.4878 漂到 −1.5474、t 从 −4.02 漂到 −6.53。
    ⇒ 结局判定必须独立于"该列是否非空"，否则同一格换列会**一边安全一边污染**。

    规则（逐条有据）：
      * `complete` —— 可用；
      * `early_stop_legit` —— 可用（`epochs_actual >= best_epoch + 99` 的合法 patience 早停）；
      * `archive_snapshot` —— `.incomplete_` 存档件**两种都有**：
        「跑满但没写 test 行」（如 `smoke→sfchd` 30ep s50，30/30）可用，
        真中断不可用 ⇒ **以实际轮数区分**，`epochs_actual >= epochs_nominal` 才可用；
      * `interrupted` —— **一律不可用**（轮数不足 ⇒ val-best 与完整件不可比）。
    """
    o = r.get('outcome')
    if o in ('complete', 'early_stop_legit'):
        return True
    if o == 'archive_snapshot':
        ea, en = f(r.get('epochs_actual')), f(r.get('epochs_nominal'))
        return ea is not None and en is not None and ea >= en
    return False


def _pick(rs, key):
    ok = [r for r in rs if f(r[key]) is not None and ok_outcome(r)]
    if not ok:
        return None
    ok.sort(key=lambda r: (PREF.get(r['outcome'], 9), len(r['run'])))
    return ok[0]


def dropped(rs, key):
    """该 (种子, 臂) 里**有该列读数、但因结局不可用而被丢掉**的行（审计用）。"""
    return [r for r in rs if f(r[key]) is not None and not ok_outcome(r)]


def cell(G, pair, ep, lb=20, fam=None, key='test_map50_95', seeds=None, min_n=3):
    """返回 dict(mean, n, t, per_seed, k) 或 None（无格）或 dict(ambiguous=[族...])。

    **绝不静默合并多族** —— 未点名族且存在多族时返回 `ambiguous`，由调用方报错。
    """
    ks = [k for k in G if k[0] == pair and k[3] == ep and (lb is None or k[2] == lb)]
    if fam is not None:
        ks = [k for k in ks if k[1] == fam]
    if not ks:
        return None
    if len(ks) > 1:
        return dict(ambiguous=sorted(k[1] for k in ks))
    k = ks[0]
    dd = {}
    for s, arms in G[k].items():
        rec = {}
        for a in ('base', 'lr005'):
            r = _pick(arms.get(a, []), key)
            if r is not None:
                rec[a] = r
        if len(rec) == 2:
            dd[s] = rec
    if seeds:
        dd = {s: v for s, v in dd.items() if seeds(s)}
    if len(dd) < min_n:
        return None
    g = [((f(dd[s]['lr005'][key]) - f(dd[s]['base'][key])) * 100, s) for s in sorted(dd)]
    vals = [x for x, _ in g]
    import math
    import statistics as st
    sd = st.stdev(vals) if len(vals) > 1 else 0.0
    mach = collections.Counter()
    dss = set()
    for s in dd:
        for a in ('base', 'lr005'):
            mach[dd[s][a]['machine']] += 1
            dss.add(dd[s][a]['dataset'])
    return dict(k=k, fam=k[1], key=key, n=len(vals), mean=st.mean(vals), sd=sd,
                t=(st.mean(vals) / (sd / math.sqrt(len(vals)))) if len(vals) > 1 and sd > 0 else float('nan'),
                per_seed={s: v for v, s in g}, ds=sorted(dss), machines=mach)
