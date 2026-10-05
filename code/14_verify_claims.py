# -*- coding: utf-8 -*-
"""14_verify_claims.py —— **稿-底座一致性守卫**（只读；不做写后断言）。

用法：
    python scripts/14_verify_claims.py              # 跑全部断言，失败即非零退出
    python scripts/14_verify_claims.py --self-test  # ★ 阴性对照：故意改坏一条，守卫**必须**报红

设计依据（`E:\\workplace\\通用经验与教训`）：
  · **#6 / #20**：每个跨文件重复的数字都要有守卫；**只盯总数不够，必须逐条盯分项** ——
    所以本件**逐条**断言，而不是只比"通过几条"。
  · **#75**：新写的检查必须现场做一次**阴性对照** —— 所以内置 `--self-test`。
  · **#56**：**空集合必须硬失败** —— 格解析不到、种子数为 0、族不唯一，都是 FAIL 而不是 PASS。
  · **#23**：核对用**只读**脚本断言目标状态；本件**不写任何文件**。
  · **#42**：凡是记录里的"已完成 X"，X 必须有一个**可执行**的检查 —— 本件就是那个检查。

口径由 `_cells.py` 提供（**格的唯一解析器**）。
"""
import math
import os
import re
import statistics as _st
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import _cells as C            # noqa: E402

TOL_MEAN = 0.0005            # 均值容差（pp）
TOL_T = 0.005                # t 容差
TOL_X = 0.01                 # 对撞容差（pp）：canonical 只存 4 位小数 ⇒ 允许 0.01 pp 级舍入差
S1051 = lambda s: 42 <= s <= 51      # 论文的"十个配对种子"= s42–s51



# ★ 必须与生成器 `norm()` 的 `_s(\d+)(n?)$` **同口径**（锚定结尾）：
#   用 `search` 取首个匹配会与生成器不一致 —— 阴性对照当场暴露过这一点。
_SEEDPAT = re.compile(r'_s(\d+)(n?)$')
# ★ 2026-10-01：`_oomfix` / `_REPB` / `_PARTIAL_<数字>` / `_OOMKILLED_<数字>` 这类**后缀件**
#   会让 `norm()` 的 `_s(\d+)(n?)$` 匹配失败（名字不以种子结尾）⇒ `seed_used` 回落到 `args.seed`=42
#   ⇒ **实际是 s43/s45/s47 的 run 被当成 s42**。若它被 `_pick` 选中，就会与 s42 的另一臂
#   **配对出一个不存在的比较**。本两条断言把它钉住（当前实测：0 次选中、0 个危险格）。
def _implied_seed(run):
    m = _SEEDPAT.search(run)
    return int(m.group(1)) if m else None


def _seedname_scan(G):
    """返回 (被 _pick 选中的"种子名不符"行数, 检查过的 (格,种子,臂,列) 组合数, 危险格数)。"""
    picked = combos = danger = 0
    for k, seeds in G.items():
        for s, arms in seeds.items():
            for arm, rs in arms.items():
                cand = [r for r in rs if (r.get('test_map50_95') or '').strip()]
                if cand and all((_implied_seed(r['run']) not in (None, int(s))) for r in cand):
                    danger += 1
                for key in ('test_map50_95', 'best_map50_95'):
                    r = C._pick(rs, key)
                    if r is None:
                        continue
                    combos += 1
                    imp = _implied_seed(r['run'])
                    used = C.f(r['seed_used'])
                    if imp is not None and used is not None and imp != int(used):
                        picked += 1
    return picked, combos, danger


def _seedname_conflict(G):
    """断言 ①：`_pick` **从不**选中种子名与实际种子不符的行。want = 0。"""
    picked, combos, _ = _seedname_scan(G)
    return dict(mean=float(picked), t=0.0, n=max(combos, 1), per_seed={0: float(picked)},
                fam='seedname', key='test_map50_95')


def _seedname_danger(G):
    """断言 ②：不存在"某 (格,种子,臂) 的候选**全部**种子名不符"的格。want = 0。"""
    _, combos, danger = _seedname_scan(G)
    return dict(mean=float(danger), t=0.0, n=max(combos, 1), per_seed={0: float(danger)},
                fam='seedname', key='test_map50_95')


