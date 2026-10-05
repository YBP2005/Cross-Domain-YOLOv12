# -*- coding: utf-8 -*-
"""recompute_family_sensitivity.py — released recomputation of every BH family variant.

WHY THIS EXISTS
---------------
A Stage-A reviewer (对抗性核查-sol) objected that the family-sensitivity values printed in
Appendix F.1 are not reproducible from the standard BH formula.  Checking the archive:
the m = 26 values come from `bh_family26.py` and are correct, but the "recorded 28" and
"arm-level 138" values were written into the text as bare literals by `apply_p0b.py`
— no released script computed them, and they are NOT reproducible from BH:

    printed (m = 28)  : 5.5e-9 / 6.6e-5     BH gives 1.79e-8 / 8.68e-5
    printed (m = 138) : 4.6e-9 / 6.7e-5     BH gives 8.83e-8 / 4.28e-4

Both printed pairs are inconsistent even among themselves (the implied multiplier is
8.6x for the first value and 10.6x for the second, whereas BH requires m/rank).  This
script recomputes every variant from the same released p-values under ONE stated
convention, so the printed numbers become derivable.

CONVENTION (stated in the manuscript): the correction is applied to configurations;
configurations carrying either a single arm or no paired seeds enter at p = 1, so the
p-value vector is two real values followed by padding, and BH's step-up monotonicity
is enforced from the largest p downward.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

# released p-values, by evidence tier (two family cells)
LEVELS = [
    ('registered 3-seed screening',            [0.011, 0.081]),
    ('pre-specified ten-seed extension',       [6.4e-10, 6.2e-6]),
    ('fresh-7 seeds only',                     [1.9e-7, 7.8e-5]),
]
EXTERNAL_P = 1.66e-13          # aitod→dota15, family-external probe arm
ALPHA = 0.05


def bh(pvals, m):
    """BH adjusted q-values with step-up monotonicity. pvals: list of real p-values."""
    k = len(pvals)
    assert m >= k, 'family size cannot be smaller than the number of real tests'
    order = sorted(range(k), key=lambda i: pvals[i])
    q = [0.0] * k
    running = 1.0
    for rank in range(k, 0, -1):
        i = order[rank - 1]
        val = min(running, pvals[i] * m / rank)
        q[i] = val
        running = val
    return q


def show(pvals, m, label=''):
    qs = bh(pvals, m)
    bits = ', '.join('%s: p = %.3g -> q = %.3g' % (n, p, q)
                     for (n, p, q) in zip(NAMES[:len(pvals)], pvals, qs))
    print('  m = %-5d %-34s %s   [%s]'
          % (m, label, bits, 'rejects at 0.05' if all(q < ALPHA for q in qs) else 'NOT rejected'))


NAMES = ['smoke→SFCHD', 'SHWD→SFCHD', 'aitod→dota15']

print('BH family-size sensitivity, one convention, released p-values')
print('convention: two real paired tests per tier; every other configuration enters at p = 1')
print()
for label, ps in LEVELS:
    print('%s  (p = %s)' % (label, ', '.join('%.3g' % p for p in ps)))
    for m, note in [(2, 'the two extended family arms alone'),
                    (26, 'enumerated roster (Appendix I)'),
                    (28, 'recorded registry count'),
                    (138, 'arm-level run count')]:
        show(ps, m, note)
    # three-arm completion that additionally contains the family-external probe
    if label.startswith('pre-specified'):
        print('  --- with the family-EXTERNAL probe arm included as a third test ---')
        ext = ps + [EXTERNAL_P]
        for m, note in [(3, 'three extended arms'), (26, 'roster'), (28, 'recorded'), (138, 'arm-level')]:
            show(ext, m, note)
        print('  --- family-external arm reported as a single test (not a family member) ---')
        print('      p = %.3g   ->   q = %.3g (a single test coincides with its raw p)'
              % (EXTERNAL_P, EXTERNAL_P))
    print()
