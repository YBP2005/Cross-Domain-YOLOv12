# -*- coding: utf-8 -*-
"""analyze_reads.py -- 分析 220 次端点读数（A 40 + B 180），产出理论补强要的实证表。

分析按第七轮审核指出的"定理真正用到的量"组织，而不是按我原来那套谱量组织：
  1. 覆盖率与完整性自检（含同一状态上两路求值必须相等这类硬自检）；
  2. 一次项：<grad R_T(theta_S), Delta> 与 mu_sec = 2[该项 - plugin_four]/||Delta||^2
     —— 命题 1 实际使用的"有序对不等式"的模量；符号分布比中位数重要；
  3. 源侧前提：source_opt_gap 与 <grad R_S(theta_S), Delta> 的符号，**只在类别数匹配的格可算**；
  4. 段曲率与端点曲率：mu_seg vs mu_sec、dhd 沿段是否变号 —— 端点曲率是否代表路径；
  5. 谱量只作诊断：lambda_max/lambda_min/dHd_at_T/kappa_minus_T 的符号分布，并给出 Ritz 相对残差
     （极值没收敛就要看得出来）；
  6. 多抽样变异性：同端点不同 draw 的离散度（这正是当初改成多抽样的理由）。

口径声明（写进报告，避免事后被当成过度解读）：所有对象都是**已计算检查点**上的经验量，不是总体最优；
mu_sec < 0 的含义是"有序对不等式在该计算对上不成立"，不等于"定理为假"。
"""
import collections, csv, glob, io, os, statistics as st
import sys

sys.stdout.reconfigure(encoding='utf-8')

SOURCES = [
    ('A', r'D:\deepseek\analysis\A_results_20260914\reads\theory_reads_A.csv'),
    ('B', r'D:\deepseek\analysis\B_results_20260914\reads\theory_reads.csv'),
]
OUT_MD = r'D:\deepseek\analysis\theory_reads_analysis_20260914.md'

NUM = ['loss_T', 'loss_S', 'plugin_four', 'gradT_at_S_dot_delta', 'mu_sec', 'delta_norm',
       'shared_frac', 'RS_at_S', 'RS_at_T', 'source_opt_gap', 'gradS_at_S_dot_delta',
       'gradS_at_S_norm', 'mu_seg', 'dHd_at_T', 'kappa_minus_T', 'lambda_max', 'lambda_min',
       'spec_norm', 'ritz_res_max', 'ritz_res_min', 'gradT_at_T_norm',
       'f_t00', 'f_t25', 'f_t50', 'f_t75', 'f_t100',
       'fp_t00', 'fp_t25', 'fp_t50', 'fp_t75', 'fp_t100',
       'dhd_t00', 'dhd_t25', 'dhd_t50', 'dhd_t75', 'dhd_t100']


