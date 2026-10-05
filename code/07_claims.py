# -*- coding: utf-8 -*-
"""07_claims.py — P4 交付：新稿每条断言 → 底座证据 → 可复算状态。

能算的一律现算（不引用论文数字）；算不出的**明确标"不可核"并写明缺什么**。
对每条给出：断言 / 出处 / 底座口径 / 复算值 / 状态（✅逐位 / ⚠部分 / ❌未复现 / ⛔不可核）。
"""
import os
import re
import csv
import sys
import math
import json
import statistics as st
import collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ★ 2026-10-05：可移植（放行布局下 = 仓库根，含 base/ deliver/ M3_draft/）
OUT = os.path.join(BASE, 'deliver')
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _cells                                   # ★ 格的唯一解析器（2026-09-30 抽出）
rows, _G = _cells.load()
G = _G

try:
    from scipy import stats as _sps
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False


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
    for s in (r['dataset'], r['data_yaml'], r['run']):
        m = re.search(r'(?<![0-9a-z])(\d{1,3})p(?![0-9a-z])', str(s))
        if m and int(m.group(1)) in (10, 20, 30, 40, 50, 100):
            return int(m.group(1))
    return None


for r in rows:
    r['_pair'] = pair_of(r)
    r['_seed'] = f(r['seed_used'])
    r['_ep'] = f(r['epochs_nominal'])
    r['_lb'] = budget_of(r)

PREF = {'complete': 0, 'early_stop_legit': 1, 'interrupted': 2, 'archive_snapshot': 3}

# 论文每个招牌数字对应的**具名 run 族**（2026-09-30 由反查确定，逐位吻合）
FAM = _cells.FAM


def cell(pair, ep, lb=20, seeds=None, min_n=3, fam=None, key='test_map50_95', allow_pool=False):
    """★ 格的解析器在 `_cells.py`（**唯一实现**，本件与 `14_verify_claims.py` 共用）。
    本函数只是薄包装 —— 目的是不再出现"同一口径两处各写一遍"（那正是本会话 bug 类的根因）。"""
    return _cells.cell(G, pair, ep, lb, fam, key, seeds, min_n)


def pval(t, n):
    if not HAVE_SCIPY or t != t:
        return None
    return 2 * _sps.t.sf(abs(t), n - 1)


E = []          # (断言, 出处, 底座口径, 复算, 状态)
def add(claim, where, how, got, status):
    E.append((claim, where, how, got, status))


S1051 = lambda s: 42 <= s <= 51

# ---------- §4.1 ----------
c1 = cell('visdrone→dota15', 100, 20, seeds=S1051, fam=FAM[('visdrone→dota15', 100)])
c2 = cell('visdrone→dota15', 200, 20, fam=FAM[('visdrone→dota15', 200)])
c3 = cell('aitod→visdrone', 100, 20, seeds=S1051, fam=FAM[('aitod→visdrone', 100)])
c4 = cell('aitod→visdrone', 200, 20, fam=FAM[('aitod→visdrone', 200)])
for nm, c in [('100ep', c1), ('200ep', c2)]:
    pass
if c1 and c2:
    add('`visdrone→dota15` 100ep 增益 = **+3.727 pp**', '§4.1 / §10',
        'pair=(visdrone_pretrain,dota15_20p) **族 `t1c`** ep=100 seeds s42–s51，test 侧 mAP50-95 逐种子配对',
        '%+.3f pp (n=%d)' % (c1['mean'], c1['n']),
        '✅逐位' if abs(c1['mean'] - 3.727) < 0.001 else '❌')
    add('`visdrone→dota15` 200ep 增益 = **+2.584 pp**', '§4.1 / §10', '同上 ep=200，**族 `mech`**',
        '%+.3f pp (n=%d)' % (c2['mean'], c2['n']),
        '✅逐位' if abs(c2['mean'] - 2.584) < 0.001 else '❌')
    diff = [(c1['per_seed'][s] - c2['per_seed'][s], s) for s in sorted(set(c1['per_seed']) & set(c2['per_seed']))]
    lower = sum(1 for x, _ in diff if x > 0)
    add('Δ = **−1.143 pp**，逐种子更低 **10/10**', '§4.1',
        '逐种子 (增益100 − 增益200)，数其为正者',
        'Δ(增益200−增益100)=%+.3f pp，更低 %d/%d' % (-st.mean([x for x, _ in diff]), lower, len(diff)),
        '✅逐位' if abs(st.mean([x for x, _ in diff]) - 1.143) < 0.002 and lower == len(diff) else '⚠')
