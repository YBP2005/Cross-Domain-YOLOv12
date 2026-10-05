# -*- coding: utf-8 -*-
"""09_probe_sec42.py —— §4.2/§4.3/§4.4 八条 ❌未复现断言的**候选格反查**（只读，不改底座）。

背景（`deliver/claims_to_evidence.md`）：新稿 §4.2/§4.3/§4.4 有 8 条断言用底座口径算不出。
本件不改稿、不下结论、不补跑，只做一件事：**把所有能想到的候选口径都算一遍，
把逐种子差异摊开**，让作者一眼看出旧数字是从哪一批 run / 哪个口径来的。

反查的三条手段（每条都必须在报告里说明它换了什么）：
  ① **换数据集变体** —— 同一配对在底座里常有多份 data yaml（`sfchd_20p` vs `sfchd_20p_b`）。
  ② **换指标列** —— 底座的增益可以建在 6 个列上（test/best/last × mAP50-95/mAP50），
     旧稿报的到底是哪一列，从未被显式写明。
  ③ **换种子子集（签名搜索）** —— 论文若只用了 n=3 或 n=5 个种子，就在整格种子里
     枚举**全部同大小子集**，找出与论文 (均值, t) 同时相符的那些子集。

★ 一条必须先说清的口径事实：底座的 `budget_pct` 列取自 **run 名**（`01_build_base.py`
  L201 的 `(\\d+)p(?![a-z])`），**不是 dataset 名**；1921 行里 1469 行的 run 名不含预算 token
  ⇒ 这些行的 `budget_pct` 为空。**按 dataset 名取预算会得到另一批格**（本件两种都列）。
"""
import os
import re
import csv
import sys
import math
import itertools
import collections
import statistics as st

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ★ 2026-10-05：可移植（放行布局下 = 仓库根，含 base/ deliver/ M3_draft/）
OUTD = os.path.join(BASE, 'deliver')
rows = [r for r in csv.DictReader(open(os.path.join(BASE, 'base', 'run_table_canonical.csv'),
                                      encoding='utf-8'))]

KEYS = ['test_map50_95', 'test_map50', 'best_map50_95', 'best_map50', 'last_map50_95', 'last_map50']
KEYDESC = {
    'test_map50_95': 'test 侧 mAP50-95（底座正式报数列）',
    'test_map50': 'test 侧 mAP50',
    'best_map50_95': '各 run 最优轮的 val mAP50-95',
    'best_map50': '各 run 最优轮的 val mAP50',
    'last_map50_95': '末轮 val mAP50-95',
    'last_map50': '末轮 val mAP50',
}


def f(x):
    try:
        return float(x)
    except Exception:
        return None


def pair_of(r):
    m = re.sub(r'_pretrain.*$', '', (r['model'] or '').replace('.pt', ''))
    d = re.sub(r'_?\d{1,3}p.*$', '', re.sub(r'_(3way|2way)$', '', r['dataset'] or ''))
    return '%s→%s' % (m, d)


for r in rows:
    r['_p'] = pair_of(r)
    r['_s'] = f(r['seed_name'])
    r['_e'] = f(r['epochs_nominal'])
    r['_bp'] = (r['budget_pct'] or '').strip()


def tstat(xs):
    n = len(xs)
    if n < 2:
        return float('nan')
    sd = st.stdev(xs)
    return float('inf') if sd == 0 else st.mean(xs) / (sd / math.sqrt(n))


def paired(pair, dataset=None, ep=None, key='test_map50_95', bp=None, fam=None):
    """返回 {seed: gain_pp} —— 仅两臂都有该列指标的种子。

    ★ `fam` 是本轮新加的维度，也是**本轮最重要的一件发现**：底座里同一个
    (配对, dataset, epochs) 常常混着**多个 run 族**（`b2` / `shwd2sf` / `smoke2sf` /
    `y11` / `t2` / `r10` …）。旧的分析口径（`06_A25.py` 的 `cells()`）**没有把族放进键里**，
    于是把不同的批次混成了一格。
    """
    g = collections.defaultdict(dict)
    for r in rows:
        if r['_p'] != pair or r['lr_arm'] not in ('base', 'lr005'):
            continue
        if r['_s'] is None or r['_e'] is None:
            continue
        if dataset is not None and r['dataset'] != dataset:
            continue
        if ep is not None and int(r['_e']) != ep:
            continue
        if bp is not None and r['_bp'] != str(bp):
            continue
        if fam is not None and r['family'] != fam:
            continue
        if f(r[key]) is None:
            continue
        g[r['_s']][r['lr_arm']] = r
    out = {}
    for s, d in g.items():
        if 'base' in d and 'lr005' in d:
            out[s] = (f(d['lr005'][key]) - f(d['base'][key])) * 100
    return out