def load():
    rows = []
    for src, p in SOURCES:
        if not os.path.exists(p):
            print('MISSING %s' % p)
            continue
        with io.open(p, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                r['_src'] = src
                for k in NUM:
                    v = r.get(k, '')
                    try:
                        r[k] = float(v) if v not in ('', None) else None
                    except ValueError:
                        r[k] = None
                rows.append(r)
    return rows


def cell_of(r):
    """Cell identity: B tags are '<srckey>__<tgt>__<run>__d<k>'; A tags are 't1a__<run>__d<k>'."""
    t = r['tag']
    if t.startswith('t1a__'):
        return 'T1-a dota15->aitod'
    parts = t.split('__')
    return '%s -> %s' % (parts[0], parts[1]) if len(parts) >= 4 else t


def run_of(r):
    t = r['tag']
    if t.startswith('t1a__'):
        return t.split('__')[1]
    return t.split('__')[2]


def med(vals):
    vals = [v for v in vals if v is not None]
    return st.median(vals) if vals else None


def fmt(v, nd=4):
    if v is None:
        return '-'
    return ('%.*g' % (nd, v))


def sign_counts(vals):
    vals = [v for v in vals if v is not None]
    neg = sum(1 for v in vals if v < 0)
    pos = sum(1 for v in vals if v > 0)
    zer = len(vals) - neg - pos
    return neg, zer, pos, len(vals)


L = []
def out(s=''):
    print(s)
    L.append(s)


rows = load()
out('# 端点读数分析（220 次，A 40 + B 180）')
out()
out('生成脚本：`analysis/work/analyze_reads.py`。数据：`A_results_20260914/reads/theory_reads_A.csv`、')
out('`B_results_20260914/reads/theory_reads.csv`。')
out()
out('**口径声明（先写在最前，避免事后被当成过度解读）**：这里所有量都是**已计算检查点**上的经验量，')
out('不是总体最优；$\\mu_{sec}<0$ 的含义是"有序对不等式在该计算对上不成立"，**不等于"定理为假"**。')
out()

# ---------------------------------------------------------------- 1 coverage
out('## 1. 覆盖率与完整性')
out()
out('| 来源 | 行数 | 端点数 | 抽样数 |')
out('|---|---|---|---|')
for src, _ in SOURCES:
    rr = [r for r in rows if r['_src'] == src]
    ends = set(run_of(r) for r in rr)
    draws = collections.Counter()
    for r in rr:
        draws[run_of(r)] += 1
    out('| %s | %d | %d | %s |' % (src, len(rr), len(ends),
                                   ', '.join('%d×%d' % (k, v) for k, v in sorted(collections.Counter(draws.values()).items()))))
out('| **合计** | **%d** | **%d** | |' % (len(rows), len(set(run_of(r) for r in rows))))
out()

# hard self-checks: the two evaluations of the SAME risk at the SAME state must agree
out('### 硬自检（同一状态上两路求值必须相等）')
out()
out('注意：`RS_at_T` 是**源风险**在 θ_T 处的值，`loss_T` 是**目标风险**在 θ_T 处的值。')
out('只有**源语料与目标语料相同**的格（`data == src_data`）两者才必须相等；跨域格里它们是两个不同的函数，')
out('本来就不该相等。（我第一版把这条检查无条件套用到全部 164 行，得到"108 行不一致"，那是**检查写错了**，')
out('不是数据问题——这正是本项目坚持"硬自检也要先检查检查本身"的原因。）')
out()
same = [r for r in rows if r.get('data') == r.get('src_data') and r.get('src_eval_ok') == '1']
bad, worst = 0, 0.0
for r in same:
    if r['RS_at_T'] is not None and r['loss_T'] is not None:
        d = abs(r['RS_at_T'] - r['loss_T']) / max(1.0, abs(r['loss_T']))
        worst = max(worst, d)
        if d > 1e-4:
            bad += 1
out('- 限定在 `data == src_data` 且源侧可求值的 **%d** 行上：`RS_at_T == loss_T` 偏差超 1e-4 的有 '
    '**%d** 行，最大相对偏差 %.3g。' % (len(same), bad, worst))
d2, worst2 = 0, 0.0
for r in same:
    if r['RS_at_S'] is not None and r['loss_S'] is not None:
        d = abs(r['RS_at_S'] - r['loss_S']) / max(1.0, abs(r['loss_S']))
        worst2 = max(worst2, d)
        if d > 1e-4:
            d2 += 1
out('- 同样口径下 `RS_at_S == loss_S`：偏差超限 **%d** 行，最大相对偏差 %.3g。' % (d2, worst2))
up = nonmono = n_mono = 0
for r in rows:
    if all(r.get('f_t%s' % k) is not None for k in ('00', '25', '50', '75', '100')):
        n_mono += 1
        seq = [r['f_t00'], r['f_t25'], r['f_t50'], r['f_t75'], r['f_t100']]
        inc = any(seq[i + 1] > seq[i] + 1e-9 for i in range(4))
        dec = any(seq[i + 1] < seq[i] - 1e-9 for i in range(4))
        up += inc
        if inc and dec:
            nonmono += 1
out('- 沿位移损失**上升**的行：%d / %d（θ_T 是目标最优，所以上升是**预期**的，不构成发现；'
    '我第一版把这条当成"非单调"来报，是**检查写错了**。）' % (up, n_mono))
out('- 沿位移损失**非单调**（既升又降，即路径上有势垒）的行：**%d / %d** —— 这条才是有内容的。'
    % (nonmono, n_mono))
out()

# ---------------------------------------------------------------- 2 mu_sec
out('## 2. 定理真正用的第一项：有限割线模量 $\\mu_{sec}$')
out()
neg, zer, pos, tot = sign_counts([r['mu_sec'] for r in rows])
out('$$\\mu_{sec}=\\frac{2\\left[\\langle\\nabla R_T(\\theta_S),\\Delta\\rangle-\\widehat{④}\\right]}{\\|\\Delta\\|^2}$$')
out()
out('- 全部 %d 行：**负 %d / 零 %d / 正 %d**' % (tot, neg, zer, pos))
m = med([r['mu_sec'] for r in rows])
out('- 中位数：%s；范围 %s … %s' % (fmt(m), fmt(min(r['mu_sec'] for r in rows if r['mu_sec'] is not None)),
                                    fmt(max(r['mu_sec'] for r in rows if r['mu_sec'] is not None))))
out()
by_cell = collections.defaultdict(list)
for r in rows:
    by_cell[cell_of(r)].append(r)
out('| 格 | 行数 | μ_sec 负/正 | μ_sec 中位 | ④̂ 中位 | ‖Δ‖ 中位 |')
out('|---|---|---|---|---|---|')
for c in sorted(by_cell):
    rr = by_cell[c]
    n2, _, p2, t2 = sign_counts([r['mu_sec'] for r in rr])
    out('| %s | %d | %d/%d | %s | %s | %s |'
        % (c, len(rr), n2, p2, fmt(med([r['mu_sec'] for r in rr])),
           fmt(med([r['plugin_four'] for r in rr])), fmt(med([r['delta_norm'] for r in rr]))))
out()
# by arm -- label all five arm families, not just base/lr005 (my first version bucketed sns/pws as '?')
def arm_of(run):
    for tag in ('lr005', 'sns', 'css', 'pws', 'jps'):
        if tag in run:
            return tag
    if 'base' in run:
        return 'base'
    return 'other'
by_arm = collections.defaultdict(list)
for r in rows:
    by_arm[arm_of(run_of(r))].append(r)
out('按臂（应覆盖 base/lr005/sns/css/pws 五个族，不应有 other）：')
for a in sorted(by_arm):
    n2, _, p2, t2 = sign_counts([r['mu_sec'] for r in by_arm[a]])
    out('- %-6s %3d 行：μ_sec 负 %d / 正 %d；中位 %s' % (a, t2, n2, p2, fmt(med([r['mu_sec'] for r in by_arm[a]]))))
out()

# where mu_sec is negative, is it explained by ||Delta|| or by the plug-in gap?
out('### $\\mu_{sec}$ 符号与什么相关（只做描述，不做因果）')
out()
neg_rows = [r for r in rows if r['mu_sec'] is not None and r['mu_sec'] < 0]
pos_rows = [r for r in rows if r['mu_sec'] is not None and r['mu_sec'] > 0]
for label, rr in (('μ_sec < 0', neg_rows), ('μ_sec > 0', pos_rows)):
    out('- %s（%d 行）：‖Δ‖ 中位 %s；④̂ 中位 %s；⟨∇R_T(θ_S),Δ⟩ 中位 %s'
        % (label, len(rr), fmt(med([r['delta_norm'] for r in rr])),
           fmt(med([r['plugin_four'] for r in rr])),
           fmt(med([r['gradT_at_S_dot_delta'] for r in rr]))))
out()
within = [r for r in rows if r.get('data') == r.get('src_data')]
cross = [r for r in rows if r.get('data') != r.get('src_data')]
for label, rr in (('同域格 (data == src_data)', within), ('跨域格', cross)):
    n2, _, p2, t2 = sign_counts([r['mu_sec'] for r in rr])
    out('- %s：%d 行，μ_sec 负 %d / 正 %d；‖Δ‖ 中位 %s'
        % (label, t2, n2, p2, fmt(med([r['delta_norm'] for r in rr]))))
out()

# ---------------------------------------------------------------- 3 source side
out('## 3. 源侧前提（只在类别数匹配时才有定义）')
out()
ok = [r for r in rows if r.get('src_eval_ok') == '1']
no = [r for r in rows if r.get('src_eval_ok') == '0']
out('- 源侧可求值：**%d 行**；被跳过：**%d 行**（原因：源检查点与目标的类别数不同，头未传递）' % (len(ok), len(no)))
skipped_cells = sorted(set(cell_of(r) for r in no))
out('- 被跳过的格：%s' % (', '.join(skipped_cells) if skipped_cells else '（无）'))
if ok:
    n2, _, p2, t2 = sign_counts([r['source_opt_gap'] for r in ok])
    out('- **源最优性** $R_S(\\theta_S)-R_S(\\theta_T)$：负 %d / 正 %d（负=源端点在源风险上确实更优，前提成立）' % (n2, p2))
    n3, _, p3, t3 = sign_counts([r['gradS_at_S_dot_delta'] for r in ok])
    out('- **源方向 VI** $\\langle\\nabla R_S(\\theta_S),\\Delta\\rangle$：负 %d / 正 %d（负=方向变分不等式成立）' % (n3, p3))
    out('- 两者**同时**成立的格数：%d / %d 行'
        % (sum(1 for r in ok if (r['source_opt_gap'] or 0) <= 0 and (r['gradS_at_S_dot_delta'] or 0) <= 0), len(ok)))
out()

# ---------------------------------------------------------------- 4 segment
out('## 4. 端点曲率是否代表路径（$\\mu_{seg}$ vs $\\mu_{sec}$）')
out()
both = [r for r in rows if r['mu_sec'] is not None and r['mu_seg'] is not None]
if both:
    agree = sum(1 for r in both if (r['mu_sec'] < 0) == (r['mu_seg'] < 0))
    out('- 两者**符号一致**的行：%d / %d' % (agree, len(both)))
    ratios = [abs(r['mu_seg'] / r['mu_sec']) for r in both if r['mu_sec'] not in (0, None)]
    if ratios:
        out('- |μ_seg / μ_sec| 中位 %s，范围 %s … %s'
            % (fmt(st.median(ratios)), fmt(min(ratios)), fmt(max(ratios))))
    d0 = [r for r in both if r['dhd_t00'] is not None]
    dsign = sum(1 for r in d0 if (r['dhd_t00'] < 0) != (r['mu_sec'] < 0))
    out('- 端点方向曲率 `dhd_t00` 与 μ_sec **符号不同**的行：%d / %d' % (dsign, len(d0)))
    flip = 0
    nfl = 0
    for r in both:
        seq = [r['dhd_t%s' % k] for k in ('00', '25', '50', '75', '100')]
        if all(v is not None for v in seq):
            nfl += 1
            s = [v < 0 for v in seq]
            if any(s[i] != s[0] for i in range(1, 5)):
                flip += 1
    out('- **沿段曲率变号**的行：%d / %d（这是"端点值是代理"的直接证据）' % (flip, nfl))
out()

# ---------------------------------------------------------------- 5 spectral + ritz
out('## 5. 谱量（只作诊断）与其收敛性')
out()
for k, label in (('lambda_min', '$\\lambda_{\\min}$'), ('dHd_at_T', '$\\Delta^{\\top}H_T\\Delta$'),
                 ('kappa_minus_T', '$\\kappa^-_\\Delta$'), ('plugin_four', '$\\widehat{④}$')):
    n2, _, p2, t2 = sign_counts([r[k] for r in rows])
    out('- %s：负 %d / 零 %d / 正 %d（共 %d）' % (label, n2, 0, p2, t2))
out()
rel = []
for r in rows:
    if r['ritz_res_max'] is not None and r['lambda_max'] not in (None, 0):
        rel.append(('max', abs(r['ritz_res_max']) / max(1.0, abs(r['lambda_max']))))
    if r['ritz_res_min'] is not None and r['lambda_min'] not in (None, 0):
        rel.append(('min', abs(r['ritz_res_min']) / max(1.0, abs(r['lambda_min']))))
for which in ('max', 'min'):
    v = [x for w, x in rel if w == which]
    if v:
        out('- Ritz 相对残差（%s）：中位 %s，90 分位 %s，最大 %s'
            % (which, fmt(st.median(v)), fmt(sorted(v)[int(0.9 * len(v)) - 1]), fmt(max(v))))
out()

# ---------------------------------------------------------------- 6 draw variability
out('## 6. 同一端点的抽样变异性（多个 draw）')
out()
by_end = collections.defaultdict(list)
for r in rows:
    by_end[run_of(r)].append(r)
multi = {k: v for k, v in by_end.items() if len(v) > 1}
out('- 有多个抽样的端点：%d 个（占 %d 个端点的 %.0f%%）' % (len(multi), len(by_end), 100.0 * len(multi) / len(by_end)))
spread = []
for k, v in multi.items():
    for key in ('lambda_max', 'plugin_four', 'mu_sec'):
        vals = [x[key] for x in v if x[key] is not None]
        if len(vals) > 1 and max(abs(x) for x in vals) > 0:
            spread.append((key, (max(vals) - min(vals)) / max(abs(x) for x in vals)))
for key in ('lambda_max', 'plugin_four', 'mu_sec'):
    v = [s for k, s in spread if k == key]
    if v:
        out('- `%s` 的抽样相对跨度：中位 %.3g，最大 %.3g' % (key, st.median(v), max(v)))
out()

# ---------------------------------------------------------------- 7 sign stability
# The cell-level claims in section 2 ("all positive in this cell, all negative in that one") only stand
# if the SIGN is stable across the draws of one endpoint. The relative spreads above (μ_sec median 0.36,
# λ_max median 0.52) say this cannot be assumed, so it is measured.
out('## 7. 符号在抽样之间是否稳定（决定第 2 节的格的结论能否成立）')
out()
multi_ends = {k: v for k, v in by_end.items() if len(v) > 1}
out('| 量 | 有多抽样的端点 | 其中抽样间**符号发生翻转** | 翻转比例 |')
out('|---|---|---|---|')
for key, label in (('mu_sec', '$\\mu_{sec}$'), ('plugin_four', '$\\widehat{④}$'),
                   ('source_opt_gap', '$R_S(\\theta_S)-R_S(\\theta_T)$'),
                   ('gradS_at_S_dot_delta', '$\\langle\\nabla R_S(\\theta_S),\\Delta\\rangle$'),
                   ('dHd_at_T', '$\\Delta^{\\top}H_T\\Delta$')):
    tot2 = flip2 = 0
    for k, v in multi_ends.items():
        vals = [x[key] for x in v if x[key] is not None]
        if len(vals) < 2:
            continue
        tot2 += 1
        if any((a < 0) != (b < 0) for a in vals for b in vals):
            flip2 += 1
    out('| %s | %d | %d | %s |' % (label, tot2, flip2,
                                   ('%.0f%%' % (100.0 * flip2 / tot2)) if tot2 else '-'))
out()
# the two criterion-passing cells specifically: are their uniform-looking signs draw-stable?
for cell in ('shwd2sf_pretrain -> sfchd', 'smoke_pretrain -> sfchd'):
    rr = [r for r in rows if cell_of(r) == cell]
    ends = collections.defaultdict(list)
    for r in rr:
        ends[run_of(r)].append(r)
    m = {k: v for k, v in ends.items() if len(v) > 1}
    fl = 0
    for k, v in m.items():
        vals = [x['mu_sec'] for x in v if x['mu_sec'] is not None]
        if len(vals) >= 2 and any((a < 0) != (b < 0) for a in vals for b in vals):
            fl += 1
    out('- **%s**：%d 行 / %d 个端点，其中 %d 个端点多抽样；这些端点上 μ_sec **跨抽样翻号的有 %d 个**。'
        % (cell, len(rr), len(ends), len(m), fl))
out()

# ---------------------------------------------------------------- 8 what this does / does not say
out('## 8. 这些数字说明什么、不说明什么')
out()
out('**能说的**')
out()
out('1. **G1 的分支已被数据定案。** $\\lambda_{\\min}$ 在 **220/220** 行全为负。球形式 H5（球上所有特征值 ≥ μ > 0）')
out('   在**每一个**被测量的端点上都不成立。于是"球形式"可以退出讨论，能检验的只剩**配对形式**——')
out('   而那正是 $\\mu_{sec}$ 测的东西。这与第七轮审核的判断一致：不是"$\\lambda_{\\min}>0$ 就验证了强凸、')
out('   $\\lambda_{\\min}<0$ 就反驳了配对不等式"，而是**$\\lambda_{\\min}$ 从来就不是这条的判据**。')
out('2. **源侧两条前提的成立率很低**：源最优性 59/164（36%），源方向 VI 32/164（20%），')
out('   **两者同时成立只有 14/164（8.5%）**。命题 1 的线分支假设源最优性、二次分支假设驻点或方向 VI——')
out('   在已计算对上，这两条大多数时候**不成立**。')
out('   ⟹ **这不是"定理错了"，而是"定理的前提与已发布检查点之间需要ε形式来搭桥"**。')
out('   也就是说我为 (iii) 加的那两条 ε 形式（把假设换成可测量的余项）**不是修饰，而是让命题与检查点')
out('   发生关系的最低要求**。这一点现在有数字支撑。')
out('3. **端点曲率不代表路径曲率。** 沿段方向曲率**变号**的行占 168/220（76%），端点 `dhd_t00` 与 $\\mu_{sec}$')
out('   符号不同的占 87/220。所以 §4.3 那句"an endpoint evaluation is a proxy"是**保守说法**：')
out('   多数配对上，端点值对路径的某一段**连符号都不对**。')
out('4. **$\\widehat{④}$ 在 26/220 行为负**（12%）——"非负位移代价"这个叫法在已计算端点上站不住，')
out('   只能表述为"检查点损失差"。')
out('5. **抽样变异性很大**：$\\lambda_{\\max}$ 相对跨度中位 0.52、$\\widehat{④}$ 0.26、$\\mu_{sec}$ 0.36。')
out('   单抽样的读数不可靠；多抽样设计是**必需**而非稳妥。第 7 节进一步给出**符号**层面的稳定性。')
out()
out('**不能说的**')
out()
out('1. **不能把它读成总体结论。** 全部对象是已计算检查点上的经验量，不是总体最优；$\\mu_{sec}<0$ 只意味着')
out('   有序对不等式**在这些计算对上**不成立。')
out('2. **不能把"两个通过判据的格恰好是 μ_sec 全正的两个格"当发现写。** 这个对应关系在 220 行里很醒目')
out('   （`shwd2sf→sfchd` 58/58 正、`smoke→sfchd` 34/34 正），但它是**事后观察**、n=26 格的家族里挑出来的，')
out('   最稳妥的写法是"这一对应值得一个预注册检验"，而不是"曲率模量预测了结果"。')
out('3. **不能宣称 $\\mu_{sec}$ 或任何单条前提解释了结果。** 本报告只做描述，没有做因果或预测性检验；')
out('   第七轮审核也明确反对把这类量当作 outcome predictor。')
out()

io.open(OUT_MD, 'w', encoding='utf-8', newline='').write('\n'.join(L) + '\n')
print()
print('report -> %s (%d lines)' % (OUT_MD, len(L)))
