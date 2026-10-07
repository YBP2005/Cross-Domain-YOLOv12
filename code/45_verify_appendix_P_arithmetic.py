# -*- coding: utf-8 -*-
r"""45_verify_appendix_P_arithmetic.py -- Appendix P / section 9 的 gamma 算术守卫（只读）。

判据（任一不成立即非零退出）
----------------------------
1. P.1 的 gamma(n) 每个印值 == (t(0.975,n-1) + t(0.80,n-1)) / sqrt(n)；
2. P.2 的 gamma(n)*sigma_hat 每个印值 == gamma(n) * 该节声明的中位 sigma_hat；
3. 由该表推出的「最小可判整数」与 P.2 所写一致；
4. 正文 section 9 的行内 gamma(3) / gamma(10) 与公式一致；
5. 校准行：n=10, sigma=0.3080 得 MDE=0.3064。

四个实现陷阱（本会话逐个踩过，全部固化在下面的代码里）
------------------------------------------------------
* **正则吃 LaTeX**：`\gamma` 里的 `\g` 在正则中是**组引用**，对含 `\gamma` 的模式调用 re
  会直接 `re.error: bad escape \g`。⇒ 定位表格只用 str 子串（`in` / `find`），
  re **只**用于数值部分。
* **表键在数据行上**：本附录是「列头 `| $n$ | 3 | ...`」+「数据行 `| $\gamma(n)$ | 3.0965 | ...`」
  两行制，`$\gamma(n)$` / `$\gamma(n)\hat\sigma$` 印在**数据行本身**上。第一版以为键在表头、
  去读命中行**之后**的行，读到的是下一段正文（0 个数值），长度对不上又静默 `return None`
  ⇒ P.1 / P.2 / P.2* 三条检查一起报「找不到表」，而表其实一直都在。⇒ 解析**命中的那一行**。
* **CRLF**：主稿与补材都是 CRLF；按 LF 切行会留行尾 CR，形如 `^|...|$` 的正则全部匹配不上
  ⇒ 一律先走 `norm()` 统一换行。
* **静默 None 是 bug 不是容错**：列数对不上必须抛 `TableParseError`，由调用方报红并**点名是哪张表**；
  「文档里没有这张表」和「这张表解析不了」必须给出不同的话。

sigma_hat 的坑：P.2 的原文是 `At the archive's **median** $\hat\sigma=0.2744$ pp:`，
"median" 与数学之间夹着 `**` 粗体标记，旧的固定字面量 `r'$\hat\sigma=0.2744'` 因此失配；
而且全文第一个 `\hat\sigma=` 是 P.1 的**校准值 0.3080**，也不能取第一个命中。
⇒ 以 `median` 为锚点，在其后窗口内找 `\hat\sigma=`，再解析紧随其后的第一个数。

用法：python scripts/45_verify_appendix_P_arithmetic.py [--self-test]
"""
import os
import re
import io
import sys
import math
import argparse

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from scipy.stats import t as T  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _cells as _C          # noqa: E402  ★ 布局无关的路径解析
# ★ 2026-10-07：向上查找 M3_draft（两种布局通用），不再写死层数
_M3D = _C.find_dir('M3_draft', HERE)
ROOT = os.path.dirname(_M3D)
MAIN = os.path.join(_M3D, 'P1_NewDraft_v1_20260927.md')
SUPP = os.path.join(_M3D, '00_SUPPLEMENTARY_v0.4.md')
ALPHA = 0.05
BETA = 0.20
TOL = 5e-4
FAILS = []

# ⚠ 下面这些含反斜杠的常量**只**用于 str 子串定位（in / find），绝不喂给 re：
#   正则会把 `\gamma` 的 `\g` 当组引用，直接 re.error。
HDR_GAMMA = r'$\gamma(n)$'
HDR_GSIG = r'$\gamma(n)\hat\sigma$'
KEY_SD = r'\hat\sigma='
KEY_G3 = r'\gamma(3) = '
KEY_G10 = r'\gamma(10) = '
KEY_SMALL = r'is the smallest integer at which a 0.30 pp effect'
# 数值专用正则：只匹配带小数点的数，绝不接触 LaTeX。
NUM_RE = re.compile(r'[0-9]+\.[0-9]+')


class TableParseError(Exception):
    """表格定位/解析失败。必须冒泡成 FAIL，绝不静默当成「文档里没有这张表」。"""
    pass


def gamma(n):
    return (float(T.ppf(1 - ALPHA / 2, n - 1)) + float(T.ppf(1 - BETA, n - 1))) / math.sqrt(n)


def mde(n, sd):
    return gamma(n) * sd


def check(cond, label, got=None, want=None):
    if cond:
        print('| OK | %s |' % label)
    else:
        print('| FAIL | %s | got=%s want=%s |' % (label, got, want))
        FAILS.append(label)


def norm(t):
    return t.replace('\r\n', '\n').replace('\r', '\n')


