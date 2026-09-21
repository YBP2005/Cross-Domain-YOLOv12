# -*- coding: utf-8 -*-
"""bh_family26.py — 家族层面**常规**统计（主分析）：26 格名册上的配对 t + BH-FDR

输入：三个层级上两个家族格的配对 p（其余 24 格为无对照/单臂格，按 p = 1 计入名册分母）：
  ① 登记三种子筛选层：强格 p = 0.011（t = 9.44）、佐证格 p ≈ 0.081（t = 3.31）
  ② 预指定十种子扩展（结果选入）：强格 p = 6.4×10⁻¹⁰、佐证格 p = 6.2×10⁻⁶
  ③ 仅新种子（fresh-7，无复用）：强格 p = 1.9×10⁻⁷、佐证格 p = 7.8×10⁻⁵
输出：BH q（m = 26，q 阈值 0.05，step-up 单调化）、Bonferroni 阈值与各层是否拒绝。
只打印，不改稿。
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

M = 26                 # 枚举名册规模（Appendix I / Table T10）
ALPHA = 0.05
LEVELS = [
    ('registered 3-seed screening', {'smoke→SFCHD': 0.011, 'SHWD→SFCHD': 0.081}, 2),
    ('pre-specified ten-seed extension (outcome-selected)', {'smoke→SFCHD': 6.4e-10, 'SHWD→SFCHD': 6.2e-6}, 2),
    ('fresh-7 seeds only (no reuse)', {'smoke→SFCHD': 1.9e-7, 'SHWD→SFCHD': 7.8e-5}, 2),
]

print('族分母 m = %d（其余 %d 格按 p = 1 计入）；BH 阈值 q = %.2f；Bonferroni α/m = %.3g'
      % (M, M - 2, ALPHA, ALPHA / M))
for name, ps, k in LEVELS:
    items = sorted(ps.items(), key=lambda kv: kv[1])
    qs, running = {}, 1.0
    for i in range(k, 0, -1):
        p = items[i - 1][1]
        val = min(running, p * M / i)
        qs[items[i - 1][0]] = val
        running = val
    print('\n=== %s ===' % name)
    for c, p in items:
        q = qs[c]
        print('  %-14s p = %-9.3g  BH q = %-9.3g  Bonferroni p×m = %-9.3g  → %s'
              % (c, p, q, p * M, 'rejects' if q < ALPHA else 'does NOT reject'))
