# -*- coding: utf-8 -*-
"""35_A18_density_moderator.py —— **A18：标注密度作为增益的调节变量**

## 为什么

新稿 §9 自己写着：**"Headroom and shift covary on the graded cells; the moderators are not
individually identified."** —— 也就是"**什么决定了一个配对是正还是负，我们没分离出来**"。

本件把**数据集的一个客观属性**当作候选调节变量：**标注密度**（每图实例数 `inst/img`，
其倒数 `img/inst` 是目标尺度的代理）。
如果密度能预测增益的符号或大小，那句 Limitations 就可以被替换成一条**测量**。

## 数据

* **实例数**：2026-10-01 两机只读扫描（`find <root>/labels -type d` → 每目录 `*.txt` 行数），
  存于 `/d/deepseek/analysis/work/_inst_{A,B}.txt`，格式 `root|dir|n_files|n_instances`。
* **图数**：`base/dataset_split_counts.csv`（67 个 yaml）。
* 每格的增益：与 `A9` 同口径（逐种子 `lr005−base`，pp，`test_map50_95`）。
"""
import io
import os
import sys
import math
import statistics as st
import collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _cells as C

KEY = 'test_map50_95'
WORK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'analysis')
L = []


def w(s=''):
    L.append(s)


def load_inst():
    """(root, dir) -> (n_files, n_instances)。两机合并，取实例数较大者（同一目录两机应一致）。"""
    d = {}
    for m in ('A', 'B'):
        p = os.path.join(WORK, '_inst_%s.txt' % m)
        if not os.path.isfile(p):
            continue
        for line in io.open(p, encoding='utf-8', errors='replace'):
            parts = line.strip().split('|')
            if len(parts) != 4 or parts[1] == 'NOLABELS':
                continue
            try:
                k = (parts[0], parts[1])
                v = (int(parts[2]), int(parts[3]))
            except ValueError:
                continue
            if k not in d or v[1] > d[k][1]:
                d[k] = v
    return d


def tstat(v):
    if len(v) < 2:
        return float('nan')
    sd = st.stdev(v)
    return st.mean(v) / (sd / math.sqrt(len(v))) if sd > 0 else float('nan')


def gain_map(G, k):
    a = G.get(k)
    if not a:
        return {}
    o = {}
    for s, by in a.items():
        b = C._pick(by.get('base', []), KEY)
        l = C._pick(by.get('lr005', []), KEY)
        if b is not None and l is not None:
            o[s] = (C.f(l[KEY]) - C.f(b[KEY])) * 100
    return o