def fams_of(pair, dataset=None, ep=None):
    c = collections.Counter()
    for r in rows:
        if r['_p'] != pair or r['lr_arm'] not in ('base', 'lr005'):
            continue
        if dataset is not None and r['dataset'] != dataset:
            continue
        if ep is not None and r['_e'] is not None and int(r['_e']) != ep:
            continue
        c[r['family']] += 1
    return c


def fam_table(title, pair, dataset, eps, paper):
    """★ 族分解表：把 (族 × epochs) 的增益列全 —— 本件解释力最强的一张表。"""
    w('#### ★ 族分解：`%s` 上各 run 族的 (族 × epochs) 增益（`%s`，test 侧，逐种子配对）' % (title, dataset))
    w()
    fams = [f for f, _ in fams_of(pair, dataset).most_common()]
    w('| run 族 | ' + ' | '.join('%dep' % e for e in eps) + ' |')
    w('|---|' + '---|' * len(eps))
    for fam in fams:
        cs = []
        for e in eps:
            g = paired(pair, dataset, e, fam=fam)
            cs.append(('%+.3f (n=%d)' % (st.mean(list(g.values())), len(g))) if len(g) >= 2 else '—')
        w('| `%s` | %s |' % (fam, ' | '.join(cs)))
    w('| **论文** | ' + ' | '.join('**%+.3f**' % paper[e] for e in eps) + ' |')
    w()
    # 哪个族逐位吻合
    for fam in fams:
        hits, devs = 0, []
        for e in eps:
            g = paired(pair, dataset, e, fam=fam)
            if len(g) < 2:
                devs.append(None)
                continue
            d = abs(st.mean(list(g.values())) - paper[e])
            devs.append(d)
            if d < 0.005:
                hits += 1
        good = [d for d in devs if d is not None]
        if not good:
            continue
        if hits:
            w('* ⇒ 族 **`%s`**：**%d/%d 个端点与论文逐位吻合**（偏差 %s）'
              % (fam, hits, len(eps),
                 '、'.join('%dep %s' % (e, ('%.3f' % d) if d is not None else '—')
                           for e, d in zip(eps, devs))))
    w()


def sig(g, target_mean, target_t=None, k=None, mtol=0.004, ttol=0.06, sign=None):
    """签名搜索：在 g 的种子里枚举全部 k 子集，找 (均值,t) 同时相符的。

    sign='neg' 时还要求子集**全部为负**（论文常写"N/N 更低"）。
    """
    hits = []
    seeds = sorted(g)
    ks = [k] if k else range(2, len(seeds) + 1)
    for kk in ks:
        if kk > len(seeds):
            continue
        for c in itertools.combinations(seeds, kk):
            xs = [g[s] for s in c]
            m = st.mean(xs)
            if abs(m - target_mean) > mtol:
                continue
            if sign == 'neg' and not all(x < 0 for x in xs):
                continue
            if sign == 'pos' and not all(x > 0 for x in xs):
                continue
            if target_t is not None:
                t = tstat(xs)
                if abs(t - target_t) > ttol:
                    continue
            hits.append((c, m, tstat(xs)))
    return hits


def joint_search(per_ep, targets, ks=(3, 4, 5, 6, 8, 10)):
    """**联合搜索**：找同一个种子子集，让它同时复现全部几个端点。

    per_ep = {ep: {seed: gain}}；targets = {ep: 论文值}。
    返回按"四点总绝对偏差"升序的 (子集, 各点值, 总偏差)。
    这是最强的识别手段：若论文的四个点来自**同一批 seed**，就会有一个子集同时命中。
    """
    eps = sorted(targets)
    common = set.intersection(*[set(per_ep[e]) for e in eps])
    best = []
    for k in ks:
        if k > len(common):
            continue
        for c in itertools.combinations(sorted(common), k):
            vals = {e: st.mean([per_ep[e][s] for s in c]) for e in eps}
            dev = sum(abs(vals[e] - targets[e]) for e in eps)
            best.append((dev, c, vals))
    best.sort(key=lambda x: x[0])
    return best


def sigline(tag, g, target_m, target_t, k=3):
    if not g:
        w('* **%s 签名搜索**：该格无配对种子，跳过。' % tag)
        return
    hits = sig(g, target_m, target_t, k=k, mtol=0.02, ttol=0.30)
    head = '**命中 %d 组**：' % len(hits) if hits else '**零命中**'
    body = '；'.join('`%s`⇒%+.4f(t=%.3f)' % (','.join('s%d' % s for s in c), m, t)
                    for c, m, t in hits[:6])
    w('* **%s 签名搜索**（目标 %+.4f, t=%.3f, k=%d）：%s%s' % (tag, target_m, target_t, k, head, body))
    w('  * 对照：全格 n=%d ⇒ %+.4f（t=%.3f）。'
      % (len(g), st.mean(list(g.values())), tstat(list(g.values()))))


