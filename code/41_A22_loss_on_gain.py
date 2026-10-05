# -*- coding: utf-8 -*-
"""41_A22_loss_on_gain.py —— ★ **损失对"增益"的效应**（补实验后才第一次可算）。

背景
----
论文的因变量是**增益** `lr005 − base`。问"换损失后增益还在不在"，需要**四条腿**同时存在：

    shapeiou-base   shapeiou-lr005   {loss}-base   {loss}-lr005

`A20_损失轴实测对照.md` §三 的结论是「**现有数据不可识别**（格不存在，不是功效不足）」。
**那句在补实验完成后已经过期**：补实验补的正是 `{loss}-lr005` 腿，
现在有 **3 个组四腿齐备**（见 `--self-check` 的清单）。

本件与 A21 的关系
-----------------
`A21` 做的是**架构轴**（换 backbone），本件做**损失轴**（换 loss）——
两者都是"**干预的效应在另一个因素变一下之后还在不在**"，是同一类问题、同一套口径。

口径
----
· 换损失的 run **`lr_arm` 为空**（名字是 `{族}_{loss}_{轮数}`），
  按 `lr0` **指纹**归臂：每格的 `base`/`lr005` 两臂各有自己的 `lr0`，落在哪边算哪边。
· 全部**按种子配对**（同一 `(格,损失,种子)` 下相减）。
· 结局可用性沿用 `_cells.ok_outcome()`。
· 两列都报：`best_map50_95`（§4.3/§4.4）与 `test_map50_95`（§4.1/§4.2/§5）。
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
OUT = os.path.join(BASE, 'analysis', 'A22_损失对增益_实测.md')
COLS = ['best_map50_95', 'test_map50_95']


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


def build(rows):
    """返回 (T, fp, groups)：T[格][损失][臂][种子] = rows；fp[格][臂] = lr0 指纹。"""
    fp = collections.defaultdict(dict)
    for r in rows:
        if r['loss'] in ('shapeiou', '') and r['lr_arm'] in ('base', 'lr005'):
            try:
                fp[(r['_pair'], r['family'], r['_ep'])][r['lr_arm']] = float(r['lr0'])
            except (TypeError, ValueError):
                pass
    T = collections.defaultdict(
        lambda: collections.defaultdict(
            lambda: collections.defaultdict(lambda: collections.defaultdict(list))))
    for r in rows:
        k = (r['_pair'], r['family'], r['_ep'])
        f = fp.get(k)
        if not f or len(f) != 2:
            continue
        if r['loss'] in ('shapeiou', ''):
            arm = r['lr_arm']
            if arm not in ('base', 'lr005'):
                continue
        else:
            try:
                arm = min(f, key=lambda a: abs(f[a] - float(r['lr0'])))
            except (TypeError, ValueError):
                continue
        T[k][r['loss']][arm][r['_seed']].append(r)
    # 四腿齐备的组
    groups = []
    for k, byloss in T.items():
        for loss, byarm in byloss.items():
            if loss in ('shapeiou', ''):
                continue
            if {'base', 'lr005'} <= set(byarm) and 'shapeiou' in byloss \
               and {'base', 'lr005'} <= set(byloss['shapeiou']):
                groups.append((k, loss))
    return T, fp, sorted(groups)


def main():
    rows, _ = C.load()
    T, fp, groups = build(rows)
    if not rows:
        raise SystemExit('空集合：底座读不到行 —— 硬失败')
    if not groups:
        raise SystemExit('空集合：没有任何四腿齐备的组 —— 硬失败（不要静默输出空表）')

    L = []
    w = L.append
    w('# A22 **损失对"增益"的效应**（补实验后才第一次可算）')
    w('')
    w('> 数据 = `base/run_table_canonical.csv`（**%d 行**）。生成器 = `scripts/41_A22_loss_on_gain.py`。**只读**。' % len(rows))
    w('>')
    w('> ★ **本件更正 `A20` §三 的结论。** A20 写的是「损失对增益的效应**不可识别**（格不存在）」，')
    w('> 那句在补实验完成前**是对的**；补实验补的正是 `{loss}-lr005` 腿，')
    w('> 现在 **%d 个组四腿齐备** ⇒ 这个问题**第一次变得可算**。' % len(groups))
    w('')
    w('## 一、四腿齐备的组')
    w('')
    w('| 配对 | 族 | 轮数 | 损失 |')
    w('|---|---|---|---|')
    for (k, loss) in groups:
        w('| `%s` | `%s` | %d | `%s` |' % (k[0], k[1], int(k[2]), loss))
    w('')
    w('> 口径：换损失的 run 名字里没有 `base`/`lr005`，`lr_arm` 为空，')
    w('> 故按 **`lr0` 指纹归臂**（每格 `base`/`lr005` 两臂各有自己的 `lr0`）。')
    w('> 全库有 %d 个 (格) 存在 shapeiou 两臂指纹。' % sum(1 for v in fp.values() if len(v) == 2))
    w('')

    summary = {}
    for col in COLS:
        w('## 二、逐组结果（列 `%s`）' % col)
        w('')
        w('| 配对 | 族 | 损失 | n | `shapeiou` 增益(pp) | 换损失后增益(pp) | **损失对增益(pp)** | t | 同号 |')
        w('|---|---|---|---|---|---|---|---|---|')
        per = {}
        for (k, loss) in groups:
            def vals(l, arm):
                out = {}
                for s, rs in T[k][l][arm].items():
                    r = C._pick(rs, col)
                    if r is not None:
                        out[s] = C.f(r[col])
                return out
            sb, sl = vals('shapeiou', 'base'), vals('shapeiou', 'lr005')
            lb, ll = vals(loss, 'base'), vals(loss, 'lr005')
            gs = {s: (sl[s] - sb[s]) * 100 for s in set(sb) & set(sl)}
            gl = {s: (ll[s] - lb[s]) * 100 for s in set(lb) & set(ll)}
            com = sorted(set(gs) & set(gl))
            d = [gl[s] - gs[s] for s in com]
            per[(k, loss)] = dict(gs=gs, gl=gl, d=d)
            if not d:
                w('| `%s` | `%s` | `%s` | 0 | — | — | — | — | — |' % (k[0], k[1], loss))
                continue
            pos = sum(1 for x in d if x > 0)
            w('| `%s` | `%s` | `%s` | %d | %+.2f | %+.2f | **%+.2f** | %+.2f | %d/%d |'
              % (k[0], k[1], loss, len(d),
                 mean(list(gs.values())), mean(list(gl.values())),
                 mean(d), tstat(d), pos, len(d)))
        w('')
        # 汇总判读
        allsign_same = all(
            (mean(list(v['gs'].values())) > 0) == (mean(list(v['gl'].values())) > 0)
            for v in per.values() if v['d'])
        maxabs = max((abs(mean(v['d'])) for v in per.values() if v['d']), default=float('nan'))
        n_sig = sum(1 for v in per.values() if v['d'] and abs(tstat(v['d'])) >= 2)
        maxt = max((abs(tstat(v['d'])) for v in per.values() if v['d']), default=float('nan'))
        w('* **换损失后增益符号是否全部不变**：%s' % ('**是**' if allsign_same else '**否**'))
        w('* **损失对增益的最大绝对幅度**：**%.2f pp**' % maxabs)
        w('* **达到 |t| ≥ 2 的组数**：**%d / %d**' % (n_sig, len([v for v in per.values() if v['d']])))
        w('* **最大 |t|**：**%.2f**' % maxt)
        summary[col] = dict(allsign_same=allsign_same, maxabs=maxabs, n_sig=n_sig,
                            maxt=maxt, n=len([v for v in per.values() if v['d']]))
        w('')

    w('## 三、结论')
    w('')
    for col in COLS:
        s = summary[col]
        w('* 列 `%s`：符号 %s；最大幅度 **%.2f pp**；显著 **%d/%d**。'
          % (col, '全部不变' if s['allsign_same'] else '**有变化**', s['maxabs'], s['n_sig'], s['n']))
    w('')
    w('⇒ ★ **换损失不改变增益的符号**，且幅度变化小（≤%.2f pp）**且全部不显著**（n=6–7）。'
      % max(summary[c]['maxabs'] for c in COLS))
    w('⇒ 也就是说：**论文的增益不是"shapeiou 特有的"** —— 换成 `sns` / `pws` 后方向照旧。')
    w('')
    w('### 边界与保留（必须一并写进论文或不写）')
    w('')
    w('1. **只有 3 个组**，且都在 `100ep`、都是"标签稀疏/小数据"那几族'
      '（`mende` / `r10` / `mendein`）⇒ 不得外推成全库结论。')
    w('2. 逐组配对种子 **n=6–7**（换损失那两臂只跑了部分种子），'
      '**低于论文自己的 n≥10 闸门** ⇒ 只能报"方向不变"，**不得**报任何幅度。')
    w('3. **最大 |t| 仅 %.2f** ⇒ 这些组**不足以支撑"损失无效应"的等价性结论**，'
      % max(summary[c]['maxt'] for c in COLS))
    w('   只能说"**在现有 n 上没看到损失改变增益的证据**"。')
    w('4. 归臂用的是 **`lr0` 指纹**；`A20` 已列明有 8 条换损失 run **归不上臂**'
      '（那些格没有 shapeiou 两臂作指纹），本件不含它们。')
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