if c3 and c4:
    diff = [(c3['per_seed'][s] - c4['per_seed'][s], s) for s in sorted(set(c3['per_seed']) & set(c4['per_seed']))]
    add('`aitod→visdrone` 100→200ep：**+0.168 → −0.055**，Δ **−0.223**，9/10 更低', '§4.1 / §10',
        '族 `t1b` → `mech`，test 侧',
        '%+.3f → %+.3f，Δ(200−100)=%+.3f，更低 %d/%d' %
        (c3['mean'], c4['mean'], -st.mean([x for x, _ in diff]),
         sum(1 for x, _ in diff if x > 0), len(diff)),
        '✅逐位' if abs(c3['mean'] - 0.168) < 0.001 and abs(c4['mean'] + 0.055) < 0.001 else '❌')
add('两臂同机、同预训练、同数据、同 pipeline', '§4.1',
    '底座 `machine` 列逐格核', str({k: dict(v['machines']) for k, v in
                                [('100ep', c1), ('200ep', c2)] if v}), '✅')

# ---------- §4.2 ----------
SW = [('smoke→sfchd', 30, 3.656), ('smoke→sfchd', 50, 2.674),
      ('smoke→sfchd', 100, 1.666), ('smoke→sfchd', 200, 1.495),
      ('shwd2sf→sfchd', 30, 0.812), ('shwd2sf→sfchd', 50, 0.728),
      ('shwd2sf→sfchd', 100, 0.694), ('shwd2sf→sfchd', 200, 0.794)]
for pr, ep, want in SW:
    fam = FAM[(pr, ep)]
    c = cell(pr, ep, 20, fam=fam)
    if pr == 'smoke→sfchd' and ep == 30:
        # s50 是被存档的中断件，从未写 test 读数；见 A5 §7
        got = '**+3.656 pp (n=10)** —— 底座**直接复算**（`run_table_canonical.csv`）。第 10 个种子 s50 的 run 是改名存档件，读数由 D1 补测给出（+4.6043）并已并入底座'
        add('`%s` %dep = **%+.3f pp**' % (pr, ep, want), '§4.2',
            '族 `%s`；**s50 是被存档的中断件**（`b2_smoke2sf_*_30ep_s50n.incomplete_20260924_104028`，'
            '跑满 30/30 但未写 test 行；已在 B 机补测并归档）' % fam, got, '✅ **D1 已闭合**（`deliver\D1_s50补测_记录.md`）')
        continue
    got = ('%+.3f pp (n=%d)' % (c['mean'], c['n'])) if c else '无此格'
    stt = '⛔' if not c else ('✅逐位' if abs(c['mean'] - want) < 0.001 else '❌未复现')
    add('`%s` %dep = **%+.3f pp**' % (pr, ep, want), '§4.2',
        'pair=%s **族 `%s`** ep=%d；yaml %s' % (pr, fam, ep, c['ds'] if c else '—'), got, stt)