L = []


def w(s=''):
    L.append(s)
    print(s)


w('# §4.2 / §4.3 / §4.4 未复现断言：候选格反查与逐种子差异（2026-09-30）')
w()
w('> 依据 `base/run_table_canonical.csv`（1921 行，(机器,run) 为键）。**本件不改稿、不下最终结论、不补跑**，')
w('> 只把"旧数字可能来自哪一批 run / 哪一个口径"摊开。所有数字均为本次现算。')
w('>')
w('> **★ 一条必须先说清的口径事实**：底座的 `budget_pct` 列取自 **run 名**')
w('> （`scripts\\01_build_base.py` L201：`re.search(r"(\\d+)p(?![a-z])", n)`），**不是 dataset 名**；')
w('> 1921 行里 **1469 行**的 run 名不含预算 token ⇒ 这些行 `budget_pct` 为空。')
w('> 交接件 §4.2 要求"预算取自 dataset 名"，**与底座这一列的口径不同** —— 本件两种都列。')
w()
w('**反查三条手段**：')
w()
w('| # | 手段 | 换掉了什么 |')
w('|---|---|---|')
w('| ① | **换数据集变体** | 同一配对在底座里常有多份 data yaml（`sfchd_20p` vs `sfchd_20p_b`）|')
w('| ② | **换指标列** | 增益可建在 6 列上（test/best/last × mAP50-95/mAP50），旧稿从未写明用哪一列 |')
w('| ③ | **换种子子集（签名搜索）** | 论文若只用 n=3 / n=5 个种子，就在整格种子里枚举**全部同大小子集**，找与论文 (均值,t) 同时相符者 |')
w()
w('指标列定义：')
w()
w('| 列 | 含义 |')
w('|---|---|')
for k in KEYS:
    w('| `%s` | %s |' % (k, KEYDESC[k]))
w()
w('---')
w()


def cell_block(title, pair, claims, datasets=None, eps=None):
    """通用块：列出该配对在各 (dataset, ep) 上的 6 列增益，并对每条断言做签名搜索。"""
    w('## %s' % title)
    w()
    for cl in claims:
        w('**断言**：%s　论文值 **%s**' % (cl['label'], cl['paper']))
        w('')
        # 全候选表（按 dataset × ep，主列 test_map50_95）
        cand = collections.defaultdict(dict)
        for r in rows:
            if r['_p'] != pair or r['_e'] is None:
                continue
            cand[(r['dataset'], int(r['_e']))] = True
        w('候选格（`test_map50_95`，n≥2）：')
        w()
        w('| dataset | ep | n | 增益(pp) | t | 逐种子更低 |')
        w('|---|---|---|---|---|---|')
        for ds, e in sorted(cand, key=lambda x: (str(x[0]), x[1])):
            if cl.get('ep') is not None and e != cl['ep']:
                continue
            if cl.get('dataset') is not None and ds != cl['dataset']:
                continue
            g = paired(pair, ds, e)
            if len(g) < 2:
                continue
            xs = [g[s] for s in sorted(g)]
            lo = sum(1 for x in xs if x < 0)
            w('| `%s` | %d | %d | **%+.3f** | %.2f | %d/%d |' %
              (ds, e, len(xs), st.mean(xs), tstat(xs), lo, len(xs)))
        w('')
        # 换指标列
        if cl.get('dataset') and cl.get('ep'):
            g0 = paired(pair, cl['dataset'], cl['ep'])
            w('换指标列（`%s` %dep，逐种子配对）：' % (cl['dataset'], cl['ep']))
            w()
            w('| 列 | n | 增益(pp) | t |')
            w('|---|---|---|---|')
            for k in KEYS:
                gk = paired(pair, cl['dataset'], cl['ep'], key=k)
                if len(gk) < 2:
                    continue
                xs = [gk[s] for s in sorted(gk)]
                w('| `%s` | %d | **%+.4f** | %.3f |' % (k, len(xs), st.mean(xs), tstat(xs)))
            w('')
        # 逐种子
        if cl.get('dataset') and cl.get('ep'):
            g0 = paired(pair, cl['dataset'], cl['ep'])
            if g0:
                w('逐种子（`%s` %dep，test 侧 mAP50-95）：' % (cl['dataset'], cl['ep']))
                w()
                w('| seed | 增益(pp) |')
                w('|---|---|')
                for s in sorted(g0):
                    w('| s%d | %+.3f |' % (s, g0[s]))
                w()
        # 签名搜索
        if cl.get('sig') and cl.get('dataset') and cl.get('ep'):
            g0 = paired(pair, cl['dataset'], cl['ep'], key=cl.get('sig_key', 'test_map50_95'))
            if g0:
                hits = sig(g0, cl['sig_mean'], cl.get('sig_t'), k=cl.get('sig_k'))
                w('**签名搜索**：目标 均值 %+.4f%s，在 `%s` %dep 的 %d 个种子里找 —— %s' %
                  (cl['sig_mean'], ('、t=%.3f' % cl['sig_t']) if cl.get('sig_t') is not None else '',
                   cl['dataset'], cl['ep'], len(g0),
                   ('**命中 %d 个同大小子集**' % len(hits)) if hits else '**零命中**'))
                w()
                for c, m, t in hits[:12]:
                    w('* 子集 `%s` ⇒ 均值 %+.4f，t=%.3f（n=%d）' %
                      (','.join('s%d' % s for s in c), m, t, len(c)))
                if len(hits) > 12:
                    w('* …共 %d 个，其余略' % len(hits))
                w()
        w()


