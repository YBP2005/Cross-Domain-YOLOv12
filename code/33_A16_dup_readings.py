# -*- coding: utf-8 -*-
"""33_A16_dup_readings.py —— **A16：多读数歧义的量化**

## 为什么

`base/数据字典.md` §十.4 定了一条规则：`sio_b_results.csv` 是**追加写**，
同一 run 可能有多行读数，**底座取首次**（与论文 §4.1 逐位吻合）。有 31 条 run 带 `dup_test_line=1`。

但**从来没有人算过"换一种取法会差多少"**。如果差得多，这条规则就是个**脆弱点**；
如果差得少，这条规则就只是个**约定**。本件把它量化。

## 数据源（四份原始终端文件，本地只读）

* A：`raw/A_aux_20260929/sio_b_results.csv`（752 行）、`raw/P1_ext_20261001/A_sio_b_results.csv`（147 行）
* B：`E:\\workplace\\AB机实验文件夹\\B_csv_20260930\\workspace\\sio_b_results.csv`（1089 行）、
  `raw/P1_ext_20261001/B_sio_b_results.csv`（64 行）

格式**无表头**：`name,loss,epochs,map50,map(=map50-95),mp,mr`。
"""
import io
import os
import sys
import statistics as st
import collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _cells as C

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.dirname(BASE)
SRC = [
    ('A', os.path.join(BASE, 'raw', 'A_aux_20260929', 'sio_b_results.csv')),
    ('B', r'E:\workplace\AB机实验文件夹\B_csv_20260930\workspace\sio_b_results.csv'),
    ('A', os.path.join(BASE, 'raw', 'P1_ext_20261001', 'A_sio_b_results.csv')),
    ('B', os.path.join(BASE, 'raw', 'P1_ext_20261001', 'B_sio_b_results.csv')),
]
OUT = os.path.join(BASE, 'analysis')
L = []


def w(s=''):
    L.append(s)


def load():
    """run -> [ (machine, map50, map, mp, mr) ]，按文件与行序保留全部读数。"""
    d = collections.defaultdict(list)
    for m, path in SRC:
        if not os.path.isfile(path):
            continue
        for line in io.open(path, encoding='utf-8', errors='replace'):
            p = line.rstrip('\n').split(',')
            if len(p) < 7:
                continue
            try:
                rec = (m, float(p[3]), float(p[4]), float(p[5]), float(p[6]))
            except ValueError:
                continue
            d[p[0]].append(rec)
    return d


