# -*- coding: utf-8 -*-
# Paths are relative: set RUNS_ROOT (and OUT_MD where relevant) to the directory holding the
# released runs before running this script. Absolute paths were removed for the submission.
"""fresh7_seed_analysis.py — 仅用扩展中"新种子"(45–51)的配对分析（GLM r7 A2 要求）
数据：{RUNS_ROOT}/{arm}_{base100,lr005_100ep}_s{42..51}n/results.csv（best mAP50-95）
说明：42/43/44 为三条筛选臂原本的 3 个种子（已在 screening 读数中使用），45–51 为扩展新增的 7 个。
"""
import io, os, csv, math, itertools, sys
import numpy as np
from scipy import stats
sys.stdout.reconfigure(encoding='utf-8')

RUNS = os.environ.get('RUNS_ROOT', r'./runs')
ARMS = [('smoke2sf', 'smoke→SFCHD'), ('shwd2sf', 'SHWD→SFCHD'), ('a2d15', 'aitod→dota15')]

def best_m95(p):
    rows = list(csv.DictReader(io.open(p, encoding='utf-8', errors='ignore')))
    return max(float(r['metrics/mAP50-95(B)']) for r in rows) if rows else None

def load(arm, kind, seeds):
    out = {}
    for s in seeds:
        p = os.path.join(RUNS, '%s_%s_s%dn' % (arm, kind, s), 'results.csv')
        v = best_m95(p) if os.path.exists(p) else None
        if v is None:
            print('  MISSING %s %s s%d' % (arm, kind, s))
        else:
            out[s] = v
    return out

def paired(base, lr, seeds):
    b = np.array([base[s] for s in seeds]); l = np.array([lr[s] for s in seeds])
    d = (l - b) * 100
    n = len(d)
    t, p = stats.ttest_rel(l, b)
    tw, pw = stats.ttest_ind(l, b, equal_var=False)
    ss = l.std(ddof=1) * 100                       # 策略侧 σ̂ (pp)
    sd = d.std(ddof=1)
    pool = np.concatenate([b, l]); combos = np.array(list(itertools.combinations(range(2*n), n)))
    sums = pool[combos].sum(axis=1); tot = pool.sum()
    pd = sums/n - (tot - sums)/n
    obs = l.mean() - b.mean()
    pperm = float(np.mean(np.abs(pd) >= abs(obs) - 1e-12))
    return dict(n=n, mean_pp=float(d.mean()), sd_pp=float(sd), t=float(t), p=float(p),
                welch_p=float(pw), perm_p=pperm, sigma_strategy=float(ss),
                effect=float(d.mean()/ss), sep=float(2.0/math.comb(2*n, n)))

print('=== 仅新种子 45–51（n=7）===')
for arm, pair in ARMS:
    base = load(arm, 'base100', range(45, 52)); lr = load(arm, 'lr005_100ep', range(45, 52))
    if len(base) == 7 and len(lr) == 7:
        r = paired(base, lr, range(45, 52))
        print('%-16s n=%d  mean=%+.2f pp  sd=%.3f  t=%.2f p=%.3g  Welch p=%.3g  perm p=%.3g  σ̂_strat=%.3f  效应=%.1fσ  完全分离p=%.4f'
              % (pair, r['n'], r['mean_pp'], r['sd_pp'], r['t'], r['p'], r['welch_p'], r['perm_p'],
                 r['sigma_strategy'], r['effect'], r['sep']))

print()
print('=== 全部 10 种子（n=10，对照）===')
for arm, pair in ARMS:
    base = load(arm, 'base100', range(42, 52)); lr = load(arm, 'lr005_100ep', range(42, 52))
    if len(base) == 10 and len(lr) == 10:
        r = paired(base, lr, range(42, 52))
        print('%-16s n=%d  mean=%+.2f pp  sd=%.3f  t=%.2f p=%.3g  perm p=%.3g  σ̂_strat=%.3f  效应=%.1fσ'
              % (pair, r['n'], r['mean_pp'], r['sd_pp'], r['t'], r['p'], r['perm_p'], r['sigma_strategy'], r['effect']))

print()
print('=== 仅原 3 种子（42–44，n=3；即 screening 读数复算）===')
for arm, pair in ARMS:
    base = load(arm, 'base100', range(42, 45)); lr = load(arm, 'lr005_100ep', range(42, 45))
    if len(base) == 3 and len(lr) == 3:
        r = paired(base, lr, range(42, 45))
        print('%-16s n=%d  mean=%+.2f pp  t=%.2f p=%.3g  σ̂_strat=%.3f  效应=%.1fσ'
              % (pair, r['n'], r['mean_pp'], r['t'], r['p'], r['sigma_strategy'], r['effect']))
