# -*- coding: utf-8 -*-
"""39_verify_protocol_fingerprint.py —— **训练协议指纹守卫**（只读；不写任何文件）。

用法：
    python scripts/39_verify_protocol_fingerprint.py              # 跑全部断言，失败即非零退出
    python scripts/39_verify_protocol_fingerprint.py --self-test  # ★ 阴性对照：故意改坏，守卫**必须**报红

为什么有这一件
--------------
用户 2026-10-02 的口径纠正：
    「固定 workers=16，batch_size=32。我没有记错的话。**有一些特别早期的不是这样的。其他应该都是。**」
这句话把一个**从未被守卫过**的协议前提摆上台面：论文里所有跨臂比较，
默认两支是**同一训练协议**。若某一臂实际是 batch=4 或 workers=8，
那不是"噪声"而是**协议不一致**，会污染格内配对。
在此之前底座里**根本没有 batch/workers 这两列** —— 也就是说这个前提
一直只是"记忆"，不是"证据"。本件把它变成证据。

证据来源（不可再生）
--------------------
`base/args_protocol_snapshot.csv` 是 2026-10-02 从 **A 机 + B 机活体 `find /workspace`**
以及 **`raw/` 归档**抓下的全量 `args.yaml` 快照（含**字节数**）。
pod 是租用的，机器一关这份现场就没了 —— 所以快照本身就是交付物。

口径（写死在代码里，便于复算）
------------------------------
· 标准协议 = `batch=32` 且 `workers=16` 且 `imgsz=640`。
· **`args.yaml` 字节数 = 0 的目录不算证据**：A 机上存在
  `/workspace/runs/<name>/{args.yaml,results.csv}` **双双 0 字节**的占位目录，
  同一 run 的实体在 `/workspace/p4_base_weights/<name>/` 或 `/workspace/b_archive/runs/<name>/`。
  0 字节文件会让 `os.path.exists()` 返回真 —— 本件因此**按字节数判实体**，
  而不是按"文件存在"（这正是上一步误判 `has_res=1` 的原因）。
· 例外类是**排除项**，判据是"**底座里的 run 不得落入任何例外类**"，
  而不是"例外类条数等于某个常数" —— 后者会随补实验增长而假红。

设计依据（`E:\\workplace\\通用经验与教训`）：
  · **#56**：**空集合必须硬失败** —— 底座 run 集或快照为空都是 FAIL，不是 PASS。
  · **#75**：新写的检查必须现场做一次**阴性对照** —— 内置 `--self-test`。
  · **#23**：核对用**只读**脚本断言目标状态；本件**不写任何文件**。
  · **#6 / #20**：只盯总数不够，必须**逐条**盯 —— 本件逐 run 断言，不只看汇总。
  · **#42**：凡是记录里的"已完成 X"，X 必须有一个**可执行**的检查 —— 本件就是那个检查。
"""
import os
import re
import csv
import sys
import argparse
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # analysis_M3/
BASE = os.path.join(ROOT, 'base', 'run_table_canonical.csv')
SNAP = os.path.join(ROOT, 'base', 'args_protocol_snapshot.csv')

STD = ('32', '16', '640')                          # batch / workers / imgsz

# 默认名产物：Ultralytics 未指定 name 时自增的 runs/detect/train, train-2, ...
DEFAULTNAME = re.compile(r'^train(-\d+)?$')

# 外来项目（B 机上另一个课题：Sparse-YOLO，project=/workspace/runs_aitod）
FOREIGN_PROJECT = '/workspace/runs_aitod'
FOREIGN_DATA = 'AI-TOD.yaml'
FOREIGN_MODEL = 'sparse_yolo'

# 早期 workers=8 基线（**已确认全部在底座之外**，见 deliver/协议指纹_核验_20261002.md）
EARLY_W8 = {'base_coco100', 'base_20p_100', 'base_30p_100', 'base_fusion_100', 'v_base'}


def _load_base_rows():
    with open(BASE, encoding='utf-8') as f:
        return list(csv.DictReader(f))


def _load_base():
    if not os.path.exists(BASE):
        raise SystemExit('缺少底座：%s' % BASE)
    return sorted({r['run'] for r in _load_base_rows() if r.get('run')})


