# -*- coding: utf-8 -*-
"""null_exceedance.py — 冻结判据"3×σ̂_strategy"的每格零假设超越率：解析式 + 蒙特卡洛双重核对
规则：cell passes iff  mean paired gain > 3 × σ̂_strategy（σ̂ 由同 3 个种子估计）
零假设下：gain ~ N(0, σ_d²/n)，σ̂_strategy/σ_s = sqrt(χ²_{n-1}/(n-1))，与 gain 独立（正态样本均值与标准差独立）
→ P(q) = E_s[1 − Φ(3√n · s / q)],  q := σ_d/σ_s,  s := σ̂_strategy/σ_s
蒙特卡洛：y ~ N(0,σ_s),(n,·)；x ~ N(0,σ_b),(n,·)；gain=mean(y)-mean(x)；判据 gain > 3·sd(y,ddof=1)
"""
import numpy as np, sys
from scipy import stats, integrate
sys.stdout.reconfigure(encoding='utf-8')

def analytic(q, n=3):
    f = lambda s: (2*s*np.exp(-s*s)) * (1 - stats.norm.cdf(3*np.sqrt(n)*s/q))   # n=3: 2s² ~ χ²₂
    return integrate.quad(f, 0, 8)[0]

def mc_pair(r, rho, n=3, N=1_500_000, seed=20260912):
    """双臂蒙特卡洛：strategy 臂 sd=1，baseline 臂 sd=r，配对相关 rho。
    零假设下 q = σ_d/σ_s = sqrt(1 + r² - 2*rho*r)。"""
    rng = np.random.default_rng(seed)
    y = rng.normal(0, 1, (N, n))
    e = rng.normal(0, 1, (N, n))
    x = r * (rho*y + np.sqrt(1-rho*rho)*e)
    gain = y.mean(1) - x.mean(1)
    return ((gain > 3*y.std(1, ddof=1)).mean(),
            np.sqrt(1 + r*r - 2*rho*r))

print('=== 每格零假设超越率 vs q = σ_d/σ_s（n=3）===')
print('  q      analytic    MC(配对双臂)   MC 实际 q')
for q in [0.6, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 2.0, 2.5]:
    if q >= 1.0:
        r, rho = np.sqrt(q*q - 1), 0.0            # 独立双臂
    else:
        r, rho = 1.0, 1 - q*q/2                   # 正相关双臂（配对）
    p_mc, q_eff = mc_pair(r, rho)
    print('  %.1f   %7.3f%%     %7.3f%%      %.3f' % (q, 100*analytic(q), 100*p_mc, q_eff))

print()
print('=== 两个判据通过格的实测输入 ===')
cells = [
    ('smoke→SFCHD', 0.23, 0.207, 'σ̂_strategy(3 seeds)=0.23 pp; paired-diff sd(n=10)=0.207 pp'),
    ('SHWD→SFCHD',  0.13, 0.182, 'σ̂_strategy(3 seeds)=0.13 pp; paired-diff sd(n=10)=0.182 pp'),
    ('SHWD→SFCHD (3-seed paired sd)', 0.13, 0.267, 'per-seed +0.30/+0.42/+0.81 → sd=0.267 pp'),
]
for name, ss, sd, note in cells:
    q = sd/ss
    print('  %-32s q=%.2f  P_null=%.2f%%   [%s]' % (name, q, 100*analytic(q), note))

print()
print('=== 家族层面（28 格）===')
for q, lab in [(0.9, 'q=0.9'), (1.4, 'q=1.4'), (2.05, 'q=2.05')]:
    p = analytic(q)
    print('  %-7s per-cell %.2f%%  → 期望假通过数 28p = %.2f  家族至少一次 = %.1f%%'
          % (lab, 100*p, 28*p, 100*(1-(1-p)**28)))
print()
print('旧稿断言：per-cell ≈1.7%，即按 28×1.7% 得期望 0.5 格 —— 低估；实测档位落在 3–8%。')
