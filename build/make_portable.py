# -*- coding: utf-8 -*-
"""make_portable.py -- 把 released code 里的**作者机器绝对路径**改成**可移植的路径**。

为什么有这一件
--------------
对抗性核查里 5 份独立报出"放行包开箱不可跑"。根因有两条：
  ① 目录结构与脚本约定不符（`data/` vs `base/`、`provenance/deliver` vs `deliver`）—— **已用 mv 修好**；
  ② **脚本里到处是作者机器的绝对路径** `BASE = r"D:\\deepseek\\analysis\\work\\analysis_M3"`
     —— 这是**真正的不可移植**：换一台机器、或只把 `复现仓库\\` 拷给别人，全部脚本立刻打不开底座。
本脚本把 ② 修成"从脚本文件自身位置反推仓库根"，**只改路径行，不动任何分析逻辑**。

判据：改完后 `python code/43_A24_power_audit.py` 与 `python code/16_draft_tag_paths.py` 必须能跑，
且 `43` 重建出的 CSV 与冻结件**逐字节一致**。
"""
import os
import re
import io
import glob
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CODE = os.path.join(REPO, 'code')

PORTABLE = '''BASE = _repo_root()          # 可移植：从脚本位置反推仓库根（见文件头的 _repo_root）
'''

HELPER = '''

def _repo_root():
    """仓库根 = 含有 `base/run_table_canonical.csv` 的那一级（从本文件向上找）。

    ⚠ 放行副本原先写死 `BASE = r"D:\\\\deepseek\\\\analysis\\\\work\\\\analysis_M3"`（作者机器），
      换台机器就打不开底座 —— 对抗性核查有 5 份独立报出"开箱不可跑"。故改为反推。
    """
    here = os.path.dirname(os.path.abspath(__file__))
    d = here
    for _ in range(5):
        if os.path.exists(os.path.join(d, 'base', 'run_table_canonical.csv')):
            return d
        d = os.path.dirname(d)
    return os.path.dirname(here)
'''


def main():
    patched = []
    for p in sorted(glob.glob(os.path.join(CODE, '*.py'))):
        s = io.open(p, encoding='utf-8', newline='').read()
        orig = s
        n = 0
        # 形态 A：BASE = r"D:\deepseek\..."（含单引号/双引号、正/反斜杠）
        s, k = re.subn(r'BASE\s*=\s*r?["\']D:[\\/]+deepseek[^"\']*["\']', 'BASE = _repo_root()', s)
        n += k
        if n and '_repo_root' in s and 'def _repo_root' not in s:
            # 插到最后一个 import 之后
            lines = s.split('\n')
            last = 0
            for i, l in enumerate(lines[:60]):
                if re.match(r'^(import |from )', l):
                    last = i
            lines.insert(last + 1, HELPER)
            s = '\n'.join(lines)
        if s != orig:
            io.open(p, 'w', encoding='utf-8', newline='').write(s)
            patched.append((os.path.basename(p), n))
    print('patched %d files' % len(patched))
    for name, k in patched:
        print('  %-34s %d 处路径' % (name, k))
    # 报告仍含绝对路径的文件（应为 0）
    left = []
    for p in sorted(glob.glob(os.path.join(CODE, '*.py'))):
        s = io.open(p, encoding='utf-8', newline='').read()
        if re.search(r'D:[\\/]+deepseek', s):
            left.append(os.path.basename(p))
    print('仍含作者机绝对路径的文件：%s' % (left if left else '无'))
    return 1 if left else 0


if __name__ == '__main__':
    sys.exit(main())