def main():
    rows, G = C.load()
    d = load()
    w('# A16 多读数歧义的量化')
    w()
    w('> 数据源：四份 `sio_b_results.csv`（无表头，`name,loss,epochs,map50,map,mp,mr`）。')
    w('> 底座规则 = **取首次**（`数据字典` §十.4）。本件量化"改成取末次"会差多少。')
    w()

    multi = {k: v for k, v in d.items() if len(v) > 1}
    w('## 一、总览')
    w()
    w('* 出现的 unique run：**%d**；其中**多读数 run：%d**；总行数 **%d**。'
      % (len(d), len(multi), sum(len(v) for v in d.values())))
    w('* 与底座对照：底座标了 `dup_test_line=1` 的 run **%d** 个。'
      % len({r['run'] for r in rows if r.get('dup_test_line') in ('1', 1)}))
    w()

    # 逐多读数 run：首 vs 末
    dl = []
    for k, v in multi.items():
        first, last = v[0], v[-1]
        dl.append((k, len(v), first[2], last[2], (last[2] - first[2]) * 100))
    w('## 二、逐 run：首次读数 vs 末次读数（`map50-95`）')
    w()
    w('| run | 读数数 | 首次 | 末次 | 差(pp) |')
    w('|---|---|---|---|---|')
    for k, n, a, b, dd in sorted(dl, key=lambda x: -abs(x[4])):
        w('| `%s` | %d | %.4f | %.4f | **%+.3f** |' % (k, n, a, b, dd))
    w()
    ads = [abs(x[4]) for x in dl]
    if ads:
        w('* 绝对差：中位 **%.3f pp**、均值 %.3f、最大 **%.3f pp**（n=%d）'
          % (st.median(ads), st.mean(ads), max(ads), len(ads)))
        w('* 差 > 0.30 pp 的 run：**%d** 个；> 1.0 pp 的：**%d** 个'
          % (sum(1 for x in ads if x > 0.30), sum(1 for x in ads if x > 1.0)))
    w()

    # 格级影响：用 首/末 两套读数重算增益
    w('## 三、★ 格级影响：取"首次" vs 取"末次"')
    w()
    def gain_with(G, k, pick):
        arms = G.get(k)
        if not arms:
            return None
        out = {}
        for s, by in arms.items():
            def val(rs):
                ok = [x for x in rs if C.f(x.get('test_map50_95')) is not None and C.ok_outcome(x)]
                if not ok:
                    return None
                if pick == 'base':
                    return C.f(ok[0]['test_map50_95'])
                # 末次：用原始 sio 里该 run 的最后一条（若无多读数则同首次）
                r = ok[0]
                v = d.get(r['run'])
                return v[-1][2] if v else C.f(r['test_map50_95'])
            b = val(by.get('base', []))
            l = val(by.get('lr005', []))
            if b is not None and l is not None:
                out[s] = (l - b) * 100
        return out

    cells = [k for k in G if any(
        C._pick(G[k][s].get(a, []), 'test_map50_95') is not None
        for s in G[k] for a in ('base', 'lr005'))]
    changed = []
    for k in cells:
        g1 = gain_with(G, k, 'base')
        g2 = gain_with(G, k, 'last')
        if not g1 or not g2:
            continue
        common = sorted(set(g1) & set(g2))
        if len(common) < 3:
            continue
        m1, m2 = st.mean([g1[s] for s in common]), st.mean([g2[s] for s in common])
        if abs(m1 - m2) > 1e-9:
            changed.append((k, len(common), m1, m2, m2 - m1))
    w('* 受影响的格（两种取法给出不同均值）：**%d / %d**' % (len(changed), len(cells)))
    w()
    if changed:
        w('| 格 | n | 取首次 | 取末次 | 差(pp) | 是否变号 |')
        w('|---|---|---|---|---|---|')
        for k, n, m1, m2, dd in sorted(changed, key=lambda x: -abs(x[4])):
            w('| `%s`/`%s` %s %s | %d | **%+.3f** | **%+.3f** | %+.3f | %s |'
              % (k[0], k[1], k[2], k[3], n, m1, m2, dd,
                 '⚠ **变号**' if (m1 > 0) != (m2 > 0) else '否'))
        w()
    w('## 四、结论')
    w()
    if changed:
        worst = max(changed, key=lambda x: abs(x[4]))
        w('* 规则"取首次"**不是无所谓的约定**：它改变 **%d** 个格的均值，最大一处 **%+.3f pp**（`%s`/%s %s %s）。'
          % (len(changed), worst[4], worst[0][0], worst[0][1], worst[0][2], worst[0][3]))
        signflip = [x for x in changed if (x[2] > 0) != (x[3] > 0)]
        w('* 其中**变号**的格：**%d** 个%s'
          % (len(signflip), '（' + '；'.join('`%s`/%s %s %s' % (x[0][0], x[0][1], x[0][2], x[0][3]) for x in signflip) + '）' if signflip else ''))
        w('* ⇒ 论文凡引用这些格，**必须写明"取首次读数"**（`数据字典` §十.4 已有此纪律，'
          '本件给出了"不写会错多少"的量化）。')
    else:
        w('* **两种取法给出完全相同的格级均值** ⇒ 该规则在这批数据上**不影响任何结论**，'
          '只是一个可复现性约定。')

    os.makedirs(OUT, exist_ok=True)
    io.open(os.path.join(OUT, 'A16_多读数歧义.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L[:80]))
    print('...')
    print('输出 -> %s' % os.path.join(OUT, 'A16_多读数歧义.md'))


if __name__ == '__main__':
    main()
