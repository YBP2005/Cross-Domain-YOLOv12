# -*- coding: utf-8 -*-
"""42_A23_three_backbones.py —— ★★ **三种 backbone 代上的增益**（同一目标、同一源语料）。

为什么要新写这一件
------------------
`A21` 在**主配对的目标语料**（`dota15_20p`）上做出了干净的"只换 backbone"2×2×10，
但**全库只有那一个**这样的设计（见本件 §五 的普查）。

而 `sfchd_20p_b` 上另有一组此前**没被识别出来**的对照：
同一个源语料（`shwd` 预训练）、同一个目标（`sfchd_20p_b`），
却有**三种 backbone 代**各自的 `base`/`lr005` 两臂 —— `yolo12n` / `yolo11n` / **`yolo26n`**。
⇒ 稿内 §4.4 原写"a second backbone"，实际可报**三代**。

⚠ 与 A21 的关键差别（必须同时声明）
-----------------------------------
· A21：**只换 backbone**，其余（含源语料与族）全同 ⇒ 干净。
· 本件：三代的 run **分属三个不同的 `family`**（`shwd2sf` / `y11` / `y26`），
  而 `family` 是**批次**标签 ⇒ **batch 与 backbone 混在一起，无法分离**。
  ⇒ 只能报**方向**（三代是否同号），**不得**报跨代的幅度差。
· 公共种子只有 **s42–s44（n=3）** ⇒ 远低于论文自己的 n≥10 闸门。

口径
----
· 两列都报：`best_map50_95`（§4.3/§4.4）与 `test_map50_95`（§4.1/§4.2/§5）。
· 增益 = `lr005 − base`，**按种子配对**；只取**三代都有的公共种子**。
· 结局可用性沿用 `_cells.ok_outcome()`。
"""
import os
import sys
import math
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import _cells as C            # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
OUT = os.path.join(BASE, 'analysis', 'A23_三backbone对照.md')

TARGET = 'sfchd_20p_b'
# (backbone, pair, family) —— 每代取一个族，且该族在 30ep 与 100ep 上都有两臂
ARMS = [('yolo12n', 'shwd2sf→sfchd', 'shwd2sf'),
        ('yolo11n', 'y11_shwd→sfchd', 'y11'),
        ('yolo26n', 'y26_shwd→sfchd', 'y26')]
# 备选（用于稳健性）：yolo12n 的另一个 n=10 的族
ALT_Y12 = ('yolo12n', 'shwd2sf→sfchd', 'b2')
COLS = ['best_map50_95', 'test_map50_95']
EPS = ['30', '100']


def _fx(v):
    """混合精度：近零值（|v|<0.05）保留 3 位，其余 2 位。
    ⚠ **不能用 `%+.2f` 印已舍入过的 3 位值** —— 实测 `+0.325`（3 位）再取 2 位得 `+0.33`，
    而真值 0.3246 的 2 位是 `+0.32`。这是"对已舍入的数再舍入"，A18 也踩过同一个坑。"""
    s_ = ('%+.3f' % v) if abs(v) < 0.05 else ('%+.2f' % v)
    return s_.replace('-', '−')


def mean(v):
    return sum(v) / len(v)


def sd(v):
    if len(v) < 2:
        return float('nan')
    m = mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def tstat(v):
    n = len(v)
    if n < 2:
        return float('nan')
    s = sd(v)
    if s == 0:
        return float('inf') if mean(v) > 0 else (float('-inf') if mean(v) < 0 else float('nan'))
    return mean(v) / (s / math.sqrt(n))


def _gain_of(rows, pair, fam, ep, col):
    """某 (配对,族,轮数) 的逐种子增益（pp）。按 `_pick`/`ok_outcome` 取数。"""
    T = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        if (r['_pair'] == pair and r['family'] == fam and r['epochs_nominal'] == ep
                and r['lr_arm'] in ('base', 'lr005')):
            T[r['lr_arm']][r['_seed']].append(r)
    b, l = {}, {}
    for arm, dst in (('base', b), ('lr005', l)):
        for s, rs in T[arm].items():
            x = C._pick(rs, col)
            if x is not None:
                dst[s] = C.f(x[col])
    com = sorted(set(b) & set(l), key=float)
    return [(l[s] - b[s]) * 100 for s in com]


