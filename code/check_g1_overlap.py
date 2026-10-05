#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""check_g1_overlap.py —— 核 G1 四个格的**训练/评估重叠**（决定 test 口径前必须查）。

为什么必须查
------------
我准备建议"test 口径统一用 `images/val`"。但在采纳前必须确认一件事：
**50p 档的训练集是否与 `images/val` 有交集？**
* AI-TOD：`aitod_20p` 用的是 `images/train_aitod_20p`（池的子集），50p 我从池里补到 5,607 张；
  若池里含 `images/val` 的图 ⇒ **训练会看到评估图**；
* DOTA15：`train/50_percent` 从 `images/train` 抽，理论上与 `images/val` 不相交，但**要实测**。

判据：**任一格交集 > 0 ⇒ 硬失败并报出**（不得静默）。输出各格的 train∩val 计数与样例文件名。
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ★ 2026-10-04 修（监视子代理报出）：c1/c2 原先写的是 `images/train_dota15_10p` ——
#   那个目录**只在 A 机存在**，B 机上没有 ⇒ 脚本在 B 报"目录缺失"并被计成需要处置（**假红**）。
#   而**两个 yaml 实际解析到的是 `train/<pct>_percent/images`，两机都有**。
#   ⇒ 路径改为 yaml 真正用的那一个。（教训：核对脚本里的路径必须用"yaml 解析出来的路径"，
#     不能凭"看起来对"的目录名 —— 那正是接线错同一类的错。）
SETS = {
    'c1 dota15 10p': ('/root/datasets_mask/dota15_yolo/train/10_percent/images',
                      '/root/datasets_mask/dota15_yolo/images/val'),
    'c2 dota15 50p': ('/root/datasets_mask/dota15_yolo/train/50_percent/images',
                      '/root/datasets_mask/dota15_yolo/images/val'),
    'c3 aitod  10p': ('/root/datasets/AI-TOD_yolo/images/train_aitod_10p',
                      '/root/datasets/AI-TOD_yolo/images/val'),
    'c4 aitod  50p': ('/root/datasets/AI-TOD_yolo/images/train_aitod_50p',
                      '/root/datasets/AI-TOD_yolo/images/val'),
    # 参考：AI-TOD 全池 vs val（判断"池本身是否含 val"）
    'REF aitod 池': ('/root/datasets/AI-TOD_yolo/images/train',
                     '/root/datasets/AI-TOD_yolo/images/val'),
    # 参考：carve 出的 val（协议的另一口径）
    'REF aitod carve': ('/root/datasets/AI-TOD_yolo/carve_aitod20/images',
                        '/root/datasets/AI-TOD_yolo/images/val'),
}


def imgs(d):
    if not os.path.isdir(d):
        return None
    return set(f for f in os.listdir(d)
               if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')))


def main():
    bad = 0
    print('%-18s %8s %8s %8s  %s' % ('格', 'train', 'val', '交集', '判定'))
    print('-' * 72)
    for tag, (tr, va) in SETS.items():
        A, B = imgs(tr), imgs(va)
        if A is None or B is None:
            print('%-18s %8s %8s %8s  ★目录缺失' % (tag, '?' if A is None else len(A),
                                                   '?' if B is None else len(B), '—'))
            bad += 1
            continue
        inter = A & B
        verdict = 'OK（无重叠）' if not inter else '★**重叠 %d 张**' % len(inter)
        if inter and not tag.startswith('REF'):
            bad += 1
        print('%-18s %8d %8d %8d  %s' % (tag, len(A), len(B), len(inter), verdict))
        if inter:
            print('      样例：%s' % '、'.join(sorted(inter)[:5]))
    print()
    if bad:
        print('★ 有 %d 项需要处置（上面标 ★ 的）——**不要静默通过**' % bad)
        return 1
    print('全部无重叠。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
