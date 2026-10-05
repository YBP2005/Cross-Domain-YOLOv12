#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_aitod_pct_subsets.py — 为 G1 造 **AI-TOD 的 10p / 50p 标注子集**。

为什么需要这一件
----------------
G1（预算 × 域差 2×2 分离设计）要用 `dota15 → aitod` 在 **10% 与 50%** 两个预算下跑。
但 A/B 两机的 AI-TOD 目录**只有 20% 一档**（`images/train_aitod_20p`，2,243 张），
历史全库里 `aitod_10p` / `aitod_50p` **一次都没出现过**
（对照：dota15 那侧的 `dota15_10p` 有 467 处引用、`dota15_50p` 403 处）。
⇒ **10p/50p 必须新建**；这是 G1 目前唯一的硬缺口。

照谁的办法造（**不自己发明**）
-----------------------------
照 `work/build_dota15_pct_subsets.py`（历史造 dota15 10/30/50p 的那份）的两条关键设计：

1. **嵌套**：`10p ⊂ 20p ⊂ 50p ⊆ 池`，**锚在历史 20% 子集上**。
   若各档独立随机抽，档间差异里就混进"抽到了哪些图"这一项，**不能纯净归因于标注量**。
2. **val/test 与既有 20p 的 yaml 逐字一致**（都指 `images/val`）。
   这样"评估面"不动，**只有训练标注量一个变量在动**。

★ 与 dota15 那侧保持一致 ⇒ 两台机、两档域差、三个预算档，**评估口径统一**。

安全（与历史脚本同款）
----------------------
* **只建软链接**，不复制图片；标签同样软链接；
* 目标目录**已存在就跳过**（幂等）；
* **不改动任何既有文件**，只新增两个链接目录 + 两个 yaml；
* 落盘前先做全部断言，**任一不过就退出**（空集合/嵌套破坏必须硬失败）。

用法（在目标机上跑；默认只做 dry-run，要看就加 --apply）：
    /root/yolo_env/bin/python build_aitod_pct_subsets.py            # 只检查+报告
    /root/yolo_env/bin/python build_aitod_pct_subsets.py --apply    # 真正建链接与 yaml
