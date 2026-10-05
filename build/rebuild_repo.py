# -*- coding: utf-8 -*-
"""rebuild_repo.py -- **从唯一真相源整体重建**放行副本，并逐字节校验关键件。

为什么必须"整体重建"而不是"补几件"
----------------------------------
本会话在放行副本上连踩三次同一类事故，根因都是**副本件比真相源旧**：
  ① 页数测量用的参考文献副本旧 ⇒ 页数**静默少算 5 条**；
  ② 放行副本的主稿/补材是**改稿前**复制的 ⇒ 副本里仍是旧 gamma 值，`45` 守卫报 12 条假 FAIL；
  ③ 放行副本的**底座旧**（`base/run_table_canonical.csv` 与真相源 md5 不同）
     ⇒ `43` 在副本上重建出**不同的聚合量**（`ngt_insuff` 2 vs 11），并把冻结 CSV 覆盖成另一份。
⇒ 纪律：**放行件只允许"整体重建 + 逐字节校验"**，不允许手工挑几件复制。
本脚本即那条纪律的可执行形式：**先删旧、再从真相源拷、最后逐字节比对**，不一致即非零退出。
"""
import os
import io
import sys
import shutil
import hashlib

SRC = r'D:\deepseek\analysis'
SRC_M3 = os.path.join(SRC, 'work', 'analysis_M3')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (真相源, 副本内相对路径)
MAP = [
    (os.path.join(SRC_M3, 'base', 'run_table_canonical.csv'), 'base/run_table_canonical.csv'),
    (os.path.join(SRC_M3, 'base', 'run_backbone_map.csv'), 'base/run_backbone_map.csv'),
    (os.path.join(SRC_M3, 'base', 'args_protocol_snapshot.csv'), 'base/args_protocol_snapshot.csv'),
    (os.path.join(SRC_M3, 'base', 'dataset_split_counts.csv'), 'base/dataset_split_counts.csv'),
    (os.path.join(SRC_M3, 'base', 'p1d1_s50_test_readings.csv'), 'base/p1d1_s50_test_readings.csv'),
    (os.path.join(SRC_M3, 'base', 'provenance.csv'), 'base/provenance.csv'),
    (os.path.join(SRC_M3, 'base', '数据字典.md'), 'base/数据字典.md'),
    (os.path.join(SRC_M3, 'base', '缺口清单.md'), 'base/缺口清单.md'),
    (os.path.join(SRC_M3, '03_榨干报告_边界与结论_20261001.md'), '03_榨干报告_边界与结论_20261001.md'),
    (os.path.join(SRC, 'M3_draft', 'P1_NewDraft_v1_20260927.md'), 'M3_draft/P1_NewDraft_v1_20260927.md'),
    (os.path.join(SRC, 'M3_draft', '00_SUPPLEMENTARY_v0.4.md'), 'M3_draft/00_SUPPLEMENTARY_v0.4.md'),
]
# 整目录
DIRMAP = [
    (os.path.join(SRC_M3, 'scripts'), 'code', '*.py'),
    (os.path.join(SRC_M3, 'deliver'), 'deliver', '*'),
    (os.path.join(SRC_M3, 'analysis'), 'analysis', '*'),
    (os.path.join(SRC, 'figures', 'F1_design_v2.png'), None, None),   # 单独处理
]


def _excluded(name):
    """实验现场不进放行件（事故：2026-10-04 误拷入 46 MB run 归档）。

    判据：`*.tar.gz` 与名字含"归档"的任何项。
    它们是**实验原始数据**，而放行件只放**文本报告**。
    """
    return name.endswith('.tar.gz') or '归档' in name


def _ignore(dirpath, names):
    return [n for n in names if _excluded(n)]


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as fh:
        for c in iter(lambda: fh.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest().upper()


def main():
    bad = []
    # ① 整目录重建（先删旧）
    for src, rel, pat in DIRMAP:
        if rel is None:
            continue
        dst = os.path.join(REPO, rel)
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=_ignore)
        print('目录 %-12s <- %s' % (rel, src))
    # ② 单件
    for src, rel in MAP:
        dst = os.path.join(REPO, rel.replace('/', os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    # ③ 图
    fsrc = os.path.join(SRC, 'figures', 'F1_design_v2.png')
    fdst = os.path.join(REPO, 'figures', 'F1_design_v2.png')
    os.makedirs(os.path.dirname(fdst), exist_ok=True)
    shutil.copy2(fsrc, fdst)
    print('图   figures/F1_design_v2.png')

    # ④ 逐字节校验
    print()
    for src, rel in MAP:
        dst = os.path.join(REPO, rel.replace('/', os.sep))
        a, b = md5(src), md5(dst)
        tag = 'OK' if a == b else 'MISMATCH'
        print('%-46s %s' % (rel, tag))
        if a != b:
            bad.append(rel)
    if bad:
        print('\nFAIL %d 件不一致' % len(bad))
        return 1
    print('\nOK 全部关键件与真相源逐字节一致。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
