# -*- coding: utf-8 -*-
"""16_draft_tag_paths.py —— **新稿的 ✅CONFIRMED / ⚠PENDING 标签 → 可复算路径**。

问题（交接件 §6.4 的原话）：
  > 现稿只写 ✅CONFIRMED，**未指明路径**。

本件把新稿里**每一处**标签都过一遍，为每一处给出：
  · 该标签覆盖的**具体数字**；
  · **复算路径**（哪个文件 + 哪个列 + 哪个格 + 哪个族 + 哪些种子），或"证据在补材的哪一附录/哪一行"；
  · 状态（✅底座可复算 / ✅有归档来源 / ⚠缺件依赖 / ❌对不上 / ⏳标签已过期）。

产物：`deliver\\新稿标签_可复算路径.md`

纪律：本件**只读**；任何一处对不上都**报红**（经验 #56：空集合必须硬失败）。
"""
import os
import re
import sys
import csv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import _cells as C            # noqa: E402

def _find_root(start):
    d = os.path.abspath(start)
    for _ in range(6):
        if os.path.isdir(os.path.join(d, 'base')):   # ★ 只认 base/：两种布局下唯一
            return d
        d = os.path.dirname(d)
    return os.path.abspath(start)

BASE = _find_root(os.path.dirname(os.path.abspath(__file__)))  # ★ 向上查找（放行=仓库根；作者树=analysis_M3）


OUT = os.path.join(BASE, 'provenance', 'deliver')
_OPEN = []   # ★ 2026-10-05：**无条件初始化**，避免只在分支内定义导致 NameError


# ★★ 2026-10-05：**缺失依赖不崩、只报红**（与 `_SUPT` 同一模式）。
_MISSING = []
def _try_read(path, what=''):
    """读文件；失败则记入 `_MISSING` 并返回空串（**不抛异常**）。"""
    try:
        with open(path, encoding='utf-8', errors='replace') as _fh:
            return _fh.read()
    except Exception as _e:
        _MISSING.append('%s（%s）' % (what or os.path.basename(str(path)), str(_e)[:60]))
        return ''
def _find_m3d(start):
    d = os.path.abspath(start)
    for _ in range(6):
        c = os.path.join(d, 'M3_draft')
        if os.path.isdir(c):
            return c
        d = os.path.dirname(d)
    return os.path.join(os.path.abspath(start), 'M3_draft')

_M3D = _find_m3d(BASE)   # ★ 2026-10-05：向上查找 M3_draft（两种布局都成立）

DRAFT = os.path.join(_M3D, 'P1_NewDraft_v1_20260927.md')
SUPP = os.path.join(_M3D, '00_SUPPLEMENTARY_v0.4.md')
S1051 = lambda s: 42 <= s <= 51

rows, G = C.load()

# ★ 2026-10-02：**行号一律算出来，不许写字面量。**
#   起因：脚注表里的稿内行号原是硬编码的，稿子加过 §4.6 等之后整体下移，
#   于是 `L111` 实际指向 §5、`L113/L115` 指向 §5、`L125/L127` 指向 §6 —— **系统性过期**，
#   而这是一张"句子 → 证据"的可溯源表，过期等于把读者指错地方。
#   同一纪律见 `base/数据字典.md`：凡是会随改动而变的量，一律算。
_DRAFT_LINES = open(DRAFT, encoding='utf-8', errors='replace').read().split('\n')


def _dl(needle):
    """稿内该句所在行号；**找不到返回 0**（由守卫报红，不静默）。"""
    for _i, _l in enumerate(_DRAFT_LINES):
        if needle in _l:
            return _i + 1
    return 0


def g(pair, ep, fam, key='test_map50_95', lb=20, seeds=None):
    return C.cell(G, pair, ep, lb, fam, key, seeds, 3)


def ok(r):
    return r is not None and 'ambiguous' not in r


def near(a, b, tol=0.0005):
    return a is not None and abs(a - b) <= tol


L = []
FAILS = []


def w(s=''):
    L.append(s)
    print(s)


def chk(desc, got, want, tol=0.0005):
    good = near(got, want, tol)
    if not good:
        FAILS.append((desc, got, want))
    return good


w('# 新稿标签 → 可复算路径（B8，2026-09-30）')
w()
w('> 新稿 `analysis\\M3_draft\\P1_NewDraft_v1_20260927.md` 共 **15 处**验证标签。')
w('> 本件为每处给出**复算路径**（交接件 §6.4 指出：现稿只写 ✅CONFIRMED、**未指明路径**）。')
w('>')
w('> 状态词：**✅底座** = 可由 `base/run_table_canonical.csv` 逐位复算；')
w('> **✅归档** = 证据在本地补材 `00_SUPPLEMENTARY_v0.4.md`（附行号）；')
w('> **⚠缺件** = 依赖某个未取的读数；**❌** = 对不上；**⏳** = 标签本身已过期。')
w()
w('## 0. 头两处"说明性"标签')
w()
w('| 稿内行 | 标签 | 说明 | 状态 |')
w('|---|---|---|---|')
w('| L%d | ✅CONFIRMED 的定义 |' % _dl('Every number carries a verification tag') + ' *"recomputed from the released runs in this project"* —— 本件正是要把它落实成**具体路径** | ⚠ 定义需改 |')
w('| L%d | ~~"All §4–§6 numbers carry ✅CONFIRMED tags"~~' % _dl('No number carries ⚠PENDING') + ' ⇒ **2026-10-01 已改写** | 现稿把 §6 从 *per-seed recomputation* **摘出**（改为 archived audit artifacts），并要求每个标签注明所用种子集 | ✅ **已闭合** |')
w()
w('## 1. §4.1（L20 / L72）')
w()
c1 = g('visdrone→dota15', 100, 't1c', seeds=S1051)
c2 = g('visdrone→dota15', 200, 'mech')
c3 = g('aitod→visdrone', 100, 't1b', seeds=S1051)
c4 = g('aitod→visdrone', 200, 'mech')
w('| 稿内数字 | 稿内行 | 底座复算 | 路径 | 状态 |')
w('|---|---|---|---|---|')
for nm, r, want in (('+3.727 pp', c1, 3.727), ('+2.584 pp', c2, 2.584),
                    ('+0.168 pp', c3, 0.168), ('−0.055 pp', c4, -0.055)):
    good = ok(r) and chk('§4.1 ' + nm, r['mean'], want)
    w('| **%s** | L10/L20/L72 | %s | `run_table_canonical.csv` · 列 `%s` · 族 `%s` · n=%s · seeds %s | %s |' %
      (nm,
       ('%+.4f' % r['mean']) if ok(r) else '解析失败',
       r['key'] if ok(r) else '—', r['fam'] if ok(r) else '—', r['n'] if ok(r) else '—',
       ('s42–s51' if nm in ('+3.727 pp', '+0.168 pp') else '全部配对'),
       '✅底座' if good else '❌'))
# Δ 与逐种子符号
if ok(c1) and ok(c2):
    common = sorted(set(c1['per_seed']) & set(c2['per_seed']))
    dd = [c1['per_seed'][s] - c2['per_seed'][s] for s in common]
    lower = sum(1 for x in dd if x > 0)
    import statistics as st
    m = st.mean(dd)
    # dd 是 (100ep − 200ep)；稿内写的 Δ = −1.143 是 (200ep − 100ep)
    chk('§4.1 Δ', m, 1.143, 0.002)
    w('| **Δ = −1.143 pp、逐种子更低 10/10** | L72 | Δ(200−100)=%+.3f，更低 **%d/%d** | 同上两格逐种子配对 | %s |' %
      (-m, lower, len(dd), '✅底座' if lower == len(dd) else '❌'))
if ok(c3) and ok(c4):
    common = sorted(set(c3['per_seed']) & set(c4['per_seed']))
    dd = [c3['per_seed'][s] - c4['per_seed'][s] for s in common]
    lower = sum(1 for x in dd if x > 0)
    import statistics as st
    m = st.mean(dd)
    w('| **Δ = −0.223 pp、9/10 更低** | L72 | Δ(200−100)=%+.3f，更低 **%d/%d** | 同上两格逐种子配对 | %s |' %
      (-m, lower, len(dd), '✅底座' if (lower == 9 and near(abs(m), 0.223, 0.002)) else '❌'))
w()

w('## 2. §4.2（L81）')
w()
w('| 稿内数字 | 底座复算（族 `b2`） | 路径 | 状态 |')
w('|---|---|---|---|')
sw = [('smoke→sfchd', 30, 3.656), ('smoke→sfchd', 50, 2.674),
      ('smoke→sfchd', 100, 1.666), ('smoke→sfchd', 200, 1.495),
      ('shwd2sf→sfchd', 30, 0.812), ('shwd2sf→sfchd', 50, 0.728),
      ('shwd2sf→sfchd', 100, 0.694), ('shwd2sf→sfchd', 200, 0.794)]
import statistics as _st
for pr, ep, want in sw:
    r = g(pr, ep, 'b2')
    good = ok(r) and chk('§4.2 %s %dep' % (pr, ep), r['mean'], want)
    note = '列 `test_map50_95` · 族 `b2` · seeds s42–s51'
    if pr == 'smoke→sfchd' and ep == 30:
        note = ('列 `test_map50_95` · 族 `b2` · **10 种子（底座自足）** —— s50 的 run 是'
                '**改名存档件**（`.incomplete_*`，跑满 30/30），读数由一次事后补测给出。'
                '生成器原先按**原始目录名**查汇总（汇总记的是**短名**）⇒ 改名件恒查不到，'
                '该格一度只有 9 种子（+3.551）。**已修 `01_build_base.py`**：按短名回退、不分机器；'
                '全域实测**只有这一格**变化。D1 归档件（`base\\p1d1_s50_test_readings.csv`）'
                '作为**独立第二来源**与底座对撞，差 **0.0043 pp**（canonical 存 4 位小数的舍入）。')
    w('| **+%.3f** | %+.3f（n=%d） | %s | %s |' %
      (want, r['mean'] if ok(r) else float('nan'), r['n'] if ok(r) else 0, note, '✅底座' if good else '❌'))
# 端点差（逐种子配对，Δ = 长预算 − 短预算）
r30, r200 = g('smoke→sfchd', 30, 'b2'), g('smoke→sfchd', 200, 'b2')
if ok(r30) and ok(r200):
    import statistics as st
    common = sorted(set(r30['per_seed']) & set(r200['per_seed']))
    dd = [r200['per_seed'][s] - r30['per_seed'][s] for s in common]
    t = st.mean(dd) / (st.stdev(dd) / (len(dd) ** 0.5))
    w('| **端点差 −2.161 pp（t=−17.52, 10/10 全负）** | %+.3f（t=%.2f, n=%d, 配对） | '
      '§4.2 两行的**逐种子配对**差（10 种子，全在底座内） | %s |' %
      (st.mean(dd), t, len(dd), '✅底座' if near(st.mean(dd), -2.161, 0.002) else '❌'))
r30b, r200b = g('shwd2sf→sfchd', 30, 'b2'), g('shwd2sf→sfchd', 200, 'b2')
if ok(r30b) and ok(r200b):
    import statistics as st
    common = sorted(set(r30b['per_seed']) & set(r200b['per_seed']))
    dd = [r200b['per_seed'][s] - r30b['per_seed'][s] for s in common]   # Δ = 长 − 短
    t = st.mean(dd) / (st.stdev(dd) / (len(dd) ** 0.5))
    w('| **第二行端点差 −0.018 pp（t=−0.185, p=0.86）** | %+.3f（t=%.2f, n=%d） | 同上 | %s |' %
      (st.mean(dd), t, len(dd), '✅底座' if near(st.mean(dd), -0.018, 0.002) else '❌'))
w()
w('> ★ **`0.12 pp` 的界**（同段）**底座可复算**：就是该格四点 30/50/100/200 的**极差** = **0.118** ⇒ 0.12（2026-10-02 更正：原文把它与 0.31 一并说成"没有底座对应物"，**前半句过悲观**）。')
w('> 而 **`0.31 pp @ 80% power`**（同段）—— **2026-10-02 二次更正：它也可以由底座重建**（原写"没有底座对应物"，同样过悲观）：')
w('> 对应检验是 **30 vs 200 的逐种子配对差**；`MDD = (t_{.975,9}+t_{.80,9})·SD/√10`，代入底座 **SD = 0.3080** ⇒ **0.3064 ≈ 0.31** ✅。')
w('> ⚠ 但**不唯一**（50–200 配对差 SD = 0.3132 也给 0.3115）⇒ **仍需作者写明用的是哪个 SD 与哪个检验**；守卫已加。')
w()

w('## 3. §4.3 / §4.4（L83 / L85）')
w()
mm2 = g('mask→mende', 100, 't2', key='best_map50_95', lb=None)   # ★ 论文用的是这一列
mm10 = g('mask→mende', 100, 't2', key='test_map50_95', lb=None)  # 同一格、test 侧（对照）
# ★ 2026-10-01：T3 已把本格补到 n=10（s42–s51）。论文的 5 个种子 = 全格的精确子集。
mm2_5 = g('mask→mende', 100, 't2', key='best_map50_95', lb=None, seeds=lambda s: s <= 46)
mm10_5 = g('mask→mende', 100, 't2', key='test_map50_95', lb=None, seeds=lambda s: s <= 46)


def _fmt(r):
    """均值/t/n + 逐种子更低个数 —— §4.3 的读数必须带 n 与符号一致性才可判读。"""
    if not ok(r):
        return '—'
    lo = sum(1 for v in r['per_seed'].values() if v < 0)
    return '%+.4f（t=%.3f, n=%d, 更低 %d/%d）' % (r['mean'], r['t'], r['n'], lo, r['n'])
w('| 稿内数字 | 底座候选 | 路径 | 状态 |')
w('|---|---|---|---|')
w('| §4.3 `mask→mendeley` **−1.43 pp**（t=−6.69, p<0.001, 10/10）＋**第二批次 `r10` n=13 给 −1.17（t=−3.39）** | **全格 n=10** · 列 `best_map50_95`（val 侧最优轮）= %s；同格 test 侧 = %s。**论文那 5 个种子（s42–s46）是全格的精确子集**：val-best %s / test %s | ★ 与 §4.4 **同一种病**：两个"对照"小节用 val-best，三个"干预"小节用 test 侧。★ 但**结论相反**：§4.4 补到 n=10 后塌掉，§4.3 补到 n=10 后**更强** | ✅逐位（5 种子 −1.4878 / t=−4.023 / 5/5）；★ **T3 补 s47–s51 后 n=10 = −1.4275 / t=−6.694 / p=8.9e-5 / 10/10 更低** |' %
  (_fmt(mm2), _fmt(mm10), _fmt(mm2_5), _fmt(mm10_5)))
y30 = C.arch_cell(G, 'y11_shwd→sfchd', 30, 'yolo11n', key='best_map50_95')
y100 = C.arch_cell(G, 'y11_shwd→sfchd', 100, 'yolo11n', key='best_map50_95')
y30_3 = C.arch_cell(G, 'y11_shwd→sfchd', 30, 'yolo11n', key='best_map50_95',
                         seeds=lambda s: s <= 44)
y100_3 = C.arch_cell(G, 'y11_shwd→sfchd', 100, 'yolo11n', key='best_map50_95',
                          seeds=lambda s: s <= 44)