"""
import io
import os
import sys
import random
import argparse

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = '/root/datasets/AI-TOD_yolo'
POOL_I = os.path.join(BASE, 'images', 'train')      # 全池 11,214
POOL_L = os.path.join(BASE, 'labels', 'train')
ANCHOR = os.path.join(BASE, 'images', 'train_aitod_20p')   # 历史 20% 子集（2,243）
ANCHOR_L = os.path.join(BASE, 'labels', 'train_aitod_20p')
SEED = 42

NC = 8
NAMES = ("['airplane', 'bridge', 'person', 'ship', 'storage-tank', 'swimming-pool', "
         "'vehicle', 'wind-mill']")

# 预算档 -> 目标张数（由锚点 20p 的张数换算，**不写死**，见 main()）
TARGETS = {10: 0.10, 50: 0.50}


def imgs(d):
    if not os.path.isdir(d):
        return []
    return [f for f in sorted(os.listdir(d))
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'))]


def fail(msg):
    print('\n❌ 硬失败：%s' % msg)
    sys.exit(2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='真正建链接与 yaml（默认 dry-run）')
    a = ap.parse_args()

    print('=' * 66)
    print('AI-TOD 10p/50p 子集构建（嵌套法，seed=%d）' % SEED)
    print('=' * 66)

    # ---------- 池与锚 ----------
    pool = imgs(POOL_I)
    anchor = imgs(ANCHOR)
    if not pool:
        fail('池目录空或缺：%s' % POOL_I)
    if not anchor:
        fail('锚（20p）目录空或缺：%s' % ANCHOR)

    # ---------- 与 20p yaml 的既有数字对撞（口径核对）----------
    EXP_ANCHOR = 2243        # A/B 机实测 images/train_aitod_20p 张数
    if len(anchor) != EXP_ANCHOR:
        fail('锚张数 %d != 既有 20p 的实测值 %d ⇒ 口径不符，停止' % (len(anchor), EXP_ANCHOR))
    if not set(anchor) <= set(pool):
        fail('锚 ⊄ 池（%d 张不在池里）' % len(set(anchor) - set(pool)))

    print('池（images/train）      : %d 张' % len(pool))
    print('锚（20p，⊆ 池）        : %d 张' % len(anchor))

    # ---------- 目标档（按池的百分比换算，锚必须落在区间内）----------
    targets = {}
    for pct, frac in sorted(TARGETS.items()):
        n = int(round(len(pool) * frac))
        targets[pct] = n
    print('目标张数（池 × 比例）  : ' + ' / '.join('%dp=%d' % (p, n) for p, n in targets.items()))

    n10, n50 = targets[10], targets[50]
    if not (n10 < len(anchor) < n50):
        fail('锚张数 %d 不落在 (%d, %d) 之间 ⇒ 10p⊂20p⊂50p 无法成立' % (len(anchor), n10, n50))

    # ---------- 抽样（嵌套）----------
    rnd = random.Random(SEED)
    # 10p ⊂ 20p：取锚的子集
    a_sorted = sorted(anchor)
    take10 = sorted(rnd.sample(a_sorted, n10))
    # 50p ⊇ 20p：补满到 n50（从池里排除锚之后取）
    rest = sorted(set(pool) - set(anchor))
    need50 = n50 - len(anchor)
    if need50 > len(rest):
        fail('池不足：需再补 %d 张，池里只剩 %d 张' % (need50, len(rest)))
    take50 = sorted(anchor) + sorted(rnd.sample(rest, need50))

    # ---------- 断言（任一不过即停）----------
    s10, s50, sa, sp = set(take10), set(take50), set(anchor), set(pool)
    checks = [
        ('10p ⊆ 20p', s10 <= sa),
        ('20p ⊆ 50p', sa <= s50),
        ('50p ⊆ 池', s50 <= sp),
        ('10p 张数 == %d' % n10, len(s10) == n10),
        ('50p 张数 == %d' % n50, len(s50) == n50),
        ('10p ∩ (20p∖10p) 的补集不重叠', len(sa - s10) == len(sa) - len(s10)),
    ]
    print('\n断言：')
    bad = []
    for name, ok in checks:
        print('  [%s] %s' % ('OK' if ok else 'FAIL', name))
        if not ok:
            bad.append(name)
    if bad:
        fail('断言未通过：%s' % '、'.join(bad))

    # ---------- 标签可用性 ----------
    def n_lbl(files):
        return sum(1 for f in files
                   if os.path.exists(os.path.join(POOL_L, os.path.splitext(f)[0] + '.txt')))
    print('\n标签可得性（池侧）：%d / %d' % (n_lbl(pool), len(pool)))

    # ---------- 落盘 ----------
    plan = {10: take10, 50: take50}
    for pct in sorted(plan):
        di = os.path.join(BASE, 'images', 'train_aitod_%dp' % pct)
        dl = os.path.join(BASE, 'labels', 'train_aitod_%dp' % pct)
        yml = os.path.join(BASE, 'aitod_%dp.yaml' % pct)
        if os.path.isdir(di) and imgs(di):
            print('\n[跳过] %s 已存在（%d 张）—— 幂等，不覆盖' % (di, len(imgs(di))))
            continue
        print('\n[建] %s ：%d 张%s' % (di, len(plan[pct]), '' if a.apply else '（dry-run，未落盘）'))
        if not a.apply:
            continue
        os.makedirs(di, exist_ok=True)
        os.makedirs(dl, exist_ok=True)
        miss = 0
        for f in plan[pct]:
            src_i = os.path.join(POOL_I, f)
            dst_i = os.path.join(di, f)
            if not os.path.exists(dst_i):
                os.symlink(src_i, dst_i)
            b = os.path.splitext(f)[0] + '.txt'
            src_l = os.path.join(POOL_L, b)
            if os.path.exists(src_l):
                dst_l = os.path.join(dl, b)
                if not os.path.exists(dst_l):
                    os.symlink(src_l, dst_l)
            else:
                miss += 1
        # yaml：val/test **与既有 aitod_20p.yaml 逐字一致**
        with io.open(yml, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write('# G1 budget subset (nested): 10p \u2282 20p \u2282 50p \u2282 pool; seed %d.\n' % SEED)
            fh.write('# val/test are IDENTICAL to aitod_20p.yaml, so only the training annotation\n'
                     '# amount varies across budget levels (same design as dota15_10p/_50p).\n')
            fh.write('path: %s\n' % BASE)
            fh.write('train: images/train_aitod_%dp\n' % pct)
            fh.write('val: images/val\n')
            fh.write('test: images/val\n')
            fh.write('nc: %d\n' % NC)
            fh.write('names: %s\n' % NAMES)
        print('     标签缺 %d 张；yaml -> %s' % (miss, yml))

    print('\n' + '=' * 66)
    if not a.apply:
        print('dry-run 结束。加 --apply 才落盘。')
    else:
        print('完成。**未改动任何既有文件**（只新增两个链接目录与两个 yaml）。')
    print('=' * 66)
    return 0


if __name__ == '__main__':
    sys.exit(main())