def _load_snap():
    if not os.path.exists(SNAP):
        raise SystemExit('缺少快照：%s（本件依赖抓取当时的 args.yaml 全量快照）' % SNAP)
    with open(SNAP, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    G = collections.defaultdict(list)
    for r in rows:
        G[r['name']].append(r)
    return rows, G


def _is_foreign(r):
    return (r['project'].startswith(FOREIGN_PROJECT)
            or FOREIGN_MODEL in r['model']
            or r['data'] == FOREIGN_DATA)


def _classify(r):
    """返回记录类别（用于报告；不是判据本身）。"""
    if _is_foreign(r):
        return '外来项目(Sparse/runs_aitod)'
    if DEFAULTNAME.match(r['name']):
        return '默认名产物(train-N)'
    if int(r['args_bytes']) == 0:
        return '本人实验_0字节占位'
    return '本人实验_实体'


def run_checks(base, snap_rows, G, verbose=True, base_rows=None):
    """返回 (failures, stats)。failures 为空即通过。

    base_rows 仅在第二遍做"底座自带 batch/imgsz 列"的交叉核对（E9/E10）时传入。
    """
    F = []
    st = collections.OrderedDict()

    # ---- E1 空集合硬失败 -------------------------------------------------
    if not base:
        F.append('E1 底座 run 集为空 —— 空集合必须硬失败（#56）')
    if not snap_rows:
        F.append('E1 快照为空 —— 空集合必须硬失败（#56）')
    st['底座 distinct run'] = len(base)
    st['快照记录数'] = len(snap_rows)
    st['快照 distinct name'] = len(G)
    if F:
        return F, st

    # ---- E2 每个底座 run 都要有档案 -------------------------------------
    missing = [r for r in base if r not in G]
    st['底座 run 在快照中缺档'] = len(missing)
    if missing:
        F.append('E2 底座有 %d 个 run 在快照里完全找不到 args 档案，样例=%s'
                 % (len(missing), missing[:5]))

    # ---- E3 每个底座 run 至少有一条**非 0 字节**的 args 记录 -------------
    no_real = [r for r in base if r in G and not any(int(x['args_bytes']) > 0 for x in G[r])]
    st['底座 run 只有 0 字节占位'] = len(no_real)
    if no_real:
        F.append('E3 底座有 %d 个 run 只有 0 字节 args.yaml 占位、无实体档案，样例=%s'
                 % (len(no_real), no_real[:5]))

    # ---- E4 逐 run：所有**实体**记录都必须等于标准协议 ------------------
    bad = []
    for r in base:
        for x in G.get(r, []):
            if int(x['args_bytes']) <= 0:
                continue                            # 占位不算证据
            if (x['batch'], x['workers'], x['imgsz']) != STD:
                bad.append((r, x['source'], x['batch'], x['workers'], x['imgsz']))
    st['底座 run 的实体 args 记录数'] = sum(
        1 for r in base for x in G.get(r, []) if int(x['args_bytes']) > 0)
    st['其中偏离标准协议'] = len(bad)
    if bad:
        for r, s, b, w, i in bad[:10]:
            F.append('E4 底座 run %s（%s）协议偏离：batch=%s workers=%s imgsz=%s（应 32/16/640）'
                     % (r, s, b, w, i))
        if len(bad) > 10:
            F.append('E4 ...另有 %d 条同类偏离' % (len(bad) - 10))

    # ---- E5 底座不得含默认名产物 ----------------------------------------
    dn = [r for r in base if DEFAULTNAME.match(r)]
    st['底座含默认名(train-N)'] = len(dn)
    if dn:
        F.append('E5 底座含 %d 个 Ultralytics 默认名产物，样例=%s' % (len(dn), dn[:5]))

    # ---- E6 底座不得含外来项目 ------------------------------------------
    fo = [r for r in base if any(_is_foreign(x) for x in G.get(r, []))]
    st['底座含外来项目 run'] = len(fo)
    if fo:
        F.append('E6 底座含 %d 个外来项目（Sparse/runs_aitod）run，样例=%s' % (len(fo), fo[:5]))

    # ---- E7 早期 workers=8 基线必须全部在底座之外 ------------------------
    leaked = sorted(EARLY_W8 & set(base))
    st['早期 workers=8 基线泄漏进底座'] = len(leaked)
    if leaked:
        F.append('E7 早期 workers=8 基线混入底座：%s' % leaked)
    st['早期 workers=8 基线条数(快照内)'] = len(EARLY_W8 & set(G))

    # ---- E8 0 字节占位现象必须被记录到（否则 E3/E4 的口径失去依据）------
    nzero = sum(1 for x in snap_rows if int(x['args_bytes']) == 0)
    st['全快照 0 字节 args.yaml 条数'] = nzero
    if nzero == 0:
        F.append('E8 快照里没有 0 字节占位 —— 与 A 机现场不符，口径（按字节数判实体）失去依据，需重查')

    # ---- E9/E10 ★ 第二条**独立**证据路径：底座自带的 `batch` / `imgsz` 列 ---
    #   底座并非没有协议信息：`ARGS_KEYS` 里就有 `batch` 与 `imgsz`
    #   （**只有 `workers` 不在底座里**——这正是快照不可替代的原因）。
    #   所以同一命题可以**不依赖快照**再核一遍；两条路径互相印证才有分量。
    if base_rows is not None:
        have = [r for r in base_rows if r.get('batch', '').strip() not in ('', '?')]
        badb = [(r['run'], r['batch']) for r in have if r['batch'].strip() != STD[0]]
        bado = [(r['run'], r['imgsz']) for r in have
                if r.get('imgsz', '').strip() not in ('', '?') and r['imgsz'].strip() != STD[2]]
        st['底座 §batch 列有值行数'] = len(have)
        st['底座 §batch 列 != 32'] = len(badb)
        st['底座 §imgsz 列 != 640'] = len(bado)
        if badb:
            F.append('E9 底座自带 batch 列有 %d 行 != 32，样例=%s' % (len(badb), badb[:5]))
        if bado:
            F.append('E9 底座自带 imgsz 列有 %d 行 != 640，样例=%s' % (len(bado), bado[:5]))
        # E10：底座 batch 列与快照实体记录**不得互相矛盾**（两条路径对撞）
        mism, noent = [], []
        for r in have:
            s = {x['batch'] for x in G.get(r['run'], []) if int(x['args_bytes']) > 0}
            if not s:
                noent.append(r['run'])
            elif r['batch'].strip() not in s:
                mism.append((r['run'], r['batch'].strip(), sorted(s)))
        st['底座 batch 列与快照实体矛盾'] = len(mism)
        st['底座 batch 有值但快照无实体'] = len(noent)
        if mism:
            F.append('E10 底座 batch 列与快照实体记录矛盾 %d 行，样例=%s' % (len(mism), mism[:5]))
        if noent:
            F.append('E10 底座 %d 行的 batch 列有值却找不到对应实体 args 记录，样例=%s'
                     % (len(noent), noent[:5]))

    # ---- 报告用：例外类计数（非判据）------------------------------------
    cc = collections.Counter(_classify(x) for x in snap_rows)
    for k, v in cc.most_common():
        st['快照类别·%s' % k] = v

    if verbose:
        print('—— 统计 ——')
        for k, v in st.items():
            print('   %-34s %s' % (k, v))
    return F, st


def _first(F, code):
    """取指定检查码的第一条失败 —— 阴性对照要展示**它守的那一条**，
    否则注入的坏数据可能先撞上别的检查（如默认名 train-7 同时偏离协议），
    打印出来的就不是被守的检查，对照等于没验证。"""
    for x in F:
        if x.startswith(code):
            return x
    return None


def self_test(base, snap_rows, G):
    """阴性对照：三种改坏方式，守卫**必须**报红。"""
    print('=== 阴性对照（守卫必须报红）===')
    ok = True

    # 对照 1：给一个底座 run 塞一条 batch=4 的实体记录
    name = base[0]
    G1 = collections.defaultdict(list, {k: [dict(x) for x in v] for k, v in G.items()})
    G1[name].append(dict(G1[name][0], args_bytes='1779', batch='4', workers='0', imgsz='640'))
    f1, _ = run_checks(base, snap_rows, G1, verbose=False)
    hit1 = _first(f1, 'E4') is not None
    print('   对照1（底座 run 改成 batch=4）→ %s %s' % ('报红 ✓' if hit1 else '没报红 ✗', _first(f1, 'E4')))
    ok &= hit1

    # 对照 2：底座里混入一个默认名产物
    f2, _ = run_checks(base + ['train-7'], snap_rows, G, verbose=False)
    hit2 = _first(f2, 'E5') is not None
    print('   对照2（底座混入 train-7）  → %s %s' % ('报红 ✓' if hit2 else '没报红 ✗', _first(f2, 'E5')))
    ok &= hit2

    # 对照 3：空底座（空集合硬失败）
    f3, _ = run_checks([], snap_rows, G, verbose=False)
    hit3 = _first(f3, 'E1') is not None
    print('   对照3（底座为空）          → %s %s' % ('报红 ✓' if hit3 else '没报红 ✗', _first(f3, 'E1')))
    ok &= hit3

    # 对照 4：把某底座 run 的实体记录全部改成 0 字节
    G4 = collections.defaultdict(list, {k: [dict(x) for x in v] for k, v in G.items()})
    for x in G4[name]:
        x['args_bytes'] = '0'
    f4, _ = run_checks(base, snap_rows, G4, verbose=False)
    hit4 = _first(f4, 'E3') is not None
    print('   对照4（实体全变 0 字节）   → %s %s' % ('报红 ✓' if hit4 else '没报红 ✗', _first(f4, 'E3')))
    ok &= hit4

    # 对照 5：早期 workers=8 基线混入底座
    f5, _ = run_checks(base + sorted(EARLY_W8 - set(base)), snap_rows, G, verbose=False)
    hit5 = _first(f5, 'E7') is not None
    print('   对照5（早期基线混入底座）  → %s %s' % ('报红 ✓' if hit5 else '没报红 ✗', _first(f5, 'E7')))
    ok &= hit5

    # 对照 6：底座自带 batch 列被改成 4（第二条证据路径）
    br = _load_base_rows()
    br6 = [dict(x) for x in br]
    for x in br6:
        if x['run'] == name:
            x['batch'] = '4'
            break
    f6, _ = run_checks(base, snap_rows, G, verbose=False, base_rows=br6)
    hit6 = _first(f6, 'E9') is not None
    print('   对照6（底座 batch 列改 4） → %s %s' % ('报红 ✓' if hit6 else '没报红 ✗', _first(f6, 'E9')))
    ok &= hit6

    # 对照 7：底座 batch 列与快照实体**对撞**（两边都自洽、但互相矛盾）
    br7 = [dict(x) for x in br]
    for x in br7:
        if x['run'] == name:
            x['batch'] = '64'          # 快照实体里没有 64 ⇒ E10 矛盾
            break
    G7 = collections.defaultdict(list, {k: [dict(y) for y in v] for k, v in G.items()})
    for y in G7[name]:
        y['batch'] = '64' if int(y['args_bytes']) == 0 else y['batch']
    f7, _ = run_checks(base, snap_rows, G7, verbose=False, base_rows=br7)
    hit7 = _first(f7, 'E10') is not None
    print('   对照7（两面证据对撞）      → %s %s' % ('报红 ✓' if hit7 else '没报红 ✗', _first(f7, 'E10')))
    ok &= hit7

    print('=== 阴性对照结论：%s ===' % ('全部按预期报红 ✓' if ok else '有对照未报红 ✗'))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--self-test', action='store_true', help='阴性对照：改坏一条，守卫必须报红')
    a = ap.parse_args()

    base = _load_base()
    base_rows = _load_base_rows()
    snap_rows, G = _load_snap()

    if a.self_test:
        return self_test(base, snap_rows, G)

    print('协议指纹守卫：标准协议 = batch 32 / workers 16 / imgsz 640')
    print('证据 1（底座自带列）：%s' % os.path.relpath(BASE, ROOT))
    print('证据 2（args 快照）  ：%s' % os.path.relpath(SNAP, ROOT))
    print()
    F, st = run_checks(base, snap_rows, G, verbose=True, base_rows=base_rows)
    print()
    if F:
        print('=== 结论：FAIL（%d 条）===' % len(F))
        for x in F:
            print('   ✗ %s' % x)
        return 1
    print('=== 结论：PASS —— 底座 %d 个 run 的训练协议与 32/16/640 完全一致 ===' % st['底座 distinct run'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
