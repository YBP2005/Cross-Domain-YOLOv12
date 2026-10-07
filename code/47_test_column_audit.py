# -*- coding: utf-8 -*-
"""47_test_column_audit.py —— 从**归档证据**重建 `deliver/G1_test列_逐run.csv`（120 行）。

为什么有这个脚本（可复算缺口）：
  §5「三点阶梯」的全部数字都读自 `G1_test列_逐run.csv` 的 `test_map50_95` 列，
  而该 CSV 此前是**临时脚本**拼出来的（未入库）。论文 §9「数据与代码可得性」声称
  "每个数字都能追到归档路径"，因此需要一个**正式的、可复算的**生成器。

数据来源（全部在本仓库内，逐文件可核）：
  · 30% 档三点（c5 = dota15→dota15、c7 = dota15→aitod）：
      `deliver/P1_30p_{A,B}机归档_20261006/**/test_eval.json`（每 run 一份）
      以及 `deliver/{A,B}机_30p_test列_20261006/*/test_eval.json`
  · 10%/50% 档（c1/c2 = dota15→dota15、c3/c4 = dota15→aitod）：
      同一批归档里的 `test_eval.json`（A 机的 c3/c4 放在 `test_eval/` 平铺目录下）

判据（本脚本自带，不通过就**不写盘**）：
  ① 每个 run 的 `test_map50_95` 与 CSV 逐位比较（round 6 位）；
  ② 行数 = 6 格 × 2 臂 × 10 种子 = 120；
  ③ 与冻结件 `G1_test列_逐run.csv` 的 md5 一致（`--check` 模式下的硬断言）。

用法：
  python scripts/47_test_column_audit.py            # 核对（默认，不写盘）
  python scripts/47_test_column_audit.py --write    # 重建并写回 deliver/G1_test列_逐run.csv
"""
import csv
import glob
import hashlib
import io
import json
import os
import sys
import collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ★ 两种布局都成立（同 16_draft_tag_paths.py 的 `_find_root` 约定，只认 `base/` 这个唯一标志）：
#   作者树  ：analysis_M3/scripts/x.py  ⇒ ROOT = analysis_M3/
#   放行仓库：repo/code/x.py           ⇒ ROOT = repo/
def _find_root(start):
    d = os.path.abspath(start)
    for _ in range(6):
        if os.path.isdir(os.path.join(d, 'base')):
            return d
        d = os.path.dirname(d)
    return os.path.abspath(start)


ROOT = _find_root(os.path.dirname(os.path.abspath(__file__)))
WORK = ROOT
OUT = os.path.join(ROOT, 'provenance', 'deliver', '01_G1_test列_逐run.csv')
if not os.path.isdir(os.path.dirname(OUT)):          # 作者树：deliver/ 直接在 ROOT 下
    OUT = os.path.join(ROOT, 'deliver', 'G1_test列_逐run.csv')
FROZEN_MD5 = '0B4AAB99ADE6E9746B40210B21DA9A08'

# 证据文件的位置：显式枚举（★ 经验：glob(recursive=True) 在中文目录名上不下钻）
EVIDENCE_GLOBS = [
    r'P1_30p_A机归档_20261006\test_eval\*.json',
    r'P1_30p_A机归档_20261006\new_runs\*\test_eval.json',
    r'P1_30p_B机归档_20261006\*\test_eval.json',
    r'A机_30p_test列_20261006\*\test_eval.json',
    r'B机_30p_test列_20261006\*\test_eval.json',
]


def _evidence_dirs():
    """证据目录：作者树在 ROOT/deliver/，放行仓在 ROOT/provenance/deliver/。"""
    for sub in ('deliver', os.path.join('provenance', 'deliver')):
        d = os.path.join(ROOT, sub)
        if os.path.isdir(d):
            yield d

# cell → 机器（c1/c2/c5 在 B 机；c3/c4/c7 在 A 机）
MACHINE = {'c1': 'B', 'c2': 'B', 'c5': 'B', 'c3': 'A', 'c4': 'A', 'c7': 'A'}
CELLS = ['c1', 'c2', 'c3', 'c4', 'c5', 'c7']
ARMS = ['base100', 'strat100']