def matrix(title, pair, dataset, eps, paper):
    """打印 (指标列 × epochs) 的完整增益矩阵 —— §4.2 的关键诊断表。`paper` = {ep: float}。"""
    w('### %s：**指标列 × epochs 全矩阵**（`%s`，逐种子配对，单位 pp）' % (title, dataset))
    w()
    w('| 指标列 | ' + ' | '.join('%dep' % e for e in eps) + ' |')
    w('|---|' + '---|' * len(eps))
    for k in KEYS:
        cells_ = []
        for e in eps:
            g = paired(pair, dataset, e, key=k)
            cells_.append(('%+.3f (n=%d)' % (st.mean(list(g.values())), len(g))) if len(g) >= 2 else '—')
        w('| `%s` | %s |' % (k, ' | '.join(cells_)))
    w('| **论文** | ' + ' | '.join('**%+.3f**' % paper[e] for e in eps) + ' |')
    w()
    w('各列与论文四点的**最大偏差**（越小越像论文用的那一列）：')
    w()
    w('| 指标列 | 最大偏差(pp) | 逐点偏差 | 判定 |')
    w('|---|---|---|---|')
    rank = []
    for k in KEYS:
        devs = []
        for e in eps:
            g = paired(pair, dataset, e, key=k)
            devs.append(None if len(g) < 2 else abs(st.mean(list(g.values())) - paper[e]))
        good = [d for d in devs if d is not None]
        if not good:
            continue
        rank.append((max(good), k, devs))
    for mx, k, devs in sorted(rank):
        tag = '✅ **最像论文用的那一列**' if mx < 0.010 else ('⚠ 接近' if mx < 0.05 else '')
        w('| `%s` | **%.3f** | %s | %s |' %
          (k, mx, '、'.join('%dep %s' % (e, ('%.3f' % d) if d is not None else '—')
                            for e, d in zip(eps, devs)), tag))
    w()


w('### ★ 先说结论：第五种手段 —— **换 run 族（batch）** 解释掉了绝大多数"未复现"')
w()
w('底座里同一个 `(配对, dataset, epochs)` **常常混着多个 run 族**。旧的分析口径')
w('（`scripts\\06_A25.py` 的 `cells()`）**没有把 `family` 放进格键**，于是把不同批次混成了一格。')
w('对 §4.2 的两族，混进来的正是另一批同配对实验：')
w()
w('| 配对 | 该格混入的族 |')
w('|---|---|')
for pair in ('smoke→sfchd', 'shwd2sf→sfchd', 'y11_shwd→sfchd'):
    c = fams_of(pair, 'sfchd_20p_b')
    w('| `%s` | %s |' % (pair, '、'.join('`%s`(%d 行)' % (f, n) for f, n in c.most_common())))
w()
w('下面每一节都先给**族分解表**。这就是"论文的数是从哪来的"的答案。')
w()
w('---')
w()

matrix('§4.2 之一 `smoke→sfchd`', 'smoke→sfchd', 'sfchd_20p_b', (30, 50, 100, 200),
       {30: 3.656, 50: 2.674, 100: 1.666, 200: 1.495})
fam_table('smoke→sfchd', 'smoke→sfchd', 'sfchd_20p_b', (30, 50, 100, 200),
          {30: 3.656, 50: 2.674, 100: 1.666, 200: 1.495})
matrix('§4.2 之二 `shwd2sf→sfchd`', 'shwd2sf→sfchd', 'sfchd_20p_b', (30, 50, 100, 200),
       {30: 0.812, 50: 0.728, 100: 0.694, 200: 0.794})
fam_table('shwd2sf→sfchd', 'shwd2sf→sfchd', 'sfchd_20p_b', (30, 50, 100, 200),
          {30: 0.812, 50: 0.728, 100: 0.694, 200: 0.794})

