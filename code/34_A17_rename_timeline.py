# -*- coding: utf-8 -*-
"""34_A17_rename_timeline.py —— **A17：改名件（`.incomplete_` / `_PARTIAL_`）的时间线与含义**

## 为什么

底座里有 **84 个改名件**（50 个 `.incomplete_<日期>_<时刻>`、34 个 `_PARTIAL_<名>_<时刻>`）。
它们只被当作 `archive_snapshot` / `interrupted` 的**来源标签**用过，**从没被当作一个数据集看过**。
本件回答三件事：
1. 它们**对分析有没有贡献**（有没有 test 读数）？
2. 它们的**时间戳分布**说明什么？
3. **"存档改名"等不等于"被截断"**？
"""
import io
import os
import re
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
    inc = [r for r in rows if '.incomplete_' in r['run'] or r['run'].startswith('_PARTIAL_')]
    w('# A17 改名件的时间线与含义')
    w()
    w('> 数据 `base/run_table_canonical.csv`（%d 行）。' % len(rows))
    w('> 改名件 = run 名含 `.incomplete_<日期>_<时刻>` 或前缀 `_PARTIAL_`（前者 50、后者 34）。')
    w()

    w('## 一、它们对分析有没有贡献？')
    w()
    tc = sum(1 for r in inc if C.f(r.get('test_map50_95')) is not None)
    vc = sum(1 for r in inc if C.f(r.get('best_map50_95')) is not None)
    w('| 项 | 值 |')
    w('|---|---|')
    w('| 改名件行数 | **%d** |' % len(inc))
    w('| **有 test 读数** | **%d** |' % tc)
    w('| 有 val 侧 `best_map50_95` | %d |' % vc)
    w()
    # ★ 2026-10-01 更正：本节原先硬编码"0 个读数"，那是**生成器缺陷**造成的假象 ——
    #   查汇总时用磁盘原始目录名、而汇总记短名 ⇒ 改名件恒查不到（见 `deliver\新稿_缺陷_汇总查名盲区_20261001.md`）。
    #   修好后 %d/%d 个改名件有 test 读数。下面按实际值陈述，不再写死。
    w('* ⇒ 改名件里 **%d / %d = %.0f%%** 有 test 读数（2026-10-01 修复生成器查名缺口后）。'
      % (tc, len(inc), 100.0 * tc / max(len(inc), 1)))
    w('* ⇒ 它们**可以**进入 test 侧分析，且**必须**进入 —— 否则就是无理由地丢种子。'
      '但**单靠改名件补不出任何格**：见下节"零贡献"的实测口径。')
    w('* ⇒ 任何"test 侧 n=10"的说法，要看该格**修好之后**的实际配对数，'
      '不能再用"改名件一律没有读数"去推断缺件。见 `A8_缺口复核.md`。')
    w()

    w('## 二、时间戳分布')
    w()
    dst = collections.Counter()
    hr = collections.Counter()
    for r in inc:
        m = re.search(r'(\d{8})_(\d{6})', r['run'])
        if m:
            dst[m.group(1)] += 1
            hr[m.group(1) + ' ' + m.group(2)[:2] + ':00'] += 1
        else:
            m2 = re.search(r'_(\d{6})$', r['run'])
            dst['(仅时刻，无日期)'] += 1
            if m2:
                hr['(无日期) ' + m2.group(1)[:2] + ':00'] += 1
    w('| 日期 | 改名件数 |')
    w('|---|---|')
    for k, v in sorted(dst.items()):
        w('| `%s` | %d |' % (k, v))
    w()
    w('| 小时桶 | 数 |')
    w('|---|---|')
    for k, v in sorted(hr.items()):
        w('| `%s` | %d |' % (k, v))
    w()
    top = max(hr.items(), key=lambda x: x[1]) if hr else None
    if top:
        w('* 最集中的一小时桶是 **`%s`（%d 个）** ⇒ 改名**不是逐 run 零散发生**，'
          '而是**成批发生**（一次停机/一次存档动作覆盖一批）。' % (top[0], top[1]))
    w()

    w('## 三、★ "存档改名"等不等于"被截断"？')
    w()
    full = [r for r in inc if C.f(r['epochs_actual']) is not None and C.f(r['epochs_nominal']) is not None
            and C.f(r['epochs_actual']) >= C.f(r['epochs_nominal'])]
    w('| 项 | 数 |')
    w('|---|---|')
    w('| 改名件 | %d |' % len(inc))
    w('| 其中**跑满名义轮数**的 | **%d** |' % len(full))
    w('| 其中**未跑满**的 | %d |' % (len(inc) - len(full)))
    w()
    if full:
        w('* **跑满的样例**（证明"改名 ≠ 截断"）：')
        for r in full[:6]:
            w('  * `%s`：`%s/%s` ep，outcome=`%s`'
              % (r['run'][:64], r['epochs_actual'], r['epochs_nominal'], r['outcome']))
    w()
    w('* ⇒ ★★ **存档改名是"来源/治理"分类，不是"完整度"分类**。'
      '这正是 `_cells.ok_outcome()` 必须用**实际轮数**（而不是结局标签）来判可用的原因：'
      '`archive_snapshot` 里既有跑满的、也有真截断的。')
    w('* ⚠ 已知的具体实例：`smoke→sfchd` 30ep 的 s50 **跑满 30/30 但被存档为中断件**。'
      '该 run 的 test 读数**本就在 B 侧汇总里**，只是生成器按原始目录名查、查不到；'
      '修好之后该格由 9 种子变 **10 种子**（`+3.551 → +3.656`）。'
      '对照见 `A5_种子方差.md` §7 与 `D1_s50补测_记录.md`。')
    w()
    w('> ★ **全域影响（实测，非估计）**：46 个改名件补上了 test 读数，'
      '但 145 个 test 侧格里**只有 1 个变化**（就是上面那格）。'
      '其余 45 个要么同机已有正常目录供数（36 个），要么只在单臂出现、凑不出配对（9 个）。')
    w()

    w('## 四、结论')
    w()
    w('1. 改名件**能**贡献 test 读数（%d/%d），但**几乎不改变结论**：补入后全域只有 **1** 个格变化。'
      % (tc, len(inc)))
    w('2. 改名**成批发生**且集中在 09-23 与 09-24 ⇒ 是**运维事件**的痕迹，不是模型行为。')
    w('3. **改名 ≠ 截断** ⇒ 任何按 outcome 标签一刀切的筛选都会错；'
      '必须按 `epochs_actual` 判（`ok_outcome()` 已如此实现）。')
    w('4. **生成器查汇总必须按短名回退** —— 否则改名件的读数会被静默丢弃，'
      '并伪装成"这些件没有读数"（本件第一版就是这么写错的）。')
    w()
    w('> ⚠ 本件是**数据治理**结论，**不进论文正文**；它支撑的是"可复现性声明"与数据字典的纪律。')

    os.makedirs(OUT, exist_ok=True)
    io.open(os.path.join(OUT, 'A17_改名件时间线.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    print()
    print('输出 -> %s' % os.path.join(OUT, 'A17_改名件时间线.md'))


if __name__ == '__main__':
    main()
