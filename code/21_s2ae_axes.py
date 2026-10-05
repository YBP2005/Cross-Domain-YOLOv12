# -*- coding: utf-8 -*-
"""21_s2ae_axes.py —— T4 的验收计算：`visdrone→dota15`（族 `s2ae`）两条预算轴。

**口径（逐字照抄 `analysis\\A6_标签预算轴.md`，不要按绝对 mAP 理解）**：
  * 被测量的量是 **损失平面增益**（loss-plane gain）= **逐种子 `(lr005 − base)`**，单位 **pp**，
    列 = test 侧 `test_map50_95`；
  * **标签轴** = 增益在 `10% → 50%` 上的差（固定轮数）；
  * **轮数轴** = 增益在 `30ep → 100ep` 上的差（固定标签预算）；
  * 轴值**逐种子配对**算（先按种子求增益，再在两个预算档间作差），不是"先求均值再作差"。

★ 为什么必须写死这条口径：`s2ae` 的**绝对 mAP** 在两条轴上**都是正的**
（标签轴 Δ(50p−10p) ≈ +6~8 pp、轮数轴 Δ(100ep−30ep) ≈ +3~4 pp），
按绝对 mAP 读会得出"两轴同号"，把 A6 §4 的"反号"结论读反。
**两条轴在这里量的都是"增益随预算怎么变"，不是"性能随预算怎么变"。**

T4 的设计（见 `01_实验补充_T4_s2ae端点_20261001.md`）：把端点 2×2
（标签 ∈ {10p,50p} × 轮数 ∈ {30ep,100ep}）补到 **n=10**。
"""
import os
import sys
import math
import statistics as st

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _cells as C

PAIR = 'visdrone→dota15'
FAM = 's2ae'
KEY = 'test_map50_95'


def tstat(vals):
    n = len(vals)
    if n < 2:
        return float('nan'), float('nan')
    sd = st.stdev(vals)
    if sd == 0:
        return float('nan'), float('nan')
    t = st.mean(vals) / (sd / math.sqrt(n))
    return t, sd


def paired_axis(cells, lo_key, hi_key):
    """逐种子配对作差：对同时出现在两个格里的种子，算 gain(hi) − gain(lo)。"""
    a, b = cells.get(lo_key), cells.get(hi_key)
    if not a or not b or 'ambiguous' in a or 'ambiguous' in b:
        return None
    common = sorted(set(a['per_seed']) & set(b['per_seed']))
    if not common:
        return None
    d = {s: b['per_seed'][s] - a['per_seed'][s] for s in common}
    vals = list(d.values())
    t, sd = tstat(vals)
    return dict(n=len(vals), mean=st.mean(vals), sd=sd, t=t, per_seed=d)


def main():
    rows, G = C.load()
    print('底座行数 =', len(rows))
    sel = [r for r in rows if (r.get('run') or '').split('_')[0] == FAM]
    print('族 `%s` 的 run 数 = %d' % (FAM, len(sel)))
    if not sel:
        print('!! 底座里没有该族的 run'); return
    import collections
    comp = collections.Counter()
    for r in sel:
        parts = r['run'].split('_')
        if len(parts) >= 5:
            comp[(parts[1], parts[2], parts[3])] += 1
    print('组成 (预算, 轮数, 臂) -> run 数：')
    for k in sorted(comp, key=str):
        print('   %-22s %d' % (str(k), comp[k]))

    # 四个端点格
    cells = {}
    for lb in (10, 50):
        for ep in (30, 100):
            cells[(lb, ep)] = C.cell(G, PAIR, ep, lb, FAM, key=KEY, min_n=2)
    print()
    print('=== 四个端点格的增益（逐种子 lr005−base，pp；列 %s）===' % KEY)
    for lb in (10, 50):
        for ep in (30, 100):
            c = cells[(lb, ep)]
            if not c or 'ambiguous' in c:
                print('  %2d%% %3dep : %s' % (lb, ep, '缺格' if not c else c))
                continue
            lo = sum(1 for v in c['per_seed'].values() if v < 0)
            print('  %2d%% %3dep : n=%2d mean=%+.4f sd=%.4f t=%+.3f 负号 %d/%d'
                  % (lb, ep, c['n'], c['mean'], c['sd'], c['t'], lo, c['n']))

    print()
    print('=== ★ 标签轴 Δ(50%%−10%%)，增益的变化（逐种子配对）===')
    for ep in (30, 100):
        a = paired_axis(cells, (10, ep), (50, ep))
        if a is None:
            print('  %3dep : 缺一端（这是 T4-A/T4-B 未收工时应当看到的）' % ep); continue
        neg = sum(1 for v in a['per_seed'].values() if v < 0)
        print('  %3dep : n=%2d mean=%+.4f sd=%.4f t=%+.3f 负号 %d/%d'
              % (ep, a['n'], a['mean'], a['sd'], a['t'], neg, a['n']))

    print()
    print('=== ★ 轮数轴 Δ(100ep−30ep)，增益的变化（逐种子配对）===')
    for lb in (10, 50):
        a = paired_axis(cells, (lb, 30), (lb, 100))
        if a is None:
            print('  %2d%% : 缺一端' % lb); continue
        neg = sum(1 for v in a['per_seed'].values() if v < 0)
        print('  %2d%% : n=%2d mean=%+.4f sd=%.4f t=%+.3f 负号 %d/%d'
              % (lb, a['n'], a['mean'], a['sd'], a['t'], neg, a['n']))

    print()
    print('=== 判读（A6 §4 的断言是"两条轴可以反号"）===')
    lab30 = paired_axis(cells, (10, 30), (50, 30))
    ep10 = paired_axis(cells, (10, 30), (10, 100))
    ok_lab = lab30 and lab30['n'] >= 10
    ok_ep = ep10 and ep10['n'] >= 10
    if lab30:
        print('  标签轴 @30ep = %+.4f (n=%d)' % (lab30['mean'], lab30['n']))
    if ep10:
        print('  轮数轴 @10p  = %+.4f (n=%d)' % (ep10['mean'], ep10['n']))
    if lab30 and ep10:
        same = (lab30['mean'] > 0) == (ep10['mean'] > 0)
        print('  同号？ %s' % ('✅ 同号（**反号断言不成立**）' if same
                             else '❌ **反号（A6 的断言在 n=%d/%d 上成立）**' % (lab30['n'], ep10['n'])))
        if not (ok_lab and ok_ep):
            print('  ⚠ 仍有端点格 n<10 ⇒ 以上只是**中间读数**，等 T4 全部收工再判。')
    else:
        print('  ⚠ 端点不全（T4 未收工），暂不判读。')


if __name__ == '__main__':
    main()