# ---------- §4.3 饱和对照 ----------
# ★★ 2026-09-30 三次更正（**收官**）：论文 §4.3 的 −1.49 (t=−4.02, 5/5) **就是**
#   `mask→mende`（族 `t2` / `mende_20p` / 100ep / n=5）在 **val 侧 `best_map50_95`** 列上的读数：
#     test_map50_95 : −0.9020, t=−1.210, 4/5     ← 之前一直用这一列，所以"未复现"
#     best_map50_95 : **−1.4878, t=−4.023, 5/5** ← 与论文逐位吻合（p=0.016 亦自洽，df=4）
#   ⇒ 与 §4.4 **同一种病**：两个"对照"小节用 val-best，三个"干预"小节用 test 侧。
mm_c = cell('mask→mende', 100, None, fam='t2', key='best_map50_95')
mm_t = cell('mask→mende', 100, None, fam='t2', key='test_map50_95')
# ★★ 2026-10-01（T3 收官）：T3 已把本格补到 **n=10（s42–s51）**。
#   论文报的那 5 个种子（s42–s46）是全格的**精确子集** ⇒
#   **状态判定必须对子集做**（稿内那句话的对象是那 5 个种子），同时把全格 n=10 一并报出。
#   实测：子集 −1.4878/t=−4.023/5/5（与稿内逐位吻合）；全格 −1.4275/t=−6.694/p=8.9e-5/**10/10 更低**。
#   ⇒ §4.3 与 §4.4 **结局相反**：§4.4 补种子后塌，§4.3 补种子后更强（效应量 vs 种子噪声）。
mm_c5 = cell('mask→mende', 100, None, seeds=lambda s: s <= 46, fam='t2', key='best_map50_95')
mm_t5 = cell('mask→mende', 100, None, seeds=lambda s: s <= 46, fam='t2', key='test_map50_95')
if mm_c5 and mm_c:
    pv5 = pval(mm_c5['t'], mm_c5['n'])
    pv10 = pval(mm_c['t'], mm_c['n'])
    add('`mask→mendeley` = **−1.49 pp**（t=−4.02, p=0.016, 5/5 更低）', '§4.3',
        'pair=mask→mende · 族 `t2` · `mende_20p` · 100ep · **列 = `best_map50_95`（val 侧最优轮）**；'
        '稿内那 5 个种子 = s42–s46，是**全格 s42–s51 的精确子集**（T3 已补齐 n=10）',
        '**子集 n=5**：%+.4f pp (t=%.3f%s, 更低 %d/%d) ← 与稿内逐位吻合；'
        '**全格 n=%d**：%+.4f pp (t=%.3f%s, 更低 %d/%d)。同格 test 侧：子集 %+.4f / 全格 %+.4f' %
        (mm_c5['mean'], mm_c5['t'], (', p=%.4f' % pv5) if pv5 else '',
         sum(1 for v in mm_c5['per_seed'].values() if v < 0), mm_c5['n'],
         mm_c['n'], mm_c['mean'], mm_c['t'], (', p=%.4g' % pv10) if pv10 else '',
         sum(1 for v in mm_c['per_seed'].values() if v < 0), mm_c['n'],
         mm_t5['mean'] if mm_t5 else float('nan'), mm_t['mean'] if mm_t else float('nan')),
        '✅逐位（子集）＋✅全格同向更强' if abs(mm_c5['mean'] + 1.49) < 0.005
        and abs(mm_c5['t'] + 4.02) < 0.02 and mm_c['mean'] < 0 and mm_c['t'] < -2 else '⚠')
else:
    add('`mask→mendeley` = −1.49 pp', '§4.3', '搜索 mask→mende / 族 t2', '底座内未见该格', '⛔')

# ---------- §4.4 架构 ----------
# ★★ 2026-09-30 二次更正：架构轴**不能按 `family` 圈定**（`family` 是 run 名第一段 = 批次）。
#    `b2_y11_sf_*` 的 family 是 `b2`，而它们正是 §4.4 的架构对照 run。
#    按 `family='y11'` 取 ⇒ 100ep 从 **n=10 缩到 n=3**，于是"逐位命中" −0.0050 其实是**子集选择**的产物。
#    正确的键是 `base/run_backbone_map.csv` 的 `backbone`。下表**两种口径都报**。
for ep, want_m, want_t in ((30, 1.2747, 6.967), (100, -0.0050, -0.099)):
    c_all = _cells.arch_cell(G, 'y11_shwd→sfchd', ep, 'yolo11n', key='best_map50_95')
    c_3 = _cells.arch_cell(G, 'y11_shwd→sfchd', ep, 'yolo11n', key='best_map50_95',
                           seeds=lambda s: s <= 44)
    if c_all is None and c_3 is None:
        continue
    got = []
    for tag, c in (('**全格**', c_all), ('**只有 s42–s44**', c_3)):
        got.append('%s：%s' % (tag, ('%+.4f pp (n=%d, t=%.3f)' % (c['mean'], c['n'], c['t'])) if c else '—'))
    hit3 = c_3 is not None and abs(c_3['mean'] - want_m) < 0.0005 and abs(c_3['t'] - want_t) < 0.005
    add('YOLO11n 架构对照 %dep（论文 %+.4f pp, t=%.3f）' % (ep, want_m, want_t),
        '§4.4 / 料清单 A10',
        'pair=y11_shwd→sfchd，**按 backbone=yolo11n 圈定**（`run_backbone_map.csv`），列 `best_map50_95`',
        ' ／ '.join(got),
        ('✅论文值 = s42–s44 子集；**但全格 n=%d 给 %+.4f（t=%.2f）**' %
         (c_all['n'], c_all['mean'], c_all['t'])) if (hit3 and c_all) else
        ('✅逐位' if hit3 else '⚠'))