def _d1_s50():
    """读**归档的 s50 补测读数**（`base\\p1d1_s50_test_readings.csv`），返回 (seed=50, 增益 pp)。

    D1：`smoke→sfchd` 30ep 的 s50 两臂跑满 30/30 但被改名存档为中断件，未写自己的 test 行，
    其读数由一次事后补测给出。**该读数自 2026-10-01 起已在 `run_table_canonical.csv` 内**
    （生成器改成按短名回退查汇总），所以本函数**不再**用于构造 §4.2 的值，
    而是作为**独立第二来源**去和底座对撞（见 `4.2-smoke-30-xcheck`）。
    """
    import csv as _csv
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'base', 'p1d1_s50_test_readings.csv')
    got = {}
    with open(p, newline='', encoding='utf-8') as fh:
        for row in _csv.reader(fh):
            if not row or row[0].startswith('#') or row[0].strip().lower() == 'name':
                continue
            nm = row[0]
            arm = 'base' if 'base30' in nm else ('lr005' if 'lr005' in nm else None)
            if arm:
                # 列序与 `sio_b_results.csv` 一致：name,loss,epochs,map50,map,mp,mr
                # ★ 本件用**百分数**（38.0560），canonical 用**小数**（0.3806）⇒ 须 /100
                got[arm] = float(row[4]) / 100.0
    if len(got) != 2:
        return None
    return 50, got['lr005'] - got['base']


def _xcheck_s50(G):
    """对撞：D1 归档件的 s50 增益 与 canonical 该 run 的 test 读数，是否一致。

    **两条独立路径**：D1 是补测当日单独写出的 CSV（百分数、全精度）；
    canonical 来自 B 侧 `sio_b_results.csv`（小数、**只存 4 位**）。
    期望差应为 0（4 位精度下），不一致即 FAIL；空集合也 FAIL（遵经验 #56）。
    """
    d = _d1_s50()
    if d is None:
        return None
    seed, g_d1 = d
    k = ('smoke→sfchd', 'b2', 20, 30)
    arms = G.get(k, {}).get(seed)
    if not arms:
        return None
    lr = C._pick(arms.get('lr005', []), 'test_map50_95')
    ba = C._pick(arms.get('base', []), 'test_map50_95')
    if lr is None or ba is None:
        return None
    g_can = (float(lr['test_map50_95']) - float(ba['test_map50_95'])) * 100.0   # pp
    g_d1 = g_d1 * 100.0                                                        # pp
    return dict(mean=g_can - g_d1, t=0.0, n=2, per_seed={seed: g_can - g_d1},
                fam='b2(对撞 D1)', key='test_map50_95')


def _pairdiff_d1(G, pair, lb, fam, key='test_map50_95'):
    """§4.2 的 **10 种子配对端点差** 30→200ep（第 10 个种子的读数已在 canonical 内）。"""
    return _pairdiff(G, pair, 30, 200, lb, fam, key=key)


def _pairdiff(G, pair, epA, epB, lb, fam, key='test_map50_95'):
    """**逐种子配对**的端点差 `epB − epA`（Δ = 长预算 − 短预算）。

    只取两格都有读数的种子；返回与 `_cells.cell` 同形的 dict，供断言器直接消费。
    这是 §4.2 端点差的唯一口径 —— 不做"均值相减"，因为两点种子集不同。
    """
    import math
    import statistics as st
    a = C.cell(G, pair, epA, lb, fam, key=key)
    b = C.cell(G, pair, epB, lb, fam, key=key)
    if not a or not b or 'mean' not in a or 'mean' not in b:
        return None
    sa, sb = a['per_seed'], b['per_seed']
    common = sorted(set(sa) & set(sb))
    if len(common) < 3:
        return None
    d = [sb[s] - sa[s] for s in common]
    m = st.mean(d)
    sd = st.stdev(d)
    t = m / (sd / math.sqrt(len(d))) if sd > 0 else float('inf')
    return dict(mean=m, t=t, n=len(d), per_seed={s: sb[s] - sa[s] for s in common},
                fam='%s/%d→%d' % (fam, epA, epB), key=key)


