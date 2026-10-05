# -*- coding: utf-8 -*-
"""22_s2ae_grid.py —— `visdrone→dota15`（族 `s2ae`）**完整 5 档预算 × 2 轮数网格**的两条预算轴。

**口径（逐字照抄 `analysis\\A6_标签预算轴.md`）**：
  * 被测量 = **损失平面增益** = 逐种子 `(lr005 − base)`，单位 **pp**，列 = test 侧 `test_map50_95`；
  * **标签轴** = 增益在 `10% → 50%` 上的差（固定轮数）；**轮数轴** = 增益在 `30ep → 100ep` 上的差（固定预算）；
  * 轴值**逐种子配对**（先按种子求增益，再在两档间作差），不是"先求均值再作差"。

★ **不要按绝对 mAP 读**：`s2ae` 的绝对 mAP 在两条轴上**都是正的**（≈+6~8 pp / +3~4 pp），
  按绝对 mAP 读会把 A6 §4 的"反号"结论读反。两条轴量的都是**增益随预算怎么变**。

与 `21_s2ae_axes.py` 的分工：21 只算 T4 的**端点 2×2**（验收用）；
本件算**完整网格**（5 档 × 2 轮数），并给相邻档的逐步差，用来看形状而不是只看端点。
"""
import os
import sys
import math
import collections
import statistics as st

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _cells as C

PAIR = sys.argv[1] if len(sys.argv) > 1 else 'visdrone→dota15'
FAM = sys.argv[2] if len(sys.argv) > 2 else 's2ae'
KEY = sys.argv[3] if len(sys.argv) > 3 else 'test_map50_95'
TIERS = (10, 20, 30, 40, 50)
EPS = (30, 100)
FULL_N = 10


def tstat(vals):
    n = len(vals)
    if n < 2:
        return float('nan'), float('nan')
    sd = st.stdev(vals)
    if sd == 0:
        return float('nan'), float('nan')
    return st.mean(vals) / (sd / math.sqrt(n)), sd


def paired(a, b):
    """逐种子配对：b.per_seed − a.per_seed（同种子交集）。"""
    if not a or not b or 'ambiguous' in a or 'ambiguous' in b:
        return None
    common = sorted(set(a['per_seed']) & set(b['per_seed']))
    if not common:
        return None
    d = {s: b['per_seed'][s] - a['per_seed'][s] for s in common}
    vals = list(d.values())
    t, sd = tstat(vals)
    return dict(n=len(vals), mean=st.mean(vals), sd=sd, t=t, per_seed=d)


def line(tag, r, width=30):
    if r is None:
        return '  %-*s  缺' % (width, tag)
    neg = sum(1 for v in r['per_seed'].values() if v < 0)
    flag = '' if r['n'] >= FULL_N else '   ⚠n<%d' % FULL_N
    return '  %-*s n=%2d mean=%+.4f sd=%.4f t=%+.3f 负号 %d/%d%s' % (
        width, tag, r['n'], r['mean'], r['sd'], r['t'], neg, r['n'], flag)