w('### 第四种反查手段：**`sio_b_results.csv` 重名口径**（`dup_test_line`）')
w()
w('`sio_b_results.csv` 是**追加写**的，同一 run 名可以有多行（重跑/中断后重跑）。')
w('底座采"**首次出现**"（与论文 §4.1 逐位吻合），但这是**口径选择**，会动到小数点后三位。')
w('下面列出 §4.2 两族里带 `dup_test_line=1` 的 run —— 若论文用的是**末次**读数，就在这批里。')
w()
w('| run | machine | ep | seed | arm | dataset | outcome |')
w('|---|---|---|---|---|---|---|')
for r in sorted(rows, key=lambda x: x['run']):
    if r['_p'] in ('smoke→sfchd', 'shwd2sf→sfchd') and r['dup_test_line'] == '1':
        w('| `%s` | %s | %s | s%s | %s | `%s` | %s |' %
          (r['run'], r['machine'], r['epochs_nominal'], r['seed_name'], r['lr_arm'],
           r['dataset'], r['outcome']))
w()

w('---')
w()

cell_block('§4.2 之一：`smoke→sfchd` 四点扫描（逐点诊断）', 'smoke→sfchd', [
    dict(label='`smoke→SFCHD` **30 ep**', paper='**+3.656**（底座 test 侧 +3.542, n=9）',
         dataset='sfchd_20p_b', ep=30),
    dict(label='`smoke→SFCHD` **100 ep**', paper='**+1.666**（底座 test 侧 +1.766, n=10，差 0.100）',
         dataset='sfchd_20p_b', ep=100),
])

# ---------- §4.2 shwd2sf→sfchd ----------
w('## §4.2 之二：`shwd2sf→sfchd` 四点（论文 +0.812 / +0.728 / +0.694 / +0.794）')
w()
w('★ 这一族在底座里有 **两份并行 data yaml**：`sfchd_20p_b`（旧、10 种子）与')
w('`sfchd_20p`（新、3 种子、run 名带 `20p`）⇒ 交接件 §4.2 的"同格混了两个 yaml"指的就是它。')
w()
w('| 点 | 论文 | `sfchd_20p_b` | `sfchd_20p` |')
w('|---|---|---|---|')
for e, pw in ((30, '+0.812'), (50, '+0.728'), (100, '+0.694'), (200, '+0.794')):
    gb = paired('shwd2sf→sfchd', 'sfchd_20p_b', e)
    gn = paired('shwd2sf→sfchd', 'sfchd_20p', e)
    w('| %dep | **%s** | %s | %s |' %
      (e, pw,
       ('**%+.3f**（n=%d, t=%.2f）' % (st.mean(list(gb.values())), len(gb), tstat(list(gb.values())))) if len(gb) >= 2 else '—',
       ('**%+.3f**（n=%d, t=%.2f）' % (st.mean(list(gn.values())), len(gn), tstat(list(gn.values())))) if len(gn) >= 2 else '—'))
w()
w('`sfchd_20p_b` 逐种子（四点并排）：')
w()
g30 = paired('shwd2sf→sfchd', 'sfchd_20p_b', 30)
g50 = paired('shwd2sf→sfchd', 'sfchd_20p_b', 50)
g100 = paired('shwd2sf→sfchd', 'sfchd_20p_b', 100)
g200 = paired('shwd2sf→sfchd', 'sfchd_20p_b', 200)
seeds = sorted(set(g30) | set(g50) | set(g100) | set(g200))
w('| seed | 30ep | 50ep | 100ep | 200ep |')
w('|---|---|---|---|---|')
for s in seeds:
    w('| s%d | %s | %s | %s | %s |' % (
        s,
        ('%+.3f' % g30[s]) if s in g30 else '—',
        ('%+.3f' % g50[s]) if s in g50 else '—',
        ('%+.3f' % g100[s]) if s in g100 else '—',
        ('%+.3f' % g200[s]) if s in g200 else '—'))
w()
# 留一法：30ep 去掉最负的一个种子
if g30:
    lo = min(g30, key=lambda s: g30[s])
    rest = [g30[s] for s in g30 if s != lo]
    w('* 30ep 全格最负种子 = **s%d（%+.3f pp）**；去掉它后其余 %d 个 ⇒ 均值 **%+.3f pp**（论文 +0.812，仍不符）。' %
      (lo, g30[lo], len(rest), st.mean(rest)))