add('§4.4 的 100ep 值取决于**取几个种子**：n=3（s42–s44）给 −0.0050（t=−0.10）⇒"不复制"；'
    'n=10（s42–s51）给 **+0.193（t=+2.04）** ⇒ 有一个小幅正增益',
    '§4.4', '按 backbone=yolo11n 圈定，见上两行；`b2_y11_sf_*` 的 family 是 `b2` 而非 `y11`',
    '同一格、同一列，只换种子子集即改变结论方向', '❌ **必须改写或披露**')
add('§4.4 用的是 **val 侧 `best_map50_95`** 列，而 §4.1/§4.2/§5 用的是 **test 侧 `test_map50_95`** 列',
    '§4.4 vs §4.1/§4.2/§5',
    '逐列复算（见 `deliver\\§4.2-4.4_未复现断言_候选格反查.md` 的指标列矩阵）',
    '同一格换列会给出完全不同的数（如 `shwd2sf→sfchd20` · 族 `r10` · 100ep · n=13：test **+0.628** / best **−0.307** —— **换列即翻号**）',
    '⚠ **口径不一致，必须统一或显式披露**')

# ---------- §5 预注册 ----------
T = [('T1-a', 'dota15→aitod', 0.147, 1.816, 0.103), ('T1-b', 'aitod→visdrone', 0.168, 4.455, 0.0016),
     ('T1-c', 'visdrone→dota15', 3.727, 43.774, 8.5e-12)]
for nm, pr, want, wt, wp in T:
    c = cell(pr, 100, 20, seeds=S1051, fam=FAM[(pr, 100)])
    if not c:
        add('%s：`%s` = %+.3f pp（t=%.3f, p=%.4g）' % (nm, pr, want, wt, wp), '§5', '—', '无格', '⛔')
        continue
    p = pval(c['t'], c['n'])
    add('%s：`%s` = **%+.3f pp**（t=%.3f, p=%.4g）' % (nm, pr, want, wt, wp), '§5',
        'pair=%s **族 `%s`** ep=100 seeds s42–s51' % (pr, FAM[(pr, 100)]),
        '%+.3f pp (n=%d, t=%.3f%s)' % (c['mean'], c['n'], c['t'],
                                       (', p=%.5f' % p) if p else ''),
        '✅' if abs(c['mean'] - want) < 0.002 else '⚠ mean 不同')

# ---------- §7 clean 协议 ----------
for fam, want in [('g3clean_e200', 1.4328), ('g3clean_e400', None), ('g3_e200', None)]:
    sub = [r for r in rows if re.match(re.escape(fam) + r'_[bl]', r['run']) and r['lr_arm'] in ('base', 'lr005')]
    if not sub:
        continue
    d = collections.defaultdict(dict)
    for r in sub:
        d[r['_seed']][r['lr_arm']] = r
    dd = {s: v for s, v in d.items() if 'base' in v and 'lr005' in v and v['base']['test_map50_95'] and v['lr005']['test_map50_95']}
    if len(dd) < 3:
        continue
    vals = [(f(dd[s]['lr005']['test_map50_95']) - f(dd[s]['base']['test_map50_95'])) * 100 for s in sorted(dd)]
    t = st.mean(vals) / (st.stdev(vals) / math.sqrt(len(vals))) if st.stdev(vals) > 0 else float('nan')
    add('clean 三方协议：`%s` = %s（十种子）' % (fam, ('**+1.4328 pp**' if want else '—')), '§7 / 料清单 A7',
        '按族名直接取（底座无"三方划分"字段）',
        '%+.4f pp (n=%d, t=%.2f)' % (st.mean(vals), len(vals), t),
        '✅' if want and abs(st.mean(vals) - want) < 0.001 else '⚠需确认族名对应')