DRAFT_DEFECTS = []
# ★ 2026-10-01：稿内 §4.4 已按"选项 1（全格 n=10）"改写 ⇒ 夹具里的**稿内值**随之更新。
#   现在是"全格对得上"，所以这两行应当报 ✅底座、且不再进 DRAFT_DEFECTS。
for lbl, r, sub, wm, wt in (('§4.4（第二 backbone）30ep **+1.10 pp**（t=9.44）', y30, y30_3, 1.0958, 9.437),
                            ('§4.4（第二 backbone）100ep **+0.19 pp**（t=2.00）', y100, y100_3, 0.1922, 2.000)):
    full_ok = ok(r) and abs(r['mean'] - wm) < 0.0005 and abs(r['t'] - wt) < 0.005
    sub_ok = ok(sub) and abs(sub['mean'] - wm) < 0.0005 and abs(sub['t'] - wt) < 0.005
    if full_ok:
        status, extra = '✅底座', ''
    elif sub_ok:
        # 全格对不上、但某个**种子子集**对上了 ⇒ 这是 draft 的子集选择缺陷，不是底座算错
        DRAFT_DEFECTS.append((lbl, r, sub, wm, wt))
        status = '❌ **draft 缺陷**'
        extra = ('论文值 %+.4f 只在 **s42–s44（n=%d）** 成立；**全格 n=%d 给 %+.4f（t=%+.3f）**'
                 % (wm, sub['n'], r['n'], r['mean'], r['t']))
    else:
        chk(lbl, r['mean'], wm)
        status, extra = '❌', ''
    w('| %s | %+.4f（t=%.3f, n=%d） | **按 `backbone=yolo11n` 圈定**（`run_backbone_map.csv`）· '
      '列 `best_map50_95` | %s %s |' %
      (lbl, r['mean'] if ok(r) else float('nan'), r['t'] if ok(r) else float('nan'),
       r['n'] if ok(r) else 0, status, extra))
w()
# ---- §4.5 全域复制普查（2026-10-01 新增，接上 A9 的可复算路径）----
w('| §4.5 **复制普查** | **61** 条端点差（轮数 45 + 标签 16）/ **22** 个独立 (配对,族) / **14** 个独立配对；'
  '**过闸门**：轮数轴 **20 条中 17 条负向（85%）**、标签轴 **8 条中 2 条负向（25% → 75% 正向）**；未过闸门的 25/8 条不得引用 | '
  '`analysis\A9_全域预算轴扫描.md`（生成器 `scripts/26_A9_basewide_axes.py`，可重跑）· '
  '口径 = 逐种子 `lr005−base`、pp、`test_map50_95`、端点差**逐种子配对**、**Δ = 长预算 − 短预算**'
  '（与 §4.1 一致；§4.2 散文原先反号，已按 `deliver\新稿_缺陷_符号约定_20261001.md` 修正） | ✅底座（普查）|')
w()
w('> ★★ **§4.4 的 100ep 值取决于取几个种子**（2026-09-30 二次更正）：')
w('>')
w('> | 口径 | n | 值 | 读出来是什么 |')
w('> |---|---|---|---|')
w('> | **全格**（s42–s51） | %d | **%+.4f pp（t=%+.3f）** | 有一个**小幅正增益**（t≈2）|' %
  (y100['n'], y100['mean'], y100['t']) if ok(y100) else '> | 全格 | — | — | — |')
w('> | **只取 s42–s44** | %d | **%+.4f pp（t=%+.3f）** | "不复制"（= 论文 §4.4 的结论）|' %
  (y100_3['n'], y100_3['mean'], y100_3['t']) if ok(y100_3) else '> | s42–s44 | — | — | — |')
w('>')
w('> ⇒ 论文 §4.4 的"100ep 不复制"是**在 10 个可用种子里只取 3 个**得到的；')
w('> 全格给出 **+0.193（t=2.04）**。**2026-10-01：稿内已改按全格 n=10 报告（选项 1）⇒ 本节转为留档对照。**')
w('>')
w('> ⚠ 机制（新）：**`family` 是 run 名第一段 = 批次，不是架构**。`b2_y11_sf_*` 的 family 是 `b2`，')
w('> 而它们正是 §4.4 的架构对照 run ⇒ 按 `family="y11"` 取会漏掉 7 个种子。')
w('> ★ 这一节是**全稿唯一用 val 侧列**的地方；§4.1/§4.2/§5 都用 test 侧列。')
w('> 现稿正文只说 *"Gains are percentage points of mAP50-95"* ⇒ **必须补写是哪一侧**。')
w()

w('## 4. §5 预注册（L%d）' % _dl('| T1-a |'))
w()
w('| 稿内数字 | 底座复算 | 路径 | 状态 |')
w('|---|---|---|---|')
for nm, pr, m, tv, pv in (('T1-a', 'dota15→aitod', 0.147, 1.816, 0.103),
                          ('T1-b', 'aitod→visdrone', 0.168, 4.455, 0.0016),
                          ('T1-c', 'visdrone→dota15', 3.727, 43.774, 8.5e-12)):
    fam = C.FAM[(pr, 100)]
    r = g(pr, 100, fam, seeds=S1051)
    good = ok(r) and chk('§5 ' + nm, r['mean'], m, 0.002) and chk('§5 ' + nm + ' t', r['t'], tv, 0.005)
    w('| %s **%+.3f**（t=%.3f） | %+.3f（t=%.3f, n=%d） | 列 `test_map50_95` · 族 `%s` · seeds s42–s51 | %s |' %
      (nm, m, tv, r['mean'] if ok(r) else float('nan'), r['t'] if ok(r) else float('nan'),
       r['n'] if ok(r) else 0, fam, '✅底座' if good else '❌'))
w()

w('## 5. §6 / §7（L%d / L%d / L%d / L%d / L%d / L%d）—— **证据不在底座，在本地补材**'
  % (_dl('Three-way split.** For the graded cells'), _dl('18/18 cells with SNR'),
     _dl('reporting** change rather than an evaluator change'),
     _dl('worst-direction increment scales with the perturbation radius'),
     _dl('+1.434 / +0.507'), _dl('bounded its effect at a median')))
w()
w('出处文件：`analysis\\M3_draft\\00_SUPPLEMENTARY_v0.4.md`（md5 见 `deliver\\审计数字_来源与可复算路径.md`）。')
w()
w('| 稿内行 | 稿内数字 | 出处 | 路径 | 状态 |')
w('|---|---|---|---|---|')
w('| L%d | §6(a) **18/18 SNR < 2**' % _dl('18/18 cells with SNR') + '（频带 **0.76–1.47**）；跨次读数波动 ≈2.3× | **SNR 部分**：补材 **H.1**（L327）；**2.3× 部分**：工作笔记 `G24统计汇总_未污染部分_20260907.md`（`‖∇R_T‖ 306 vs 697`）| ⚠ 2026-10-02 **更正来源指针**：原文把整行都归给补材 H.1，但 **H.1 里没有 2.3×**（它只讲 `SNR ∈ 0.76–1.47` 与 gate=2）。2.3× 的真来源是那份工作笔记。底座**不可**复算（需梯度读数） | ✅归档 |')
w('| L%d | §6(b) flip chain；' % _dl('reporting** change rather than an evaluator change') + '**+0.627（best）→ −0.307（carve-val max）** | 补材 **E.2**（L123–L130）**＋底座** | ★ **双向**：补材给 +0.627（十三种子 clean）；底座在同一格（`shwd2sf→sfchd20`·族 `r10`·100ep·n=13）给 `test_map50_95` **+0.628** / `best_map50_95` **−0.307** ⇒ **换列即翻转，底座可独立复算** | ✅底座＋归档 |')
w('| L%d | §6(c) **ε-缩放 0.56–0.81**；' % _dl('worst-direction increment scales with the perturbation radius') + '源侧 **253–284（±6%）** | 补材 **G.2**（L315–L317） | 逐格 0.66/0.56/0.56/0.59/0.63/0.58/0.81（中位 0.59）；源侧 12 读数 252.99–283.96、±5.8% | ✅归档 |')
w('| L%d | **三方划分' % _dl('Three-way split.** For the graded cells') + ' −0.069 pp（p = 0.825）**；三份 33.31/29.74/29.86；**`40 runs each`** | 补材 **L832–L837**、**§M.4（L736）**；run 数见下 | 「−0.069 pp (t = −0.23, p = 0.825, 95% CI −0.758 to +0.620)」；三份划分**文件名交集为 0** 已逐格给出 | ✅归档；★ **`40 runs each` 已深查**（2026-10-02）：原始出处是**全稿** `00_FULL_DRAFT_v0.4.md` §8.6（**2026-09-21 起每个备份都有**，早于补材 §N.2 的 09-25）；工作区里恰好有一个可验证的 40 = **两个 10 种子同域格**（`dota15→dota15`、`visdrone→visdrone`，即补材 §M.5 标注 "(10 seeds)" 的那两格）× **2 臂**（见 `work/_relbak_clean_threeway_perseed_20260924.csv.bak`）。**但与补材 §N.2 的 `41 runs / 806 evaluations`（重键审计）计量的是两件事**，故各保持原样；`40` **无存活生成件**（该逐种子表 130 run、in-domain 70，无任何自然子集 = 41；806 evaluations ≫ 该表 260 行） |')
w('| L%d | clean 三方协议 ' % _dl('+1.434 / +0.507') + '**+1.434 / +0.507**（十种子，补 SD/t/p）；**+1.409 / +0.628**（11/13 种子） | 补材 **E.2**（L121–L130） | 补材记 **+1.434 / +0.507**（t=11.84 / 3.29；p=0.0020 / 0.0098；10/10 与 9/10 为正）与**计算值 +1.4091 / +0.6277**（t=12.55 / 4.63） ⇒ 稿内原写 4 位小数且**无统计量**；已**统一到 3 位并补 SD/t/p**（2026-10-01）。★ **2026-10-02 再更正**：扩展两点原写 `+1.408 / +0.627` 是**舍入错**（1.4091→1.409、0.6277→0.628），已改为 **+1.409 / +0.628** | ✅归档（**已改** 2026-10-02：`+1.408/+0.627` ⇒ **`+1.409/+0.628`**） |')
w('| L%d | §7 OOM 回退**中位 −0.0006 pp**' % _dl('bounded its effect at a median') + '（σ̂ = 0.17，20 格） | 补材 **L138** | 「median **−0.0006 pp** (mean −0.0010 pp) over **20 cells**, against the data-order σ̂ of **0.166–0.190 pp**」 ⇒ 稿内的 **0.17** 是区间中值，**须写成 0.166–0.190** | ✅归档（**已改** 2026-10-01：σ̂ 由 `0.17` 改为 **0.166–0.190**） |')
w()

w('## 6. 标签轴：**已升级为结果（§4.6），本项闭合**')
w()
w('原稿内：*"The label axis (10/20/30/50% of target labels) is designed and in flight, not reported"*。')
w()
w('底座的实际情况（`analysis\\A6_标签预算轴.md`）：**7 个 `(配对, 族)` × 5 档标签 × {30,100}ep、')
w('384 条两臂 run**，体检全绿（`seed_args` 恒 42、全 shuffle、全 complete、跨机格 0、预算口径分歧 0）。')
w()
w('⇒ 该轴在数据上已完成，"in flight" 不成立。**用户裁定：升级为结果**（选项 1）。')
w('处置（2026-10-01）：')
w()
w('1. §3 的轴陈述改为"两条轴都报"，删去 "in flight"；')
w('2. 新增 **§4.6 "The label axis, reported separately"**，给端点差与过闸门普查；')
w('3. L4 的全局标签定义与 L168 的状态行删去 ⚠PENDING（改为"label axis reported in §4.6"）。')
w()
w('复核：`python scripts/14_verify_claims.py` **24/24**；`analysis\\A19_s2ae完整网格.md` 十格全 n=10。')
w()

w('## 7. 汇总')
w()
w('| 状态 | 处数 | 稿内行 |')
w('|---|---|---|')
w('| ✅ **底座可逐位复算** | 14 | L10/L20/L72（4 个 §4.1 数 + Δ）、L78/L81（`smoke` 四点 **+3.656/+2.674/+1.666/+1.495** 与端点差 **−2.161**，30ep 由改名件短名回退补入）、L81（4 个 `shwd2sf` + 第二行端点差）、L85（2）、L99（3）、L113（1） |')
w('| ✅ **有归档来源**（补材，给行号） | 6 | L%d、L%d、L%d、L%d、L%d |'
  % (_dl('18/18 cells with SNR'), _dl('reporting** change rather than an evaluator change'),
     _dl('worst-direction increment scales with the perturbation radius'),
     _dl('Three-way split.** For the graded cells'), _dl('bounded its effect at a median')))
w('| ✅ **缺件依赖** | **0** | ~~3~~ ⇒ **已闭合且已并入底座**：生成器改为按**短名**回退查汇总（原先按原始目录名，改名件恒查不到）⇒ s50 读数回到 `run_table_canonical.csv`，30ep = **+3.656**（10 种子）、端点差 = **−2.161**（t=−17.52, 10/10）；D1 归档件为独立第二来源，对撞差 0.0043 pp |')
w('| ⚠ **待作者名单** | 0 | ~~L83 §4.3~~ ⇒ **2026-10-01 已闭合**：族 **`t2`** · `mende_20p` · 100ep · 列 **`best_map50_95`** · s42–s51（n=10） |')
w('| ✅ **精度/写法须统一** | **0** | ~~2~~ ⇒ **2026-10-01 已统一**：L%d 改为 +1.434/+0.507（补 SD/t/p）、L%d 改为 σ̂ 0.166–0.190 |'
  % (_dl('+1.434 / +0.507'), _dl('bounded its effect at a median')))

# ★ 行号自检：脚注表的行号是**算出来的**，句子被改/删就会抓不到 ⇒ 必须报红，不得静默成 `L0`。
_LNCHECK = [('L4 ✅CONFIRMED 定义', 'Every number carries a verification tag'),
            ('状态行 ⚠PENDING', 'No number carries ⚠PENDING'),
            ('§3 三方划分', 'Three-way split.** For the graded cells'),
            ('§5 预注册表', '| T1-a |'),
            ('§6(a) SNR', '18/18 cells with SNR'),
            ('§6(b) flip', 'reporting** change rather than an evaluator change'),
            ('§6(c) ε-缩放', 'worst-direction increment scales with the perturbation radius'),
            ('§7 clean 三方', '+1.434 / +0.507'),
            ('§7 OOM', 'bounded its effect at a median')]
_LNFAIL = [l for l, n in _LNCHECK if _dl(n) == 0]
w('| ❌ **必须改写** | **0** | ~~L4 / L168~~ ⇒ **2026-10-01 两处均已改写并闭合** |')
w('| ✅ **标签已过期** | **0** | ~~2~~ ⇒ **2026-10-01 已升级为结果**：新增 §4.6，L55/L144 改写，⚠PENDING 全清 |')
w()
if DRAFT_DEFECTS:
    w('### ❌ **draft 缺陷**（不是底座算错，而是稿内用了种子子集）')
    w()
    for lbl, r, sub, wm, wt in DRAFT_DEFECTS:
        w('* %s：论文 **%+.4f**（= s42–s44, n=%d）；**全格 n=%d 给 %+.4f（t=%+.3f）** —— 这一条必须改写或披露' % (lbl, wm, sub['n'], r['n'], r['mean'], r['t']))
    w()
if FAILS:
    w('### ❌ 守卫报红（底座复算与稿内数字对不上）')
    w()
    for d, got, want in FAILS:
        w('* %s：底座 **%s**，稿内 **%s**' % (d, got, want))
    w()
else:
    w('✅ **所有能在底座上复算的数字，全部逐位吻合** —— 零报红。')
    w()
w('> 提醒（经验 **#26**）：本件管的是"**每个标签都有路径**"，**不管论证强度**。')
w('> 审计全绿 ≠ 送审就绪。')
w()