def main():
    rows, G = C.load()
    sel = [r for r in rows if (r.get('run') or '').split('_')[0] == FAM]
    print('底座行数 = %d；族 `%s` 的 run 数 = %d' % (len(rows), FAM, len(sel)))

    cells = {}
    for lb in TIERS:
        for ep in EPS:
            cells[(lb, ep)] = C.cell(G, PAIR, ep, lb, FAM, key=KEY, min_n=2)

    print()
    print('=== 一、网格：每格的损失平面增益（逐种子 lr005−base，pp）===')
    print('  %-6s %-28s %-28s' % ('预算', '30ep', '100ep'))
    for lb in TIERS:
        s30, s100 = cells[(lb, 30)], cells[(lb, 100)]
        f = lambda c: ('n=%2d %+.4f (t=%+.2f)%s' % (c['n'], c['mean'], c['t'],
                       '' if c['n'] >= FULL_N else ' ⚠')) if c and 'ambiguous' not in c else '缺'
        print('  %-6s %-28s %-28s' % ('%d%%' % lb, f(s30), f(s100)))

    print()
    print('=== 二、★ 标签轴：Δ(50%%−10%%)，增益的变化 ===')
    for ep in EPS:
        print(line('%dep' % ep, paired(cells[(10, ep)], cells[(50, ep)])))

    print()
    print('=== 二b、标签轴逐步差（看形状是否单调）===')
    for ep in EPS:
        print('  --- %dep ---' % ep)
        for i in range(len(TIERS) - 1):
            lo, hi = TIERS[i], TIERS[i + 1]
            print(line('%d%%→%d%%' % (lo, hi), paired(cells[(lo, ep)], cells[(hi, ep)]), 18))

    print()
    print('=== 三、★ 轮数轴：Δ(100ep−30ep)，增益的变化 ===')
    for lb in TIERS:
        print(line('%d%%' % lb, paired(cells[(lb, 30)], cells[(lb, 100)])))

    print()
    print('=== 四、判读：A6 §4 的断言"两条预算轴可以反号" ===')
    lab = paired(cells[(10, 30)], cells[(50, 30)])
    epa = paired(cells[(10, 30)], cells[(10, 100)])
    if not lab or not epa:
        print('  端点不全（T4/T5 未收工），暂不判读。')
        return
    same = (lab['mean'] > 0) == (epa['mean'] > 0)
    print('  标签轴 @30ep（10%%→50%%） = %+.4f  (n=%d, t=%+.3f)' % (lab['mean'], lab['n'], lab['t']))
    print('  轮数轴 @10%% （30→100ep）= %+.4f  (n=%d, t=%+.3f)' % (epa['mean'], epa['n'], epa['t']))
    print('  同号？ %s' % ('✅ 同号 ⇒ **反号断言不成立**' if same else '❌ **反号**'))
    if lab['n'] < FULL_N or epa['n'] < FULL_N:
        print('  ⚠ 端点 n<%d ⇒ 只是中间读数，不得当结论。' % FULL_N)

    print()
    print('=== 五、覆盖度自检（缺哪个格会直接决定哪条轴能不能报）===')
    miss = [(lb, ep) for lb in TIERS for ep in EPS
            if not cells[(lb, ep)] or 'ambiguous' in cells[(lb, ep)]]
    short = [(lb, ep, cells[(lb, ep)]['n']) for lb in TIERS for ep in EPS
             if cells[(lb, ep)] and 'ambiguous' not in cells[(lb, ep)]
             and cells[(lb, ep)]['n'] < FULL_N]
    print('  完全缺格: %s' % (miss if miss else '无 ✅'))
    print('  n<%d 的格: %s' % (FULL_N, short if short else '无 ✅'))
    if not miss and not short:
        print('  ⇒ **5×2 网格在 n=%d 上完整**。' % FULL_N)

if __name__ == '__main__':
    import io as _io
    import contextlib as _ctx
    _buf = _io.StringIO()
    with _ctx.redirect_stdout(_buf):
        main()
    _out = _buf.getvalue()
    print(_out)
    _stem = 'A19_%s完整网格.md' % FAM
    _path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'analysis', _stem)
    NL = chr(10)
    _head = ('# A19 `%s` / 族 `%s` 完整 5x2 网格' % (PAIR, FAM)) + NL + NL \
        + ('> 生成：`scripts/22_s2ae_grid.py %s %s %s`（可重跑）。' % (PAIR, FAM, KEY)) + NL \
        + ('> 口径：增益 = 逐种子 `(lr005 - base)`，pp，列 `%s`；端点差逐种子配对；' % KEY) \
        + ('**Delta = 长预算 - 短预算**（负号=支持主线）。') + NL + NL
    _io.open(_path, 'w', encoding='utf-8').write(_head + _out + NL)
    print('输出 -> %s' % _path)
