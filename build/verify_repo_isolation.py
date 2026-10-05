# -*- coding: utf-8 -*-
"""verify_repo_isolation.py -- 在**隔离副本**里逐个跑放行脚本，得到**可信**的开箱可跑率。

为什么需要隔离
--------------
`code/` 里有几个脚本会**写共享输入**（最典型：`01_build_base.py` 会**从 raw/ 重建底座**）。
第一次我直接在放行件上跑全集，结果：
  · `01_build_base.py` 把放行的底座**覆盖成一个不完整的版本**（147 格 → 68 格）；
  · 之后 `43` 就报"聚合量 rows = 68，稿内引用为 147"，看起来像 43 坏了，**其实是底座被前面那步改坏了**。
⇒ 结论：**判断"某个脚本能不能跑"必须在干净副本里单独跑**，否则测的是脚本之间的互相污染。

本脚本：把 `复现仓库/` 复制到临时目录（跳过 build/ 与 MANIFEST），对每个 `code/*.py` 单独跑一次，
记录 exit code 与最后一行；并**按是否写共享输入分类报告**。
"""
import os
import io
import sys
import glob
import shutil
import tempfile
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 这些脚本会写共享输入（底座 / 分析件），单独跑也会改副本；在隔离副本里无所谓
WRITERS = {'01_build_base.py', '12_A1_backbone.py', '39b_capture_args_snapshot.py'}
# 需要网络或凭据，允许失败
NEEDS_NET = {'90_fetch_via_jump.py'}


def main():
    tmp = tempfile.mkdtemp(prefix='p1repo_')
    dst = os.path.join(tmp, 'repo')
    ignore = shutil.ignore_patterns('build', 'MANIFEST_sha256.csv', '__pycache__')
    shutil.copytree(REPO, dst, ignore=ignore)
    print('隔离副本: %s' % dst)
    results = []
    # ★ 先隔离跑一遍"会重写共享输入"的那几个脚本，看它们把副本改成什么样（见报告）
    for f in sorted(glob.glob(os.path.join(dst, 'code', '*.py'))):
        name = os.path.basename(f)
        env = dict(os.environ, PYTHONIOENCODING='utf-8')
        try:
            r = subprocess.run([sys.executable, f], cwd=dst, env=env,
                               capture_output=True, timeout=300)
            code = r.returncode
            tail = (r.stdout.decode('utf-8', 'replace').strip().split('\n') or [''])[-1]
        except subprocess.TimeoutExpired:
            code, tail = 'TIMEOUT', '超时'
        tag = 'OK' if code == 0 else ('允许失败' if name in NEEDS_NET else 'FAIL')
        results.append((name, code, tag, tail[:70]))
        print('  %-38s exit=%-8s %-8s %s' % (name, code, tag, tail[:70]))

    ok = sum(1 for r in results if r[1] == 0)
    realfail = [r for r in results if r[2] == 'FAIL']
    print()
    print('开箱可跑 %d / %d' % (ok, len(results)))
    print('真失败 %d 件：%s' % (len(fail_names := [r[0] for r in realfail]),
                               '、'.join(fail_names) if fail_names else '无'))
    print('（隔离副本保留在 %s，供复核）' % dst)
    return 1 if realfail else 0


if __name__ == '__main__':
    sys.exit(main())
