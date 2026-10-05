# -*- coding: utf-8 -*-
"""32_A15_loss_axis.py —— **A15：损失函数轴的边界（对 A1/A2 否定结论的复核）**

## 为什么

`A1_格完整性.md` 与 `A2_损失平面可测性.md` 都下过一个**否定结论**：
"损失轴撑不起独立轴"。否定结论和肯定结论一样需要证据，
而且底座已从 1921 行长到 **2243** 行 ⇒ 必须**用当前数据复核**。

## 判据（本件采用两条，任一条不成立则"损失轴"不可做）

1. **有实体**：存在非 `shapeiou` 的 run；
2. **有对照**：存在**至少一格**，其内部同时含**两种非空 loss**（否则任何"loss 的效应"都与族/批次完全混淆）。
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
    w('# A15 损失函数轴的边界（A1/A2 否定结论的复核）')
    w()
    w('> 数据 `base/run_table_canonical.csv`（**%d 行 / %d 个唯一 run**）。' % (len(rows), len({r['run'] for r in rows})))
    w()

    w('## 一、loss 取值分布')
    w()
    c = collections.Counter((r.get('loss') or '(空)') for r in rows)
    w('| loss | 行数 | 占比 |')
    w('|---|---|---|')
    for k, v in c.most_common():
        w('| `%s` | %d | %.1f%% |' % (k, v, 100.0 * v / len(rows)))
    w()

    w('## 二、判据①：有没有非 `shapeiou` 的实体')
    w()
    ns = [r for r in rows if (r.get('loss') or '') not in ('shapeiou', '')]
    w('* 非 `shapeiou` 且非空的 run：**%d** 个（unique run %d）。' % (len(ns), len({r['run'] for r in ns})))
    cc = collections.Counter(r['loss'] for r in ns)
    w('* 构成：%s' % '、'.join('`%s` %d' % (k, v) for k, v in cc.most_common()))
    w('* ⇒ **判据①成立**（有实体），所以"A1 说没有非 shapeiou 实体"这个读法**是错的** —— '
      '正确的是"**有实体但没有对照**"，见下。')
    w()

    w('## 三、★ 判据②：有没有"同一格内含两种非空 loss"')
    w()
    ax = collections.defaultdict(set)
    for r in rows:
        if r['lr_arm'] not in ('base', 'lr005'):
            continue
        ep = int(C.f(r['epochs_nominal'])) if C.f(r['epochs_nominal']) else None
        ax[(r['_pair'], r['family'], r['_lb'], ep)].add(r.get('loss') or '')
    multi = {k: v for k, v in ax.items() if len(v) >= 2}
    real = {k: v for k, v in multi.items() if len({x for x in v if x}) >= 2}
    w('* 格内出现 ≥2 种 loss 值的格：**%d** 个。' % len(multi))
    w('* **其中"两种都是非空"的格：%d 个**。' % len(real))
    w()
    if not real:
        w('* ⇒ 在**这一口径**（格图只收 `base`/`lr005` 两臂）下，判据②不成立。')
        w('* ⚠⚠ **但这个"0"是口径造成的，不能读成"数据里没有损失对照"** —— 见下节。')
        w('* 那 %d 个"多 loss"格**全部**是 `{{\'\', \'shapeiou\'}}` 这种组合 —— '
          '即"标注了 shapeiou" vs "没标注"，**不是损失函数的对照**。' % len(multi))
    else:
        w('* ⚠ **判据②成立** ⇒ A1/A2 的否定结论**需要修正**：存在可对照的格。')
        for k, v in list(real.items())[:10]:
            w('  * `%s` → %s' % (str(k), sorted(v)))
    w()
    w('### ★★ 3.1 更正：换损失的 run **根本没进格图**')
    w()
    w('换损失的 run 名形如 `{族}_{loss}_{轮数}`（如 `dota15_css_100ep`），其 `lr_arm` **为空**；')
    w('`_cells.load()` 的格图只收 `base` / `lr005` 两臂 ⇒ 这些 run **一个都进不来**。')
    w('所以上一节的 0 **不是**"数据里没有损失对照"，而是"管线看不见"。')
    w()
    w('按 `lr0` 指纹归臂（每格的 `base` 臂与 `lr005` 臂各有自己的 `lr0`）后实测：')
    w()
    # ★ 2026-10-02：这三行**原先写死**（`base 81` / `lr005 0` / `归不上 8`），
    #   补实验补上 `{loss}-lr005` 腿之后，写死的 `lr005 = 0` 就**变成了假事实**。
    #   教训：**凡是会随数据增长的量，一律算，不许写字面量**。
    _fp = collections.defaultdict(lambda: {'base': set(), 'lr005': set()})
    for _r in rows:
        if (_r.get('loss') or '').strip() != 'shapeiou':
            continue
        if _r['lr_arm'] not in ('base', 'lr005') or not C.f(_r['epochs_nominal']):
            continue
        if _r['lr0']:
            _fp[(_r['_pair'], _r['family'], int(C.f(_r['epochs_nominal'])))][_r['lr_arm']].add(_r['lr0'])
    _n_base = _n_lr = _n_na = 0
    for _r in rows:
        _lo = (_r.get('loss') or '').strip()
        if not _lo or _lo == 'shapeiou' or not C.f(_r['epochs_nominal']):
            continue
        _k = (_r['_pair'], _r['family'], int(C.f(_r['epochs_nominal'])))
        _p = _fp.get(_k, {'base': set(), 'lr005': set()})
        if _r['lr0'] and _r['lr0'] in _p['base'] and _r['lr0'] not in _p['lr005']:
            _n_base += 1
        elif _r['lr0'] and _r['lr0'] in _p['lr005'] and _r['lr0'] not in _p['base']:
            _n_lr += 1
        else:
            _n_na += 1
    w('| 归臂结果 | 条数 |')
    w('|---|---|')
    w('| 归到 **`base`** 臂 | **%d** |' % _n_base)
    w('| 归到 **`lr005`** 臂 | **%d** |' % _n_lr)
    w('| 归不上（该格无 shapeiou 两臂可作指纹） | %d |' % _n_na)
    w()
    w('⇒ **base 臂的损失效应是存在的、可算的**（逐组读数见 `analysis\\A20_损失轴实测对照.md`）；')
    if _n_lr:
        w('⇒ ★ **`lr005` 臂现有 %d 条** ⇒ **"损失对增益的效应"已经可算**'
          '（补实验前是 0 条；逐组见 `analysis\\A22_损失对增益_实测.md`）。' % _n_lr)
    else:
        w('⇒ 但 **`lr005` 臂一条都没有** ⇒ **"损失对增益的效应"不可识别**（格不存在，不是功效不足）。')
    w('👉 逐条见 `analysis\\A20_损失轴实测对照.md`（生成器 `scripts\\36_A20_loss_contrast.py`）。')
    w()

    w('## 四、结论')
    w()
    w('* ★ **"损失轴在 `_cells` 格图里看不见"这一点仍然成立**：换损失的 run `lr_arm` 为空，')
    w('  格图只收 `base`/`lr005` ⇒ 在**那个口径**下"同格两种非空 loss 的格 = 0"。')
    w('  > 损失轴的问题**不是"没有非 shapeiou 实体"**（有 %d 个 run），' % len(ns))
    w('  > 而是**"格图里没有能对照两种损失的格"**。')
    w('* ⇒ 论文里若写"我们没有损失轴"，**不能**写成"只有 shapeiou"'
      '（那与事实不符，会被 `sns/pws/css` 直接反驳）。')
    w('* ★★ **但"不可识别"这个更强的说法，在补实验完成后已经不成立**（2026-10-02）：')
    w('  按 `lr0` 指纹把换损失 run 归臂后，**base 臂的损失效应**与**损失对增益的效应**都可算 ——')
    w('  逐组数字见 `analysis\\A20_损失轴实测对照.md` 与 `analysis\\A22_损失对增益_实测.md`。')
    w('  ⚠ **本件不重复抄那两个数** —— 抄一次就会漂一次（本脚本曾把 `lr005 臂 = 0` 写死，')
    w('  补实验做完后那句就成了假事实）。')
    w('  ⇒ 因此**不得**再写"损失轴不可识别"；应写成：')
    w('  "损失轴**在格图口径下不可见**，但经 `lr0` 归臂后**可算**，')
    w('   且**增益方向在换损失下不变**（幅度未达显著，n=6–7）"。')
    w('* ⚠ 那 %d 个非 `shapeiou` 的 run **不是废物**：它们支撑上面两件，' % len(ns))
    w('  但**不得**在没有对照的格上用来报"损失 A 比损失 B 好"。')

    os.makedirs(OUT, exist_ok=True)
    io.open(os.path.join(OUT, 'A15_损失函数轴的边界.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    print()
    print('输出 -> %s' % os.path.join(OUT, 'A15_损失函数轴的边界.md'))


if __name__ == '__main__':
    main()