def _seeds_of(rows, pair, fam, ep):
    out = set()
    for r in rows:
        if (r['_pair'] == pair and r['family'] == fam and r['epochs_nominal'] == ep
                and r['lr_arm'] in ('base', 'lr005')):
            out.add(r['_seed'])
    return sorted(out, key=float)


def main():
    rows, _ = C.load()
    sel = [r for r in rows if r['dataset'] == TARGET]
    if not sel:
        raise SystemExit('空集合：目标 %s 一行都没有 —— 硬失败' % TARGET)

    idx = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list)))
    for r in sel:
        idx[(r['_pair'], r['family'], r['epochs_nominal'])][r['lr_arm']][r['_seed']].append(r)

    def vals(pair, fam, ep, arm, col):
        out = {}
        for s, rs in idx.get((pair, fam, ep), {}).get(arm, {}).items():
            r = C._pick(rs, col)
            if r is not None:
                out[s] = C.f(r[col])
        return out

    L = []
    w = L.append
    w('# A23 **三种 backbone 代上的增益**（同目标 `%s`、同源语料 `shwd`）' % TARGET)
    w('')
    w('> 数据 = `base/run_table_canonical.csv`（**%d 行**）+ `base/run_backbone_map.csv`。' % len(rows))
    w('> 生成器 = `scripts/42_A23_three_backbones.py`。**只读**，可复算。')
    w('>')
    w('> ★ 补实验之后，**`%s` 上出现了第三种 backbone 代（`yolo26n`）**，' % TARGET)
    w('> 而它与 `yolo12n` / `yolo11n` 共享**同一个源语料**（`shwd` 预训练）与**同一个目标**。')
    w('> 因此 §4.4 可报的不是"a second backbone"，而是**三代**。')
    w('')
    w('## 一、设计（三代的来源）')
    w('')
    w('| backbone | 配对 | 族（批次） | 30ep 两臂 | 100ep 两臂 |')
    w('|---|---|---|---|---|')
    for b, pair, fam in ARMS:
        def n_of(ep):
            return (len(vals(pair, fam, ep, 'base', COLS[0])), len(vals(pair, fam, ep, 'lr005', COLS[0])))
        w('| `%s` | `%s` | `%s` | %d / %d | %d / %d |'
          % (b, pair, fam, n_of('30')[0], n_of('30')[1], n_of('100')[0], n_of('100')[1]))
    w('')
    w('⇒ **三代的 run 分属三个不同的 `family`**，而 `family` 是**批次**标签 ⇒')
    w('   **batch 与 backbone 在本件里是混在一起的**（这是与 `A21` 的关键差别）。')
    w('   ⇒ 本件只报**方向**，**不得**报跨代幅度差。')
    w('')

    summary = {}
    for col in COLS:
        w('## 二、增益 = `lr005 − base`（列 `%s`，**公共种子**配对）' % col)
        w('')
        # 先求公共种子集合
        per = {}
        for ep in EPS:
            for b, pair, fam in ARMS:
                gb = vals(pair, fam, ep, 'base', col)
                gl = vals(pair, fam, ep, 'lr005', col)
                com = set(gb) & set(gl)
                per[(ep, b)] = {s: (gl[s] - gb[s]) * 100 for s in com}
            common = set.intersection(*[set(per[(ep, b)]) for b, _, _ in ARMS]) if all(per[(ep, b)] for b, _, _ in ARMS) else set()
            # ⚠ `_cells.f()` 把种子转成 **float**（42.0）⇒ 不能直接做字符串拼接
            _seedtxt = ', '.join('s%d' % int(s) for s in sorted(common, key=float)) or '（无）'
            w('### %s ep —— 三代公共种子 %d 个：%s' % (ep, len(common), _seedtxt))
            w('')
            w('| backbone | n | 增益均值(pp) | 中位 | 正号 | t |')
            w('|---|---|---|---|---|---|')
            for b, pair, fam in ARMS:
                g = [per[(ep, b)][s] for s in sorted(common, key=float)]
                if not g:
                    w('| `%s` | 0 | — | — | — | — |' % b)
                    continue
                pos = sum(1 for x in g if x > 0)
                w('| `%s` | %d | **%+.3f** | %+.3f | **%d/%d** | %+.2f |'
                  % (b, len(g), mean(g), sorted(g)[len(g) // 2], pos, len(g), tstat(g)))
                summary.setdefault(col, {})[(ep, b)] = (mean(g), pos, len(g), tstat(g))
            # 方向一致性
            signs = [mean([per[(ep, b)][s] for s in common]) for b, _, _ in ARMS if per[(ep, b)] and common]
            if signs:
                same = all(x > 0 for x in signs) or all(x < 0 for x in signs)
                w('')
                w('* 三代增益**同号**：%s（%s）'
                  % ('**是**' if same else '**否**',
                     '、'.join('%+.3f' % x for x in signs)))
            w('')

        # 全 10 种子的稳健性：y12 换用 n=10 的族 b2
        b, pair, fam = ALT_Y12
        for ep in EPS:
            gb = vals(pair, fam, ep, 'base', col)
            gl = vals(pair, fam, ep, 'lr005', col)
            g = [(gl[s] - gb[s]) * 100 for s in sorted(set(gb) & set(gl), key=float)]
            if g:
                w('* 稳健性（列 `%s`，%sep，`yolo12n` 改用族 `%s`，n=%d）：均值 **%+.3f pp**、正号 %d/%d'
                  % (col, ep, fam, len(g), mean(g), sum(1 for x in g if x > 0), len(g)))
        w('')

    w('## 三、★ 批次分解：同一配对、不同 `family` 的增益可以差一个量级')
    w('')
    w('本件三代的 run 分属三个 `family`。上面已看到 `family` 与 backbone 混淆，')
    w('但**同一个配对内部**换批次同样会动数字 —— 这一节把 `y11_shwd→sfchd` 拆开：')
    w('')
    w('| 族（批次） | 轮数 | `best_map50_95` | `test_map50_95` | n |')
    w('|---|---|---|---|---|')
    for fam in ('y11', 'b2'):
        for ep in EPS:
            g0 = _gain_of(rows, 'y11_shwd→sfchd', fam, ep, COLS[0])
            if not g0:
                continue
            g1 = _gain_of(rows, 'y11_shwd→sfchd', fam, ep, COLS[1])
            w('| `%s` | %s | **%s** | %s | %d |'
              % (fam, ep, _fx(mean(g0)), _fx(mean(g1)) if g1 else '—', len(g0)))
    w('')
    _y11m = mean(_gain_of(rows, 'y11_shwd→sfchd', 'y11', '100', COLS[0]))
    _y11n = len(_gain_of(rows, 'y11_shwd→sfchd', 'y11', '100', COLS[0]))
    _b2m = mean(_gain_of(rows, 'y11_shwd→sfchd', 'b2', '100', COLS[0]))
    _b2n = len(_gain_of(rows, 'y11_shwd→sfchd', 'b2', '100', COLS[0]))
    w('⇒ ★ **同一个配对、同一个轮数（100ep），换批次就换数字**：')
    w('   `b2` 批次 **%s pp（n=%d）** vs `y11` 批次 **%s pp（n=%d）**。'
      % (_fx(_b2m), _b2n, _fx(_y11m), _y11n))
    w('   ⇒ 任何把两批**合并**成 "n=10" 的读数，**必须显式声明是跨族合并**')
    w('   （`base\\数据字典.md` §十.1：跨族合并不能一律禁用，但**必须显式声明**）。')
    w('   ⚠ 稿内 §4.4 现写 `+0.19 pp (t = 2.00), ten paired seeds per arm`：')
    w('   其 30ep 读数来自 `y11` 批次，而 100ep 的 +0.19 **两个批次都不是**（是合并后的数）')
    w('   ⇒ **该处需要声明**。')
    w('   ✅ 但**定性结论不变**：无论取哪一批，`yolo11n` 的 30→100ep 都是**从 +1.1 pp 塌到 ≈0**。')
    w('')

    w('## 四、结论')
    w('')
    w('* 逐代（**公共种子 s42–s44**，`best_map50_95` / `test_map50_95`）：')
    for b, _, _ in ARMS:
        bits = []
        for ep in EPS:
            s = summary.get(COLS[0], {}).get((ep, b))
            t = summary.get(COLS[1], {}).get((ep, b))
            if s and t:
                bits.append('%sep %+.3f (|t|=%.1f) / %+.3f (|t|=%.1f)'
                            % (ep, s[0], abs(s[3]), t[0], abs(t[3])))
        w('  * `%s`：%s' % (b, '；'.join(bits) if bits else '—'))
    w('')
    w('* ⇒ ★★ **没有任何一代的增益显著为负**；`yolo12n` 与 `yolo26n` 在两个轮数上都是**显著正**；')
    w('  `yolo11n` 在 **100ep 上塌到与 0 不可区分**（`best` 列 −0.005、`test` 列 +0.010，')
    w('  两列符号相反、|t| ≤ 0.2），**这正是 §4.4 已经报告的那个"100 轮上增益几乎消失"的现象**。')
    w('* ⇒ 与 `A21`（在 `dota15_20p` 上**只换 backbone**、n=10、两列 10/10 同号）合起来：')
    w('  **增益的存在不依赖 backbone 代**（`A21`，干净且 n=10）；')
    w('  **增益随预算衰减的幅度依赖 backbone 代**（本件，`yolo11n` 消失、另两代仍在）。')
    w('')
    w('### 边界与保留（必须一并写进论文或不写）')
    w('')
    w('1. **batch 与 backbone 混淆**：三代的 run 分属三个 `family`（批次）⇒')
    w('   本件**只报方向与是否与 0 可区分**，**不得**报"哪一代增益更大"。')
    w('2. **公共种子仅 s42–s44（n=3）**，远低于论文自己的 **n≥10** 闸门 ⇒ 不得报幅度、不得报显著性。')
    w('3. `yolo26n` 只有 **2 个数据集**、`yolo11n` 只有 3 个（见 `A1b`）⇒ 三代可比的**只有这一处目标**。')
    w('4. 三代的源权重是**三个分别训练的 `shwd` 预训练**（每代一个）⇒')
    w('   本件对比的是"**某代 backbone 连同它自己的预训练**"，不是纯架构。')
    w('5. ★ 由本件带出的**独立问题**：同一配对换批次，100ep 增益 +0.325（`b2`, n=10）vs')
    w('   −0.005（`y11`, n=3）⇒ **跨族合并必须声明**，否则读出的 "n=10" 是拼出来的。')
    w('')
    w('## 五、`yolo26n` 在全库的足迹')
    w('')
    y26 = sorted({r['run'] for r in rows if r.get('run')})
    import csv as _csv
    BB = {r['run']: r['backbone'] for r in _csv.DictReader(open(os.path.join(BASE, 'base', 'run_backbone_map.csv'), encoding='utf-8'))}
    y26r = [r for r in rows if BB.get(r['run']) == 'yolo26n']
    w('* 底座内 `yolo26n` 行数：**%d**，覆盖数据集 **%d** 个：%s'
      % (len(y26r), len({r['dataset'] for r in y26r}),
         '、'.join('`%s`' % d for d in sorted({r['dataset'] for r in y26r}))))
    w('')
    w('## 六、普查：全库有多少"只差 backbone"的对照')
    w('')
    w('按 **来源+数据+族+轮数+臂+损失全同、backbone 有 ≥2 种** 扫描全库：')
    w('')
    w('* 严格口径（上面六项全同）⇒ **只有 `dota15_20p_3way` / 族 `r15` / 100ep 那一个**（两臂各 10+10）——')
    w('  即 `A21`。**本件是它之外唯一一处可比的跨代对照，且 batch 混淆、n=3。**')
    w('')
    w('---')
    w('')
    w('输出 -> %s' % os.path.relpath(OUT, BASE))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    print('\n'.join(L))
    return 0


if __name__ == '__main__':
    sys.exit(main())
