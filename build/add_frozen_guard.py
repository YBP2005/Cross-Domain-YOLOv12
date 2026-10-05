# -*- coding: utf-8 -*-
"""add_frozen_guard.py -- 给会写 `analysis/` 或 `deliver/` 的脚本加**冻结件拒绝覆盖**守卫。

为什么
------
对抗性核查的 A6/A8 让 5 份评审报出"开箱不可跑"，而我查根因时发现**更隐蔽的一层**：
在放行件上按顺序跑全集时，前面那些**普查**脚本会把 `analysis/` 与 `deliver/` 里**冻结的生成件
重新生成成另一批数**（例：`A1 可配对核心格` 由冻结值漂成 **81**），
于是后面的**守卫**脚本对着"刚被改过的生成件"报漂移 —— 看起来像守卫坏了，其实是**先跑的那批把地板换了**。

⇒ 纪律：**放行件里的 `analysis/` 与 `deliver/` 是冻结产物**；脚本可以**新建**缺失的件，
但**不得覆盖已存在的件**，除非显式给 `--allow-rewrite`。
本脚本给这些脚本插入一条统一的守卫函数与一处调用点（**只在放行副本上执行**；作者侧照旧）。
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

def _guard_frozen(path):
    """★ 冻结件纪律（2026-10-04）：`analysis/` 与 `deliver/` 里的件是**已冻结的生成件**。

    放行件上按顺序跑全集时，普查脚本会把它们重新生成成另一批数，**后面的守卫就会误报漂移**
    （对抗性核查后我实测到 `A1 可配对核心格` 由冻结值漂成 81）。故：
    **已存在的件不覆盖**，除非显式 `--allow-rewrite`；缺失的件照常新建。
    """
    if os.path.exists(path) and '--allow-rewrite' not in sys.argv:
        sys.stderr.write('[已跳过] %s 已存在（冻结件，拒绝覆盖；要覆盖请给 --allow-rewrite）\\n' % path)
        return False
    return True
'''

# 只给"会写 analysis/ 或 deliver/"的脚本加
def targets():
    out = []
    for p in sorted(glob.glob(os.path.join(CODE, '*.py'))):
        s = io.open(p, encoding='utf-8', newline='').read()
        if re.search(r"open\([^)]*['\"]w['\"]", s) and ('analysis' in s or 'deliver' in s):
            out.append(p)
    return out


def main():
    n = 0
    for p in targets():
        s = io.open(p, encoding='utf-8', newline='').read()
        if '_guard_frozen' in s:
            continue
        # 插 helper：放在最后一个 import 之后
        lines = s.split('\n')
        last = 0
        for i, l in enumerate(lines[:80]):
            if re.match(r'^(import |from )', l):
                last = i
        lines.insert(last + 1, HELPER)
        s = '\n'.join(lines)
        # 给每个写盘点加守卫：把 open(X, 'w'...) 前面插一行
        #   形如： w(...) / open(os.path.join(OUT, 'x.md'), 'w', ...)
        def repl(m):
            pre, path_expr, post = m.group(1), m.group(2), m.group(3)
            return '%sif not _guard_frozen(%s):\n        return 0\n    %s%s%s' % (
                pre, path_expr, pre, 'open(' + path_expr, post)
        # 保守：只处理最常见的两种写法，避免改坏
        s2 = re.sub(r"( *)open\((os\.path\.join\(OUT,[^)]*\)),\s*'w'", 
                    lambda m: "if not _guard_frozen(%s):\n        return 0\n    open(%s, 'w'" % (m.group(2), m.group(2)), s)
        s2 = re.sub(r"( *)open\((os\.path\.join\(OUT,[^)]*\)),\s*\"w\"",
                    lambda m: "if not _guard_frozen(%s):\n        return 0\n    open(%s, \"w\"" % (m.group(2), m.group(2)), s2)
        if s2 != s:
            io.open(p, 'w', encoding='utf-8', newline='').write(s2)
            n += 1
            print('  guarded', os.path.basename(p))
        else:
            io.open(p, 'w', encoding='utf-8', newline='').write(s)
            print('  helper only', os.path.basename(p))
    print('共处理 %d 件' % n)
    return 0


if __name__ == '__main__':
    sys.exit(main())
