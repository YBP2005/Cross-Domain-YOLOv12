# -*- coding: utf-8 -*-
# Paths are relative: set RUNS_ROOT (and OUT_MD where relevant) to the directory holding the
# released runs before running this script. Absolute paths were removed for the submission.
"""account_runs.py — 归档 run 的完整分类账（供 §8.1 的 run 计数如实改口径）

分类：
  A 源预训练（data 非 20% 预算的 *_pretrain / 源域自评）
  B 名册 run：属于 26 个可配对配置的 base 与策略臂
  C 名册内的扩展/辅助 run：额外预算（150/200ep）、模块臂（mod*）、无基线的组、以及 20% 组内的其他臂
"""
import collections, io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.environ.get('RUNS_ROOT', r'./runs')
ARM_RX = [('lr005', r'lr005'), ('sns', r'_sns'), ('css', r'_css'), ('pws', r'_pws'),
          ('jps', r'_jps'), ('coslr', r'coslr'), ('spi', r'_spi')]
MOD_RX = re.compile(r'mod[A-Za-z0-9]*_|_mod', re.I)


def arm_of(n):
    for tag, rx in ARM_RX:
        if re.search(rx, n, re.I):
            return tag
    if re.search(r'base\d+', n, re.I):
        return 'base'
    return None


runs = {}
for d in sorted(os.listdir(ROOT)):
    a = os.path.join(ROOT, d, 'args.yaml')
    if not os.path.exists(a):
        continue
    t = io.open(a, encoding='utf-8', errors='replace').read()
    def g(k):
        m = re.search(r'^%s:\s*(\S+)' % k, t, re.M)
        return m.group(1) if m else ''
    runs[d] = dict(data=g('data'), epochs=g('epochs'), model=os.path.basename(g('model') or '?'))

A = [n for n, r in runs.items() if '20p' not in (r['data'] or '')]
groups = collections.defaultdict(lambda: collections.defaultdict(list))
for n, r in runs.items():
    if '20p' not in (r['data'] or ''):
        continue
    if arm_of(n) is None:
        continue
    obj = os.path.basename(r['data']).replace('_20p_b.yaml', '').replace('_20p.yaml', '')
    groups[(r['model'].replace('.pt', ''), obj, r['epochs'])][arm_of(n)].append(n)

B_runs, C_runs = [], []
for k, arms in groups.items():
    src, obj, ep = k
    pairable = 'base' in arms and len(arms) > 1
    for a, names in arms.items():
        for n in names:
            if pairable and a != 'base' and not MOD_RX.search(n):
                B_runs.append(n)
            elif pairable and a == 'base':
                B_runs.append(n)
            else:
                C_runs.append(n)

print('归档 run 总数（含 args.yaml）= %d' % len(runs))
print('  A 源预训练/非 20%% 预算        = %d' % len(A))
print('  B 名册内（26 配置的 base+策略） = %d' % len(B_runs))
print('  C 名册组内的扩展/辅助 run       = %d' % len(C_runs))
print('  合计 %d + %d + %d = %d' % (len(A), len(B_runs), len(C_runs), len(A) + len(B_runs) + len(C_runs)))
print('\nC 类样例（前 25）：')
for n in sorted(C_runs)[:25]:
    print('   ', n)
print('\nB 类中带种子后缀的 run 数 = %d；带 _s42n.._s51n 的分布：' %
      sum(1 for n in B_runs if re.search(r'_s\d+n?$', n)))
seedcnt = collections.Counter()
for n in B_runs:
    m = re.search(r'_s(\d+)n?$', n)
    if m:
        seedcnt[m.group(1)] += 1
print('   ', dict(sorted(seedcnt.items(), key=lambda kv: int(kv[0]))))
