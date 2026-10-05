# -*- coding: utf-8 -*-
"""31_A14_quality_census.py —— **A14：数据质量普查（按族的结局与读数完备性）**

## 为什么

前面所有分析（A1–A13）都只关心**数字**，从不区分一个 run 是
`complete` / `early_stop_legit` / `interrupted` / `archive_snapshot`，
也不看它有没有 `args.yaml`、有没有 test 读数、是不是多读数。
`_cells._pick` 在**取值时**做了筛选，但**没有任何地方统计过"这批数据本身有多干净"**。

这是"榨干数据"必须补的一块：它决定**哪条结论建立在完整件上、哪条靠缺件撑着**。

## 口径

逐 run 统计；分组到 (配对, 族)。`test覆盖率` = 有 test 读数的 run / 该组 run 数。
"""
import io
import os
import sys
import collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _cells as C

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'analysis')
L = []


def w(s=''):
    L.append(s)


def main():
    rows, G = C.load()
    w('# A14 数据质量普查（按族的结局与读数完备性）')
    w()
    w('> 数据 `base/run_table_canonical.csv`（**%d 行**）。' % len(rows))
    w('> 目的：说清**每条结论建立在什么样的件上** —— 完整件、早停件、中断件、还是存档件。')
    w()

    # 全库总览
    w('## 一、全库结局构成')
    w()
    oc = collections.Counter(r['outcome'] for r in rows)
    w('| outcome | 行数 | 占比 |')
    w('|---|---|---|')
    for o, n in oc.most_common():
        w('| `%s` | %d | %.1f%% |' % (o, n, 100.0 * n / len(rows)))
    w()
    w('* 有 `args.yaml`：**%d/%d**；有 test 读数：**%d/%d**；带 `dup_test_line=1`（多读数）：**%d**。'
      % (sum(1 for r in rows if r.get('has_args') in ('1', 1, True)), len(rows),
         sum(1 for r in rows if C.f(r.get('test_map50_95')) is not None), len(rows),
         sum(1 for r in rows if r.get('dup_test_line') in ('1', 1))))
    w()

    # 按 (pair, family)
    w('## 二、按 (配对, 族) 的结局构成（只列 ≥8 run 的组）')
    w()
    grp = collections.defaultdict(list)
    for r in rows:
        grp[(r['_pair'], r['family'])].append(r)
    w('| 配对 | 族 | run | complete | early_stop | interrupted | archive | test覆盖 | 多读数 |')
    w('|---|---|---|---|---|---|---|---|---|')
    dirty = []
    for k, rs in sorted(grp.items(), key=lambda x: -len(x[1])):
        if len(rs) < 8:
            continue
        c = collections.Counter(r['outcome'] for r in rs)
        tc = sum(1 for r in rs if C.f(r.get('test_map50_95')) is not None)
        dup = sum(1 for r in rs if r.get('dup_test_line') in ('1', 1))
        w('| `%s` | `%s` | %d | %d | %d | %d | %d | **%.0f%%** | %d |'
          % (k[0], k[1], len(rs), c.get('complete', 0), c.get('early_stop_legit', 0),
             c.get('interrupted', 0), c.get('archive_snapshot', 0),
             100.0 * tc / len(rs), dup))
        if tc < len(rs):
            dirty.append((k, len(rs), tc, len(rs) - tc))
    w()

    w('## 三、★ test 读数不全的组（**这些组的格一定是缺件的**）')
    w()
    if dirty:
        w('| 配对 | 族 | run | 有 test 读数 | 缺 |')
        w('|---|---|---|---|---|')
        for k, tot, tc, miss in sorted(dirty, key=lambda x: -x[3]):
            w('| `%s` | `%s` | %d | %d | **%d** |' % (k[0], k[1], tot, tc, miss))
    else:
        w('（无）')
    w()
    w('* ⇒ 凡是出现在本表的组，其"全格 n=10"的说法都要打问号：'
      '**缺的那几个 run 是缺 `results.csv`、还是只缺 test 行，处置完全不同**（见 `A8_缺口复核.md`）。')
    w()

    w('## 四、判读')
    w()
    tot_miss = sum(x[3] for x in dirty)
    w('* ≥8 run 的组里，共 **%d** 个 run 没有 test 读数 ⇒ 这些 run 在任何 test 侧分析里**都不存在**。' % tot_miss)
    w('* `interrupted` 全库 **%d** 条：它们**没有 test 读数**（eval 未跑到），'
      '但**有 val 侧读数** ⇒ 这就是 `_cells.ok_outcome()` 必须独立于"该列是否非空"的原因。'
      % oc.get('interrupted', 0))
    w('* `archive_snapshot` 全库 **%d** 条：`.incomplete_` 存档件**两种都有**'
      '（跑满但没写 test 行的、与真中断的）⇒ `ok_outcome()` 用**实际轮数**区分，不能用结局标签一刀切。'
      % oc.get('archive_snapshot', 0))
    w('* ⇒ **本普查是"数字之外"的元信息**：它不改变任何已算出的数，'
      '但决定**每条结论该配多强的措辞**。')

    os.makedirs(OUT, exist_ok=True)
    io.open(os.path.join(OUT, 'A14_数据质量普查.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L[:60]))
    print('...')
    print('输出 -> %s' % os.path.join(OUT, 'A14_数据质量普查.md'))


if __name__ == '__main__':
    main()