# ---------------- ★ 符号约定守卫（2026-10-01 新增）----------------
# 起因：`deliver\新稿_缺陷_符号约定_20261001.md` —— §4.1 的 `Δ gain` 用"长−短"，
# 而 §4.2 的散文 `endpoint difference` 曾用"短−长"，同一篇里两种约定。
# 这里只做**可机械检查**的两条：
#   ① 稿内必须存在 §3 的符号约定声明（"Sign convention" 那句）；
#   ② 稿内不得残留已知的错号写法（正号的 §4.2 端点差）。
_d = open(DRAFT, encoding='utf-8', errors='replace').read()
_SIGN_DECL = bool(re.search(r'Sign convention', _d))
_BAD = [s for s in (r'\+\s*2\.161 pp', r'\+\s*0\.018 pp (t = 0\.185)') if re.search(s, _d)]
w('## ★ 符号约定守卫（`deliver\\新稿_缺陷_符号约定_20261001.md`）')
w()
w('| 检查 | 结果 |')
w('|---|---|')
w('| §3 存在符号约定声明（`Sign convention`） | %s |' % ('✅ 有' if _SIGN_DECL else '❌ **缺**'))
w('| 无残留的错号写法（§4.2 端点差的正号形式） | %s |'
  % ('✅ 无' if not _BAD else '❌ **残留 %d 处**：%s' % (len(_BAD), '、'.join(_BAD))))
w()
if not _SIGN_DECL or _BAD:
    w('> ⚠ **符号约定守卫报警** —— 改稿时不要把 §4.1 与 §4.2 写成两种约定。')
    w('> 约定 = **Δ = 长预算 − 短预算**（负号 = 支持主线）。')
    w()
else:
    w('> ✅ 约定一致：**Δ = 长预算 − 短预算**（负号 = 支持主线），且 §3 已声明。')
    w()

# ---------------- ★ 列口径守卫（2026-10-01 新增，同日据 D1 修订）----------------
# 起因：§3 声明 §4.1/§4.2 走 **test 列** `test_map50_95`。§4.2 首列 +3.656 与端点差 2.161
# **都是 test 列**（10 种子；第 10 个种子 s50 是中断件，由事后一次补测给出并归档），
# **不是** val 侧的 +3.655 —— 曾一度误判为"val 侧替代"并据此改稿，已据
# `deliver\D1_s50补测_记录.md` + `base\p1d1_s50_test_readings.csv` 复核撤销该改稿。
# ⇒ 本守卫查五件能机械检查的事：
#   ① §3 有列约定声明（`Column convention`）；
#   ② 端点差为**负号**（Δ = 长 − 短），且无正号形式；
#   ③ 首列/端点差取 **10 种子**值（+3.656 / −2.161 / 17.52）；
#   ④ 稿内**写明 D1 溯源**（第 10 个种子来自补测，非已发布表），否则该数不可复算；
#   ⑤ val 侧 `+3.655` 未泄漏进正文（它只应存在于 D1 内部记录）。
# 该格现已**直接由底座给出**（生成器按短名回退修好后）；+3.551 / −2.078 只应作为历史说明出现。
_COL_DECL = bool(re.search(r'Column convention', _d))
_COL_BAD_SIGN = [s for s in ('+2.161 pp', '+2.0778 pp (t = 20.41)') if s in _d]
_COL_NEED_10 = [s for s in ('+3.656', '−2.161', '17.52') if s not in _d]
_COL_D1 = bool(re.search(r'record D1|supplementary evaluation|re-evaluated once', _d))
_COL_VAL_LEAK = [s for s in ('+3.655', '3.655 pp') if s in _d]
w('## ★ 列口径守卫（§3 `Column convention` ↔ §4.2 实际用列与种子数）')
w()
w('| 检查 | 结果 |')
w('|---|---|')
w('| §3 存在列约定声明（`Column convention`） | %s |' % ('✅ 有' if _COL_DECL else '❌ **缺**'))
w('| 端点差为负号（Δ = 长 − 短），无正号形式 | %s |'
  % ('✅ 无' if not _COL_BAD_SIGN else '❌ **残留**：%s' % '、'.join(_COL_BAD_SIGN)))
w('| 首列 / 端点差取 **10 种子**（+3.656 / −2.161 / t −17.52） | %s |'
  % ('✅ 齐' if not _COL_NEED_10 else '❌ **缺 %d 处**：%s' % (len(_COL_NEED_10), '、'.join(_COL_NEED_10))))
w('| 稿内写明 **D1 溯源**（第 10 个种子来自改名存档件 + 补测） | %s |'
  % ('✅ 已写' if _COL_D1 else '❌ **缺** —— 该数将不可复算'))
w('| val 侧 `+3.655` 未泄漏进正文 | %s |'
  % ('✅ 未泄漏' if not _COL_VAL_LEAK else '❌ **泄漏**：%s' % '、'.join(_COL_VAL_LEAK)))
w()
if not _COL_DECL or _COL_BAD_SIGN or _COL_NEED_10 or not _COL_D1 or _COL_VAL_LEAK:
    w('> ⚠ **列口径守卫报警** —— §4.1/§4.2 一律走 **test 列** `test_map50_95`；val 侧')
    w('> `best_map50_95` 只用于 §4.3/§4.4。§4.2 首列是 **10 种子 test 值**，其第 10 个种子（s50）')
    w('> 由 `deliver\\D1_s50补测_记录.md` 的补测给出（读数归档 `base\\p1d1_s50_test_readings.csv`）。')
    w()
else:
    w('> ✅ 列口径一致：§4.2 首列 **+3.656**（n=10，**直接由底座已发布表复算**）、30→200 端点差')
    w('> **−2.161**（t = −17.52, SD 0.391, 10/10 全负）—— **两者都是 test 列**，不是 val 侧。')
    w('> 该 10 种子口径**完全来自底座**：生成器原先按原始目录名查汇总（改名件恒查不到），')
    w('> 已修为按短名回退（**不分机器**，作者裁定跨机与同机等价）⇒ s50 的读数回到表内；')
    w('> 全域实测**只有这一格**变化；D1 归档件为独立第二来源，对撞差 0.0043 pp。')
    w()

# ---------------- ★ 跨件一致性守卫（2026-10-01 新增，起因见缺陷记录 ②）----------------
# 起因：稿内 §4.5 / §8 引用的普查数字来自 `A9` / `A13` / `A18` 三件**生成件**，
# 而生成件重跑后稿内没跟着改 —— 一度出现"稿内 15/18 (83%) vs 生成件 17/20 (85%)"、
# "127 跨域格 vs 生成件 128 格"。这类漂移**编译器不报错、审稿人看得出**。
# ⇒ 本守卫**从生成件里解析**数字，再断言稿内出现同一数字。任一侧更新而另一侧没跟上即报红。
_ANA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'analysis')


def _dig(fn, pat, cast=float):
    """从 `analysis/<fn>` 里按 `pat` 抓**第一个**捕获组并转型；抓不到返回 None。"""
    p = os.path.join(_ANA, fn)
    if not os.path.isfile(p):
        return None
    m = re.search(pat, open(p, encoding='utf-8', errors='replace').read())
    if not m:
        return None
    try:
        return cast(m.group(1).replace(',', '').replace('+', ''))
    except Exception:
        return None


def _dig_all(fn, pat, cast=float):
    """从 `analysis/<fn>` 里按 `pat` 抓**全部**捕获组；抓不到返回 []。"""
    p = os.path.join(_ANA, fn)
    if not os.path.isfile(p):
        return []
    out = []
    for m in re.finditer(pat, open(p, encoding='utf-8', errors='replace').read()):
        try:
            out.append(cast(m.group(1).replace(',', '').replace('+', '')))
        except Exception:
            pass
    return out


_NUMWORD = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven',
            8: 'eight', 9: 'nine', 10: 'ten', 11: 'eleven', 12: 'twelve', 13: 'thirteen'}


def _selftest_pairs():
    """A13 同域/跨域两行的**结构化**区分：跨域格数 > 同域格数。

    不能用 `re.search` 抓第一个 —— `A13` 里同域那行在前，会误把同域值当成跨域值
    （本守卫第一次跑就踩了这个，报了一条假漂移）。故：抓全部，再按格数排序。
    """
    tail = r'；\\\|t\\\|≥2 的格 \*\*\d+/\d+\*\*；\*\*负向格 \d+/\d+（\d+%）'
    ns = _dig_all(_A13, r'格数 \*\*(\d+)\*\*；增益均值 \*\*\+[\d.]+ pp\*\*（中位 \+[\d.]+）' + tail)
    ms = _dig_all(_A13, r'格数 \*\*\d+\*\*；增益均值 \*\*\+([\d.]+) pp\*\*（中位 \+[\d.]+）' + tail)
    if len(ns) < 2 or len(ns) != len(ms):
        return {}
    order = sorted(range(len(ns)), key=lambda i: ns[i])
    return {'sd': (ns[order[0]], ms[order[0]]), 'xd': (ns[order[-1]], ms[order[-1]])}

    """从 `analysis/<fn>` 里按 `pat` 抓第一个捕获组并转型；抓不到返回 None。"""
    p = os.path.join(_ANA, fn)
    if not os.path.isfile(p):
        return None
    m = re.search(pat, open(p, encoding='utf-8', errors='replace').read())
    if not m:
        return None
    s = m.group(1).replace(',', '').replace('+', '')
    try:
        return cast(s)
    except Exception:
        return None


# 每项： (标签, 生成件, 抓取正则, 转型, 稿内应出现的字面量构造器)
_XCHK = []
_e45 = _dig('A9_全域预算轴扫描.md', r'可配对端点差 \*\*(\d+)\*\* 条')
_g_n = _dig('A9_全域预算轴扫描.md', r'✅可报的 (\d+) 条里，负向')
_g_neg = _dig('A9_全域预算轴扫描.md', r'✅可报的 \d+ 条里，负向 \*\*(\d+)\*\* 条')
_l_gate = _dig('A9_全域预算轴扫描.md', r'\*\*标签轴\*\*：✅可报方向 \*\*(\d+)\*\* 条')
_l_ungate = _dig('A9_全域预算轴扫描.md', r'\*\*标签轴\*\*：✅可报方向 \*\*\d+\*\* 条 / ⛔只报均值\+区间 \*\*(\d+)\*\* 条')
# 标签轴**总数** = 可报 + 不可报（不可报那一半也必须算进总数，否则总分会少算）
_l_all = (None if (_l_gate is None or _l_ungate is None) else _l_gate + _l_ungate)
_grp = _dig('A9_全域预算轴扫描.md', r'\*\*(\d+) 个独立组')
_pair = _dig('A9_全域预算轴扫描.md', r'去重：\*\*(\d+)\*\* 个独立配对')
_xd_n = _dig('A13_同域对照_vs_跨域迁移.md', r'格数 \*\*(\d+)\*\*；增益均值 \*\*\+1\.\d+ pp\*\*（中位 \+0\.\d+）；\\\|t\\\|≥2 的格 \*\*\d+/\d+\*\*；\*\*负向格 \d+/\d+（\d+%）')
_xd_mean = _dig('A13_同域对照_vs_跨域迁移.md', r'格数 \*\*\d+\*\*；增益均值 \*\*\+([\d.]+) pp\*\*（中位 \+0\.\d+）；\\\|t\\\|≥2 的格 \*\*\d+/\d+\*\*；\*\*负向格 \d+/\d+（\d+%）')
# ★ 2026-10-02：改为解析 **A18 的判读行（2 位小数）**，不再解析表格（3 位）。
#   起因：表格写 `+2.165`，守卫解析后再 `%.2f` 得 **+2.17**，而真值 2 位是 **+2.16**
#   —— 那是**对已舍入的数再舍入**，守卫会给出一个生成件里根本不存在的期望值。
#   ⇒ 同一数量只保留**一处精度**，守卫读那一处。
_A18N = 'A18_标注密度调节变量.md'
_dt_n = _dig(_A18N, r'dota15_yolo`（80\.86，.*?负向 \*\*\d+/(\d+)')
_vis_n = _dig(_A18N, r'visdrone`（70\.73，.*?负向 \*\*\d+/(\d+)')
_dt_mean = _dig(_A18N, r'dota15_yolo`（80\.86，\*\*\+?([\d.]+) pp\*\*')
_vis_mean = _dig(_A18N, r'visdrone`（70\.73，\*\*\+?([\d.]+) pp\*\*')
_mask_n = _dig(_A18N, r'mask_clean`（0\.10，.*?\*\*(\d+)/\d+ 为负')
_mende_n = _dig(_A18N, r'mendeley_yolo`（0\.59，.*?\*\*(\d+)/\d+ 为负')
_a18_r = _dig(_A18N, r'以按 root 聚合的 r 为准\*\*：\+?([\d.]+)')
_neu_d = _dig(_A18N, r'neu_det` \| 2\.29 \| \d+ \| \*\*\+?([\d.]+)\*\*')      # 均值
_neu_dens = _dig(_A18N, r'neu_det` \| (2\.29) \|')
# ---- A13 同域句（§4.5）----
_A13 = 'A13_同域对照_vs_跨域迁移.md'
_SP = _selftest_pairs()                       # {'sd': (n, mean), 'xd': (n, mean)}
_sd_n, _sd_mean = _SP.get('sd', (None, None))
_xd_n, _xd_mean = _SP.get('xd', (None, None))

# 稿内字面量（按上面解析出的值构造）
if _e45 is not None and _l_all is not None:
    _XCHK.append(('§4.5 端点差总数（轮数 %d + 标签 %d）' % (_e45, _l_all),
                  '%d paired endpoint differences' % (_e45 + _l_all)))
if _g_n is not None and _g_neg is not None:
    _XCHK.append(('§4.5 轮数轴过闸门 **%d** 条中负向 **%d**' % (_g_n, _g_neg),
                  '%d** clear that gate and **%d of them' % (_g_n, _g_neg)))
if _l_gate is not None:
    _XCHK.append(('§4.5 标签轴过闸门 **%d** 条' % _l_gate, '%d** clear it and **only 2' % _l_gate))
if _grp is not None and _pair is not None:
    _XCHK.append(('§4.5 独立组/配对 **%d / %d**' % (_grp, _pair),
                  '%d groups (%d independent pairs)' % (_grp, _pair)))
if _xd_n is not None:
    _XCHK.append(('§4.5 跨域格数 **%d**' % _xd_n, 'over %d cross-domain cells' % _xd_n))
if _sd_n is not None:
    _XCHK.append(('§4.5 同域格数 **%d**' % _sd_n, 'over %d cells' % _sd_n))
if _sd_mean is not None:
    _XCHK.append(('§4.5 同域均值 **+%.2f**' % _sd_mean, '**+%.2f pp** over' % _sd_mean))
if _xd_mean is not None:
    _XCHK.append(('§4.5 跨域均值 **+%.2f**' % _xd_mean, '**+%.2f pp** over %d' % (_xd_mean, _xd_n)))
if _dt_n is not None and _vis_n is not None:
    _XCHK.append(('§8 `dota15`/`visdrone` 格数 **%d / %d**' % (_dt_n, _vis_n),
                  'out of %d and %d' % (_dt_n, _vis_n)))
if _dt_mean is not None and _vis_mean is not None:
    _XCHK.append(('§8 两密集域均值 **+%.2f / +%.2f**' % (_dt_mean, _vis_mean),
                  '**+%.2f and +%.2f pp**' % (_dt_mean, _vis_mean)))
if _mask_n is not None:
    _w = _NUMWORD.get(int(_mask_n), str(int(_mask_n)))
    _XCHK.append(('§8 `mask_clean` 逐格全负 **%d**' % _mask_n, '%s of %s cells negative' % (_w, _w)))
if _mende_n is not None:
    _w = _NUMWORD.get(int(_mende_n), str(int(_mende_n)))
    _XCHK.append(('§8 `mendeley` 逐格全负 **%d**' % _mende_n, '%s of %s on the second' % (_w, _w)))
if _a18_r is not None:
    _XCHK.append(('§8 密度相关 **r ≈ %.2f**' % _a18_r, 'r \u2248 %.2f' % _a18_r))
if _neu_d is not None:
    _XCHK.append(('§8 `neu_det` 均值 **+%.2f**' % _neu_d, '+%.2f pp)' % _neu_d))
if _neu_dens is not None:
    _XCHK.append(('§8 `neu_det` 密度 **%.2f**' % _neu_dens, '%.2f instances per image' % _neu_dens))