def find_table(text, header, n_vals, table_name):
    r"""按字面子串定位含 header 的**那一行**，直接从该行解析数值列，返回 [v1..vn]。

    * header 用 str 子串判断（不用 re，理由见模块 docstring 陷阱 1）；
    * 表键在数据行上，所以解析命中行本身（陷阱 2）；
    * 数值个数 != n_vals 时抛 TableParseError 并在消息里点名 table_name（陷阱 4），
      绝不 return None —— 那正是三条检查误报「找不到表」的根源。
    """
    for l in text.split(chr(10)):
        s = l.strip()
        if not s.startswith('|') or header not in s:   # ★ str 子串，不是 re
            continue
        vals = [float(x) for x in NUM_RE.findall(s)]
        if len(vals) != n_vals:
            raise TableParseError(
                '%s：含 %s 的行只解析出 %d 个数值，应为 %d 个（行内容：%s）'
                % (table_name, header, len(vals), n_vals, s))
        return vals
    raise TableParseError('%s：全文没有含 %s 的表格行' % (table_name, header))


def find_declared_sigma(text):
    r"""P.2 声明的「中位 sigma_hat」，找不到返回 None。

    锚点必须是 median（容忍 `**median**`），因为全文第一个 `\hat\sigma=` 是 P.1 的校准值
    0.3080，取第一个命中会静默取错数。定位用 str.find，re 只解析 `=` 之后的数字。
    """
    k = text.find(KEY_SD)
    while k >= 0:
        if 'median' in text[max(0, k - 40):k]:
            m = re.match(r'\s*([0-9]+(?:\.[0-9]+)?)', text[k + len(KEY_SD):])
            if m:
                return float(m.group(1))
        k = text.find(KEY_SD, k + 1)
    return None


def after_key(text, key):
    k = text.find(key)
    if k < 0:
        return None
    m = re.match(r'([0-9.]+)', text[k + len(key):])
    return float(m.group(1)) if m else None


def main(self_test=False):
    main_t = norm(io.open(MAIN, encoding='utf-8', newline='').read())
    supp_t = norm(io.open(SUPP, encoding='utf-8', newline='').read())

    # 1) P.1 gamma 表：7 列（n = 3,5,8,9,10,13,20）
    NS = [3, 5, 8, 9, 10, 13, 20]
    row1 = None
    try:
        row1 = dict(zip(NS, find_table(supp_t, HDR_GAMMA, len(NS), 'P.1 gamma(n) 表')))
    except TableParseError as e:
        check(False, 'P.1 找到 gamma(n) 表', str(e), '一行 n->值')
    else:
        check(len(row1) == len(NS), 'P.1 找到 gamma(n) 表', row1, '一行 n->值')
    if row1:
        for n, v in sorted(row1.items()):
            want = gamma(n)
            if self_test and n == 10:
                v = v + 0.5
            check(abs(v - want) < TOL, 'P.1 gamma(%d) == (t975+t80)/sqrt(n)' % n,
                  '%.4f' % v, '%.4f' % want)

    # 2) P.2 gamma*sigma 表：4 列（n = 8,9,10,11）
    sd = find_declared_sigma(supp_t)
    check(sd is not None, 'P.2 找到声明的中位 sigma_hat',
          '未找到「median ... \\hat\\sigma=<数>」', None)
    NS2 = [8, 9, 10, 11]
    row2 = None
    try:
        row2 = dict(zip(NS2, find_table(supp_t, HDR_GSIG, len(NS2), 'P.2 gamma(n)*sigma_hat 表')))
    except TableParseError as e:
        check(False, 'P.2 找到 gamma(n)*sigma_hat 表', str(e), '一行 n->值')
    else:
        check(len(row2) == len(NS2), 'P.2 找到 gamma(n)*sigma_hat 表', row2, '一行 n->值')
    if sd is not None and row2:
        for n, v in sorted(row2.items()):
            want = mde(n, sd)
            if self_test and n == 9:
                v = v + 0.05
            check(abs(v - want) < 2e-3, 'P.2 gamma(%d)*sigma_hat == gamma(%d)*%.4f' % (n, n, sd),
                  '%.4f' % v, '%.4f' % want)
        smallest = None
        for n in range(3, 60):
            if mde(n, sd) <= 0.30:
                smallest = n
                break
        claimed = None
        k = supp_t.find(KEY_SMALL)
        if k >= 0:
            seg = supp_t[max(0, k - 40):k]
            m = re.findall(r'n=(\d+)', seg)
            if m:
                claimed = int(m[-1])
        check(claimed is not None and claimed == smallest,
              'P.2 的「最小可判整数」与表一致', claimed, smallest)

    # 3) 正文 section 9 的行内 gamma
    v3 = after_key(main_t, KEY_G3)
    v10 = after_key(main_t, KEY_G10)
    check(v3 is not None and v10 is not None, 'section 9 找到行内 gamma(3)/gamma(10)', (v3, v10))
    for n, v in ((3, v3), (10, v10)):
        if v is None:
            continue
        if self_test and n == 3:
            v = v + 0.5
        check(abs(v - gamma(n)) < 5e-3, 'section 9 gamma(%d) 与公式一致' % n, v, '%.4f' % gamma(n))

    # 4) 校准行
    check(abs(mde(10, 0.3080) - 0.3064) < TOL, '校准 n=10, sigma=0.3080 得 MDE=0.3064',
          '%.4f' % mde(10, 0.3080), '0.3064')

    print('')
    if FAILS:
        print('FAIL %d 条：' % len(FAILS))
        for f in FAILS:
            print('  - %s' % f)
        return 1
    print('OK 全绿：Appendix P 与 section 9 的 gamma 算术与公式逐值一致，最小可判整数一致。')
    return 0


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--self-test', action='store_true', help='阴性对照：故意改坏一个印值，必须报红')
    sys.exit(main(self_test=ap.parse_args().self_test))