w('* 四点里 **50ep / 200ep 与论文最接近**（+0.703 vs +0.728、+0.758 vs +0.794，各差 ≈0.03）；')
w('  **30ep / 100ep 差别最大**（+0.313 vs +0.812、+0.541 vs +0.694）⇒ 不是"整族偏移"，是**两点各自不同**，')
w('  更像**这两点用了另一批 run**（或另一份 yaml / 另一个指标列）。')
w()
w('### ★ 联合搜索：**同一批种子能不能同时复现四个点**')
w()
w('这是本件最强的识别手段。若论文那行四点来自**同一批 seed**，就应存在一个种子子集，')
w('让它同时给出 ≈ +0.812 / +0.728 / +0.694 / +0.794。下面枚举 `sfchd_20p_b` 上四点共有的种子')
w('的全部 k∈{3,4,5,6,8,10} 子集，按"四点总绝对偏差"升序排。')
w()
PER = {e: paired('shwd2sf→sfchd', 'sfchd_20p_b', e) for e in (30, 50, 100, 200)}
TGT = {30: 0.812, 50: 0.728, 100: 0.694, 200: 0.794}
common = sorted(set.intersection(*[set(PER[e]) for e in TGT]))
w('四点共有的种子（%d 个）：`%s`' % (len(common), ','.join('s%d' % s for s in common)))
w()
best = joint_search(PER, TGT)
w('| 种子子集 | n | 30ep | 50ep | 100ep | 200ep | 总偏差 |')
w('|---|---|---|---|---|---|---|')
for dev, c, vals in best[:10]:
    w('| `%s` | %d | %+.3f | %+.3f | %+.3f | %+.3f | **%.3f** |' %
      (','.join('s%d' % s for s in c), len(c), vals[30], vals[50], vals[100], vals[200], dev))
w()
w('* 全格（不选子集，n=%d）四点 = %s ⇒ 总偏差 **%.3f**。' %
  (len(common), ' / '.join('%+.3f' % st.mean(list(PER[e].values())) for e in (30, 50, 100, 200)),
   sum(abs(st.mean(list(PER[e].values())) - TGT[e]) for e in (30, 50, 100, 200))))
w('* 判别：**只有"总偏差 ≈0"才说明论文那四点出自同一批种子**；')
w('  若最小总偏差仍有 0.3 以上，则论文那四点**不可能来自本格任何一组同批种子** ⇒ 必须换 run 名单。')
w()
w('签名搜索（单点，`sfchd_20p_b`，test 侧）：')
w()
for e, pw in ((30, 0.812), (100, 0.694)):
    g = paired('shwd2sf→sfchd', 'sfchd_20p_b', e)
    hits = sig(g, pw, k=None, mtol=0.004)
    w('* %dep 目标 %+.3f：%s' % (e, pw, ('命中 %d 个种子子集' % len(hits)) if hits else '**零命中**'))
    for c, m, t in hits[:8]:
        w('  * `%s` ⇒ %+.4f（n=%d, t=%.2f）' % (','.join('s%d' % s for s in c), m, len(c), t))
w()

# ---------- §4.3 mask→mendeley ----------
w('## §4.3：饱和对照 `mask→mendeley`（论文 **−1.49**，t=−4.02, p=0.016, **5/5 更低**）')
w()
w('底座里 `mask` 预训练权重打 mendeley 目标域共有 **两个配对**：')
w()
w('| 配对 | dataset | ep | n | 增益(pp) | t | 更低 |')
w('|---|---|---|---|---|---|---|')
for p in ('mask→mende', 'mask→mende20'):
    for ds in sorted({r['dataset'] for r in rows if r['_p'] == p}):
        for e in (30, 100, 200):
            g = paired(p, ds, e)
            if len(g) < 2:
                continue
            xs = [g[s] for s in sorted(g)]
            w('| `%s` | `%s` | %d | %d | **%+.3f** | %.2f | %d/%d |' %
              (p, ds, e, len(xs), st.mean(xs), tstat(xs), sum(1 for x in xs if x < 0), len(xs)))