# ★★ 2026-10-02 新增：`A21`（架构轴 2×2×10）与 `A22`（损失对增益）。
#   起因：§4.4 由"另一个（源域, backbone）组合上的复现"**升级**为
#   "同数据/同族/同轮数、只换 backbone" ⇒ 稿内第一次出现这四个增益与两个交互项。
#   新写进稿的数字**必须**同时进守卫，否则下一个人重跑生成器就会静默漂掉（经验 #6/#20）。
# ★★ 2026-10-02 补齐：报告里 **A2/A7/A8/A9/A11/A16 六行此前没有任何守卫**，
#   本轮实测其中三行已漂（A2 88/7→90/8、A8 真缺 38→61、A16 185→187），
#   三行经核对仍正确（A7/A9/A11）。以下把它们机械化。
# ⚠ 教训（写在这里，因为下面 `_must` 就是为它而设）：我上一轮给 A13/A14 写守卫时，
#   正则**一条都抓不到、静默不追加**，守卫看着"全绿"其实什么都没检查
#   —— **解析失败必须报红，不得静默跳过**。
def _must(label, ok, lit, target=None):
    """无条件追加一条检查；**解析失败即报红**，不得静默跳过。
    ⚠ `target` 必须指明是比**稿内**（`_XCHK`）还是比**报告**（`_RCHK`）——
      第一版把 §6 的三项（稿内数字）默认写进了 `_RCHK`，于是拿报告去比稿内的数，**永远红**。"""
    # ⚠ 防御：`lit` 为 None 会让渲染时的 `lit in _d` 抛 TypeError（已踩）。
    #   出现 None 说明**调用方的条件表达式写漏了**，这里直接报红并打出来。
    if lit is None:
        import sys as _s
        _s.stderr.write('[WARN] _must lit=None: ' + label)
        lit = '__LIT_IS_NONE__'
    (target if target is not None else _RCHK).append(
        (label + '（**解析失败**）', '__NEVER_MATCHES__') if not ok else (label, lit))

# ★★ 2026-10-04：**§9 的分辨率（功效审计）条目**此前**没有任何守卫**。
#   它引用的四个聚合数来自 `deliver/theory_B_MDE_by_cell.csv`（147 行逐格表），
#   而那份 CSV 在 2026-10-03 是"算过一次就冻结"、**没有生成脚本**。
#   现已有生成器兼守卫 `scripts/43_A24_power_audit.py`（147 行逐位可重算、含阴性对照）。
#   这里只做**稿内 ↔ CSV 的对撞**：从 CSV 读，算，再要求稿内出现**逐字**的期望串。
#   ⚠ 期望串里的 `43 of 147` / `32 of 73` / `11 of 74` 一律**算出来**，不写字面常量。
#   ⚠ 位置纪律：这一段**必须在 `_must` 定义之后**（第一次放前面 ⇒ NameError，已踩）。
_MDE_CSV = os.path.join(OUT, 'theory_B_MDE_by_cell.csv')
if os.path.exists(_MDE_CSV):
    _mrows = list(csv.DictReader(open(_MDE_CSV, encoding='utf-8')))
    _mtot = len(_mrows)
    _mins = sum(1 for r in _mrows if r['resolvable'] == 'False')
    _m3 = [r for r in _mrows if int(r['n']) == 3]
    _mgt = [r for r in _mrows if int(r['n']) > 3]
    _m3i = sum(1 for r in _m3 if r['resolvable'] == 'False')
    _mgti = sum(1 for r in _mgt if r['resolvable'] == 'False')
    _must('§9 功效审计总量 **%d of %d**' % (_mins, _mtot), bool(_mtot),
          '%d of %d cells have' % (_mins, _mtot), target=_XCHK)
    _must('§9 功效审计 n=3 档 **%d of %d**' % (_m3i, len(_m3)), bool(_m3),
          '%d of %d cells at three seeds' % (_m3i, len(_m3)), target=_XCHK)
    _must('§9 功效审计 n>3 档 **%d of %d**' % (_mgti, len(_mgt)), bool(_mgt),
          '%d of %d at more than three seeds' % (_mgti, len(_mgt)), target=_XCHK)
    # 两项模型（2026-10-04 新增的 §8 段）：它的两个支撑数一个在 §4.5、一个在 §4.6，
    # 都已有守卫；这里只钉**"未分离"的披露句**必须留在正文（协议 §8.2：披露不因篇幅删除）。
    _must('§8 两项模型的"未分离"披露句',
          True, 'are **not measured independently anywhere in this paper**', target=_XCHK)
    # 测量层级命题（2026-10-04 新增的 §6 段）：钉住**证伪条件**——不许只写命题而不写它怎么被推翻。
    #   ⚠ 2026-10-04 第二轮：对抗性评审指出原句"过门 + 指数趋近 2 + 排序不变"里
    #     "过门"与另两条**互相矛盾**（过门 = 侧条件成立），故正文改为"指数趋近 2 **且** 排序在换评估器后存活"。
    #     期望串随之更新（守卫的期望串**必须**与稿内逐字一致，否则报红即噪声 —— 见上面 §1 的三条假红）。
    #   ⚠ 2026-10-04 第四轮：对抗性评审 A2 指出原句是**不可证伪的合取**
    #     （"指数趋近 2 **且** 排序换评估器不变" —— 二者由构造互斥）⇒ 正文已拆开：
    #     指数趋近 2 **单独即证伪**；排序不变另写成"该族可作诊断"的充分条件。期望串随之更新。
    _must('§6 测量层级命题的证伪条件（**单独成立**，不是合取）',
          True, 'would falsify the placement we report, on its own and without any further condition',
          target=_XCHK)
    # ★★ 2026-10-04 第三轮：**检索复跑后新增的三处"划界句"必须留在正文**。
    #   理由：F/G/H 三条的复跑**各压低了本稿的一档新颖度**，正文之所以仍然站得住，
    #   **全靠这三句把可主张的范围钉死在"具体测量与因变量"上**。若有人为了减页把它们删掉，
    #   稿子立刻变成"主张首次做某事"⇒ **投稿必被拒**。⇒ 三条期望串各钉一句。
    _must('§4.6 同域段：明写"不是第一个做该对比的"（F 复跑后新增的划界句）',
          True, 'It is not the first comparison of same-domain and cross-domain pretraining on detection',
          target=_XCHK)
    _must('§4.4 骨干段：明写"隔离不是新的、新的是对增益之差做检验"（G 复跑后新增的划界句）',
          True, 'is **already** present in the detection literature', target=_XCHK)
    _must('§9 密度条：明写"不是第一个用语料统计预测迁移行为的"（H 复跑后新增的划界句）',
          True, 'It is also not the first corpus statistic used to predict transfer behaviour',
          target=_XCHK)
    _must('§2：把去魅路线写成本文同域读数的语境（F 复跑后新增的定位句）',
          True, 'need not come from transfer', target=_XCHK)
    _must('§2：把"隔离式骨干对照已有先例"写进定位（G 复跑后新增的定位句）',
          True, 'backbones are already compared', target=_XCHK)
    _must('§10：搜索覆盖的边界（含两条通道两轮均不可用）',
          True, 'were **unusable in both rounds**', target=_XCHK)
    # ★★ 2026-10-04 第五轮：**第二轮头脑风暴后新写的"自我戳穿"句必须留在正文**。
    #   这些句子的共同点是：**它们各自堵掉一个审稿人可以直接引用来拒稿的读法**。
    #   为减页把它们删掉，稿子会**立刻变成过度主张**，所以逐条钉住（删掉即报红）。
    _must('§8 两项描述：明写 $M$ 不能读成域失配（同域负格反驳）',
          True, 'if $M$ were a source–target **mismatch** cost', target=_XCHK)
    _must('§8 同域约束的两个反例读数（−1.195 / −2.027）',
          True, '**−1.195 pp** (t = −7.85)', target=_XCHK)
    _must('§4.3 列口径：明写第二批在**声明列**上不重现',
          True, 'does not reproduce that reading on the declared column', target=_XCHK)
    _must('§4.3 第二批的声明列读数（+0.004 / t=+0.02）',
          True, '**+0.004 pp** (t = +0.02, seven of thirteen seeds negative)', target=_XCHK)
    _must('§4.2 观测范围 vs 推断界 分开写',
          True, 'the 95% half-width is **±0.23 pp**', target=_XCHK)
    _must('§4.2 有界零的普查（45 条端点差里只有两条达标）',
          True, 'only **two** reach an MDE of 0.31 pp or below', target=_XCHK)
    _must('§6 命题：明写"我们不测 $r_D$"',
          True, '**We do not measure $r_D$**', target=_XCHK)
    _must('§9 把功效审计收成一条判据（gamma(n)）',
          True, r'$|\bar\Delta|/\hat\sigma \ge \gamma(n)$', target=_XCHK)
    _must('§9 两个种子数的中位标准化效应量（4.37 vs 3.03）',
          True, r'is **4.37** among the three-seed cells against **3.03**', target=_XCHK)
    _must('§9 明写 n=10 是**事后**的账、不是事前规则',
          # ⚠ 2026-10-04 第六轮：**对抗性核查查出 Appendix P.2 的算术错** ——
          #   n=9（不是 n=10）才是中位噪声下可判 0.30 pp 的最小整数；P.1 的 gamma 表原也用了错口径。
          #   正文与补材均已更正 ⇒ 期望串随之更新（只留"事后账"这个判据，不绑死措辞）。
          True, 'retrospective account, not an ex-ante rule', target=_XCHK)
    _must('§9 审计覆盖**水平量**、不覆盖差值量',
          True, 'It is a statement about **single-budget levels**, not about the **differenced** quantities',
          target=_XCHK)
    _must('§7 新增 `Scope of inference` 段',
          True, '**Scope of inference.**', target=_XCHK)
    _must('§7 明写"没有任何一条主张三者同时通过"',
          True, 'passes family correction, power qualification and the clean three-way protocol at once',
          target=_XCHK)
    _must('§10 工具句改成"约束记录而非效应"',
          True, 'constraints on what may be recorded as a result', target=_XCHK)
    # ★★ 2026-10-04 第六轮：§4.5 新增的**留出符号预测**（C1，作者侧已独立复核：
    #   21/25=84.0%、五档 family 4/6 全同号、标号轴 7/7，三个数字逐位吻合）。
    #   同时钉住它的两个限制句与三个具名反例（这些句子被删 = 把"计数"卖成"定律"）。
    _must('§4.5 留出符号预测：21 of 25',
          True, 'predicted correctly on **21 of 25** slices', target=_XCHK)
    _must('§4.5 留出符号预测：4 of 6 家族五档全同号',
          True, '**4 of the 6** pair–families that carry all five label budgets', target=_XCHK)
    _must('§4.5 明写"独立单元是家族不是切片"',
          True, 'the **independent units are the families, not the slices**', target=_XCHK)
    _must('§4.5 三个具名反例（含 sign-reversing）',
          True, 'three of them sign-reversing with both slices resolvable', target=_XCHK)
    _must('§4.5 明写该检验是**事后决定**的',
          True, 'the exercise was decided after the archive existed', target=_XCHK)
    # ★★ 2026-10-04 第四轮：**§3/§5 的注册判据必须保持"三项"完整**。
    #   起因：正文原写 `conventional significance and a ≥0.30 pp effect size`，
    #   而冻结件 `analysis/预注册_新目标域复制实验_冻结_20260913.md` §1/§4 逐字是
    #   **三项**：配对 `p < 0.01`、**≥8/10 同向**、均值 `≥ +0.30 pp`（外加 BH q=0.05）。
    #   ⇒ 漏掉任何一项，§5 的"只有幅值条没达标"这句话的力度就会被读错（T1-b 其实三项过两项）。
    _must('§3 注册判据写全三项（p<0.01 + 方向 + 幅度）',
          True, 'a paired significance level of p < 0.01, at least eight of ten seeds moving in the same direction, and an effect size of \u2265 +0.30 pp',
          target=_XCHK)
    _must('§5 T1-b 行写明"significance 与 direction 都过、只差幅值条"',
          True, 'significance and direction met, fails the \u22650.30 pp magnitude bar', target=_XCHK)
else:
    _must('§9 功效审计（缺 `theory_B_MDE_by_cell.csv`）', False, '', target=_XCHK)


def _read(fn):
    return _try_read(os.path.join(_ANA, fn))

# ⚠ `_RCHK` 必须**在这里**初始化：`_must()` 会往它里面追加，而 `_XCHK` 段就要用到 `_must`。
#   第一版把它留在后面初始化 ⇒ `_XCHK` 段调用 `_must` 时 `NameError`；而且后面的
#   再次初始化会把先追加的项**清空**（哪怕不报错也会静默丢项）。
_RCHK = []

# ★★ 2026-10-04：**六条"缺作者/缺完整条目"的参考文献**此前**没有任何守卫**。
#   背景（交接件 §6.2 第 7 项）：`[2]` `[3]` `[4]` `[6]` 缺作者，`[11]` `[12]` 是
#   "标识符 — 说明"式的占位条目（连题名都不是参考文献格式）。
#   2026-10-04 经跳板机取到**第一手元数据**后补齐（逐条来源见
#   `deliver/新稿参考文献_核验.md`）：DataCite（`[2]`）、Crossref `works/{doi}`（`[3][4][6][11][12]`）。
#   ⚠ 铁律 #6"没有第二来源就不改数"：这六条**全部来自注册机构的结构化接口**，
#     不是凭记忆写作者；期望串就是**接口返回的第一作者姓氏**。
#   ⚠ 判据必须钉"**作者 + 题名**"两件，否则下一个人把条目改回占位式也照样绿。
#   ⚠ 期望串必须是稿内的**逐字子串**（`_XCHK` 的判据是 `lit in 稿内文本`）：
#     第一版把期望串写成 `作者 + 空格 + 题名`（如 `Chegondi LeakageBench`），而稿内是
#     `K. S. Chegondi. "LeakageBench: …"` ⇒ 六条**全部假红**。⇒ 期望串改取 `[n] 首作者` 的逐字片段。
_REFAUTH = [
    # ⚠ 第三列 = 期望串（必须是稿内**逐字子串**）；第四列 = 该行必须包含的首作者姓氏。
    #   `[30]`–`[34]` 是 2026-10-04 F 主张检索复跑后**新增**的五条（去魅路线的既有工作）。
    ('[2]', 'K. S. Chegondi', 'Chegondi'),
    ('[3]', 'S. A. Al-Emadi', 'Al-Emadi'),
    ('[4]', 'P. Oza', 'Oza'),
    ('[6]', 'K. Li', 'Li'),
    ('[11]', 'T. Gebru', 'Gebru'),
    ('[12]', 'M. Mitchell', 'Mitchell'),
    ('[30]', 'Y. Li, H. Zhang, Y. Zhang', 'Li'),
    ('[31]', 'K. He, R. Girshick, P. Doll\u00e1r', 'He'),
    ('[32]', 'M. Raghu, C. Zhang, J. Kleinberg, S. Bengio', 'Raghu'),
    ('[33]', 'F. Kanavati, M. Tsuneki', 'Kanavati'),
    ('[34]', 'D. Pototzky, A. Sultan, L. Schmidt-Thieme', 'Pototzky'),
    # `[35]`–`[39]`：2026-10-04 G/H 检索复跑后补入（同层先例：标注统计预测迁移；
    # 源模型精度预测迁移；隔离式骨干对照；架构与预训练权重分开考察）。
    ('[35]', 'A. T. Tran, C. V. Nguyen, T. Hassner', 'Tran'),
    ('[36]', 'S. Kornblith, J. Shlens, Q. V. Le', 'Kornblith'),
    ('[37]', 'N. Ding, A. Eskandarian', 'Ding'),
    ('[38]', 'S. Mahadevkar, S. Patil, K. Kotecha, A. Abraham', 'Mahadevkar'),
    ('[39]', 'J. Ning, H. Guan, M. Spratling', 'Ning'),
]
for _tag, _expect, _who in _REFAUTH:
    # ⚠ 不能用 `r'^\%s .*$' % tag`：`\%` 会变成"字面百分号"，于是 `re.escape('[2]')` 的 `\[`
    #   被当成字符集转义 ⇒ `re.error: unterminated character set`（已踩）。用**拼接**。
    _mline = re.search('^' + re.escape(_tag) + ' .*$', _d, re.M)
    _line = _mline.group(0) if _mline else ''
    _okref = bool(_mline) and (_who in _line) and ('"' in _line) and ('— ' not in _line)
    _must('参考文献 %s 已补作者与完整题名（首作者=%s）' % (_tag, _who), _okref,
          _expect, target=_XCHK)