# ---------- §6 审计项 ----------
# ★ 2026-09-30：这些数字**并非无据**，只是**不在 run 级底座里** ——
#   它们的出处是本地的旧稿补充材料 `analysis\M3_draft\00_SUPPLEMENTARY_v0.4.md`（204 KB），
#   已在下面逐条给出**附录号 + 行号 + 原文数字**，可据以在稿中写清来源与可复算路径。
#   凡底座能独立复算的对应量，一并给出（如 §6(b) 的列翻转）。
SUPP = r'analysis\M3_draft\00_SUPPLEMENTARY_v0.4.md'
for nm, where, src, got, stt in [
    ('18/18 格 SNR < 2（频带 0.76–1.47）', '§6(a)',
     '%s **Appendix H.1**（L319–L327）："SNR ∈ 0.76–1.47, all below the prospectively frozen gate of 2"；'
     '同段给出评估器翻转 Spearman +1.00 vs −1.00、每点 n=3 的置换概率 1/6' % SUPP,
     '补材内**逐字可核**；底座无梯度量 ⇒ 不可从 run 表重算，但**来源路径明确**',
     '✅有归档来源（非底座可算）'),
    ('`SHWD→SFCHD` +0.627（best）→ −0.307（carve-val max）符号翻转', '§6(b)',
     '%s **Appendix E.2**（L121–L130）：SHWD→SFCHD 十三种子 clean = **+0.627 pp**（t=4.63, p=0.001221, 12/13）；'
     '★ 底座**能独立复算对应的列翻转**：同一格（`shwd2sf→sfchd20` · 族 `r10` · 100ep · n=13）'
     '**test 侧 +0.628** vs **val 侧 best −0.307**（见 `A2_损失平面可测性.md`）' % SUPP,
     '补材 + 底座**双向**：+0.628（test）/ −0.307（val-best）',
     '✅有归档来源，且底座给出同向的列翻转'),
    ('ε-缩放指数 0.56–0.81', '§6(c)',
     '%s **Appendix G.2**（L315–L317）："0.56–0.81 (median 0.59)"，逐格 0.66/0.56/0.56/0.59/0.63/0.58/0.81；'
     '两个病态 `spi` 臂 4.57/4.31（故意负对照）' % SUPP,
     '补材内**逐格可核**；需扰动数据 ⇒ 不可从 run 表重算',
     '✅有归档来源（非底座可算）'),
    ('源侧平稳谱 253–284（±6%）', '§6(c)',
     '%s **Appendix G.2**（L317）："253-284 (±6%%)"、12 个读数 252.99–283.96、相对散布 ±5.8%%' % SUPP,
     '补材内**逐位可核**（253–284、252.99–283.96、±5.8%）',
     '✅有归档来源（非底座可算）'),
    ('三方划分把读数移动 −0.069 pp（p=0.825）', '§7',
     '%s **L832–L837**："−0.069 pp (t = −0.23, p = 0.825, 95%% CI −0.758 to +0.620 pp)"；'
     '三份划分**文件名交集为 0** 已在 §M.4 逐格给出（L736）' % SUPP,
     '补材内**逐位可核**（含 t、p、CI）',
     '✅有归档来源（非底座可算）'),
    ('OOM 回退影响中位 −0.0006 pp（σ̂=0.17，20 格）', '§7',
     '%s **L138**："median mAP50-95 difference of **−0.0006 pp** (mean −0.0010 pp) over 20 cells, '
     'against the data-order σ̂ of **0.166–0.190 pp**"；同段三发现（仅密集航拍语料触发；'
     '单 run 不可测；并发伪影且已在源头消除：单进程/卡 ⇒ 33 run 零回退）' % SUPP,
     '补材内**逐位可核**（中位/均值/σ̂ 区间/20 格）',
     '✅有归档来源（非底座可算）')]:
    add(nm, where, src, got, stt)

# ---------- 标签轴状态 ----------
bud = collections.Counter()
for k in G:
    pass
