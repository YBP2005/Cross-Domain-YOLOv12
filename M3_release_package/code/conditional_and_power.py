# -*- coding: utf-8 -*-
"""conditional_and_power.py — 回答 dsflash r8 MUST#2 与 SHOULD#5（可复算）
(a) 零假设下 28 格家族出现 ≥1 / ≥2 次筛选通过的家族级概率（每格率随 q 变化）
(b) 给定"已取两臂前推"，两格分别通过十种子配对检验 / 新 7 种子检验的联合概率（零假设下）
(c) 80% 功效下可检测效应量：配对 t（n=3 / n=10）与冻结判据（3×σ̂_strategy 的期望阈值）
"""
import math, sys
import numpy as np
from scipy import stats
sys.stdout.reconfigure(encoding='utf-8')

# ---------- (a) 家族层面 ----------
def p_null(q, n=3):
    from scipy import integrate
    f = lambda s: 2*s*np.exp(-s*s)*(1 - stats.norm.cdf(3*np.sqrt(n)*s/q))
    return integrate.quad(f, 0, 8)[0]

print('=== (a) 28 格家族：零假设下的通过计数 ===')
print('  q     每格率     E[#pass]   P(>=1)    P(>=2)    P(>=3)')
for q in [0.9, 1.0, 1.4, 2.05]:
    p = p_null(q); m = 28
    pmf = [math.comb(m, k) * p**k * (1-p)**(m-k) for k in range(m+1)]
    print('  %.2f  %6.3f%%   %6.2f     %6.1f%%   %6.1f%%   %5.2f%%'
          % (q, 100*p, m*p, 100*(1-pmf[0]), 100*(1-pmf[0]-pmf[1]), 100*(1-sum(pmf[:3]))))

# ---------- (b) 联合通过十种子检验 ----------
print()
print('=== (b) 已选两臂的联合通过概率（零假设下，十种子 / 新七种子）===')
p_smoke10, p_shwd10, p_a2d15_10 = 6.45319860903507e-10, 6.243912150241744e-06, 1.6607865640324452e-13
p_smoke7, p_shwd7 = 1.9e-07, 7.77e-05
print('  两格同时通过十种子配对检验        : %.3g × %.3g = %.3g' % (p_smoke10, p_shwd10, p_smoke10*p_shwd10))
print('  两格同时通过新 7 种子配对检验      : %.3g × %.3g = %.3g' % (p_smoke7, p_shwd7, p_smoke7*p_shwd7))
print('  三臂（含 aitod→dota15）十种子       : %.3g' % (p_smoke10*p_shwd10*p_a2d15_10))
print('  注：这是"给定这两格被选中"的条件概率；不是家族级保证（选择发生在筛选读数上）。')

# ---------- (c) 功效 ----------
print()
print('=== (c) 80% 功效下的可检测效应量 ===')
for n, sig in [(3, 0.19), (3, 0.21), (10, 0.18), (10, 0.21)]:
    tcrit = stats.t.ppf(1-0.05/2, n-1)
    delta = (tcrit + stats.norm.ppf(0.80)) * sig / math.sqrt(n)
    print('  配对 t:  n=%2d  σ_d=%.2f → 80%% 功效可检测 %+.3f pp' % (n, sig, delta))
print()
print('  冻结判据（gain > 3σ̂_strategy）的期望阈值：E[σ̂/σ] = sqrt(2/(n-1))·Γ(n/2)/Γ((n-1)/2)')
for n in [3, 10]:
    factor = np.sqrt(2.0/(n-1)) * math.gamma(n/2)/math.gamma((n-1)/2)
    for ss in [0.13, 0.166, 0.23]:
        print('    n=%2d  σ_strategy=%.3f pp → 期望阈值 3·%.3f·%.3f = %.3f pp'
              % (n, ss, factor, ss, 3*factor*ss))