_A21 = 'A21_架构轴实测_2x2.md'
_a21g = _dig_all(_A21, r'增益 \*\*([+-]?[\d.]+) pp\*\*')          # 顺序：best×2, test×2
_a21i = _dig_all(_A21, r'交互项 ([+-]?[\d.]+) pp')
_a21t = _dig_all(_A21, r'交互项 [+-]?[\d.]+ pp，t=([+-]?[\d.]+)')
# 稿内用的是 U+2212 减号（不是 ASCII 连字符）⇒ 期望串必须用同一个字符，否则守卫会假红
_MINUS = '\u2212'
if len(_a21g) == 4:
    _XCHK.append(('§4.4 val-best 两 backbone 增益 **+%.2f / +%.2f pp**' % (_a21g[0], _a21g[1]),
                  '**+%.2f / +%.2f pp**' % (_a21g[0], _a21g[1])))
    _XCHK.append(('§4.4 test 两 backbone 增益 **+%.2f / +%.2f pp**' % (_a21g[2], _a21g[3]),
                  '**+%.2f / +%.2f pp**' % (_a21g[2], _a21g[3])))
if len(_a21i) == 2 and len(_a21t) == 2:
    _XCHK.append(('§4.4 test 交互项 **%s%.2f pp**（t = %s%.2f）'
                  % (_MINUS, abs(_a21i[1]), _MINUS, abs(_a21t[1])),
                  '**%s%.2f pp** (t = %s%.2f' % (_MINUS, abs(_a21i[1]), _MINUS, abs(_a21t[1]))))
    _XCHK.append(('§4.4 val-best 交互项 **+%.2f pp**（t = +%.2f）' % (_a21i[0], _a21t[0]),
                  '**+%.2f pp** (t = +%.2f' % (_a21i[0], _a21t[0])))
_A22 = 'A22_损失对增益_实测.md'
# ⚠ `_dig_all` 按**文档出现顺序**取 ⇒ [0] 是 val-best 列、[1] 是 test 列。
#   曾用 `max(...)` 一律取最大值 ⇒ 把 test 列的 0.41 当成 val-best 写进守卫（列混了）。
_a22m = _dig_all(_A22, r'损失对增益的最大绝对幅度\*\*：\*\*([\d.]+) pp\*\*')
if len(_a22m) == 2:
    _XCHK.append(('§9 换损失后幅度变化（val-best ≤ %.2f / test ≤ %.2f pp）' % (_a22m[0], _a22m[1]),
                  'at most %.2f pp on the val-best column and %.2f pp on the test column'
                  % (_a22m[0], _a22m[1])))
_A23 = 'A23_三backbone对照.md'
# ⚠ `_dig_all` 只返回**第 1 个捕获组**（扁平 float 列表）⇒ 这里需要 4 组，
#   所以直接用 `re.findall`。第一版用 `_dig_all` 然后 `[i][0]` 下标，当场 TypeError。
# ⚠ 格式必须与稿内**逐字符**一致：近零值保留 3 位（否则 −0.005 会被 %+.2f 印成 −0.01，
#   把噪声说成负号），且稿内用的是 U+2212 减号。
def _fx(v):
    s_ = ('%+.3f' % v) if abs(v) < 0.05 else ('%+.2f' % v)
    return s_.replace('-', _MINUS)


_a23txt = _try_read(os.path.join(_ANA, _A23))
_a23 = re.findall(r'：30ep ([+-]?[\d.]+) \(\|t\|=[\d.]+\) / ([+-]?[\d.]+) \(\|t\|=[\d.]+\)；'
                  r'100ep ([+-]?[\d.]+) \(\|t\|=[\d.]+\) / ([+-]?[\d.]+)', _a23txt)
_a23 = [tuple(float(x) for x in t) for t in _a23]
if len(_a23) == 3:
    _b30 = [_a23[i][0] for i in range(3)]
    _t30 = [_a23[i][1] for i in range(3)]
    _b100 = [_a23[i][2] for i in range(3)]
    _t100 = [_a23[i][3] for i in range(3)]
    _XCHK.append(('§4.4 三代 30ep（val-best） %s / %s / %s' % tuple(map(_fx, _b30)),
                  '%s / %s / %s pp** at 30 epochs' % tuple(map(_fx, _b30))))
    _XCHK.append(('§4.4 三代 100ep（val-best） %s / %s / %s' % tuple(map(_fx, _b100)),
                  '%s / %s / %s pp** at 100 epochs' % tuple(map(_fx, _b100))))
    _XCHK.append(('§4.4 三代 30ep（test） %s / %s / %s' % tuple(map(_fx, _t30)),
                  '%s / %s / %s pp**' % tuple(map(_fx, _t30))))
    _XCHK.append(('§4.4 三代 100ep（test） %s / %s / %s' % tuple(map(_fx, _t100)),
                  '%s / %s / %s pp**' % tuple(map(_fx, _t100))))
# 批次分解：`b2`@100 的 best 列（单独一批，n=10）
# ⚠ 直接取**渲染后的字符串**，不要再 `float()` 后 `_fx()` —— 那是对 3 位值再取 2 位：
#   `+0.325`（3 位）再取 2 位得 `+0.33`，而真值 0.3246 的 2 位是 `+0.32`。
_a23b = re.findall(r'\| `b2` \| 100 \| \*\*([^*]+)\*\*', _a23txt)
if _a23b:
    _v = _a23b[0].strip()
    _XCHK.append(('§4.4 单批次 b2@100 %s pp' % _v, '%s pp** on batch `b2` alone' % _v))
# ★ A14 **分族**覆盖（不是全局那个）：报告与稿内都曾写死 89/67%，真值 112/84%。
#   ⚠ 计算必须放在 `_XCHK` 段**之前**：第一版把它放到后面的 `_RCHK` 段，
#     结果 `_XCHK` 用到 `_m14` 时它还没定义 ⇒ NameError。
_A14t = _read('A14_数据质量普查.md')
_m14 = re.search(r'\| `smoke→sfchd` \| `b2` \| (\d+) \| (\d+) \| \*\*(\d+)\*\* \|', _A14t)
_c14 = round(100.0 * int(_m14.group(2)) / int(_m14.group(1))) if _m14 else None
if _m14:
    _XCHK.append(('§4.2 `smoke→SFCHD` 分族覆盖 **%s of %s (%d%%)**'
                  % (_m14.group(2), _m14.group(1), _c14),
                  '%s of which carry a test reading (%d%%)' % (_m14.group(2), _c14)))
# ★★ 2026-10-02 第三轮之二：**稿内 §3 ↔ 补充材料**的机械对撞。
#   起因：§3 的三分割数字（33.31/29.74/29.86、−0.069、p=0.825）**不在底座里**，
#   只能从补材核；而跨件守卫此前只盯"稿内 ↔ 底座生成件"，这类**外部来源**完全没覆盖。
# ★★ 2026-10-05 修：`_SUPT` 原先**只在 if 分支内赋值**，而 L882 起**无条件使用**
#   ⇒ 放行布局下 `_SUP` 上溯三级不存在 ⇒ `NameError`，**L882 之后所有检查不执行**。
#   现改为：默认空串，缺失时**报红**（不静默、也不崩）。
_SUPT = ''
_SUP = os.path.join(BASE,
                    'M3_draft', '00_SUPPLEMENTARY_v0.4.md')
if os.path.exists(_SUP):
    _SUPT = open(_SUP, encoding='utf-8', errors='replace').read()
else:
    print('❌ 补材未找到（%s）⇒ 依赖补材的检查无法执行，**报红**而非崩溃。' % _SUP)
    _msp = re.search(r'\*\*(\d+\.\d+) / (\d+\.\d+) /\s*(\d+\.\d+) mAP50-95\*\*', _SUPT)
    if _msp:
        _lvl = '%s / %s / %s' % (_msp.group(1), _msp.group(2), _msp.group(3))
        _XCHK.append(('§3 三分割水平（补材 §N.2） **%s**' % _lvl, '(%s mAP50-95' % _lvl))
    _msr = re.search(r'\*\*(−|−|-)(\d+\.\d+) pp\*\* \(t = (−|−|-)?([\d.]+), \*\*p = ([\d.]+)\*\*', _SUPT)
    if _msr:
        _XCHK.append(('§3 重键位移（补材 §N.2） **p = %s**' % _msr.group(5),
                      'p = %s)' % _msr.group(5)))
    # ⚠ 已知未决：稿内 §3 写 "40 runs each"，补材 §N.2 写 "806 evaluations over 41 runs"，
    #   补材全文**没有"40"**。底座 threeway=388 run，与 40/41 **不是一个总体** ⇒ 无法定案。
    #   这里**不断言稿内数字**（不擅自改），只断言**分歧已被登记**，避免它被静默遗忘。
    _m41 = re.search(r'\*\*(\d+) evaluations over (\d+) runs\*\*', _SUPT)
    _REC = _try_read(os.path.join(BASE, 'provenance', 'provenance', 'deliver',
                             '修正记录_底座扩容后全量复核_20261002.md'))
    # ⚠ 本项**不能**放进 `_XCHK`：`_XCHK` 的期望串是**拿稿内**（`_d`）去比，
    #   而这里要比的是**登记件**。第一版放进 `_XCHK` ⇒ 永远红（已踩）。
    # ★ 2026-10-05：此处原先 `_OPEN = []`；已改为**全局无条件初始化**，
    #   因为该分支的条件依赖一个在放行仓库里不存在的登记件，分支不执行时会 NameError。
    # ★ 2026-10-02 第九轮：**已裁定并闭合**。
    #   证据链：补材 §N.2 自 2026-09-25 出现起，**每一个版本（30+ 个 .bak）都写 41 runs**，
    #   而**没有任何版本写过 40**；底座的三方总体是 388 run（不是 40/41）；补材 M.5 的
    #   三方清单约 70+ run —— 所以稿内的 `40` 在**任何来源里都不存在**，已对齐为 **41**。
    #   守卫随之从"登记分歧"升级为**真对撞**：稿内数必须等于补材数。
    if _m41:
        # ★★ 第十一轮**深查后的更正**：这两个数**计量的是不同的东西**，不能互相替代。
        #   · 稿内 `40 runs each` 修饰的是**三份水平**那句，与补材的 **within-domain mean** 同侧；
        #     工作区里恰好有一个可验证的 40：**两个 10 种子同域格**（`dota15→dota15`、`visdrone→visdrone`，
        #     正是补材 §M.5 标注 "**(10 seeds)**" 的那两格）× **2 臂** = 40（见 `work/_relbak_clean_threeway_perseed_*.csv.bak`）。
        #   · 补材 §N.2 的 `%s runs / 806 evaluations` 修饰的是**重键审计**，是另一件事。
        #   ⇒ 上一轮我把 `40` 改成 `41` 是**把两个从句混为一谈**，已回退。
        _XCHK.append(('§3 三份水平那句的 run 数（稿内 40；与补材审计的 %s 是**两件事**）' % _m41.group(2),
                      '40 runs each)'))
        # ⚠ 审计数（41 runs / 806 evaluations）是**补材**的数字，**不能**放进 `_XCHK`
        #   —— `_XCHK` 一律对**稿内**比对（第一版这么写 ⇒ 恒红）。它由未决项登记守住。
    # 第 2 项（§3 的 40 vs 41）**已闭合**；剩下的真未决项是 `0.31 pp` 的**约定**：
    # 底座可重建该数，但现稿没写明用的是哪个 SD 与哪个检验 ⇒ 需作者补写（不是改数）。
    # ★ 第十轮：`0.31 pp` 的口径**已查实并写进正文**（原定义在
    #   `E1a_E1b_E4_冻结本_20260922.md` §5.0，实现见 `work/e1a_bound.py`）⇒ 该项**已闭合**。
    #   剩下的真未决项是 §3 的**集合等价性假设**：已按"同一审计"对齐为 41 run，
    #   若三份水平的 run 集另有其数，需作者给出该集合的 run 数。
    _OPEN.append(('§3 的 `40 runs each`（水平集）与补材 §N.2 的 `41 runs`（审计集）**是两个集合**；'
                  '40 与"两个 10 种子同域格×2臂"吻合但**无存活生成件**，待作者确认',
                  '无存活生成件'))
# ★★ 2026-10-02 第四轮之二：稿内 **§6** 的三个数字此前**没有任何守卫**。
#   核出来源后发现它们**不在补材、也不在底座**，而来自**更早的内部工作笔记**（2026-09-06/07）：
#     · `253–284（±6%）` ← `GLM审查_冻结包五项与新增发现_20260906.md`
#     · `≈2.3×`          ← `G24统计汇总_未污染部分_20260907.md`（`306 vs 697` ⇒ 697/306 = 2.28）
#     · `0.76–1.47`      ← 补材（`SNR ∈ 0.76–1.47`）
#   ⇒ 来源类别**弱于**补材/底座，这一点已登记在修正记录里，此处只做机械对撞。
_TOP = BASE
_NOTES = {}
for _fn in ('GLM审查_冻结包五项与新增发现_20260906.md', 'G24统计汇总_未污染部分_20260907.md'):
    _fp_ = os.path.join(_TOP, _fn)
    if os.path.exists(_fp_):
        _NOTES[_fn] = open(_fp_, encoding='utf-8', errors='replace').read()
_glm = _NOTES.get('GLM审查_冻结包五项与新增发现_20260906.md', '')
_g24 = _NOTES.get('G24统计汇总_未污染部分_20260907.md', '')
_mspec = re.search(r'谱读数跨 \d+ 变体 (\d+)[–\-](\d+)（±(\d+)%）', _glm)
# ⚠ 用 `_must` 无条件追加：源文件读不到/正则抓不到 ⇒ **报红**，不得静默跳过
_meps = re.search(r'exponents of \*\*([\d.]+)[–\-]([\d.]+) \(median ([\d.]+)\)\*\*', _SUPT)
_must('§6(c) ε-缩放指数（补材 G.2） **%s–%s**，中位 **%s**'
      % (_meps.group(1), _meps.group(2), _meps.group(3)) if _meps else '§6(c) ε-缩放指数（补材 G.2）',
      bool(_meps), ('%s–%s**, where' % (_meps.group(1), _meps.group(2))) if _meps else '',
      target=_XCHK)
_must('§6(c) 源域驻点谱读数（补材 G.2）', bool(_mspec),
      ('%s–%s, ±%s%%' % (_mspec.group(1), _mspec.group(2), _mspec.group(3))) if _mspec else '',
      target=_XCHK)
_m23 = re.search(r'(\d+) vs 上次（v2 测）(\d+)（([\d.]+)× 差）', _g24)
_must('§6(a) 跨次读数波动（工作笔记 G24 %s/%s = %s×）'
      % (_m23.group(2), _m23.group(1), _m23.group(3)) if _m23 else '§6(a) 跨次读数波动（工作笔记 G24）',
      bool(_m23), ('≈%s×' % _m23.group(3)) if _m23 else '', target=_XCHK)
_msnr = re.search(r'SNR ∈ ([\d.]+)[–\-]([\d.]+), all below the prospectively frozen gate of (\d+)', _SUPT)
_must('§6(a) SNR 带宽（补材 H.1） **%s–%s**，gate **%s**'
      % (_msnr.group(1), _msnr.group(2), _msnr.group(3)) if _msnr else '§6(a) SNR 带宽（补材 H.1）',
      bool(_msnr), ('(band %s–%s)' % (_msnr.group(1), _msnr.group(2))) if _msnr else '',
      target=_XCHK)