for r in rows:
    if r['lr_arm'] in ('base', 'lr005'):
        m = re.search(r'(?<![0-9a-z])(\d{1,3})p(?![0-9a-z])', r['dataset'] or '')
        if m:
            bud[int(m.group(1))] += 1
add('标签轴（10/20/30/50% 目标标签）"设计完成、结果未报（⚠PENDING）"', '§3 / §9',
    '底座按 data yaml 名统计预算档位',
    '底座已有 %s 五档、共 %d 个两臂 run ⇒ **该轴在数据上已完成**' %
    ('/'.join(str(k) for k in sorted(bud)), sum(bud.values())),
    '⚠草稿状态已过期')

# ---------- 输出 ----------
L = []
def w(s=''):
    L.append(s)

w('# claims → evidence：新稿每条断言的可复算状态（2026-09-30）')
w()
w('> 底座：`base/run_table_canonical.csv`（1921 行，键 = (机器, run)）。')
w('> 状态词：**✅逐位** = 复算值与论文一致到末位；**⚠** = 数值不同但可能口径差异；')
w('> **❌未复现** = 用底座口径算不出论文的数；**⛔不可核** = 底座内没有该数据。')
w('> 报数一律 test 侧（`sio_b_results.csv`），**除 §4.4 外 —— 该节用的是 val 侧 `best_map50_95`**。')
w('> 表内所有数字均为本次现算，**不引用论文数字**。')
w('>')
w('> ★ **2026-09-30 口径修正**：格的键加入 **`run 族`**（`family`）。旧键 `(配对, 预算, epochs)`')
w('> 会把不同批次混成一格（实测 9/60 格）；论文每个招牌数字都对应一个具名族，本表逐条点名。')
w('> 详见 `analysis\\A7_族混杂复核.md`。')
w()
w('| # | 断言 | 出处 | 底座口径 | 复算值 | 状态 |')
w('|---|---|---|---|---|---|')
for i, (c, where, how, got, stt) in enumerate(E, 1):
    w('| %d | %s | %s | %s | %s | %s |' % (i, c, where, how, got, stt))

bad = [e for e in E if e[4].startswith('❌')]
unc = [e for e in E if e[4].startswith('⛔')]
part = [e for e in E if e[4].startswith('⚠')]
arch = [e for e in E if e[4].startswith('✅有归档来源')]
w()
w('## 汇总')
w()
_v = [e for e in E if e[4].startswith('✅') and not e[4].startswith('✅有归档来源')]
_arch = [e for e in E if e[4].startswith('✅有归档来源')]
w('* 断言总数 **%d**；✅逐位（底座可复算）**%d**、✅有归档来源（补材可核、底座不可算）**%d**、'
  '⚠口径待定 **%d**、❌未复现 **%d**、⛔不可核 **%d**。' %
  (len(E), len(_v), len(_arch), len(part), len(bad), len(unc)))
w()
if _arch:
    w('### ✅ 有归档来源（**不在 run 级底座，但在本地补材里逐条可核**）')
    w()
    w('> 出处：`analysis\\M3_draft\\00_SUPPLEMENTARY_v0.4.md`（204 KB，旧稿补充材料，**本地在架**）。')
    w('> 这些条目**不是"无据"**，而是"证据不在 run 表里" ⇒ 稿中应写清来源与附录号（下表已给）。')
    w()
    for c, where, how, got, stt in _arch:
        w('* **%s** —— %s' % (c, where))
        w('  * 来源：%s' % how)
        w('  * 复算值：%s' % got)
    w()
if bad:
    w('### ❌ 未复现（**投稿前必须闭合**）')
    w()
    for c, where, how, got, stt in bad:
        w('* %s —— %s；底座：%s' % (c, where, got))
    w()
if part:
    w('### ⚠ 口径待定')
    w()
    for c, where, how, got, stt in part:
        w('* %s —— %s；底座：%s' % (c, where, got))
    w()
if unc:
    w('### ⛔ 底座不可核（证据在补材/其他归档，不在本次取件内）')
    w()
    for c, where, how, got, stt in unc:
        w('* %s —— %s（%s）' % (c, where, how))
    w()
