# -*- coding: utf-8 -*-
"""add_frozen_guard2.py -- 冻结件纪律（第二版，替换第一版那个会改坏语法的做法）。

纪律：**放行件里 `analysis/` 与 `deliver/` 是冻结产物**。脚本可以新建缺失的件，
但**不得覆盖已存在的件**，除非显式 `--allow-rewrite`。

实现：把
    open(os.path.join(OUT, X), 'w', ...).write(Y)
换成
    _frozen_write(os.path.join(OUT, X), Y)
并在文件头插入 `_frozen_write`。
（第一版往 `with open(...)` 语句里插 `return` ⇒ 语法错误，已撤。）
"""
import os
import re
import io
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CODE = os.path.join(REPO, 'code')

HELPER = '''

def _frozen_write(path, text):
    """★ 冻结件纪律（2026-10-04）：`analysis/` 与 `deliver/` 里的件是**已冻结的生成件**。

    放行件上按顺序跑全集时，普查脚本会把它们重新生成成另一批数，**后面的守卫就会误报漂移**
    （对抗性核查后实测：`A1 可配对核心格` 由冻结值漂成 81）。故：
    **已存在的件不覆盖**，除非显式 `--allow-rewrite`；缺失的件照常写入。
    返回 True 表示写了。
    """
    if os.path.exists(path) and '--allow-rewrite' not in sys.argv:
        sys.stderr.write('[已跳过] %s 已存在（冻结件，拒绝覆盖；要覆盖请给 --allow-rewrite）\\n' % path)
        return False
    with open(path, 'w', encoding='utf-8', newline='') as _fh:
        _fh.write(text)
    return True
'''

PAT = re.compile(
    r"open\(\s*(os\.path\.join\(OUT,[^)]*\))\s*,\s*['\"]w['\"](?:[^)]*)?\)\s*\.write\((?P<body>.*?)\)\s*$",
    re.M)


def main():
    total = 0
    for p in sorted(glob.glob(os.path.join(CODE, '*.py'))):
        s = io.open(p, encoding='utf-8', newline='').read()
        if 'analysis' not in s and 'deliver' not in s:
            continue
        if '_frozen_write' in s:
            continue
        def rep(m):
            return '_frozen_write(%s, %s)' % (m.group(1), m.group('body'))
        s2, n = PAT.subn(rep, s)
        if n == 0:
            continue
        lines = s2.split('\n')
        last = 0
        for i, l in enumerate(lines[:90]):
            if re.match(r'^(import |from )', l):
                last = i
        lines.insert(last + 1, HELPER)
        io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
        total += n
        print('  %-34s %d 处写盘' % (os.path.basename(p), n))
    print('共改 %d 处' % total)
    return 0


if __name__ == '__main__':
    sys.exit(main())