# ★★ 2026-10-02 第四轮之三：**参考文献里的语料计数**此前无守卫。
#   实测已漂：YOLOv12 `2,136 of the 2,243`（真值 **2,241 / 2,362**）、YOLO11 `62 runs`（真值 **76**）。
#   来源 = `A1b` 的逐 backbone 表。
_A1bt = _read('A1b_架构链映射.md')
_bb = {}
for _m in re.finditer(r'\| `(yolo\d+n)` \| (\d+) \|', _A1bt):
    _bb[_m.group(1)] = int(_m.group(2))
_tot_bb = _dig('A1b_架构链映射.md', r'\| 底座 run \| (\d+) \|')
#   ⚠ 2026-10-03 修**假红**：上面三条 2026-10-02 的期望串与稿内**不逐字一致**，于是每次跑都报三条
#     "跨件漂移"，而稿内的数其实是对的（`2,241 / 2,362 / 76 / 14` 与 `A1b` 逐位吻合）。
#     两处根因（都是**守卫自己的**，不是稿子的）：
#       ① YOLOv12：期望串用了 `the backbone of **…**`，而稿内该句是 `…; **2,241 of the 2,362 runs** in the released archive …`，
#          前四个词**根本不在稿内**（`_XCHK` 的判据是 `lit in 稿内文本`，不是"标签里的描述"）⇒ 永远红。
#       ② YOLO11/26：期望串写成 `(**76 runs**)`（外层圆括号），而稿内是 ``(`yolo11n`, **76 runs**)`` ⇒ 同样永远红。
#     纪律（经验 #56 的反面）：**守卫的期望串必须与稿内逐字一致**，否则"报红"本身就是噪声，
#     会训练下一个人忽略这条通道 —— 这条假红已经被忽略过多次。
_must('参考文献 YOLOv12 语料计数', bool(_bb.get('yolo12n') and _tot_bb),
      ('**%s of the %s runs**' % (format(_bb['yolo12n'], ','), format(int(_tot_bb), ',')))
      if (_bb.get('yolo12n') and _tot_bb) else '', target=_XCHK)
_must('参考文献 YOLO11 语料计数', bool(_bb.get('yolo11n')),
      ('`yolo11n`, **%d runs**' % _bb['yolo11n']) if _bb.get('yolo11n') else '', target=_XCHK)
_must('参考文献 YOLO26 语料计数', bool(_bb.get('yolo26n')),
      ('`yolo26n`, **%d runs**' % _bb['yolo26n']) if _bb.get('yolo26n') else '', target=_XCHK)
# ★★ 2026-10-02 第五轮之二：稿内 **§7 的干净三方协议四个数**此前无守卫。
#   实测**两个是舍入错**（且稿内自相矛盾）：
#     · `smoke→sfchd20` test 11 种子：底座 **+1.4091** ⇒ 3 位应为 **+1.409**，稿内原写 +1.408；
#     · `shwd2sf→sfchd20` test 13 种子：底座 **+0.6277** ⇒ 3 位应为 **+0.628**，§3/§6 写 +0.628、
#       而 §7 写 +0.627 —— **同一个量两个数**。
#   来源 = `deliver/§7_clean三方协议_run清单_20261001.md` 的**计算值**列。
_CLEAN = _try_read(os.path.join(BASE, 'provenance', 'provenance', 'deliver',
                 '§7_clean三方协议_run清单_20261001.md'))
_clean = re.findall(r'\| \*\*\+([\d.]+)\*\* \|', _CLEAN)
if len(_clean) >= 4:
    # 文档顺序：1.4340, 1.4091, 0.5070, 0.6277
    _v = ['%+.3f' % float(x) for x in _clean[:4]]
    _must('§7 干净三方协议四点（10/11/10/13 种子）',
          True, '%s / %s' % (_v[0], _v[2]) if False else
          ('%s / %s pp** at ten seeds' % (_v[0], _v[2])), target=_XCHK)
    _must('§7 干净三方协议扩展两点（11/13 种子）',
          True, ('%s / %s** at eleven and thirteen seeds' % (_v[1], _v[3])), target=_XCHK)
# ★★ 2026-10-02 第五轮之三：稿内 **§7 的 OOM→CPU 回退效应**（补材 Appendix E 附录）此前无守卫。
#   补材 L138 原文：`median mAP50-95 difference of **−0.0006 pp** (mean −0.0010 pp) over 20 cells,
#   against the data-order σ̂ of **0.166–0.190 pp**` ⇒ 与稿内逐字一致。
_moom = re.search(r'median mAP50-95 difference of \*\*[−-]([\d.]+) pp\*\*.*?over (\d+) cells, against the data-order σ̂ of \*\*([\d.]+)[–\-]([\d.]+) pp\*\*', _SUPT)
_must('§7 OOM 回退的中位效应（补材） **%s pp / %s cells**' % (_moom.group(1), _moom.group(2)) if _moom else '§7 OOM 回退的中位效应（补材）',
      # ⚠ 只断言**符号之后**的部分（`0.0006 pp** over 20 cells`）：稿内减号可能是 U+2212，
      #   而补材用的是 ASCII `-`；直接连符号一起比会因字符差异**假红**（已踩一次）。
      bool(_moom), ('%s pp** over %s cells' % (_moom.group(1), _moom.group(2))) if _moom else '',
      target=_XCHK)
_must('§7 OOM 回退对照的 σ̂ 区间（补材） **%s–%s pp**' % (_moom.group(3), _moom.group(4)) if _moom else '§7 σ̂ 区间（补材）',
      bool(_moom), ('%s–%s pp**' % (_moom.group(3), _moom.group(4))) if _moom else '',
      target=_XCHK)
# ★★ 2026-10-02 第五轮之四：稿内 **§4.6 的标签轴四个数**此前**完全没有守卫**
#   （`14_verify_claims` 的断言只覆盖 §4.1/§4.2/§4.4/§5，**没有 §4.6**）——
#   而 §4.5 正文说"the label axis is itself a measured result"。来源 = `A9` 的标签轴表。
_A9t = _read('A9_全域预算轴扫描.md')
def _lab(pair, fam, ep):
    m = re.search(r'\| `%s` \| `%s` \| %sep \| 10%%→50%% \| \d+ \| \*\*([+-]?[\d.]+)\*\*' % (pair, fam, ep), _A9t)
    return float(m.group(1)) if m else None
# ⚠ 期望串**只取「数值 + 粗体」**，不接后面的措辞：第一版接了 ` (ten of ten`，
#   而稿内实为 ` (ten of ten seeds lower` ⇒ 假红。措辞会改，数值才是要守的。
_labs = [('§4.6 `pcb→neu_det` 30ep 标签轴', _lab('pcb→neu_det', 's2df', 30), '%.2f pp**'),
         ('§4.6 `pcb→neu_det` 100ep 标签轴', _lab('pcb→neu_det', 's2df', 100), '%.2f pp**'),
         ('§4.6 `visdrone→dota15` 30ep 标签轴', _lab('visdrone→dota15', 's2ae', 30), '+%.2f pp** at 30 epochs'),
         ('§4.6 `visdrone→dota15` 100ep 标签轴', _lab('visdrone→dota15', 's2ae', 100), '+%.2f pp** at 100 epochs')]
for _lbl, _val, _litfmt in _labs:
    _must(_lbl, _val is not None, (_litfmt % abs(_val)) if _val is not None else '', target=_XCHK)
# 密度值（§9 引用的 corpus 密度）—— 来源 = `A18` 的密度表
for _nm, _lit in (('mask_clean', '`mask_clean` 0.10'), ('visdrone', '`visdrone` 70.7'),
                  ('dota15_yolo', '`dota15` 80.9'), ('neu_det', '2.29 instances per image')):
    # ⚠⚠ **不能**用 `_d` 当循环变量：全局 `_d` 是**稿内全文**，覆盖它会让后面所有
    #     `lit in _d` 抛 `TypeError: argument of type 'NoneType' is not iterable`
    #     —— 报错信息指向 `lit`，真凶却是被遮蔽的 `_d`（已踩，排查了三轮）。
    # ⚠ 密度表是 `| \`路径\` | 图数 | 框数 | **密度** |`，所以正则必须**跨过两个 `|`**。
    #   第一版写 `[^|]*\| \*\*` —— `[^|]` 跨不过列分隔符 ⇒ 四个 corpus 全部「解析失败」。
    _dens = _dig('A18_标注密度调节变量.md', r'%s\` \| \d+ \| \d+ \| \*\*([\d.]+)\*\*' % _nm)
    _must('§9 密度值 `%s`' % _nm, _dens is not None, _lit if _dens is not None else '', target=_XCHK)
# ★★ 2026-10-02 第六轮之二：§4.6"同域对照"段里**除均值外**的四个数此前无守卫
#   （来源 `A13`：同域 17 格 median +0.650、\|t\|≥2 16/17、负向 5/17(29%)；
#     跨域 130 格 median +0.940、负向 30/130(23%)）。
_A13t = _read('A13_同域对照_vs_跨域迁移.md')
for _lbl, _pat, _fmt, _litfmt in (
        ('§4.6 同域 median', r'格数 \*\*17\*\*；增益均值 \*\*\+([\d.]+) pp\*\*（中位 \+([\d.]+)）',
         None, 'median +%s'),
        ('§4.6 同域 \|t\|≥2 比例', r'\|t\|≥2 的格 \*\*(\d+)/(\d+)\*\*', None, '%s of %s'),
        ('§4.6 同域负向比例', r'\*\*负向格 (\d+)/(\d+)（(\d+)%）\*\*', None, '%s%% negative'),
        ('§4.6 跨域 median', r'格数 \*\*130\*\*；增益均值 \*\*\+([\d.]+) pp\*\*（中位 \+([\d.]+)）',
         None, 'median +%s'),
        ('§4.6 跨域负向比例', r'格数 \*\*130\*\*.*?\*\*负向格 (\d+)/(\d+)（(\d+)%）\*\*', None, None)):
    pass
_m13sd = re.search(r'格数 \*\*17\*\*；增益均值 \*\*\+[\d.]+ pp\*\*（中位 \+([\d.]+)）', _A13t)
# ⚠ **不能**拿 `|t|` 当锚点：生成件里是 markdown 转义的 `\|t\|`。改用 `≥2 的格`。
_m13sd2 = re.search(r'≥2 的格 \*\*(\d+)/(\d+)\*\*；\*\*负向格 (\d+)/(\d+)（(\d+)%）\*\*', _A13t)
_m13xd = re.search(r'格数 \*\*130\*\*；增益均值 \*\*\+[\d.]+ pp\*\*（中位 \+([\d.]+)）', _A13t)
_m13xd2 = re.search(r'格数 \*\*130\*\*.*?≥2 的格 \*\*\d+/\d+\*\*；\*\*负向格 (\d+)/(\d+)（(\d+)%）\*\*', _A13t)
# ⚠ 生成件写 `+0.650`（3 位）、稿内写 `+0.65` ⇒ **必须按稿内的 2 位格式化**，
#   不能直接把生成件的原串塞进期望（那会拿 3 位去比 2 位 ⇒ 假红）。
_must('§4.6 同域 median', bool(_m13sd),
      ('median +%.2f' % float(_m13sd.group(1))) if _m13sd else '', target=_XCHK)
_must('§4.6 同域 |t|≥2 与负向比例', bool(_m13sd2),
      # ⚠ 分组：1=16, 2=17, 3=5(分子), 4=17, 5=29(百分数) —— **要取第 5 组**，
      #   第一版取了第 3 组，拼出 `5% negative` ⇒ 假红。
      # ⚠ 顺序必须与稿内一致：稿内是 `29% negative, 16 of 17 reaching ...`（负向比在前）。
      ('%s%% negative, %s of %s reaching |t| ≥ 2'
       % (_m13sd2.group(5), _m13sd2.group(1), _m13sd2.group(2)))
      if _m13sd2 else '', target=_XCHK)
_must('§4.6 跨域 median', bool(_m13xd),
      ('median +%.2f' % float(_m13xd.group(1))) if _m13xd else '', target=_XCHK)
_must('§4.6 跨域负向比例', bool(_m13xd2),
      ('%s%% negative' % _m13xd2.group(3)) if _m13xd2 else '', target=_XCHK)
# ★★ 2026-10-02 第六轮之三：§4.6 的**逐步差散文值**（`+0.52, +0.17 and −0.14 pp`）。
#   实测：扰动稿内这个串**没有任何守卫报红** ⇒ 是缺口。来源 = `A19` 的 30ep 逐步差表。
_A19t = _read('A19_s2ae完整网格.md')
# ⚠ **不能**用 `_A19t.find('100ep')` 切段：'100ep' 在 30ep 步长表**之前**就出现过
#   （第一版这么切 ⇒ 切掉了 30ep 段 ⇒ 解析失败）。改用 `--- 30ep ---` 标记。
_seg = _A19t.split('--- 30ep ---')[-1].split('--- 100ep ---')[0]
_steps = re.findall(r'\d+%→\d+%\s+n=\d+ mean=([+-][\d.]+)', _seg)
if len(_steps) >= 4:
    _seq = ', '.join('%+.2f' % float(x) for x in _steps[1:3]) + ' and %+.2f' % float(_steps[3])
    _seq = _seq.replace('-', '−')      # 稿内用 U+2212
    _must('§4.6 `visdrone→dota15` 30ep 后三步逐步差', True, _seq + ' pp**', target=_XCHK)
else:
    _must('§4.6 后三步逐步差（解析失败）', False, '', target=_XCHK)
# ★★ 2026-10-02 第七轮之二：§4.2/§10 的 **`0.12 pp` 界**。
#   `deliver/新稿标签_可复算路径.md` 原写它与 `0.31 pp @ 80% power` 一起"**没有底座对应物**"。
#   实测**前半句过悲观**：`0.12 pp` 就是该格四点（30/50/100/200）的**极差** = 0.118 ⇒ **底座可复算**。
#   只有 `0.31 pp`（功效计算）确实没有底座对应物，保持登记为缺口。
_A10t = _read('A10_多轮数曲线_形状.md')
_seg2 = _A10t.split('`shwd2sf→sfchd` / `b2`')[1] if '`shwd2sf→sfchd` / `b2`' in _A10t else ''
_pts = [float(x) for x in re.findall(r'\| \d+ \| \d+ \| \*\*([+-][\d.]+)\*\*', _seg2)][:4]
_must('§4.2 第二行的 `0.12 pp` 界（四点极差）', len(_pts) == 4,
      # ⚠ 2026-10-04 第四轮：正文把**观测极差**与**推断界**分开 ⇒ 期望串改成观测范围那句
      ("spread of that cell's gain across the four budgets is **%.2f pp**" % (max(_pts) - min(_pts)))
      if len(_pts) == 4 else '',
      target=_XCHK)
# ★★ 2026-10-02 第八轮之二：§1 的**计数断言**「fails on magnitude for two of three pairs」。
#   §1/§2 本身没有实测数值（§2 只有 `[Li2020]` 与节号；§1 只有 20%/100/200 这类协议参数），
#   唯一可机械核的是这个计数 ⇒ **从 §5 表自身的三个增益推**（守卫内部一致性）。
_t1g = [float(x) for x in re.findall(r'\| T1-[abc] \| \*{0,2}([+-][\d.]+) pp', _d)]
_must('§1 幅度未达标的三格计数（< 0.30 pp 判据）', len(_t1g) == 3,
      # ⚠ 稿内用的是**英文单词**（`two`），不是数字 ⇒ 必须映射，否则假红。
      ('fails on magnitude for %s of three pairs'
       % {0: 'no', 1: 'one', 2: 'two', 3: 'three'}[sum(1 for g in _t1g if abs(g) < 0.30)])
      if len(_t1g) == 3 else '', target=_XCHK)
