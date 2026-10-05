# -*- coding: utf-8 -*-
"""fix_repo_paths.py -- 修放行副本里**剩下的**几处路径推导（每次都从"脚本位置"反推仓库根）。

背景：作者侧的目录层数是
    analysis\\work\\analysis_M3\\scripts\\*.py        （脚本）
    analysis\\                                 （`_TOP` 找的东西：M3_draft 在它下面）
而放行副本是
    复现仓库\\code\\*.py  /  复现仓库\\M3_draft\\  /  复现仓库\\deliver\\  /  复现仓库\\base\\  /  复现仓库\\analysis\\
层数**少了两级**，于是 `dirname(dirname(dirname(_ANA)))` 之类的反推会**跑过头**。
本脚本把这几处改成"从脚本位置找仓库根"，并**补上缺的 45 号脚本**。
"""
import os
import io
import re
import sys
import glob
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CODE = os.path.join(REPO, 'code')
SRC_SCRIPTS = r'D:\deepseek\analysis\work\analysis_M3\scripts'

ROOT_FN = '''
def _repo_root():
    """仓库根 = 含 `M3_draft` 的那一级（从本文件向上找）。放行副本层数比作者侧少，故不能靠 dirname 数级。"""
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        if os.path.isdir(os.path.join(d, 'M3_draft')):
            return d
        d = os.path.dirname(d)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
'''


def patch(name, subs, add_helper_after=None):
    p = os.path.join(CODE, name)
    s = io.open(p, encoding='utf-8', newline='').read()
    n = 0
    for a, b in subs:
        if a in s:
            s = s.replace(a, b)
            n += 1
        else:
            print('  ! %s: 未找到 %r' % (name, a[:60]))
    if n and add_helper_after and 'def _repo_root' not in s:
        lines = s.split('\n')
        last = 0
        for i, l in enumerate(lines[:70]):
            if re.match(r'^(import |from )', l):
                last = i
        lines.insert(last + 1, ROOT_FN)
        s = '\n'.join(lines)
    if n:
        io.open(p, 'w', encoding='utf-8', newline='').write(s)
    print('  %-34s 改了 %d 处' % (name, n))
    return n


def main():
    print('① 16_draft_tag_paths.py：_ANA 改为"仓库根下的 analysis"；_TOP 改为仓库根')
    patch('16_draft_tag_paths.py', [
        ("_ANA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'analysis')",
         "_ANA = os.path.join(_repo_root(), 'analysis')"),
        ("_TOP = os.path.dirname(os.path.dirname(os.path.dirname(_ANA)))",
         "_TOP = _repo_root()"),
    ], add_helper_after=True)

    print('② 15_audit_sources.py：被引来源路径同样按仓库根解析')
    s = io.open(os.path.join(CODE, '15_audit_sources.py'), encoding='utf-8', newline='').read()
    if 'def _repo_root' not in s:
        lines = s.split('\n')
        last = 0
        for i, l in enumerate(lines[:70]):
            if re.match(r'^(import |from )', l):
                last = i
        lines.insert(last + 1, ROOT_FN)
        s = '\n'.join(lines)
        io.open(os.path.join(CODE, '15_audit_sources.py'), 'w', encoding='utf-8', newline='').write(s)
        print('  %-34s 插入 _repo_root' % '15_audit_sources.py')

    print('③ 补上缺的 45_verify_appendix_P_arithmetic.py，并改其 ROOT')
    src45 = os.path.join(SRC_SCRIPTS, '45_verify_appendix_P_arithmetic.py')
    dst45 = os.path.join(CODE, '45_verify_appendix_P_arithmetic.py')
    if not os.path.exists(dst45):
        shutil.copy2(src45, dst45)
        print('  已从作者侧复制 45 号脚本')
    s45 = io.open(dst45, encoding='utf-8', newline='').read()
    s45 = s45.replace("ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))   # analysis/",
                      "ROOT = os.path.dirname(HERE)          # 放行副本：仓库根（M3_draft 在它下面）")
    io.open(dst45, 'w', encoding='utf-8', newline='').write(s45)
    print('  45 号脚本的 ROOT 已改为仓库根')

    print()
    print('剩余含作者机绝对路径的文件：')
    left = []
    for p in sorted(glob.glob(os.path.join(CODE, '*.py'))):
        s = io.open(p, encoding='utf-8', newline='').read()
        for ln in s.split(chr(10)):
            if '`' in ln:
                continue
            if re.search(r'D:[\\/]+deepseek|/d/deepseek', ln):
                left.append(os.path.basename(p))
                break
    print('  ', left if left else '无')
    return 0


if __name__ == '__main__':
    sys.exit(main())