def md5f(path):
    h = hashlib.md5()
    with open(path, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest().upper()


def load_evidence():
    """返回 {run: dict}；同一 run 取第一份非空证据（后出现的空文件不覆盖）。"""
    ev, seen, empty = {}, 0, 0
    for base in _evidence_dirs():
        for pat in EVIDENCE_GLOBS:
            for p in sorted(glob.glob(os.path.join(base, pat))):
                seen += 1
                raw = io.open(p, encoding='utf-8', errors='replace').read().strip()
                if not raw:
                    empty += 1                       # 空占位（早先重复评估的残留）
                    continue
                d = json.loads(raw)
                run = d.get('run') or os.path.splitext(os.path.basename(p))[0]
                ev.setdefault(run, d)
    print('证据文件 %d 份（其中空文件 %d 份）⇒ 解析到 %d 个 run' % (seen, empty, len(ev)))
    return ev


def build(ev):
    rows = []
    for cell in CELLS:
        for arm in ARMS:
            for seed in range(42, 52):
                run = 'g1_%s_%s_%s_%s_s%d' % (
                    cell,
                    'd15tod15' if cell in ('c1', 'c2', 'c5') else 'd15toaitod',
                    arm,
                    {'c1': '10p', 'c2': '50p', 'c5': '30p',
                     'c3': '10p', 'c4': '50p', 'c7': '30p'}[cell],
                    seed,
                )
                d = ev.get(run)
                if d is None:
                    raise SystemExit('❌ 缺证据：%s（归档里找不到 test_eval.json）' % run)
                rows.append(dict(
                    machine=MACHINE[cell], run=run, cell=cell,
                    domain=run.split('_')[2], arm=arm,
                    budget=run.split('_')[4], seed=seed,
                    test_map50_95=round(float(d['test_map50_95']), 6),
                    val_best_map50_95='',
                    wall_sec=d.get('wall_sec', ''),
                ))
    return rows


def main():
    write = '--write' in sys.argv
    ev = load_evidence()
    rows = build(ev)

    # ---- 判据 ① 逐位核对 ----
    if os.path.exists(OUT):
        old = list(csv.DictReader(io.open(OUT, encoding='utf-8')))
        om = {r['run']: r for r in old}
        bad = []
        for r in rows:
            o = om.get(r['run'])
            if o is None:
                bad.append((r['run'], 'CSV 里没有'))
            elif abs(float(o['test_map50_95']) - r['test_map50_95']) > 1e-9:
                bad.append((r['run'], '%s vs %s' % (o['test_map50_95'], r['test_map50_95'])))
        print('逐位核对：%d/%d 行吻合，%d 行不符' % (len(rows) - len(bad), len(rows), len(bad)))
        for b in bad[:8]:
            print('   ·', b)
        if bad:
            print('*** 重建结果与冻结件不一致 —— 拒绝写盘')
            return 1
    else:
        print('（冻结件不存在，跳过逐位核对）')

    # ---- 判据 ② 规模 ----
    cnt = collections.Counter(r['cell'] for r in rows)
    if len(rows) != 120 or set(cnt) != set(CELLS) or set(cnt.values()) != {20}:
        print('*** 规模判据不通过：%d 行 %s' % (len(rows), dict(cnt)))
        return 1
    print('规模判据：120 行 = 6 格 × 2 臂 × 10 种子 ✓')

    # ---- 判据 ③ 与冻结件 md5 一致 ----
    txt = io.StringIO()
    w = csv.DictWriter(txt, fieldnames=list(rows[0].keys()), lineterminator='\r\n')
    w.writeheader()
    w.writerows(rows)
    new_bytes = txt.getvalue().encode('utf-8')
    h = hashlib.md5(new_bytes).hexdigest().upper()
    print('重建件 md5 = %s' % h)
    if h != FROZEN_MD5:
        print('*** 与冻结 md5 %s 不一致 ⇒ 拒绝写盘（先查清差异）' % FROZEN_MD5)
        return 1
    print('md5 判据：与冻结件 %s 逐字节一致 ✓' % FROZEN_MD5)

    if write:
        io.open(OUT, 'wb').write(new_bytes)
        print('已写回 %s（md5 %s）' % (OUT, md5f(OUT)))
    else:
        print('（核对模式，未写盘；加 --write 才写回）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
