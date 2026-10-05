# -*- coding: utf-8 -*-
# Paths are relative: set RUNS_ROOT (and OUT_MD where relevant) to the directory holding the
# released runs before running this script. Absolute paths were removed for the submission.
"""make_appendixI_v3.py — 生成附录 I v3 表（26 个可配对配置：22 B 管线 + 4 SFCHD 管线）"""
import collections, io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.environ.get('RUNS_ROOT', r'./runs')
OUT = os.environ.get('OUT_MD', r'./appendix_I_v3_table.md')
ARM_RX = [('lr005', r'lr005'), ('sns', r'_sns'), ('css', r'_css'), ('pws', r'_pws'),
          ('jps', r'_jps'), ('coslr', r'coslr'), ('spi', r'_spi')]


def arm_of(n):
    for tag, rx in ARM_RX:
        if re.search(rx, n, re.I):
            return tag
    if re.search(r'base\d+', n, re.I):
        return 'base'
    return None


def seed_of(n):
    m = re.search(r'_s(\d+)n?$', n)
    return m.group(1) if m else None


runs = {}
for d in sorted(os.listdir(ROOT)):
    a = os.path.join(ROOT, d, 'args.yaml')
    if not os.path.exists(a):
        continue
    t = io.open(a, encoding='utf-8', errors='replace').read()
    def g(k):
        m = re.search(r'^%s:\s*(\S+)' % k, t, re.M)
        return m.group(1) if m else ''
    runs[d] = dict(data=g('data'), epochs=g('epochs'), model=g('model'))

cells = collections.defaultdict(lambda: collections.defaultdict(list))
for n, A in runs.items():
    d = A['data'] or ''
    if '20p' not in d:
        continue
    a = arm_of(n)
    if a is None:
        continue
    obj = os.path.basename(d).replace('_20p_b.yaml', '').replace('_20p.yaml', '')
    src = os.path.basename(A['model'] or '?').replace('.pt', '')
    cells[(src, obj, A['epochs'] or '?')][a].append(seed_of(n))

pairs = []
for k in sorted(cells, key=lambda x: (x[1], int(x[2]) if x[2].isdigit() else 0, x[0])):
    arms = cells[k]
    if 'base' not in arms:
        continue
    strat = [a for a in arms if a != 'base']
    if not strat:
        continue
    pairs.append((k, arms))

SFCHD_TARGETS = ('sfchd',)
rows = []
for i, (k, arms) in enumerate(pairs, 1):
    src, obj, ep = k
    b = arms['base']
    oth = '; '.join('%s×%d[%s]' % (a, len(arms[a]), ','.join(sorted({s for s in arms[a] if s})) or 'ns')
                    for a in sorted(arms) if a != 'base')
    kind = 'SFCHD-pipeline' if obj in SFCHD_TARGETS else ('cross-domain' if src.split('_')[0] not in obj else 'within-domain')
    rows.append('| %d | %s | %s → %s | %s ep | %d | %s | %d |'
                % (i, kind, src, obj, ep, len(b), oth, sum(len(v) for v in arms.values())))

head = ['| # | pipeline | source → target | budget | baseline runs | strategy arms (runs[seeds]) | runs |',
        '|---|---|---|---|---|---|---|']
io.open(OUT, 'w', encoding='utf-8').write('\n'.join(head + rows) + '\n')
print('\n'.join(head + rows))
n_sfchd = sum(1 for (src, obj, ep), _ in pairs if obj in SFCHD_TARGETS)
print('\n可配对配置 = %d（其中 SFCHD 管线 %d，B 管线 %d）' % (len(pairs), n_sfchd, len(pairs) - n_sfchd))
print('名册内 run = %d' % sum(sum(len(v) for v in arms.values()) for _, arms in pairs))