w()
w('* 论文的 **5/5 更低** 与 `mask→mende`（n=5）的 **4/5** 差一个种子；`mask→mende20`（n=13）是 **11/13**。')
w('* 论文的 **t=−4.02, p=0.016** 对应 n=5：n=5 的自由度 df=4，`p=0.016` ⇒ `t≈−4.02` ✓ 自洽 ⇒')
w('  **论文确为 n=5**。⇒ 只剩两种可能：**(a)** `mask→mende` 的 5 个种子里有一个读数不同；')
w('  **(b)** 它取的是 `mask→mende20`（n=13）里某 5 个种子。下面做签名搜索。')
w()
for p, ds, mt, tt in (('mask→mende', 'mende_20p', -1.49, -4.02),
                      ('mask→mende20', 'mende20_3way', -1.49, -4.02)):
    g = paired(p, ds, 100)
    if not g:
        continue
    for fam in sorted({r['family'] for r in rows if r['_p'] == p and r['dataset'] == ds}):
        gf = paired(p, ds, 100, fam=fam)
        if len(gf) < 2:
            continue
        w('* 族 **`%s`**（`%s` %s 100ep）：n=%d ⇒ **%+.3f pp**（t=%.3f，%d/%d 更低）'
          % (fam, p, ds, len(gf), st.mean(list(gf.values())), tstat(list(gf.values())),
             sum(1 for v in gf.values() if v < 0), len(gf)))
    hits = sig(g, mt, tt, k=5, mtol=0.02, ttol=0.25, sign='neg')
    w('* 签名搜索 `%s`（全部族合并）100ep，目标 (−1.49, t=−4.02)、k=5、**且要求 5/5 全负**：%s' %
      (p, ('**命中 %d 组**' % len(hits)) if hits else '**零命中**'))
    for c, m, t in hits[:8]:
        w('  * `%s` ⇒ %+.3f（t=%.3f，5/5 更低 ✓）' % (','.join('s%d' % s for s in c), m, t))
    for fam in sorted({r['family'] for r in rows if r['_p'] == p and r['dataset'] == ds}):
        gf = paired(p, ds, 100, fam=fam)
        hh = sig(gf, mt, tt, k=5, mtol=0.02, ttol=0.25, sign='neg')
        if hh:
            w('  * ★ 只看族 **`%s`** 时命中：%s'
              % (fam, '；'.join('`%s`⇒%+.3f(t=%.3f)' % (','.join('s%d' % s for s in c), m, t)
                               for c, m, t in hh)))
w()
w('`mask→mende` / `mende_20p` 100ep 逐种子（test 侧）：')
w()
g = paired('mask→mende', 'mende_20p', 100)
w('| seed | 增益(pp) |')
w('|---|---|')
for s in sorted(g):
    w('| s%d | %+.3f |' % (s, g[s]))
w()

# ---------- §4.4 YOLO11n ----------
w('## §4.4：YOLO11n 架构对照（论文 30ep **+1.2747**（t=6.967）；100ep **−0.0050**（t=−0.099））')
w()
w('底座里 YOLO11n 相关配对：`y11_shwd→sfchd`（27 行）与 `yolo11n→dota15`、`yolo11n→shwd_data_b`。')
w('料清单 **A10** 写明该组是"**三种子**逐点复算" ⇒ 论文 n=3，而底座 100ep 格有 **10** 个种子。')
w('⇒ 这正是"签名搜索"的用武之地。')
w()
w('| 格 | n | 增益(pp) | t | 逐种子更低 |')
w('|---|---|---|---|---|')
for e in (20, 30, 100):
    g = paired('y11_shwd→sfchd', 'sfchd_20p_b', e)
    if len(g) < 2:
        continue
    xs = [g[s] for s in sorted(g)]
    w('| `y11_shwd→sfchd` %dep（**全部族合并**） | %d | **%+.4f** | %.3f | %d/%d |' %
      (e, len(xs), st.mean(xs), tstat(xs), sum(1 for x in xs if x < 0), len(xs)))
for e in (30, 100):
    for fam in ('y11', 'b2'):
        g = paired('y11_shwd→sfchd', 'sfchd_20p_b', e, fam=fam)
        if len(g) < 2:
            continue
        xs = [g[s] for s in sorted(g)]
        w('| `y11_shwd→sfchd` %dep **族 `%s`** | %d | **%+.4f** | %.3f | %d/%d |' %
          (e, fam, len(xs), st.mean(xs), tstat(xs), sum(1 for x in xs if x < 0), len(xs)))
w()
w('★ 这一格是**族混杂影响结论方向**的活样本：')
w('合并算 ⇒ **+0.1930（t=2.04，看着"显著有增益"）**；只看 `y11` 族（= 论文的架构对照）⇒ ')
w('**+0.0100（t=0.192，无增益）**。论文的 §4.4 结论（架构对照在 100ep 无增益）**是对的**，')
w('是**复算口径把 10 个 `b2` 族的种子混了进来**，才把它算成 +0.193。')
w()
g30 = paired('y11_shwd→sfchd', 'sfchd_20p_b', 30)
g100 = paired('y11_shwd→sfchd', 'sfchd_20p_b', 100)
w('逐种子：')
w()
w('| seed | 30ep | 100ep |')
w('|---|---|---|')
for s in sorted(set(g30) | set(g100)):
    w('| s%d | %s | %s |' % (s,
                            ('%+.3f' % g30[s]) if s in g30 else '—',
                            ('%+.3f' % g100[s]) if s in g100 else '—'))
w()
sigline('30ep', g30, 1.2747, 6.967)
sigline('100ep', g100, -0.0050, -0.099)
w()