def build_checks():
    """返回 [(id, 描述, 出处, 期望, 解析函数)]。

    每条**只断言一个分项**（#20）。`期望` 是 None 表示"只断言能解析到且 n 达标"。
    """
    K = C.FAM
    chk = []

    def add(cid, desc, where, want, fn, kind='mean', min_n=3):
        # `min_n` 默认 3（空/退化格必须硬失败，经验 #56）；**对撞类**只有 2 个来源，
        # 允许显式下调 —— 下调必须逐条写明理由，不得为了让检查通过而调。
        chk.append(dict(id=cid, desc=desc, where=where, want=want, fn=fn, kind=kind, min_n=min_n))

    # ---------- §4.1 ----------
    add('4.1-a', '`visdrone→dota15` 100ep 增益', '§4.1/§10', 3.727,
        lambda S: C.cell(S, 'visdrone→dota15', 100, 20, K[('visdrone→dota15', 100)], seeds=S1051))
    add('4.1-b', '`visdrone→dota15` 200ep 增益', '§4.1/§10', 2.584,
        lambda S: C.cell(S, 'visdrone→dota15', 200, 20, K[('visdrone→dota15', 200)]))
    add('4.1-c', '`aitod→visdrone` 100ep 增益', '§4.1/§10', 0.168,
        lambda S: C.cell(S, 'aitod→visdrone', 100, 20, K[('aitod→visdrone', 100)], seeds=S1051))
    add('4.1-d', '`aitod→visdrone` 200ep 增益', '§4.1/§10', -0.055,
        lambda S: C.cell(S, 'aitod→visdrone', 200, 20, K[('aitod→visdrone', 200)]))

    # ---------- §4.2：族 b2，四点扫描（test 列 `test_map50_95`）----------
    # ★ 2026-10-01：30ep 与端点差走 **10 种子**口径。第 10 个种子（s50）的 run 是
    #   **改名存档件**（`.incomplete_*`，跑满 30/30），其 test 读数原被生成器漏掉 ——
    #   生成器按**原始目录名**查汇总，而汇总记的是**短名**，于是改名件恒查不到。
    #   已修 `01_build_base.py`（按短名回退、**只认同机**）⇒ 该读数现在 canonical 内，
    #   下面三条因此**直接读 canonical**，不再需要任何特判。
    #   全域影响已实测：所有格中**只有这一格**变化（n 9→10）。
    add('4.2-smoke-30', '`smoke→sfchd` 30ep 增益（test 列，10 种子）', '§4.2', 3.6564,
        lambda S: C.cell(S, 'smoke→sfchd', 30, 20, 'b2'))
    for ep, want in ((50, 2.674), (100, 1.666), (200, 1.495)):
        add('4.2-smoke-%d' % ep, '`smoke→sfchd` %dep 增益' % ep, '§4.2', want,
            (lambda e: lambda S: C.cell(S, 'smoke→sfchd', e, 20, 'b2'))(ep))
    add('4.2-smoke-endpoint', '`smoke→sfchd` 30→200ep 端点差（10 种子配对）', '§4.2', -2.1614,
        lambda S: _pairdiff_d1(S, 'smoke→sfchd', 20, 'b2'))
    add('4.2-smoke-endpoint-t', '`smoke→sfchd` 30→200ep 端点差的 t（10 种子）', '§4.2', -17.518,
        lambda S: _pairdiff_d1(S, 'smoke→sfchd', 20, 'b2'), kind='t')
    # ★ 对撞：D1 归档件 与 canonical 必须是**同一个读数**（两条独立路径，期望差 = 0）
    add('4.2-smoke-30-xcheck', 'D1 归档件 与 canonical 的 s50 逐种子增益对撞（期望差 0 pp）', '§4.2', 0.0,
        lambda S: _xcheck_s50(S), kind='xcheck', min_n=2)
    for ep, want in ((30, 0.812), (50, 0.728), (100, 0.694), (200, 0.794)):
        add('4.2-shwd2sf-%d' % ep, '`shwd2sf→sfchd` %dep 增益' % ep, '§4.2', want,
            (lambda e: lambda S: C.cell(S, 'shwd2sf→sfchd', e, 20, 'b2'))(ep))

    # ---------- §4.4：**按 backbone=yolo11n 圈定** + **val 侧** `best_map50_95` ----------
    # ★ 2026-10-01：口径已裁定为**全格 n=10**（选项 1）。旧值 1.2747 / −0.0050 是
    #   s42–s44 三种子子集，**不再作为期望值**（见 deliver/新稿_改动包_选项1_20260930.md）。
    # ★★ 2026-10-02：下面两条是**按 backbone 分格**的读数 —— 它把**两个批次**
    #   （族 `y11` 与族 `b2`）的种子**合并**成 n=10。字典 §十.1 要求跨族合并**必须显式声明**，
    #   所以标签里写明；并把**单批次**的两个读数也一并注册（下两条），
    #   否则读者会以为 +0.1922 是某一批的值（实测：`b2` 批 +0.32、`y11` 批 −0.005）。
    add('4.4-30-mean', 'YOLO11n 30ep 增益（按 backbone 分格，n=10）', '§4.4', 1.0958,
        lambda S: C.arch_cell(S, 'y11_shwd→sfchd', 30, 'yolo11n', key='best_map50_95'))
    add('4.4-30-t', 'YOLO11n 30ep 的 t（n=10）', '§4.4', 9.437,
        lambda S: C.arch_cell(S, 'y11_shwd→sfchd', 30, 'yolo11n', key='best_map50_95'), kind='t')
    add('4.4-100-mean', 'YOLO11n 100ep 增益（**跨族 y11+b2 合并**，n=10）', '§4.4', 0.1922,
        lambda S: C.arch_cell(S, 'y11_shwd→sfchd', 100, 'yolo11n', key='best_map50_95'))
    add('4.4-100-t', 'YOLO11n 100ep 的 t（n=10）', '§4.4', 2.000,
        lambda S: C.arch_cell(S, 'y11_shwd→sfchd', 100, 'yolo11n', key='best_map50_95'), kind='t')
    # 单批次（把"合并"摊开：两批的读数差一个量级，稿内必须都写明）
    add('4.4-100-mean-y11batch', '同格、**仅族 `y11` 批次**（n=3）', '§4.4', -0.0050,
        lambda S: C.cell(S, 'y11_shwd→sfchd', 100, 20, fam='y11', key='best_map50_95', min_n=2))
    add('4.4-100-mean-b2batch', '同格、**仅族 `b2` 批次**（n=10）', '§4.4', 0.3246,
        lambda S: C.cell(S, 'y11_shwd→sfchd', 100, 20, fam='b2', key='best_map50_95', min_n=2))

    # ---------- ★ 底座结构完整性：后缀件导致的种子误归（2026-10-01 新增）----------
    add('S-1', '种子名与实际种子不符的行被 `_pick` 选中的次数（须 0）', '底座结构', 0.0,
        lambda S: _seedname_conflict(S), kind='xcheck')
    add('S-2', '候选**全部**种子名不符的 (格,种子,臂) 数（须 0）', '底座结构', 0.0,
        lambda S: _seedname_danger(S), kind='xcheck')

    # ---------- §5 预注册三格 ----------
    for nm, pr, m, tv in (('T1-a', 'dota15→aitod', 0.147, 1.816),
                          ('T1-b', 'aitod→visdrone', 0.168, 4.455),
                          ('T1-c', 'visdrone→dota15', 3.727, 43.774)):
        add('5-%s-mean' % nm, '%s `%s` 增益' % (nm, pr), '§5', m,
            (lambda p: lambda S: C.cell(S, p, 100, 20, K[(p, 100)], seeds=S1051))(pr))
        add('5-%s-t' % nm, '%s 的 t' % nm, '§5', tv,
            (lambda p: lambda S: C.cell(S, p, 100, 20, K[(p, 100)], seeds=S1051))(pr), kind='t')
    # ★ 2026-10-02：§5 表格里的 **p 值**此前无断言（只注册了增益与 t）。
    #   p 由该格的 t 与 n 按**双侧 t 分布**算出（df = n−1），用 scipy。
    def _pval(S, pr):
        c = C.cell(S, pr, 100, 20, K[(pr, 100)], seeds=S1051)
        if not c or 't' not in c or 'mean' not in c:
            return None
        import scipy.stats as _ss
        return dict(mean=float(2 * _ss.t.sf(abs(c['t']), c['n'] - 1)),
                    n=c['n'], fam=c['fam'], key=c['key'], t=c['t'])
    for nm, pr, pv in (('T1-a', 'dota15→aitod', 0.103),
                       ('T1-b', 'aitod→visdrone', 0.0016),
                       ('T1-c', 'visdrone→dota15', 8.5e-12)):
        add('5-%s-p' % nm, '%s 的 p（双侧 t，df=n−1）' % nm, '§5', pv,
            (lambda q: lambda S: _pval(S, q))(pr))

    # ---------- ★★ §4.6 标签轴（2026-10-02 新增）----------
    # ⚠ 此前**整个 §4.6 一条断言都没有**：`14` 只覆盖 §4.1/§4.2/§4.4/§5。
    #   而 §4.5 正文称标签轴 *"itself a measured result"*、§9 也引用其极值。
    #   口径：**逐种子配对**的档间差（hi% 档增益 − lo% 档增益），与 `scripts/41_A19` 同口径。
    def _lab_step(S, pair, ep, lo, hi, fam, key='test_map50_95'):
        a = C.cell(S, pair, ep, lo, fam=fam, key=key, min_n=3)
        b = C.cell(S, pair, ep, hi, fam=fam, key=key, min_n=3)
        if not a or not b or 'mean' not in a or 'mean' not in b:
            return None
        com = sorted(set(a['per_seed']) & set(b['per_seed']))
        v = [b['per_seed'][x] - a['per_seed'][x] for x in com]
        if len(v) < 3:
            return None
        _sd = _st.stdev(v)
        return dict(mean=_st.mean(v), n=len(v), fam='%s/%s' % (fam, lo), key=key,
                    per_seed={x: y for x, y in zip(com, v)},
                    t=(_st.mean(v) / (_sd / math.sqrt(len(v)))) if _sd > 0 else float('nan'))

    # 步长（形状）：visdrone→dota15 · s2ae · 30ep
    for _i, (_lo, _hi, _w) in enumerate([(10, 20, 1.4230), (20, 30, 0.5200),
                                         (30, 40, 0.1730), (40, 50, -0.1380)]):
        add('4.6-vis-30-s%d' % (_i + 1),
            '§4.6 `visdrone→dota15` 30ep %d%%→%d%% 步长' % (_lo, _hi), '§4.6', _w,
            (lambda lo, hi: lambda S: _lab_step(S, 'visdrone→dota15', 30, lo, hi, 's2ae'))(_lo, _hi))
    # 端点差（10%→50%）
    add('4.6-vis-30-10to50', '§4.6 `visdrone→dota15` 30ep 10%→50% 端点差', '§4.6', 1.9780,
        lambda S: _lab_step(S, 'visdrone→dota15', 30, 10, 50, 's2ae'))
    add('4.6-vis-100-10to50', '§4.6 `visdrone→dota15` 100ep 10%→50% 端点差', '§4.6', 1.1930,
        lambda S: _lab_step(S, 'visdrone→dota15', 100, 10, 50, 's2ae'))
    add('4.6-vis-30-10to50-t', '§4.6 `visdrone→dota15` 30ep 端点差的 t', '§4.6', 14.85,
        lambda S: _lab_step(S, 'visdrone→dota15', 30, 10, 50, 's2ae'), kind='t')
    add('4.6-pcb-30-10to50', '§4.6 `pcb→neu_det` 30ep 10%→50% 端点差', '§4.6', -10.7140,
        lambda S: _lab_step(S, 'pcb→neu_det', 30, 10, 50, 's2df'))
    add('4.6-pcb-100-10to50', '§4.6 `pcb→neu_det` 100ep 10%→50% 端点差', '§4.6', -2.3910,
        lambda S: _lab_step(S, 'pcb→neu_det', 100, 10, 50, 's2df'))
    # 100ep 的四步（**稿内目前不引用**，但注册上可让 §4.6 网格两个轮数都钉住；
    # 将来若正文要引，直接可用，不必再找来源）
    for _i, (_lo, _hi, _w) in enumerate([(10, 20, 0.5140), (20, 30, 0.0510),
                                         (30, 40, 0.3500), (40, 50, 0.2780)]):
        add('4.6-vis-100-s%d' % (_i + 1),
            '§4.6 `visdrone→dota15` 100ep %d%%→%d%% 步长' % (_lo, _hi), '§4.6', _w,
            (lambda lo, hi: lambda S: _lab_step(S, 'visdrone→dota15', 100, lo, hi, 's2ae'))(_lo, _hi))
    add('4.6-pcb-30-10to50-t', '§4.6 `pcb→neu_det` 30ep 端点差的 t', '§4.6', -9.22,
        lambda S: _lab_step(S, 'pcb→neu_det', 30, 10, 50, 's2df'), kind='t')

    return chk


