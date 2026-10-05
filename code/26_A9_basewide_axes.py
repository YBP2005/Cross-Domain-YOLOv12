# -*- coding: utf-8 -*-
"""26_A9_basewide_axes.py —— **A9：全域预算轴扫描（复制普查）**

## 动机

`analysis\\A6_标签预算轴.md` 只覆盖 **8 个 (配对, 族)**，而底座里有 **115 个组**。
2026-10-01 盘点：63 个"≥8 run"的组里 **55 个从未进过任何轴分析**，合计 **1307 个 run**。
其中已有现成的**多轮数系列**（例：`smoke→sfchd / b2` 有 30/50/100/200/300 五个轮数点；
`dota15→dota15 / g3clean` 有 50/100/200/400）。

⇒ 本件回答一个论文级问题：**"预算越大、增益越小/反号"这条主线，在底座里有多少个独立配对复现？**
   这决定它能被写成"普遍规律"还是"两个例子"。

## 口径（与 A6 逐条一致）

* 增益 = **逐种子 `(lr005 − base)`**，单位 **pp**，列 = **test 侧 `test_map50_95`**；
* 格的键 = **(配对, 族, 预算来自 dataset 名, epochs)**；**族**= run 名首段（批次），不是架构；
* 端点差**逐种子配对**（同种子求增益再作差），不是"先求均值再作差"；
* ★★ **符号约定（务必先读）**：本件一律 **Δ = 增益(长预算) − 增益(短预算)**，
  所以 **负号 = 支持论文主线**（"预算越大、增益越小"）。
  ⚠ **新稿 §4.1 用的是同一约定**（其 "Δ gain" 行 = 200ep − 100ep = −1.143）；
  新稿 §4.2 的散文**原先用相反约定**（写 "endpoint difference +2.161"；30ep=+3.656、200ep=+1.495，
  长−短应为 **−2.161**）—— **2026-10-01 已修正为负号**，并加了符号守卫与列口径守卫
  （见 `deliver\新稿_缺陷_符号约定_20261001.md`、`deliver\新稿_缺陷_列口径与s50_20261001.md`）。
  本件读数与 §4.1 一致、与 §4.2 散文**反号**，不是矛盾；
* 只计入**两臂都有**的种子。
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
MIN_N = 3
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'analysis')
L = []


def w(s=''):
    L.append(s)


def tstat(v):
    if len(v) < 2:
        return float('nan')
    sd = st.stdev(v)
    return st.mean(v) / (sd / math.sqrt(len(v))) if sd > 0 else float('nan')


def gain_map(G, k):
    """(种子 -> 增益 pp)，只保留两臂都取到读数的种子。"""
    arms = G.get(k)
    if not arms:
        return {}
    out = {}
    for s, byarm in arms.items():
        b = C._pick(byarm.get('base', []), KEY)
        l = C._pick(byarm.get('lr005', []), KEY)
        if b is not None and l is not None:
            out[s] = (C.f(l[KEY]) - C.f(b[KEY])) * 100
    return out


def endpoint(a, b):
    """逐种子配对：b − a。"""
    common = sorted(set(a) & set(b))
    if len(common) < MIN_N:
        return None
    v = [b[s] - a[s] for s in common]
    return dict(n=len(v), mean=st.mean(v), t=tstat(v),
                neg=sum(1 for x in v if x < 0))


def main():
    rows, G = C.load()
    w('# A9 全域预算轴扫描（复制普查）')
    w()
    w('> 数据 = `base/run_table_canonical.csv`，**%d 行 / %d 个唯一 run**。'
      % (len(rows), len({r['run'] for r in rows})))
    w('> 口径：增益 = 逐种子 `(lr005−base)`，pp，列 `test_map50_95`；端点差**逐种子配对**。')
    w('> ★ **A6 只覆盖 8 个 (配对,族)**；本件扫**全部**可配对的组。')
    w()

    grp = collections.defaultdict(set)
    for (pair, fam, lb, ep) in G:
        grp[(pair, fam)].add((lb, ep))

    # ★ 2026-10-01 修一个**压低复制的 bug**：端点不能取"名义最短/最长"，
    #   要取"**实际配对读数够 MIN_N 的最宽区间**"。
    #   实例：`smoke→sfchd / b2`（123 run、轮数 30/50/100/200/300）名义跨度是 30→300，
    #   但 300ep 那个格 base/lr005 都是 0 个可用读数 ⇒ 旧写法**整组被丢弃**，
    #   而它 30 vs 200 本来完全可算。`shwd2sf→sfchd / shwd2sf` 同理（200ep 只有 1 个）。
    gm = {}

    def G_(pair, fam, lb, ep):
        k = (pair, fam, lb, ep)
        if k not in gm:
            gm[k] = gain_map(G, k)
        return gm[k]

    def widest(pair, fam, fixed, vals, is_epoch):
        """在 vals 里取"两端都够 MIN_N"的最宽区间。

        `G_(pair, fam, lb, ep)`：**轮数轴**变化的是 `ep`（`lb` 固定），
        **标签轴**变化的是 `lb`（`ep` 固定）—— 两轴的固定/变化维必须分清。
        """
        ok = []
        for v in vals:
            g = G_(pair, fam, fixed, v) if is_epoch else G_(pair, fam, v, fixed)
            if len(g) >= MIN_N:
                ok.append(v)
        if len(ok) < 2:
            return None
        return min(ok), max(ok)

    epoch_rows, label_rows = [], []
    for (pair, fam), cells in grp.items():
        by_lb = collections.defaultdict(set)
        for lb, ep in cells:
            by_lb[lb].add(int(ep))
        for lb, eps in by_lb.items():
            sp = widest(pair, fam, lb, sorted(eps), True)
            if not sp:
                continue
            e_lo, e_hi = sp
            r = endpoint(G_(pair, fam, lb, e_lo), G_(pair, fam, lb, e_hi))
            if r:
                r.update(pair=pair, fam=fam, lb=lb, e_lo=e_lo, e_hi=e_hi)
                epoch_rows.append(r)
        by_ep = collections.defaultdict(set)
        for lb, ep in cells:
            if lb is not None:
                by_ep[int(ep)].add(lb)
        for ep, lbs in by_ep.items():
            sp = widest(pair, fam, ep, sorted(lbs), False)
            if not sp:
                continue
            l_lo, l_hi = sp
            r = endpoint(G_(pair, fam, l_lo, ep), G_(pair, fam, l_hi, ep))
            if r:
                r.update(pair=pair, fam=fam, ep=ep, l_lo=l_lo, l_hi=l_hi)
                label_rows.append(r)

    for title, rs, is_epoch in (('一、轮数轴（同一预算，最长轮数 − 最短轮数）', epoch_rows, True),
                                ('二、标签轴（同一轮数，最高预算 − 最低预算）', label_rows, False)):
        w('## %s' % title)
        w()
        if not rs:
            w('（无可配对项）'); w(); continue
        neg = sum(1 for r in rs if r['mean'] < 0)
        sig = [r for r in rs if abs(r['t']) >= 2]
        sig_neg = sum(1 for r in sig if r['mean'] < 0)
        w('* 可配对端点差 **%d** 条（两端各至少 %d 个种子配对）' % (len(rs), MIN_N))
        w('* **负向**（增益随预算增大而下降）：**%d / %d = %.0f%%**'
          % (neg, len(rs), 100.0 * neg / len(rs)))
        w('* **显著**（|t|≥2）：**%d** 条，其中负向 **%d** 条' % (len(sig), sig_neg))
        w()
        w('| 配对 | 族 | 预算 | 轮数 短→长 | n | 端点差(pp) | t | 更低 |'
          if is_epoch else '| 配对 | 族 | 轮数 | 预算 低→高 | n | 端点差(pp) | t | 更低 |')
        w('|---|---|---|---|---|---|---|---|')
        for r in sorted(rs, key=lambda x: x['mean']):
            if is_epoch:
                w('| `%s` | `%s` | %s%% | %d→%d | %d | **%+.3f** | %+.2f | %d/%d |'
                  % (r['pair'], r['fam'], r['lb'], r['e_lo'], r['e_hi'], r['n'], r['mean'], r['t'], r['neg'], r['n']))
            else:
                w('| `%s` | `%s` | %dep | %d%%→%d%% | %d | **%+.3f** | %+.2f | %d/%d |'
                  % (r['pair'], r['fam'], r['ep'], r['l_lo'], r['l_hi'], r['n'], r['mean'], r['t'], r['neg'], r['n']))
        w()

    w('## 三、★ 两条轴的**多数符号相反**（本件最主要的发现）')
    w()
    if epoch_rows and label_rows:
        en = sum(1 for r in epoch_rows if r['mean'] < 0)
        ln = sum(1 for r in label_rows if r['mean'] < 0)
        w('| 轴 | 条目 | 负向 | 负向占比 | 显著(|t|≥2) | 显著负向 |')
        w('|---|---|---|---|---|---|')
        w('| **轮数轴**（30→100ep 等） | %d | **%d** | **%.0f%%** | %d | %d |'
          % (len(epoch_rows), en, 100.0 * en / len(epoch_rows),
             sum(1 for r in epoch_rows if abs(r['t']) >= 2),
             sum(1 for r in epoch_rows if abs(r['t']) >= 2 and r['mean'] < 0)))
        w('| **标签轴**（10%%→50%%） | %d | **%d** | **%.0f%%** | %d | %d |'
          % (len(label_rows), ln, 100.0 * ln / len(label_rows),
             sum(1 for r in label_rows if abs(r['t']) >= 2),
             sum(1 for r in label_rows if abs(r['t']) >= 2 and r['mean'] < 0)))
        w()
        w('⇒ **轮数轴以负向为主、标签轴以正向为主** —— 两条轴的多数符号**相反**。')
        w('  这比 `A6` §4 那条"个别配对反号"更强：它是在**全部可配对条目**上的系统性差异。')
        w('  ⚠ 但**不是普遍规律**：两条轴各自都有相当比例的反例（见上两表）。')
        w()
    w('## 四、按证据强度分层（**只有这一层能当结论**）')
    w()
    def tier(rs, name):
        strong = [r for r in rs if r['n'] >= 10]
        unan = [r for r in rs if r['n'] >= 5 and (r['neg'] == 0 or r['neg'] == r['n'])]
        w('**%s**' % name)
        w()
        w('* `n≥10`：**%d** 条 —— %s' % (len(strong),
          ('；'.join('%s/%s %s %+.3f(t=%+.1f)' % (r['pair'], r['fam'],
                      ('%s→%s' % (r.get('e_lo'), r.get('e_hi'))) if 'e_lo' in r else ('%s%%→%s%%' % (r.get('l_lo'), r.get('l_hi'))),
                      r['mean'], r['t']) for r in strong) if strong else '无')))
        w('* `n≥5 且逐种子全同号`：**%d** 条' % len(unan))
        for r in unan:
            w('  * `%s`/`%s` %s n=%d **%+.3f**（t=%+.2f，%s）' % (
                r['pair'], r['fam'],
                ('%d→%dep' % (r['e_lo'], r['e_hi'])) if 'e_lo' in r else ('%d%%→%d%% %dep' % (r['l_lo'], r['l_hi'], r['ep'])),
                r['n'], r['mean'], r['t'], '全负' if r['neg'] == r['n'] else '全正'))
        w()
    tier(epoch_rows, '轮数轴')
    tier(label_rows, '标签轴')

    w('## 七、★ 用 A11 的闸门回筛：**哪些条目的方向真的可报**')
    w()
    w('> 依据 `analysis\\A11_种子闸门标定.md`（48 个 n≥8 格、数千个 3 子集的实测校准）：')
    w('> 全格 `|t|≥4` ⇒ 3 子集方向正确率 **99–100%**；全格 `|t|<2` ⇒ 仅 **66%**、全同号率 **25%** ⇒ **不得报方向**。')
    w('>')
    w('> 据此给每条定级（**满足其一即为"可报方向"**）：① `n ≥ 10`；② `n ≥ 5` 且**逐种子全同号**；③ `|t| ≥ 4`。')
    w()

    def _tier(r):
        if r['n'] >= 10:
            return 'A'
        if r['n'] >= 5 and (r['neg'] == 0 or r['neg'] == r['n']):
            return 'A'
        return 'A' if abs(r['t']) >= 4 else 'B'

    for name, rs in (('轮数轴', epoch_rows), ('标签轴', label_rows)):
        A = [r for r in rs if _tier(r) == 'A']
        B = [r for r in rs if _tier(r) == 'B']
        w('**%s**：✅可报方向 **%d** 条 / ⛔只报均值+区间 **%d** 条' % (name, len(A), len(B)))
        if A:
            na = sum(1 for r in A if r['mean'] < 0)
            w('* ✅可报的 %d 条里，负向 **%d** 条（**%.0f%%**）⇒ **这一组才是可引用的分母**'
              % (len(A), na, 100.0 * na / len(A)))
        if B:
            nb = sum(1 for r in B if r['mean'] < 0)
            w('* ⛔不可报方向的 %d 条里，负向 %d 条（%.0f%%）—— **这组数字不得引用**'
              % (len(B), nb, 100.0 * nb / max(1, len(B))))
        w()
        w('| 配对 | 族 | 端点 | n | 端点差(pp) | t | 更低 | 定级 | 理由 |')
        w('|---|---|---|---|---|---|---|---|---|')
        for r in sorted(rs, key=lambda x: (_tier(x) != 'A', x['mean'])):
            span = ('%d→%dep' % (r['e_lo'], r['e_hi'])) if 'e_lo' in r \
                else ('%d%%→%d%% %dep' % (r['l_lo'], r['l_hi'], r['ep']))
            t_ = _tier(r)
            why = ('n≥10' if r['n'] >= 10 else
                   ('n≥5 且全同号' if r['n'] >= 5 and (r['neg'] == 0 or r['neg'] == r['n']) else
                    ('|t|≥4' if abs(r['t']) >= 4 else '—')))
            w('| `%s` | `%s` | %s | %d | **%+.3f** | %+.2f | %d/%d | %s | %s |'
              % (r['pair'], r['fam'], span, r['n'], r['mean'], r['t'], r['neg'], r['n'],
                 '✅ 可报' if t_ == 'A' else '⛔ 不可报', why))
        w()
    w('> ⇒ **第五节的总计（全部条目、负向占比）包含不可报方向的条目**；')
    w('> 正文若要写"多数为负"，**必须用本节"可报"那一组的分母**。')
    w()

    w('## 五、总结')
    w()
    allr = epoch_rows + label_rows
    if allr:
        neg = sum(1 for r in allr if r['mean'] < 0)
        sig = [r for r in allr if abs(r['t']) >= 2]
        w('* 两条轴合计可配对端点差 **%d** 条，其中**负向 %d 条（%.0f%%）**。'
          % (len(allr), neg, 100.0 * neg / len(allr)))
        w('* 达 **|t|≥2** 的 **%d** 条中，负向 **%d** 条。'
          % (len(sig), sum(1 for r in sig if r['mean'] < 0)))
        w('* 轮数轴 **%d** 条 / 标签轴 **%d** 条。' % (len(epoch_rows), len(label_rows)))
        w()

    w('## 六、★ 独立性计数（**别把"条目数"读成"独立复制数"**）')
    w()
    if allr:
        def paircount(rs):
            return len({(r['pair'], r['fam']) for r in rs})
        ep_pairs = paircount(epoch_rows)
        lb_pairs = paircount(label_rows)
        all_pairs = paircount(allr)
        w('| 层 | 条目数 | **独立 (配对,族) 数** |')
        w('|---|---|---|')
        w('| 轮数轴 | %d | **%d** |' % (len(epoch_rows), ep_pairs))
        w('| 标签轴 | %d | **%d** |' % (len(label_rows), lb_pairs))
        w('| 合计 | %d | **%d** |' % (len(allr), all_pairs))
        w()
        # 每对"多数方向"只算一次
        agg = collections.defaultdict(list)
        for r in allr:
            agg[(r['pair'], r['fam'])].append(r['mean'])
        maj_neg = sum(1 for k, v in agg.items() if st.mean(v) < 0)
        w('* 把同一个 (配对,族) 的多条条目**按均值合并成一次复制**后：'
          '**%d 个独立组，其中 %d 个为负向（%.0f%%）**。'
          % (len(agg), maj_neg, 100.0 * maj_neg / max(1, len(agg))))
        w('* ⇒ 摘要里若写"在 N 个配对上复现"，**N 应当用本表的独立组数，不是条目数**。')
        w('* ⚠ 分母还包含**同一配对的不同族**（如 `a0` / `b2` / `la` 都是 `shwd*→sfchd`），'
          '它们共享数据集，**不是完全独立的域**；若要最保守的计数，应按**配对**去重。')
        npair = len({r['pair'] for r in allr})
        w('* 按**配对**（不分族）去重：**%d** 个独立配对。' % npair)
        w()

    w('> ⇒ 论文主线的"复制计数"应以本表为准，而不是只引 `A6` 的 8 个族。')
    w('> ⚠ 但**每条都要看它自己的 n 与符号一致性**（`更低` 列）：'
      '`n=3` 且混合符号的条目，按 `A5_种子方差.md` §3 的闸门**方向不可信** —— '
      '**只有第四节那一层能进正文**。')

    os.makedirs(OUT, exist_ok=True)
    io.open(os.path.join(OUT, 'A9_全域预算轴扫描.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L[:40]))
    print('...')
    print('输出 -> %s' % os.path.join(OUT, 'A9_全域预算轴扫描.md'))


if __name__ == '__main__':
    main()
