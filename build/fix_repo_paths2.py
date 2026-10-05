# -*- coding: utf-8 -*-
"""fix_repo_paths2.py -- 第二遍：把**所有**"按层数反推"的路径都换成 `_repo_root()`。

第一遍只修了赋值语句本身，但忘了 `DRAFT`/`SUPP`/`_SUP` 这些**由 BASE 再 dirname 反推**的路径
（作者侧 BASE 是 `...\\work\\analysis_M3`，`dirname(dirname(BASE))` 正好到 `analysis\\`；
放行副本里 BASE 已是**仓库根**，再反推两级就跑到 `E:\\WorkBuddy\\` 去了）。
"""
import os
import io
import re
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CODE = os.path.join(REPO, 'code')

ROOT_FN = '''def _repo_root():
    """仓库根 = 含 `M3_draft` 的那一级（从本文件位置向上找）。放行副本的层数比作者侧少，不能靠 dirname 数级。"""
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        if os.path.isdir(os.path.join(d, 'M3_draft')):
            return d
        d = os.path.dirname(d)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
'''

# 所有形态：os.path.join(<反推>, 'M3_draft', '...')
PAT = re.compile(
    r"os\.path\.join\(\s*os\.path\.dirname\(os\.path\.dirname\((?P<v>[A-Za-z_][A-Za-z0-9_]*)\)\)\s*,"
    r"\s*'M3_draft'")
PAT2 = re.compile(
    r"os\.path\.join\(\s*os\.path\.dirname\(os\.path\.dirname\(os\.path\.dirname\((?P<v>[A-Za-z_][A-Za-z0-9_]*)\)\)\)\s*,"
    r"\s*'M3_draft'")


def main():
    total = 0
    for p in sorted(glob.glob(os.path.join(CODE, '*.py'))):
        s = io.open(p, encoding='utf-8', newline='').read()
        o = s
        s, n1 = PAT2.subn("os.path.join(_repo_root(), 'M3_draft'", s)
        s, n2 = PAT.subn("os.path.join(_repo_root(), 'M3_draft'", s)
        n = n1 + n2
        if n:
            if 'def _repo_root' not in s:
                lines = s.split('\n')
                last = 0
                for i, l in enumerate(lines[:70]):
                    if re.match(r'^(import |from )', l):
                        last = i
                lines.insert(last + 1, ROOT_FN)
                s = '\n'.join(lines)
            io.open(p, 'w', encoding='utf-8', newline='').write(s)
            total += n
            print('  %-38s %d 处' % (os.path.basename(p), n))
    print('共修 %d 处' % total)

    print()
    print('仍含"dirname(dirname(" 且带 M3_draft 的行：')
    bad = []
    for p in sorted(glob.glob(os.path.join(CODE, '*.py'))):
        s = io.open(p, encoding='utf-8', newline='').read()
        for i, ln in enumerate(s.split('\n'), 1):
            if 'M3_draft' in ln and 'dirname' in ln and '`' not in ln:
                bad.append('%s:%d %s' % (os.path.basename(p), i, ln.strip()[:80]))
    for b in (bad if bad else ['无']):
        print('  ', b)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
