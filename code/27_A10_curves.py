# -*- coding: utf-8 -*-
"""27_A10_curves.py —— **A10：多轮数曲线（形状）**

## 为什么

`A9` 只比**端点**（最短 vs 最长轮数），把中间点丢掉了；而 §4.2 的主题恰恰是**曲线的形状**
（"第四个点 stops falling"这类论断只能从形状看出来）。
本件把底座里**所有 ≥3 个可用轮数点**的 (配对, 族, 预算) 系列的完整曲线列出来。

## 口径（与 A6/A9 一致）

* 增益 = 逐种子 `(lr005 − base)`，pp，列 `test_map50_95`；格键含 `family`；
* **Δ = 长预算 − 短预算**（与 §4.1 一致，负号 = 支持主线）；
* 每点给 n / 均值 / t；相邻步给逐种子配对的差。
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
    w('# A10 多轮数曲线（形状）')
    w()
    w('> 数据 `base/run_table_canonical.csv`；口径见脚本头。增益 = 逐种子 `(lr005−base)`，pp，`test_map50_95`。')
    w('> **Δ = 长预算 − 短预算**（负号 = 支持主线）。只列**≥3 个可用轮数点**的系列。')
    w()

    ser = collections.defaultdict(dict)
    for (p, f, lb, ep) in G:
        g = gain_map(G, (p, f, lb, ep))
        if len(g) >= MIN_N:
            ser[(p, f, lb)][int(ep)] = g

    multi = {k: v for k, v in ser.items() if len(v) >= 3}
    w('共 **%d** 个系列满足"≥%d 个可用轮数点"（底座全部 (配对,族,预算) 组合里）。' % (len(multi), 3))
    w()
    w('| 配对 | 族 | 预算 | 轮数点 | 起点 n | 终点 n | 端点差(pp) | t | 形状 |')
    w('|---|---|---|---|---|---|---|---|---|')
    detail = []
    for k in sorted(multi, key=str):
        v = multi[k]
        eps = sorted(v)
        g0, g1 = v[eps[0]], v[eps[-1]]
        common = sorted(set(g0) & set(g1))
        dv = [g1[s] - g0[s] for s in common]
        means = [st.mean(v[e].values()) for e in eps]
        inc = all(means[i] <= means[i + 1] for i in range(len(means) - 1))
        dec = all(means[i] >= means[i + 1] for i in range(len(means) - 1))
        shape = '**单调递减**' if dec else ('**单调递增**' if inc else '非单调')
        w('| `%s` | `%s` | %s%% | %s | %d | %d | **%+.3f** | %+.2f | %s |'
          % (k[0], k[1], k[2], '/'.join(str(e) for e in eps),
             len(g0), len(g1), st.mean(dv) if dv else float('nan'),
             tstat(dv), shape))
        detail.append((k, eps, v, means, shape))
    w()

    w('## 逐系列明细（每点 n / 均值 / t，以及相邻步的逐种子配对差）')
    w()
    for k, eps, v, means, shape in detail:
        w('### `%s` / `%s` · 预算 %s%% · %s' % (k[0], k[1], k[2], shape))
        w()
        w('| 轮数 | n | 增益(pp) | t |')
        w('|---|---|---|---|')
        for e in eps:
            vals = list(v[e].values())
            w('| %d | %d | **%+.3f** | %+.2f |' % (e, len(vals), st.mean(vals), tstat(vals)))
        w()
        w('| 相邻步 | n | Δ增益(pp) | t | 更少 |')
        w('|---|---|---|---|---|')
        for i in range(len(eps) - 1):
            a, b = v[eps[i]], v[eps[i + 1]]
            common = sorted(set(a) & set(b))
            if not common:
                continue
            dv = [b[s] - a[s] for s in common]
            w('| %d→%d | %d | **%+.3f** | %+.2f | %d/%d |'
              % (eps[i], eps[i + 1], len(dv), st.mean(dv), tstat(dv),
                 sum(1 for x in dv if x < 0), len(dv)))
        w()

    w('## 判读')
    w()
    w('* 4 个系列里，`smoke→sfchd/b2` 与 `shwd2sf→sfchd/b2` 的**预算都是 20%%**，'
      '与 §4.2 已报的 `smoke→SFCHD` / `shwd2sf` 是**不同批次**（族不同）⇒ 可作**同配对的第二次独立扫描**。')
    w('* `dota15→dota15/g3clean` 有 **4 个点（50/100/200/400）**，是底座里**跨度最长**的轮数系列。')
    w('* ⚠ 每点 n 多为 3–5；按 `A5_种子方差.md` §3 的闸门，**只有逐种子全同号的相邻步才可读方向**。')
    w()
    w('### 用 A11 闸门逐条判（`analysis\A11_种子闸门标定.md`）')
    w()
    w('| 系列 | 相邻步 | n | Δ | t | 更少 | 过闸门？ |')
    w('|---|---|---|---|---|---|---|')
    for k, eps, v, means, shape in detail:
        for i in range(len(eps) - 1):
            a_, b_ = v[eps[i]], v[eps[i + 1]]
            common = sorted(set(a_) & set(b_))
            if not common:
                continue
            dv = [b_[s] - a_[s] for s in common]
            tt = tstat(dv)
            nlow = sum(1 for x in dv if x < 0)
            gate = (len(dv) >= 10) or (len(dv) >= 5 and (nlow == 0 or nlow == len(dv))) or (abs(tt) >= 4)
            w('| `%s`/%s | %d→%d | %d | **%+.3f** | %+.2f | %d/%d | %s |'
              % (k[1], k[2], eps[i], eps[i + 1], len(dv), st.mean(dv), tt, nlow, len(dv),
                 '✅ 可报' if gate else '⛔ 不可报'))
    w()
    w('* ⇒ 4 个系列共 11 个相邻步，**过闸门的只有 `smoke→sfchd/b2` 的前两步**'
      '（30→50：n=9、**9/9 更低**；50→100：n=10、**10/10**）与它的第三步（|t|=2.53 但 n=10）。')
    w('* ⚠ **`dota15→dota15/g3clean` 的驼峰（+0.572→+1.034→+0.968→+0.650，n=5）三步全部不过闸门**'
      '（相邻步 1/5、4/5、4/5 同号，|t| 最大 2.31）⇒ **只能作为观察，不得写进正文**。')

    os.makedirs(OUT, exist_ok=True)
    io.open(os.path.join(OUT, 'A10_多轮数曲线_形状.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    print()
    print('输出 -> %s' % os.path.join(OUT, 'A10_多轮数曲线_形状.md'))


if __name__ == '__main__':
    main()