def run(checks, S, perturb=None, quiet=False):
    ok = bad = 0
    rows = []
    for c in checks:
        cid = c['id']
        want = c['want']
        if perturb and perturb == cid:
            want = want + 9.99            # 阴性对照：故意改坏
        r = c['fn'](S)
        if r is None:
            rows.append(('FAIL', cid, c['desc'], c['where'], '格解析不到（空集合 ⇒ 硬失败）', want))
            bad += 1
            continue
        if 'ambiguous' in r:
            rows.append(('FAIL', cid, c['desc'], c['where'],
                         '族不唯一：%s（必须点名）' % r['ambiguous'], want))
            bad += 1
            continue
        if r['n'] < c.get('min_n', 3):
            rows.append(('FAIL', cid, c['desc'], c['where'],
                         'n=%d < %d（空/过少 ⇒ 硬失败）' % (r['n'], c.get('min_n', 3)), want))
            bad += 1
            continue
        if want is None:
            rows.append(('ok', cid, c['desc'], c['where'], 'n=%d 均值 %+.4f' % (r['n'], r['mean']), want))
            ok += 1
            continue
        K = c['kind']
        got = r['mean'] if K in ('mean', 'xcheck') else r['t']
        tol = {'mean': TOL_MEAN, 't': TOL_T, 'xcheck': TOL_X}[K]
        good = abs(got - want) <= tol
        rows.append(('ok' if good else 'FAIL', cid, c['desc'], c['where'],
                     '%s = %+.5f（n=%d, 族 `%s`, 列 `%s`）' % (c['kind'], got, r['n'], r['fam'], r['key']),
                     want))
        ok += good
        bad += (not good)
    if not quiet:
        print('| 判定 | id | 断言 | 出处 | 实测 | 期望 |')
        print('|---|---|---|---|---|---|')
        for st, cid, desc, where, got, want in rows:
            print('| %s | `%s` | %s | %s | %s | %s |' %
                  ('✅' if st == 'ok' else '❌ **FAIL**', cid, desc, where, got,
                   ('%+.5f' % want) if want is not None else '—'))
    return ok, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--self-test', action='store_true', help='阴性对照：改坏一条，守卫必须报红')
    a = ap.parse_args()

    _, G = C.load()
    checks = build_checks()
    print('# 稿-底座一致性守卫（`scripts/14_verify_claims.py`，只读）')
    print()
    print('断言条目 **%d** 条；口径由 `_cells.py` 提供（格的唯一解析器）。' % len(checks))
    print()

    if a.self_test:
        # 先确认全绿
        ok1, bad1 = run(checks, G, quiet=True)
        print('## 0. 阴性对照（★ 经验 #75：新写的检查必须现场做一次对照）')
        print()
        print('* 未注入缺陷：ok=%d / FAIL=%d' % (ok1, bad1))
        target = checks[0]['id']
        ok2, bad2 = run(checks, G, perturb=target, quiet=True)
        print('* 注入缺陷（把 `%s` 的期望值 +9.99）：ok=%d / **FAIL=%d**' % (target, ok2, bad2))
        print()
        if bad1 == 0 and bad2 == 1:
            print('✅ **对照通过**：全绿时零红；改坏一条时恰好一条红 ⇒ 守卫**确实在检查**，')
            print('   不是"匹配不上任何东西"的空转。')
            return 0
        print('❌ **对照失败**：守卫的行为不符合预期（这本身就是缺陷）。')
        return 2

    ok, bad = run(checks, G)
    print()
    print('## 汇总')
    print()
    print('* 通过 **%d** / 失败 **%d**（共 %d）' % (ok, bad, len(checks)))
    if bad:
        print()
        print('❌ **守卫报红** ⇒ 底座或论文的某个数字已经漂移，投稿前必须处理。')
        return 1
    print()
    print('✅ 全绿。**但这只说明数字与底座一致，不说明论证强度** —— 见经验 #26：')
    print('   「审计全绿 ≠ 送审就绪」：审计管数字一致性，不管论证强度。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