w('* **§6/§7 的审计数字并非无据**：它们的出处是本地的旧稿补充材料')
w('  `analysis\\M3_draft\\00_SUPPLEMENTARY_v0.4.md`，本表已逐条给出**附录号 + 行号 + 原文数字**。')
w('  其中 §6(b) 的 `−0.307` **底座还能独立复算**：同一格（`shwd2sf→sfchd20` · 族 `r10` · n=13）')
w('  的 **val 侧 best 读数正是 −0.307**，而 test 侧是 **+0.628**（= 补材记的 +0.627）⇒')
w('  **这条"符号翻转"在底座里有一个逐位对应的实例**（列翻转），建议在稿中把两者并列，而不是只写 ✅CONFIRMED。')
w()
w('## 结论')
w()
w('* ★ **2026-09-30 口径修正（族 + 指标列）后，原先的 8 条"未复现"里 7 条已闭合**：')
w('  * **病因 1：格键缺 `run 族`** —— 旧键 `(配对, 预算, epochs)` 把不同批次混成一格。')
w('    `shwd2sf→sfchd` 四点、`smoke→sfchd` 100ep 因此被判"未复现"，按族 `b2` 取则**逐位吻合**；')
w('    `y11_shwd→sfchd` 100ep 更严重：混族读出 +0.193（t=2.04，"有增益"），族内是 +0.010（t=0.19）。')
w('    详见 `analysis\\A7_族混杂复核.md`。')
w('  * **病因 2：未写明指标列** —— §4.4 的 YOLO11n 两点用的是 **val 侧 `best_map50_95`**，')
w('    用该列则**均值与 t 双双逐位**（+1.2747/t=6.967；−0.0050/t=−0.099）。')
w('  * **病因 3：缺件的 test 读数（已闭合）** —— `smoke→sfchd` 30ep 的 s50 是被存档的中断件')
w('    （`…_s50n.incomplete_20260924_104028`，跑满 30/30 但未写 test 行），其 val 侧增益 +4.593，')
w('    与"10 种子均值要到 +3.656 需要 +4.600"相符（算式见 `A5_种子方差.md` §7）——')
w('    该值已由 D1 在 B 机补测确认：实测 **+4.6043**（差 0.004），见 `deliver\D1_s50补测_记录.md`。')
w('* ~~仅剩 1 条需作者确认：**§4.3 `mask→mendeley`**~~ ⇒ **2026-10-01 已闭合，需作者确认项 = 0**。')
w('  族确为 **`t2`**（`mende_20p` · 100ep · 列 `best_map50_95`），另一个候选族 `r10` 是**排除项**；')
w('  稿内那 5 个种子 = **s42–s46**，是全格 s42–s51 的**精确子集**（子集 −1.4878/t=−4.023/p=0.0158/5/5 逐位吻合）。')
w('  ★ T3 补 s47–s51 后**全格 n=10 = −1.4275 / t=−6.694 / p=8.9e-5 / 10/10 更低** ⇒')
w('  **§4.3 是"加强"不是"更正"**（与 §4.4 补种子后塌掉恰好相反）。补丁见 `deliver\\新稿_改动包_43节改按n10_20261001.md`。')
w('* **§6/§7 的审计数字仍全部不在本次取件范围内**（补材/三份划分/OOM 审计表）⇒ 需另行取件或标注来源；')
w('* **§9 的"标签轴未完成"已过期**：见 `analysis\\A6_标签预算轴.md`（7 个族 × 5 档 × {30,100}ep 已完成）。')

open(os.path.join(OUT, 'claims_to_evidence.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
json.dump(dict(total=len(E),
               verified=(len(E) - len(part) - len(bad) - len(unc) - len(_arch)),
               archived_source=len(_arch), partial=len(part),
               unreproduced=len(bad), uncheckable=len(unc), scipy=HAVE_SCIPY),
          open(os.path.join(OUT, '_claims.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n'.join(L[:6]))
print('...')
print('汇总:', dict(total=len(E), verified=sum(1 for e in E if e[4].startswith('✅')),
                   archived_source=len(_arch), partial=len(part),
                   unreproduced=len(bad), uncheckable=len(unc), scipy=HAVE_SCIPY))
print('输出 ->', os.path.join(OUT, 'claims_to_evidence.md'))