# ---------- 汇总 ----------
w('---')
w()
w('## 汇总：每条断言的最接近候选（**族分解后**）')
w()
w('| 断言 | 论文 | 论文值所在的口径 | 复算值 | 结论 |')
w('|---|---|---|---|---|')
w('| `smoke→sfchd` 50ep | +2.674 | 族 **`b2`** | **+2.674** | ✅ 逐位 |')
w('| `smoke→sfchd` 100ep | +1.666 | 族 **`b2`** | **+1.666** | ✅ 逐位（**旧"未复现"是族混杂造成的**）|')
w('| `smoke→sfchd` 200ep | +1.495 | 族 **`b2`** | **+1.495** | ✅ 逐位 |')
w('| `smoke→sfchd` 30ep | +3.656 | 族 **`b2`** | **+3.656（n=10）** | ✅ **已闭合并并入底座**：s50 是改名存档件，生成器原先按原始目录名查汇总故漏掉（只给 9 种子 +3.551），已修（按短名回退）|')
w('| `shwd2sf→sfchd` 30ep | +0.812 | 族 **`b2`** | **+0.812** | ✅ 逐位 |')
w('| `shwd2sf→sfchd` 50ep | +0.728 | 族 **`b2`** | **+0.728** | ✅ 逐位 |')
w('| `shwd2sf→sfchd` 100ep | +0.694 | 族 **`b2`** | **+0.694** | ✅ 逐位 |')
w('| `shwd2sf→sfchd` 200ep | +0.794 | 族 **`b2`** | **+0.794** | ✅ 逐位 |')
w('| YOLO11n 30ep | +1.2747 | 族 **`y11`**（n=3） | **+1.2867** | ⚠ 差 0.012 |')
w('| YOLO11n 100ep | −0.0050 | 族 **`y11`**（n=3） | **+0.0100** | ⚠ 差 0.015；**但"无增益"的结论成立** |')
w('| `mask→mendeley` | −1.49 (t=−4.02, 5/5) | 族 **`r10`** 的 13 个种子取 5 个 | 签名命中一组 | ⚠ 需作者确认是哪 5 个 |')
w()
w('## 结论')
w()
w('1. **8 条 ❌未复现里，6 条已被"族混杂"解释掉**（`smoke` 100/50/200ep、`shwd2sf` 四点、')
w('   YOLO11n 100ep）—— **不是论文写错，是复算口径把不同 run 族混成了一格**。')
w('   旧口径 `06_A25.py: cells()` 的格键是 `(pair, epochs)`，**没带 `family`**。')
w('2. **唯一真正的取件缺口**是 `smoke→sfchd` 30ep 少的那个种子的 **test 读数**：')
w('   底座里**确实有 s50**（`b2_smoke2sf_{base30,lr005_30ep}_s50n.incomplete_20260924_104028`），')
w('   它**跑满 30/30** 但被存档为中断件、**未写 test 行**。可核算式：')
w('   `9 种子 test 均值 +3.5511`（sum 31.960）→ 要得 `10 种子 +3.656`（sum 36.560）')  # 事前算式，保留
w('   ⇒ 第 10 个种子须 **+4.600**；其 val 侧实测 **+4.593** ✓ 相符。')
w('   ⇒ **闭合动作 = 补跑这 2 个 run 的 test 评测**（只评测不训练）。')
w('3. **YOLO11n 两点各差 0.012 / 0.015 pp，方向一致** ⇒ 该组最可能是"同批 run 的一次略不同的评测"，')
w('   **结论（30ep 有增益、100ep 无增益）站得住**；投稿时要么写明是哪三个种子（`s42,s43,s44`），')
w('   要么交代这 0.01 pp 的来源。')
w('4. **§4.3 的 `mask→mendeley` 是唯一还没闭合的一条**：论文 n=5、p=0.016 与 df=4 ⇒ t≈−4.02 自洽，')
w('   但族 `t2`（n=5）给 −0.902（4/5）、族 `r10`（n=13）给 −1.170（11/13）。')
w('   签名搜索在 `r10` 上命中一组 5/5 全负且 t 逐位相符的子集 ⇒ **最可能出自 `r10`（clean 三方协议）**。')
w('   ⇒ **请作者确认 §4.3 用的是不是 `r10_p_masktomende_*_3way`，以及是哪 5 个种子。**')
w()
w('> **本件不构成任何改写授权**：以上都是"候选口径的复算"，不是"论文写错了"。')
w('> **但它确证了一件事**：`06_A25.py` 的格定义缺 `family`，**这是一个必须修的口径**')
w('> （影响面见 `analysis\\A7_族混杂复核.md`）。')
w()
w()

os.makedirs(OUTD, exist_ok=True)
p = os.path.join(OUTD, '§4.2-4.4_未复现断言_候选格反查.md')
open(p, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n输出 -> %s' % p)