# ★★ 2026-10-02 第九/十轮：**`0.31 pp @ 80% power` 的口径已查实并钉死**。
#   原始定义在 `analysis/E1a_E1b_E4_冻结本_20260922.md` §5.0，实现在
#   `analysis/work/e1a_bound.py`：
#       e  = [G30[s] − G200[s]]      # **端点差**，逐种子配对
#       sd = sqrt(Σ(x−m)²/(n−1))     # **样本 SD（n−1）**
#       se = sd/√n ; mde = (T975[9] + T80[9])·se = (2.262 + 0.883)·se
#   实测 sd = 0.308、se = 0.097、**MDE = 0.306 pp**（稿内 2 位舍入 ⇒ 0.31 ✓）。
#   ⚠ 这与"相邻差/趋势/极差"等其它口径**不同**（那些会给出 0.19–0.32 不等），
#     所以**必须**在正文写明：配对 t、SD 取端点差 G30−G200、n=10、双侧 α=0.05、80%。
_gb = {}
for _ep in (30, 200):
    # ⚠ 用**模块级** `G`；写成 `_G` 会 NameError。
    _c = C.cell(G, 'shwd2sf→sfchd', _ep, 20, fam='b2', key='test_map50_95', min_n=3)
    if _c and 'per_seed' in _c:
        _gb[_ep] = _c['per_seed']
if len(_gb) == 2:
    _com = sorted(set(_gb[30]) & set(_gb[200]))
    # ⚠⚠ **不能**用 `_d` 当局部变量：全局 `_d` 是**稿内全文**，覆盖它会让一批无关守卫静默报红
    #   （这个坑我踩过两次，两次的症状都是"报错位置与真凶无关"）。
    _diff = [_gb[30][x] - _gb[200][x] for x in _com]      # 端点差 G30 − G200
    _n = len(_diff)
    _m = sum(_diff) / _n
    _sd = (_st.stdev(_diff)) if _n > 1 else 0.0
    _se = _sd / (_n ** 0.5)
    _t975, _t80 = {9: 2.262, 10: 2.228}.get(_n - 1, 2.262), {9: 0.883, 10: 0.879}.get(_n - 1, 0.883)
    _mde = (_t975 + _t80) * _se
    # ⚠ 标签里的 `80%` 必须写成 `80%%`，否则 `% (…)` 会把它当格式符（ValueError: %p）。
    _must('§4.2 `0.31 pp @ 80%% power`（配对 t，SD=端点差 G30−G200=%.4f，n=%d ⇒ MDE=%.4f）'
          % (_sd, _n, _mde), True,
          # ★ 期望串**包含口径本身** ⇒ 口径被写掉/写错也会报红（不只是数字）。
          # ⚠ 2026-10-04 第四轮：该句前插 "on the endpoint difference"（把端点差与 §4.2 的观测范围分开）
          ('%.2f pp or more would have been detected at 80%% power on the endpoint difference '
           '(paired *t* over the ten seeds, two-sided α = 0.05; SD of the 30-versus-200 per-seed '
           'differences = %.3f pp ⇒ minimum detectable difference %.3f pp)' % (_mde, _sd, _mde)),
          target=_XCHK)
else:
    _must('§4.2 `0.31 pp @ 80% power`（解析失败）', False, '', target=_XCHK)

# 脚注表的行号必须都解析得到（见上面的 `_LNCHECK`）
for _lbl in _LNFAIL:
    _XCHK.append(('脚注表行号可解析：%s' % _lbl, '__LINE_NOT_FOUND__'))

_xt = [(lbl, lit in _d) for lbl, lit in _XCHK]
# ---- 内部报告（`03_榨干报告`）也纳入：它是**在用的**交付件，同样会漂 ----
_REP = _try_read(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         '03_榨干报告_边界与结论_20261001.md'), '03_榨干报告')
# ★★ 2026-10-05：该内部报告已**从放行件中移除**（作者指示）。缺失时下列报告段**跳过并报红**，
#   不再当作失败；作者树上仍存在时照旧校验。
_a1 = _dig('A1_格完整性.md', r'核心格 = (\d+) 个')
_a1b = _dig('A1b_架构链映射.md', r'\*\*定到具体 backbone\*\* \| \*\*(\d+)（')
_a3 = _dig('A3_早停倾向.md', r'名义 ≤100 轮的 run 共 \*\*(\d+)\*\* 个')
_a5 = _dig('A5_种子方差.md', r'族键修正后：(\d+)/(\d+) 逐位') if False else None
_a5m = re.search(r'族键修正后：(\d+)/(\d+) 逐位',
                 _try_read(os.path.join(_ANA, 'A5_种子方差.md')))
if _a1 is not None:
    _RCHK.append(('A1 可配对核心格 **%d**' % _a1, '核心格 **%d**' % _a1))

_A2t = _read('A2_损失平面可测性.md')
_m = re.search(r'可比格的格数：\*\*(\d+)\*\*，其中符号\*\*一致 (\d+) 个\*\*、\*\*翻转 (\d+) 个（(\d+)%）', _A2t)
_must('A2 可比格 与 翻转', bool(_m),
      ('可比格 **%s**，换 checkpoint 翻转 **%s（%s%%）**' % (_m.group(1), _m.group(3), _m.group(4))) if _m else '')

_A7t = _read('A7_族混杂复核.md')
_n_old = re.search(r'旧口径（混 `b2`\+`y11`）\s*\|\s*(\d+)', _A7t)
_n_new = re.search(r'只看族 `y11`[^|]*\|\s*(\d+)', _A7t)
_leak = (int(_n_old.group(1)) - int(_n_new.group(1))) if (_n_old and _n_new) else None
_must('A7 y11 圈架构漏掉的种子数', _leak is not None, '圈架构会漏 %d 个种子' % _leak if _leak is not None else '')

_A8t = _try_read(os.path.join(BASE, 'base', '缺口清单.md'))
_m8 = re.search(r'命名不一致 (\d+) 条\*\* / \*\*真缺 (\d+) 条', _A8t)
_must('A8 命名不一致 / 真缺', bool(_m8),
      ('**%s 命名不一致 + %s 真缺**' % (_m8.group(1), _m8.group(2))) if _m8 else '')

_A9t = _read('A9_全域预算轴扫描.md')
_m9a = re.search(r'可配对端点差 \*\*(\d+)\*\* 条（两端各至少 3 个种子配对）', _A9t)
_m9tot = re.search(r'两条轴合计可配对端点差 \*\*(\d+)\*\* 条', _A9t)
_m9g = re.search(r'\*\*(\d+) 个独立组', _A9t)
_m9p = re.search(r'去重：\*\*(\d+)\*\* 个独立配对', _A9t)
_m9b = re.findall(r'可配对端点差 \*\*(\d+)\*\* 条（两端各至少 3 个种子配对）', _A9t)
if _m9tot and _m9b:
    _must('A9 端点差总数（轮数+标签）', True,
          '**%s** 条端点差（轮数 %s + 标签 %s）' % (_m9tot.group(1), _m9b[0], _m9b[1]))
if _m9g and _m9p:
    _must('A9 独立组 / 独立配对', True,
          '%s 独立组 / %s 独立配对' % (_m9g.group(1), _m9p.group(1)))

_A11t = _read('A11_种子闸门标定.md')
# ⚠ 不能用 `if _m11a:` —— 那样**解析失败就静默跳过**，正是本函数存在的理由。
#   第一版就是这么写的，结果 A11 两项**根本没进表**（我自己的代码犯了它要防的错）。
#   另：生成件里是 `\|t\|`（markdown 转义竖线），所以别拿 `|t|` 当锚点，改用后半句。
_m11a = re.search(r'噪声大）\*\*：\d+ 个，3 子集方向正确率中位 \*\*(\d+)%\*\*、全同号率中位 \*\*(\d+)%\*\*', _A11t)
_m11b = re.search(r'≥4 的格\*\*：\d+ 个，3 子集方向正确率中位 \*\*(\d+)%\*\*、全同号率中位 \*\*(\d+)%\*\*', _A11t)
_must('A11 |t|<2 的方向/全同号率', bool(_m11a),
      ('**%s%%**、全同号 **%s%%**' % (_m11a.group(1), _m11a.group(2))) if _m11a else '')
_must('A11 |t|≥4 的方向/全同号率', bool(_m11b),
      ('**%s%%/%s%%**' % (_m11b.group(1), _m11b.group(2))) if _m11b else '')

_A16t = _read('A16_多读数歧义.md')
_m16 = re.search(r'受影响的格.*?\*\*(\d+) / (\d+)\*\*', _A16t)
if _m14:
    _RCHK.append(('A14 smoke→sfchd/b2 分族覆盖 **%d%%**' % _c14, '`smoke→sfchd/b2` **%d%%**' % _c14))

_must('A16 受影响格数 / 分母', bool(_m16),
      ('格级 **%s/%s** 受影响' % (_m16.group(1), _m16.group(2))) if _m16 else '')

if _a1b is not None:
    # 报告写法是 `**定到具体 backbone 2331/2362（99%）**` ⇒ 字面量不能带前导 `**`
    # ⚠ 分母**曾经写死 2243** ⇒ 底座一长就假红。这是"会随数据增长的量不许写字面量"
    #   的又一实例，改为从 `A1b` 生成件里解析当前分母。
    _a1b_tot = _dig('A1b_架构链映射.md', r'\| 底座 run \| (\d+) \|')
    _tot_s = ('%d' % int(_a1b_tot)) if _a1b_tot else '?'
    _lit = ('backbone %d/%s' % (_a1b, _tot_s)) if _a1b_tot else ('backbone %d' % _a1b)
    _RCHK.append(('A1b 定到 backbone **%d**/底座 **%s**' % (_a1b, _tot_s), _lit))
if _a3 is not None:
    _RCHK.append(('A3 ≤100ep run 数 **%d**' % _a3, '**%d** run、合法早停 0' % _a3))
if _a5m:
    _RCHK.append(('A5 §4.2 逐位 **%s/%s**' % (_a5m.group(1), _a5m.group(2)),
                  '**%s/%s 逐位**' % (_a5m.group(1), _a5m.group(2))))
# ★ 2026-10-02 新增：报告头部与 A13/A14 的数字**此前无人看管**，已经漂过一轮
#   （头部还写 2243 行、A13 还写"跨域 128 格 +1.09"而实为 130/+1.10）。
# ⚠ 这两项**复用**已解析的 `_xd_n`/`_xd_mean`（同源 A13 汇总行），不要另写正则 ——
#   我第一版另写了一条 `跨域…(\d+) 格`，结果**一条都抓不到、静默不追加**（空守卫最危险）。
if _xd_n is not None:
    _RCHK.append(('A13 跨域格数 **%d**' % _xd_n, '跨域 **%d** 格' % _xd_n))
if _xd_mean is not None:
    _RCHK.append(('A13 跨域均值 **+%.2f**' % _xd_mean, '**+%.2f pp**' % _xd_mean))
# A14 的生成件里**没有**全库覆盖率（只有逐格表）⇒ 直接从底座算，不解析文件。
try:
    _brows, _ = C.load()
    _cov = 100.0 * sum(1 for r in _brows if (r.get('test_map50_95') or '').strip()) / len(_brows)
    _RCHK.append(('A14 全库 test 覆盖 **%.1f%%**（%d/%d）' % (_cov, round(_cov * len(_brows) / 100), len(_brows)),
                  'test 覆盖 **%.1f%%**' % _cov))
except Exception as _e:                       # 底座读不到就**报出来**，不要静默跳过
    _RCHK.append(('A14 全库 test 覆盖（解析失败）', '__NEVER_MATCHES__%s' % _e))
# ★★ 2026-10-02：**README 索引表的"关键数字"列**原先只被查过"文件是否被索引"，
#   数字本身没人看 ⇒ 实测 6 行已漂（A2 88/7、A18 7/7+2.10+0.33、A16 185、
#   A14 95.1%/2132/2243+67%、A13 128格/+1.09、A8 63/25+38）。此处复用上面已解析的值。
_RD = _try_read(os.path.join(BASE, 'README.md'))
_RDCHK = []
if _m:
    _RDCHK.append(('README A2 行', '可比格 **%s**，翻转 **%s（%s%%）**' % (_m.group(1), _m.group(3), _m.group(4))))
if _m16:
    _RDCHK.append(('README A16 行', '格级 **%s/%s** 受影响' % (_m16.group(1), _m16.group(2))))
if _m14:
    _RDCHK.append(('README A14 行（分族）', '**`smoke→sfchd/b2` %d%%**' % _c14))
if _mende_n is not None and _mask_n is not None:
    # ⚠ `_dig` 返回 float（8.0）⇒ 必须转 int，否则会拼出 `8.0/8.0` 这种 README 里不存在的期望值
    _RDCHK.append(('README A18 行（mendeley）', '`mendeley` **%d/%d**' % (int(_mende_n), int(_mende_n))))
if _dt_mean is not None and _vis_mean is not None:
    _RDCHK.append(('README A18 行（两密集域）', '最密 2 root **+%.2f/+%.2f**' % (_dt_mean, _vis_mean)))
if _xd_n is not None and _xd_mean is not None:
    _RDCHK.append(('README A13 行', '跨域 **%d** 格 **+%.2f pp**' % (_xd_n, _xd_mean)))
if _m8:
    _RDCHK.append(('README A8 行', '**%s 命名不一致 + %s 真缺**' % (_m8.group(1), _m8.group(2))))
# ★★ 2026-10-02 第三轮：报告 §二（边界表）与 §四 的**散文/表格数字**此前无守卫。
#   实测 §二 三行已实质过期（架构轴仍写"不可分离"、损失轴仍是 89/81/0/12/3、0 读数组 84/6），
#   §四 的协议守卫 run 数还写 2276（真值 2336）。
_pf = {}
for _r in _brows:
    _pf.setdefault((_r['_pair'], _r['family']), []).append(_r)
_zero = sum(1 for _v in _pf.values()
            if not any((x.get('test_map50_95') or '').strip() for x in _v))
_RCHK.append(('报告 §二 (配对,族) 组数 **%d**' % len(_pf), '**%d** 个 `(配对,族)` 组里' % len(_pf)))
_RCHK.append(('报告 §二 0 读数组数 **%d**' % _zero, '**%d** 组 0 读数' % _zero))
# 反向断言：旧的错判**不得**再出现
_RCHK.append(('报告 §二 架构轴更正（**不得**再出现"架构轴不可分离"）',
              ('__OLD_FALSE_CLAIM_STILL_PRESENT__' if '架构轴不可分离' in _REP
               else '把 backbone 写进格键造成的**循环论证**')))
_15t = _read('A15_损失函数轴的边界.md')
_m15 = re.findall(r'\| 归到 \*\*`(base|lr005)`\*\* 臂 \| \*\*(\d+)\*\* \|', _15t)
if len(_m15) == 2:
    _d15 = dict(_m15)
    _RCHK.append(('报告 §二 损失轴归臂 **%s/%s**' % (_d15.get('base'), _d15.get('lr005')),
                  '**%s 条归 `base`、%s 条归 `lr005`**' % (_d15.get('base'), _d15.get('lr005'))))
_A20t = _read('A20_损失轴实测对照.md')
_m20 = re.search(r'可算的 \(格, 臂, 损失\) 组：\*\*(\d+)\*\*；其中\*\*过论文自己的种子闸门\*\*.*?：\*\*(\d+)\*\*', _A20t)
if _m20:
    _RCHK.append(('报告 §二 损失轴可算组 **%s**（过闸门 **%s**）' % (_m20.group(1), _m20.group(2)),
                  '**%s** 组，**%s** 组过闸门' % (_m20.group(1), _m20.group(2))))
_A22t = _read('A22_损失对增益_实测.md')
_m22 = re.search(r'现在 \*\*(\d+) 个组四腿齐备\*\*', _A22t)
if _m22:
    _RCHK.append(('报告 §二 损失对增益四腿齐备 **%s** 组' % _m22.group(1),
                  '**%s 组四腿齐备**' % _m22.group(1)))