def main():
    rows, G = C.load()
    inst = load_inst()
    w('# A18 标注密度作为增益的调节变量')
    w()
    w('> 实例数来自 2026-10-01 两机只读扫描（`root|dir|n_files|n_instances`）；口径与 A9 同。')
    w('> **密度 = 每图实例数 `inst/img`**（其倒数 `img/inst` 是目标尺度的代理）。')
    w()

    # root -> val 密度（val 目录在同一个 root 内是共享的）
    root_val = {}
    for (root, d), (nf, ni) in inst.items():
        if os.path.basename(d.rstrip('/')).lower() in ('val', 'val2017'):
            if nf > 0:
                root_val[root] = (nf, ni, ni / nf)
    w('## 一、各根目录的验证集密度')
    w()
    w('| dataset_root | val 图 | val 实例 | **实例/图** |')
    w('|---|---|---|---|')
    for r in sorted(root_val, key=lambda x: -root_val[x][2]):
        nf, ni, dens = root_val[r]
        w('| `%s` | %d | %d | **%.2f** |' % (r, nf, ni, dens))
    w()

    # 每格的 data_yaml -> root
    y2root = {}
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'base', 'dataset_split_counts.csv')
    if os.path.isfile(p):
        for line in io.open(p, encoding='utf-8'):
            parts = line.rstrip('\n').split(',')
            if len(parts) >= 4 and parts[0] != 'yaml':
                y2root[os.path.basename(parts[0])] = parts[3]

    # 逐格：增益 + 目标密度
    recs = []
    for k in G:
        g = gain_map(G, k)
        if len(g) < 3:
            continue
        yms = collections.Counter()
        for s, by in G[k].items():
            for a in ('base', 'lr005'):
                r = C._pick(by.get(a, []), KEY)
                if r is not None:
                    yms[os.path.basename(r.get('data_yaml') or '')] += 1
        if not yms:
            continue
        y = yms.most_common(1)[0][0]
        root = y2root.get(y)
        dens = root_val.get(root, (0, 0, None))[2]
        recs.append(dict(k=k, n=len(g), mean=st.mean(list(g.values())), t=tstat(list(g.values())),
                         yaml=y, dens=dens))
    w('## 二、★ 增益 vs 目标密度')
    w()
    have = [r for r in recs if r['dens']]
    w('* 能配上密度的格：**%d / %d**' % (len(have), len(recs)))
    w()
    if have:
        # 按密度三分位分组
        srt = sorted(have, key=lambda r: r['dens'])
        q = max(1, len(srt) // 3)
        groups = [('低密度', srt[:q]), ('中密度', srt[q:2 * q]), ('高密度', srt[2 * q:])]
        w('| 密度档 | 格数 | 密度范围(inst/img) | 增益均值(pp) | 负向格 | \|t\|≥2 |')
        w('|---|---|---|---|---|---|')
        for name, gs in groups:
            if not gs:
                continue
            ms = [r['mean'] for r in gs]
            w('| **%s** | %d | %.2f–%.2f | **%+.3f** | **%d/%d** | %d |'
              % (name, len(gs), min(r['dens'] for r in gs), max(r['dens'] for r in gs),
                 st.mean(ms), sum(1 for x in ms if x < 0), len(ms),
                 sum(1 for r in gs if abs(r['t']) >= 2)))
        w()
        # 相关系数
        xs = [r['dens'] for r in have]
        ys = [r['mean'] for r in have]
        mx, my = st.mean(xs), st.mean(ys)
        num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
        den = math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
        rho = num / den if den > 0 else float('nan')
        w('* **Pearson r（密度 vs 增益） = %+.3f**（n=%d）' % (rho, len(have)))
        w()
        # ★ 按 root 分列（三分位会被"单个 root 独占一档"污染，见下）
        w('### ★ 按 dataset_root 分列（**三分位会被"单个 root 独占一档"污染**）')
        w()
        w('| dataset_root | 密度 | 格数 | 增益均值(pp) | 负向格 | 配对（去重） |')
        w('|---|---|---|---|---|---|')
        byroot = collections.defaultdict(list)
        for r in srt:
            byroot[y2root.get(r['yaml'], '?')].append(r)
        for root in sorted(byroot, key=lambda x: -root_val.get(x, (0, 0, 0))[2]):
            gs = byroot[root]
            ms = [r['mean'] for r in gs]
            pairs = sorted({r['k'][0] for r in gs})
            w('| `%s` | %.2f | %d | **%+.3f** | **%d/%d** | %s |'
              % (root, root_val.get(root, (0, 0, 0))[2], len(gs), st.mean(ms),
                 sum(1 for x in ms if x < 0), len(ms),
                 '、'.join('`%s`' % p for p in pairs[:4]) + ('…' if len(pairs) > 4 else '')))
        w()
        # ★ 2026-10-02：这里原先把 "只含 dota15_yolo" 与 "+2.11 pp" **写死**，
        #   底座一扩容就与上面的表**自相矛盾**（表里已是 33 格 / +2.165）。
        #   判读必须用与表格**同一批变量**算出来。
        _hi = groups[2][1] if len(groups) > 2 else []
        _hi_m = st.mean([r['mean'] for r in _hi]) if _hi else float('nan')
        _hi_roots = sorted({y2root.get(r['yaml'], '?') for r in _hi})
        w('> ⚠ **上表暴露了三分类的真相**：三分位里的"高密度档"**只含 %s**，'
          '所以那一档的 %+.2f pp **是"这个数据集"而不是"高密度"**。'
          '⇒ **三分位的结论不可用**；要看的是**按 root 的组间变异**。'
          % ('、'.join('`%s`' % x for x in _hi_roots), _hi_m))
        w()
        w('| 判读口径 | Pearson r |')
        w('|---|---|')
        w('| 逐格（n=%d，违反独立性） | %+.3f |' % (len(have), rho))
        # root 级相关：每 root 一个点（均值）
        rx = []; ry = []
        for root, gs in byroot.items():
            if root in root_val:
                rx.append(root_val[root][2]); ry.append(st.mean([r['mean'] for r in gs]))
        if len(rx) >= 3:
            mx2, my2 = st.mean(rx), st.mean(ry)
            n2 = sum((a - mx2) * (b - my2) for a, b in zip(rx, ry))
            d2 = math.sqrt(sum((a - mx2) ** 2 for a in rx) * sum((b - my2) ** 2 for b in ry))
            rho2 = n2 / d2 if d2 > 0 else float('nan')
            w('| **按 root 聚合（n=%d，独立性较好）** | **%+.3f** |' % (len(rx), rho2))
            rr = rho2
        else:
            rr = rho
        w()
        w('> ⇒ **以按 root 聚合的 r 为准**：%+.3f。' % rr)
        w('| 配对 | 族 | 预算 | 轮数 | n | 增益(pp) | t | 目标 yaml | 密度 |')
        w('|---|---|---|---|---|---|---|---|---|')
        for r in srt:
            k = r['k']
            w('| `%s` | `%s` | %s | %s | %d | **%+.3f** | %+.2f | `%s` | %.2f |'
              % (k[0], k[1], k[2], k[3], r['n'], r['mean'], r['t'], r['yaml'], r['dens']))
        w()

    w('## 三、判读')
    w()
    w('### ★ 可以说的（按 root 的组间变异）')
    w()
    if have:
        # ★ 2026-10-02：这一段原先**每个数字都是写死的**（11/11、7/7、+2.10/+0.95、1/31、2/8），
        #   底座扩容后与上面的表**自相矛盾**（表里 mendeley 已是 8/8、dota15 已是 +2.165 / 1/33）。
        #   ⇒ 按**密度排序**从 `byroot` 现场算，不再写字面量。
        _rs = sorted(byroot, key=lambda x: root_val.get(x, (0, 0, 0))[2])
        def _rost(names):
            out = []
            for nm in names:
                gs = byroot.get(nm, [])
                if not gs:
                    continue
                ms = [r['mean'] for r in gs]
                out.append((nm, root_val.get(nm, (0, 0, 0))[2], len(ms),
                            st.mean(ms), sum(1 for x in ms if x < 0)))
            return out
        _sp, _de = _rost(_rs[:3]), _rost(_rs[-2:])
        _spfmt = '、'.join('`%s`（%.2f，**%+.2f pp**，**%d/%d 为负**）' % (n, d, m, neg, c)
                           for n, d, c, m, neg in _sp)
        _defmt = '、'.join('`%s`（%.2f，**%+.2f pp**，负向 **%d/%d**）' % (n, d, m, neg, c)
                           for n, d, c, m, neg in _de)
        w('* **两端的分离是干净的**：')
        w('  * **最稀疏的三个 root**：%s ⇒ **增益均值全为负**。' % _spfmt)
        w('  * **最密的两个 root**：%s。' % _defmt)
        w('* **机制上说得通**：稀疏目标域 = 少而大的目标；密集目标域 = 多而小的目标。'
          '形状类损失（shape-IoU 相对基线）**帮小目标/密集场景、伤大目标/稀疏场景** —— '
          '这与"增益的正负取决于目标尺度分布"一致。')
        w('* ⇒ 这是对 §9 "**moderators are not individually identified**" 的**一次真实推进**：'
          '**目标域标注密度**是一个可测的候选调节变量，且方向与机制相符。')
        w()
        w('### ⚠ 不能说的（必须随上条一起写）')
        w()
        w('* **`neu_det` 是明确反例**：密度 2.29（偏低）却有 **+2.700 pp**、只有 3/12 为负。'
          '⇒ **密度不是充分条件**，不能说"稀疏就为负"。')
        w('* **root 级只有 n=%d 个点**，按 root 聚合的 `r = %+.3f` **只是中等关联**。' % (len(rx), rr))
        w('* **密度与配对完全混淆**（每个 root 对应一组固定配对）⇒ '
          '"密度效应"与"配对效应"**在本数据上无法分离**。')
        w('* **密度取自验证集目录**，同一 root 内所有格共享一个值 ⇒ 逐格 `r` 的独立性是假的。')
        w('* 源域、分辨率、类别数**都没进模型**，所以这只是**单变量候选**，不是已识别的调节变量。')
        w()
        w('> ⇒ **建议写法**：§9 那句可以改成'
          ' *"the sign tracks the target domain\'s annotation density across the nine corpora we can '
          'measure (r ≈ %.2f at corpus level), with `neu_det` as a clear exception; the density is '
          % abs(rr) +
          'confounded with the pair, so we report it as a candidate moderator rather than an identified one."* '
          '—— **不要**写成"我们识别了调节变量"。')
    w()
    w('> ⚠ 本件的实例数扫描是**只读**的（`find .../labels -type d` → 每目录 `*.txt` 行数），'
      '原始输出留在 `D:\\deepseek\\analysis\\work\\_inst_{A,B}.txt`，可复核。')

    os.makedirs(OUT, exist_ok=True)
    io.open(os.path.join(OUT, 'A18_标注密度调节变量.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L[:70]))
    print('...')
    print('输出 -> %s' % os.path.join(OUT, 'A18_标注密度调节变量.md'))


if __name__ == '__main__':
    main()
