# -*- coding: utf-8 -*-
r"""46_verify_prereg_draft.py -- 预注册草案里的**可算数**守卫（只读）。

为什么有这一件
--------------
草案里出现的每个数都必须**能从公式或底座重算**，否则就是"写在纸上的字面量"，
而纪律要求"**算出来的量绝不许写成字面量**"。本件把草案 §2/§4/§5 的三个可算数逐一对撞：

1. $\gamma(10)$ 与 $\mathrm{MDE}(10)$ 用的是**档案中位 $\hat\sigma$**（该值本身也从
   `deliver/theory_B_MDE_by_cell.csv` 重算，不采信文案）；
2. $\mathrm{MDE}(10) < 0.30$（注册幅度条）是否成立；
3. run 数：4 格 × 2 臂 × 10 种子 = 80；加同域对照后 = 120；
4. 止损线 = $2.5 \times$ 中位 $\hat\sigma$，且**印出来的值**与重算值一致。

用法：python scripts/46_verify_prereg_draft.py
"""
import os
import re
import io
import sys
import csv
import math
import statistics
import argparse

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from scipy.stats import t as T  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


# ★★ 2026-10-05：**向上查找仓库根**（布局无关）。放行布局 `仓库/code/x.py`、
#   作者布局 `analysis_M3/code/x.py`，两者"根"的定义不同 ⇒ 不能写死层数。
def _find_root(start):
    d = os.path.abspath(start)
    for _ in range(6):
        if os.path.isdir(os.path.join(d, 'base')) and (
                os.path.isdir(os.path.join(d, 'M3_draft'))
                or os.path.isdir(os.path.join(d, 'deliver'))):
            return d
        d = os.path.dirname(d)
    return os.path.abspath(start)
ROOT = _find_root(HERE)   # ★ 2026-10-05：向上查找仓库根（布局无关）


# ★★ 2026-10-05：**缺失依赖不崩、只报红**（与 `_SUPT` 同一模式）。
_MISSING = []
def _try_read(path, what=''):
    """读文件；失败则记入 `_MISSING` 并返回空串（**不抛异常**）。"""
    try:
        with open(path, encoding='utf-8', errors='replace') as _fh:
            return _fh.read()
    except Exception as _e:
        _MISSING.append('%s（%s）' % (what or os.path.basename(str(path)), str(_e)[:60]))
        return ''
DRAFT = os.path.join(ROOT, 'deliver',
                     '预注册草案_预算×域差2x2分离设计_20261004.md')
MDE_CSV = os.path.join(ROOT, 'deliver', 'theory_B_MDE_by_cell.csv')

ALPHA, BETA = 0.05, 0.20
BAR = 0.30
TOL = 5e-4
FAILS = []


def gamma(n):
    return (float(T.ppf(1 - ALPHA / 2, n - 1)) + float(T.ppf(1 - BETA, n - 1))) / math.sqrt(n)



def after_key(text, key):
    r"""按**字面子串**定位，再取紧随其后的第一个小数。

    ⚠ 不能拿 LaTeX 去做正则：`\mathrm` 里的 `\m`、`\gamma` 里的 `\g` 都会被当成转义/组引用，
      直接 `re.error: bad escape`（本会话在 44/45/46 各踩一次）。故一律 `str.find`。
    """
    k = text.find(key)
    if k < 0:
        return None
    m = re.match(r'([0-9]+\.[0-9]+)', text[k + len(key):])
    return float(m.group(1)) if m else None


def check(cond, label, got=None, want=None):
    if cond:
        print('| OK | %s |' % label)
    else:
        print('| FAIL | %s | got=%s want=%s |' % (label, got, want))
        FAILS.append(label)


def main(self_test=False):
    t = io.open(DRAFT, encoding='utf-8', newline='').read().replace('\r\n', '\n')

    # ---- 中位 σ̂：从表重算，不采信文案 ----
    rows = list(csv.DictReader(io.open(MDE_CSV, encoding='utf-8', newline='')))
    sds = [float(r['sd']) for r in rows if r.get('sd')]
    med = statistics.median(sds)
    check(abs(med - 0.2744) < 5e-5, '档案中位 σ̂（%d 格）' % len(sds), '%.4f' % med, '0.2744')

    # ---- 草案里印的先验 σ̂ 必须等于重算值 ----
    m = re.search(r'中位 \$\\hat\\sigma = ([\d.]+)\$ pp', t)
    check(m is not None and abs(float(m.group(1)) - med) < 5e-5,
          '草案印的先验 σ̂ == 重算中位', m.group(1) if m else None, '%.4f' % med)
    prior = float(m.group(1)) if m else med

    # ---- γ(10) 与 MDE(10) ----
    g10, mde10 = gamma(10), gamma(10) * prior
    v2 = after_key(t, 'MDE}(10) = ')
    check(v2 is not None and abs(v2 - mde10) < TOL,
          'MDE(10) == γ(10)·σ̂', v2, '%.4f' % mde10)
    #   ⚠ 两个坑都踩过：① 锚点 `hat\sigma = ` 先命中 §2 命名先验的 0.2744（假红）；
    #     ② 锚点 `MDE} = ` 先命中 §2 的 `MDE}(9) = 0.2922`（"MDE}" 后面不是 " = "）。
    #     ⇒ 用**两段锚**：先定位 §4 的 `MDE} = `，再在其后找 `hat\sigma = `。
    def _sec4_value(text):
        k = text.find('MDE} = ')
        if k < 0:
            return None
        return after_key(text[k:], 'hat' + chr(92) + 'sigma = ')

    v3 = _sec4_value(t)
    if self_test:
        v3 = (v3 or 0) + 0.5          # 阴性对照：把印值改坏
    check(v3 is not None and abs(v3 - mde10) < TOL,
          '§4 的 MDE 印值一致', v3, '%.4f' % mde10)
    check(mde10 < BAR, 'MDE(10) < 0.30 pp ⇒ 事前功效成立', '%.4f' % mde10, '< 0.30')

    # ---- 止损线 = 2.5 × 中位 ----
    stop = 2.5 * med
    v4 = after_key(t, 'hat' + '\\' + 'sigma > ')
    check(v4 is not None and abs(v4 - stop) < TOL,
          '止损线 == 2.5 × 中位 σ̂', v4, '%.4f' % stop)

    # ---- run 数 ----
    m5 = re.search(r'= \*\*(\d+) run\*\*', t)
    check(m5 is not None and int(m5.group(1)) == 4 * 2 * 10, 'run 数 == 4×2×10',
          m5.group(1) if m5 else None, 80)
    check('**120**' in t or '120' in t, '加同域对照后的 120 已登记')

    # ---- 未冻结：不得出现已填的哈希 ----
    m6 = re.search(r'FROZEN-HASH[^\n]*?:\s*([0-9a-f]{32})', t)
    check(m6 is None, '草案未填 FROZEN-HASH（仍是未冻结状态）', m6.group(1) if m6 else '未填')

    print('')
    if FAILS:
        print('FAIL %d 条' % len(FAILS))
        for f in FAILS:
            print('  - %s' % f)
        return 1
    print('OK 全绿：草案里的可算数与重算值逐项一致，且仍处于未冻结状态。')
    return 0


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--self-test', action='store_true', help='阴性对照：故意改坏一个印值，必须报红')
    sys.exit(main(self_test=ap.parse_args().self_test))