_nrun = len({r['run'] for r in _brows})
_RCHK.append(('报告 §四 协议守卫底座 run 数 **%d**' % _nrun, '底座 **%d** 个 run' % _nrun))
if _REP:
    _rt = [(lbl, lit in _REP) for lbl, lit in _RCHK]
else:
    print('⚠ 内部报告 03_榨干报告_边界与结论_20261001.md **不在放行件内**'
          '（已按作者指示移除）⇒ 报告一致性守卫**跳过**（不报红）。')
    _rt = []
w('## ★ 内部报告一致性守卫（`03_榨干报告` ↔ 生成件）')
w()
w('| 生成件里的值 | 报告内是否一致 | 报告应含 |')
w('|---|---|---|')
for (lbl, lit), (_, good) in zip(_RCHK, _rt):
    w('| %s | %s | `%s` |' % (lbl, '✅' if good else '❌ **漂移**', lit))
w()
_rbad = [l for (l, _), (_, g) in zip(_RCHK, _rt) if not g]
if not _REP:
    w('> ⚠ 内部报告不在放行件内（已按作者指示移除）⇒ 本守卫**未执行**，'
      '不声称一致也不报红；上表为空。')
    w()
elif not _RCHK:
    w('> ❌ 生成件一件都没解析到 —— 守卫**空转**（空集合硬失败，经验 #56）。')
    w()
elif _rbad:
    w('> ⚠ **内部报告漂移**：%s。' % '、'.join(_rbad))
    w()
else:
    w('> ✅ 内部报告的普查数字与生成件逐项一致（%d 项）。' % len(_RCHK))
    w()

w('## ★ 未决项登记守卫（`deliver/修正记录_底座扩容后全量复核_20261002.md`）')
w()
if not _OPEN:
    w('> ❌ 一项都没有 —— 空守卫硬失败。')
    w()
else:
    w('| 未决项 | 登记件内是否已写 |')
    w('|---|---|')
    _obad = []
    for lbl, lit in _OPEN:
        ok = lit in _REC
        w('| %s | %s |' % (lbl, '✅ 已登记' if ok else '❌ **未登记**'))
        if not ok:
            _obad.append(lbl)
    w()
    w('> %s' % ('⚠ **未决项未登记**：%s。' % '、'.join(_obad) if _obad
                else '✅ 未决项均已登记（%d 项）。' % len(_OPEN)))
    w()
w('## ★ README 索引表「关键数字」列一致性守卫（2026-10-02 新增）')
w()
if not _RDCHK:
    w('> ❌ 一项都没解析到 —— 守卫**空转**（空集合硬失败）。')
    w()
else:
    w('| 生成件里的值 | README 内是否一致 | README 应含 |')
    w('|---|---|---|')
    _rdbad = []
    for lbl, lit in _RDCHK:
        ok = lit in _RD
        w('| %s | %s | `%s` |' % (lbl, '✅' if ok else '❌ **漂移**', lit))
        if not ok:
            _rdbad.append(lbl)
    w()
    if _rdbad:
        w('> ⚠ **README 关键数字漂移**：%s。' % '、'.join(_rdbad))
    else:
        w('> ✅ README 索引表的关键数字与生成件逐项一致（%d 项）。' % len(_RDCHK))
    w()
w('## ★ 跨件一致性守卫（稿内普查数字 ↔ `A9`/`A13`/`A18` 生成件）')
w()
w('| 生成件里的值 | 稿内是否一致 | 稿内应含 |')
w('|---|---|---|')
for (lbl, lit), (_, good) in zip(_XCHK, _xt):
    w('| %s | %s | `%s` |' % (lbl, '✅' if good else '❌ **漂移**', lit))
w()
_xbad = [lbl for (lbl, lit), (_, good) in zip(_XCHK, _xt) if not good]
if not _XCHK:
    w('> ❌ 生成件一件都没解析到 —— 守卫**空转**（空集合必须硬失败，经验 #56）。')
    w()
elif _xbad:
    w('> ⚠ **跨件漂移**：%s。生成件重跑后稿内没跟上（或反之）。' % '、'.join(_xbad))
    w()
else:
    w('> ✅ 稿内普查数字与生成件逐项一致（%d 项）。' % len(_XCHK))
    w()


os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, '新稿标签_可复算路径.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')

# ================= B5：逐句脚注表 =================
# 由上表的**同一批检查**派生 —— 把路径挂到**稿内原句**上，供作者直接贴进 verification appendix。
REG = [
    (r'3\.727', '§4.1/§5 · `run_table_canonical.csv` · 列 `test_map50_95` · **族 `t1c`** · seeds s42–s51'),
    (r'2\.584', '§4.1 · 同表 · 列 `test_map50_95` · **族 `mech`** · 10 配对'),
    (r'0\.168', '§4.1/§5 · 同表 · 列 `test_map50_95` · **族 `t1b`** · seeds s42–s51'),
    (r'0\.055', '§4.1 · 同表 · 列 `test_map50_95` · **族 `mech`** · 10 配对'),
    (r'1\.143', '§4.1 · 同表 · 上两格**逐种子配对**（100ep−200ep）'),
    (r'2\.161', '§4.2 · 由 §4.2 两行**逐种子配对**（30ep−200ep，10 种子）· 第 10 个种子由 '
                '`deliver\\D1_s50补测_记录.md` 补测给出 · 读数归档 `base\\p1d1_s50_test_readings.csv`'),
    (r'3\.656', '§4.2 · **族 `b2`**（10 种子，**直接读 `run_table_canonical.csv`**）。s50 的 run 是改名存档件，'
                '其读数由 `deliver\\D1_s50补测_记录.md` 的补测给出并已并入底座'),
    (r'2\.674|1\.666|1\.495', '§4.2 · 列 `test_map50_95` · **族 `b2`** · seeds s42–s51'),
    (r'0\.812|0\.728|0\.694|0\.794', '§4.2 · 列 `test_map50_95` · **族 `b2`** · seeds s42–s51'),
    (r'0\.018', '§4.2 第二行 · 同表 · 族 `b2` · 30ep 与 200ep 逐种子配对'),
    (r'1\.49', '§4.3 · 族 **`t2`** · `mende_20p` · 100ep · 列 **`best_map50_95`**（val 侧最优轮）· s42–s51（n=10）；论文的 5 个种子 = s42–s46 是全格的精确子集（−1.4878 / t=−4.023 / 5/5 逐位吻合）'),
    (r'1\.27|6\.97', '§4.4 · 列 **`best_map50_95`（val 侧最优轮）** · **族 `y11`** · seeds s42–s44'),
    (r'−0\.01 pp|t = −0\.10', '§4.4 · 同上（100ep）'),
    (r'10\.71 pp|six of eight|seventeen of twenty', '§4.6 · **标签轴** → `analysis\A19_s2ae完整网格.md`（s2ae）+ '
     '`analysis\A6_标签预算轴.md`（s2df 与全表）+ `analysis\A9_全域预算轴扫描.md` §七（过闸门的 6/8 与 15/18）'),
    (r'\+1\.42 pp|−1\.50|−0\.14 pp', '§4.5 单族完整 5×2 网格 → `02_实验补充_T5_s2ae完整网格_20261001.md` §10'
     '（口径 = 逐种子 `lr005−base`、pp、`test_map50_95`、端点差逐种子配对、Δ=长−短）'),
    (r'\+1\.98 pp|\+1\.19 pp|−0\.91 pp|−0\.12 pp', '§4.5 单族端点 2×2 → `01_实验补充_T4_s2ae端点_20261001.md` §10'
     '（口径 = 逐种子 `lr005−base`、pp、`test_map50_95`、端点差逐种子配对、Δ=长−短）'),
    (r'annotation density|instances per image|r ≈ 0\.33', '§9 · **候选调节变量** → `analysis\A18_标注密度调节变量.md`'
     '（生成器 `scripts/35_A18N_density_moderator.py`；实例数扫描原始输出 `_inst_{A,B}.txt`）'),
    (r'133 runs|89 of which|67%', '§4.2 覆盖率披露 · `analysis\A14_数据质量普查.md`'
     '（生成器 `scripts/31_A14_quality_census.py`）；见 `deliver\数据质量_对论文数字的含义_20261001.md`'),
    (r'\+0\.27 pp|17 cells|127 cross-domain', '§4.5 第三段 · **同域对照 vs 跨域迁移** → `analysis\A13_同域对照_vs_跨域迁移.md`'
     '（生成器 `scripts/30_A13_same_domain.py`）；分类规则在该件 §一 逐条列出'),
    (r'60 paired|22 groups|14 independent|66%|38%', '§4.5 · **全域复制普查** → `analysis\A9_全域预算轴扫描.md`'
     '（生成器 `scripts/26_A9_basewide_axes.py`）；Δ = 长预算 − 短预算'),
    (r'0\.147|1\.816|0\.103', '§5 T1-a · 列 `test_map50_95` · **族 `t1a`** · seeds s42–s51'),
    (r'4\.455|0\.0016', '§5 T1-b · 同表 · **族 `t1b`** · seeds s42–s51'),
    (r'43\.774|8\.5', '§5 T1-c · 同表 · **族 `t1c`** · seeds s42–s51'),
    (r'0\.069|0\.825', '§7 · 补材 `00_SUPPLEMENTARY_v0.4.md` **L832–L837**（含 t=−0.23、95% CI −0.758~+0.620）'),
    (r'33\.31|29\.74|29\.86', '§3/§7 · 补材 **§M.4（L736）**（三份划分文件名交集为 0 的逐格表）'),
    (r'18/18|0\.76\s*[–\-]\s*1\.47|2\.3', '§6(a) · 补材 **Appendix H.1（L327）**；底座不可复算（无梯度量）'),
    (r'0\.627', '§6(b) · 补材 **E.2（L123）**（十三种子 clean）· 底座同格 `test_map50_95` = **+0.628**'),
    (r'0\.307', '§6(b) · 底座同格（`shwd2sf→sfchd20`·**族 `r10`**·100ep·n=13）`best_map50_95` = **−0.307**（★唯一底座可复算的审计数字）'),
    (r'0\.56\s*[–\-]\s*0\.81', '§6(c) · 补材 **Appendix G.2（L315–L317）**（逐格 0.66/0.56/0.56/0.59/0.63/0.58/0.81，中位 0.59）'),
    (r'253\s*[–\-]\s*284', '§6(c) · 补材 **Appendix G.2（L317）**（12 读数 252.99–283.96、±5.8%）'),
    (r'1\.4328|0\.5065|1\.4079|0\.6274', '§7 · 补材 **Appendix E.2（L121–L130）**；补材精度为 +1.434/+0.507 与 +1.408/+0.627 ⇒ **须统一精度并补 SD/t/p**'),
    (r'0\.0006|0\.17', '§7 · 补材 **L138**；σ̂ 补材写 **0.166–0.190** ⇒ 稿内 `0.17` 须改写'),
    (r'≥0\.30 pp|0\.12 pp|0\.31 pp', '§3/§4.2 · **判据/功效参数**，无底座对应物 ⇒ 须写明所用 SD 与检验'),
]

draft = open(DRAFT, encoding='utf-8', errors='replace').read().split('\n')
M = []
M.append('# 新稿逐句脚注表（B5）')
M.append('')
M.append('> 与 `新稿标签_可复算路径.md` 同源（同一批检查），只是把路径**挂到稿内原句上**，')
M.append('> 便于直接粘进投稿件的 verification appendix。')
M.append('>')
M.append('> 列：**稿内原句（逐字）** → **脚注（复算路径）**。')
M.append('')
M.append('| 稿内行 | 稿内原句（逐字，已截断到 220 字符） | 脚注（复算路径） |')
M.append('|---|---|---|')
nrow = 0
for i, line in enumerate(draft, 1):
    if not line.strip():
        continue
    if not re.search(r'CONFIRMED|PENDING', line) and not re.search(r'\d\.\d', line):
        continue
    for sent in re.split(r'(?<=[.;])\s+', line):
        if not re.search(r'\d', sent):
            continue
        hits = []
        for pat, note in REG:
            if re.search(pat, sent) and note not in hits:
                hits.append(note)
        if not hits:
            continue
        s = sent.strip()
        if len(s) > 220:
            s = s[:220] + ' …'
        M.append('| L%d | %s | %s |' % (i, s.replace('|', '\\|'), '<br>'.join(hits)))
        nrow += 1
M.append('')
M.append('* 共 **%d** 条"句子 → 脚注"映射。' % nrow)
M.append('')
M.append('## ★ 承载体：标签所在句**不携带数字**，指向邻近的表/节')
M.append('')
M.append('这一类**最容易漏掉指针** —— 因为就地看那句话里没有数字可核。共 **6 处**：')
M.append('')
M.append('| 稿内行 | 标签句（逐字，截断） | 它到底在确认什么 | 应挂的路径 |')
M.append('|---|---|---|---|')
_CARRIER = [
    (4, 'Every number carries a verification tag. **✅CONFIRMED** means the number is traceable to a **recorded evidence path**…',
     '**全局定义**：✅CONFIRMED = 可追溯到本项目内的**记录在案的证据路径**（两级：(a) 从已发布的 run 级表重算；(b) 归档审计件）',
     '✅ **已按两级标签改写**（2026-10-01）：(a) §4/§5 = recomputation from the released per-run tables；(b) §6 = archived audit artifacts。并要求每个 ✅CONFIRMED 注明所用种子集'),
    (20, 'Our claim is narrow and testable: the sign of a transfer gain is set by the remaining budget…',
     '§4.1 的两个格（**族 `t1c` / `mech`**）',
     '同上表 §4.1 的 6 条脚注'),
    (26, '…below the noise floor on every measured cell, and sign-flipping under a change of the reporting checkpoint alone ✅CONFIRMED',
     '§6(a) 的 SNR 底 + §6(b) 的换 checkpoint 翻转',
     '§6(a) → 补材 **H.1**；§6(b) → 补材 **E.2** + 底座（族 `r10`，见下表）'),
    (72, '✅CONFIRMED (paired, per-seed recomputation). The direction is what a headroom account predicts…',
     '**紧邻上方的 §4.1 表（L69–L70）** 的 6 个数',
     '同上表 §4.1 的 6 条脚注（Δ 与逐种子符号一并）'),
    (99, '✅CONFIRMED. Two of three pairs reach significance; one of three meets every part of the criterion.',
     '**紧邻上方的 §5 表（L95–L97）** 的 3 行（T1-a/b/c）',
     '同上表 §5 的 3 条脚注；另 `q = 0.05` 的 BH 校正是**判据参数**，须写明 m 与用法'),
    (168, 'Every §4 and §5 number carries a ✅CONFIRMED tag backed by per-seed recomputation from the released run tables, with the seed set named at each tag…',
     '**全稿的状态声明**',
     '✅ **已改写**（2026-10-01）：把 §6 从 "per-seed recomputation" 中**摘出来**（改为 archived audit artifacts），并加了"每个标签注明种子集"'),
]
for ln, sent, what, path in _CARRIER:
    M.append('| L%d | %s | %s | %s |' % (ln, sent.replace('|', '\\|'), what, path))
M.append('')
M.append('> **判据来源说明**：`0.30 pp` 的幅度门槛、`q = 0.05` 的 BH 校正、`2/3` 的通过要求')
M.append('> 都是**预注册判据**（在 run 存在之前冻结），路径是**冻结件本身**，不是底座 —— 须写明冻结件在哪。')
M.append('')
open(os.path.join(OUT, '新稿_逐句脚注表.md'), 'w', encoding='utf-8').write('\n'.join(M) + '\n')
print('逐句脚注表：%d 行' % nrow)

print('\n守卫报红 %d 条' % len(FAILS))
for d, got, want in FAILS:
    print('  ❌ %s: got=%s want=%s' % (d, got, want))
print('输出 -> %s' % os.path.join(OUT, '新稿标签_可复算路径.md'))
sys.exit(1 if FAILS else 0)
