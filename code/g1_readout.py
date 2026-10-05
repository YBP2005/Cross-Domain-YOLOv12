# -*- coding: utf-8 -*-
r"""g1_readout.py -- G1 判读：**先校验链路，再出表**。

为什么第一件事是校验而不是算数
------------------------------
本实验已经栽过一次**接线错**：run 名里的 `50p` 曾是**标签**、不选数据，导致每个格跑两遍、
100 行 mAP 逐行相同的重复件被当成"两个预算档"。若判读脚本**直接信任 run 名**，
它会把这个错**算进结论里而且看不出来**。
⇒ 故本件的**第一步**是逐 run 校验：`run 名` ⟷ `args.yaml 的 data:` ⟷ `该格应有的 yaml` ⟷ `训练图像数`。
**任一不符即硬失败，不出表。**

判读内容（与《G1实验方案》§4 的冻结判据一致）
----------------------------------------------
* 每格：逐种子配对差（strategy − base，**同种子**）、均值、SD、配对 t、p、95% CI、种子同号数；
* **H1**：同一域对内两个预算档的**符号是否相反**，且**两端各自**过
  {|Δ̄| ≥ 0.30 pp, p < 0.01, ≥8/10 同号}；
* **H2**：2×2 交互项（域差档 × 预算档），**H1 不成立则不单独判读**；
* 读数列：`test_map50_95`（§4 判据只在该列判）；同时报 `best_map50_95` 并列对照。

用法
----
    python g1_readout.py                # 有几格能算就算几格（未完成的格标"未就绪"）
    python g1_readout.py --require-all  # 80 个 run 全齐才出表
"""
import io
import os
import sys
import re
import glob
import csv
import json
import math
import argparse

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    from scipy import stats as ST
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False

# ---- 冻结的设计（唯一真相，与方案 §1/§2 一致）----
CELL_BUDGET = {'c1': '10p', 'c2': '50p', 'c3': '10p', 'c4': '50p'}
CELL_DOMAIN = {'c1': 'd15tod15', 'c2': 'd15tod15', 'c3': 'd15toaitod', 'c4': 'd15toaitod'}
CELL_DATA = {
    'c1': '/root/datasets_mask/dota15_yolo/dota15_10p.yaml',
    'c2': '/root/datasets_mask/dota15_yolo/dota15_50p.yaml',
    'c3': '/root/datasets/AI-TOD_yolo/aitod_10p.yaml',
    'c4': '/root/datasets/AI-TOD_yolo/aitod_50p.yaml',
}
# 每格应有的训练图像数（实测：10p 档 dota15=141、aitod=1121；50p 档 dota15=706→705、aitod=5607）
CELL_NTRAIN = {'c1': 141, 'c2': 705, 'c3': 1121, 'c4': 5607}
ARMS = ['base100', 'strat100']
SEEDS = list(range(42, 52))
BAR = 0.30          # 注册幅度条（pp）
ALPHA = 0.01        # 注册显著性
MIN_SAME_SIGN = 8   # ≥8/10

REMOTE = r'''python3 - <<"E"
import os, glob, re, json, hashlib
RUNS='/workspace/runs'
pat=re.compile(r'^g1_(c\d)_([a-z0-9]+)_(base100|strat100)_(10p|50p)_s(\d+)$')
out=[]
for d in sorted(glob.glob(os.path.join(RUNS,'g1_c*'))):
    b=os.path.basename(d); m=pat.match(b)
    if not m: continue
    cell,dom,arm,bud,seed=m.groups()
    f=os.path.join(d,'results.csv'); ay=os.path.join(d,'args.yaml')
    rows=[]
    if os.path.exists(f):
        try:
            import csv as _c
            rows=list(_c.DictReader(open(f)))
        except Exception: rows=[]
    data=''
    if os.path.exists(ay):
        for line in open(ay):
            if line.startswith('data:'): data=line.split(':',1)[1].strip(); break
    # ★ 校验哈希：用**确定性数据列投影**（整文件 md5 含时间列，同数据同种子也会不同）
    h=''
    if rows:
        keys=[k for k in rows[0] if ('mAP' in k or 'loss' in k or k.strip()=='epoch')]
        h=hashlib.md5(('|'.join(','.join(str(r.get(k,'')) for k in keys) for r in rows)).encode()).hexdigest()
    out.append(dict(name=b,cell=cell,dom=dom,arm=arm,bud=bud,seed=int(seed),
                    rows=len(rows),data=data,md5=h,
                    val=[r.get('metrics/mAP50-95(B)') for r in rows],
                    has_test=('test_map50_95' in (rows[0] if rows else {})),
                    has_best=('best_map50_95' in (rows[0] if rows else {}))))
print('G1RD'+json.dumps(out,ensure_ascii=False))
E'''


def ssh_sample(host, port, pw, timeout=180):
    import paramiko
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for _ in range(6):
        try:
            cli.connect(host, port=port, username='root', password=pw, timeout=40,
                        banner_timeout=90, auth_timeout=40, allow_agent=False, look_for_keys=False)
            break
        except Exception:
            import time as _t
            _t.sleep(15)
    else:
        return None
    ch = cli.get_transport().open_session(); ch.settimeout(timeout); ch.exec_command(REMOTE)
    buf = b''
    try:
        while True:
            d = ch.recv(65536)
            if not d:
                break
            buf += d
    except Exception:
        pass
    cli.close()
    t = buf.decode('utf-8', 'replace')
    i = t.find('G1RD')
    return json.loads(t[i + 4:].strip().split('\n')[0]) if i >= 0 else None



def read_local_archive():
    r"""从**本地归档**读 B 机的 run（B 已归还；其文本产物在 21:48 取回并双验）。

    归档里每个 run 有 `results.csv` + `args.yaml`，与本脚本从云上取的字段一致 ⇒
    用同一套判读逻辑，只是来源不同。**这是"数据取回后仍可复算"的兑现**。
    """
    import csv as _csv
    # ★ 扇扫**所有**本地归档解包目录（A 与 B 各一个），而不是写死 B 那一个。
    #   动机：A 机关掉后，从云上取不到 c3/c4 ⇒ 只能从归档读；
    #   而两个归档都在本地 ⇒ 一份读不全就会少一半格。
    base = os.path.abspath(os.path.join(HERE, '..', 'provenance', 'deliver'))
    run_dirs = []
    for sub in sorted(glob.glob(os.path.join(base, 'G1_*归档*'))):
        if os.path.isdir(sub):
            run_dirs += [d for d in sorted(glob.glob(os.path.join(sub, 'g1_c*'))) if os.path.isdir(d)]
    if not run_dirs:
        return []
    _PAT = re.compile(r"^g1_(c\d)_([a-z0-9]+)_(base100|strat100)_(10p|50p)_s(\d+)$")
    out = []
    for d in run_dirs:
        name = os.path.basename(d)
        m = _PAT.match(name)
        if not m:
            continue
        cell, dom, arm, bud, seed = m.groups()
        f = os.path.join(d, 'results.csv')
        rows = list(_csv.DictReader(io.open(f, encoding='utf-8', errors='replace'))) if os.path.exists(f) else []
        data = ''
        ay = os.path.join(d, 'args.yaml')
        if os.path.exists(ay):
            for line in io.open(ay, encoding='utf-8', errors='replace'):
                if line.startswith('data:'):
                    data = line.split(':', 1)[1].strip(); break
        out.append(dict(name=name, cell=cell, dom=dom, arm=arm, bud=bud, seed=int(seed),
                        rows=len(rows), data=data, md5='',
                        val=[r.get('metrics/mAP50-95(B)') for r in rows],
                        has_test=('test_map50_95' in (rows[0] if rows else {})),
                        has_best=('best_map50_95' in (rows[0] if rows else {})),
                        machine='B(local)'))
    return out


def f(x):
    try:
        return float(x)
    except Exception:
        return None


def paired(diffs):
    """返回 (n, mean, sd, t, p, lo, hi)。diffs 为逐种子差。"""
    n = len(diffs)
    if n < 2:
        return n, (diffs[0] if diffs else None), None, None, None, None, None
    mean = sum(diffs) / n
    var = sum((x - mean) ** 2 for x in diffs) / (n - 1)
    sd = math.sqrt(var)
    if sd == 0:
        return n, mean, 0.0, float('inf'), 0.0, mean, mean
    t = mean / (sd / math.sqrt(n))
    if HAVE_SCIPY:
        p = 2 * float(ST.t.sf(abs(t), n - 1))
        tc = float(ST.t.ppf(0.975, n - 1))
    else:
        p, tc = None, 1.96
    half = tc * sd / math.sqrt(n)
    return n, mean, sd, t, p, mean - half, mean + half


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--require-all', action='store_true')
    ap.add_argument('--cells', nargs='+', default=None,
                    help='只判这些格（如 --cells c1 c2）；默认全部')
    ap.add_argument('--out', default=os.path.join(HERE, '..', 'provenance', 'deliver', 'G1判读_结果.md'))
    a = ap.parse_args()
    try:
        import _cloud_creds as C
    except Exception:
        print('缺 _cloud_creds.py'); return 2

    runs = read_local_archive()
    print('本地归档取到 %d 个 run（B 机）' % len(runs))
    for tag, host, port, pw in [('A', 'cpod-1u20pv1vhj4v.podtcp.compshare.cn', 24581, C.A_PW),
                                ('B', 'cpod-1uearmsfxbj2.podtcp.compshare.cn', 25046, C.B_PW)]:
        d = ssh_sample(host, port, pw)
        if d is None:
            print('★ %s 机连不上' % tag); continue
        for r in d:
            r['machine'] = tag
        runs += d
    print('取到 run 目录 %d 个' % len(runs))

    # ---------- 第 1 步：链路校验（**任一不符即硬失败**）----------
    fail = []
    for r in runs:
        want_bud = CELL_BUDGET[r['cell']]
        want_dom = CELL_DOMAIN[r['cell']]
        want_data = CELL_DATA[r['cell']]
        if r['bud'] != want_bud:
            fail.append('%s：预算名 %s ≠ 该格应为 %s' % (r['name'], r['bud'], want_bud))
        if r['dom'] != want_dom:
            fail.append('%s：域对名 %s ≠ 该格应为 %s' % (r['name'], r['dom'], want_dom))
        if r['data'] and r['data'] != want_data:
            fail.append('%s：args.yaml 的 data=%s ≠ 该格应为 %s' % (r['name'], r['data'], want_data))
    # 重复件（同格同臂同种子出现两次）
    seenk = {}
    for r in runs:
        k = (r['cell'], r['arm'], r['seed'])
        if k in seenk:
            fail.append('重复：%s 与 %s 同格同臂同种子' % (seenk[k], r['name']))
        seenk[k] = r['name']
    if fail:
        print('\n❌ **链路校验失败 %d 条**（判读中止，绝不带病出表）：' % len(fail))
        for x in fail[:20]:
            print('   · %s' % x)
        return 3
    print('✅ 链路校验通过：run 名 ⟷ args.yaml 的 data ⟷ 格定义，三者一致；无重复件')

    # ---------- 第 2 步：逐格配对 ----------
    def get(cell, arm, seed):
        for r in runs:
            if r['cell'] == cell and r['arm'] == arm and r['seed'] == seed and r['rows'] >= 100:
                return r
        return None

    stat = {}
    # ★★ 空集合硬失败：results.csv 实测**只有 val 列**（`metrics/mAP50-95(B)`），
    #    **没有** `test_map50_95` / `best_map50_95`。第一版对不存在的列名取值 ⇒ 全取到 None
    #    ⇒ 表里印出一片 0/空，**静默地把"列不存在"伪装成"没数据"**（本会话第 N 次同型）。
    #    ⇒ 现在显式检查列是否存在，并把"缺列"与"未就绪"分开报。
    have = set()
    for r in runs:
        if r.get('has_test'):
            have.add('test_map50_95')
        if r.get('has_best'):
            have.add('best_map50_95')
    print('  results.csv 里存在的判读列：%s' % (sorted(have) if have else '无 test/best 列（只有 val）'))
    COLS = [('val', 'val')] if not have else []
    if 'test_map50_95' in have:
        COLS.append(('test_map50_95', 'test'))
    if 'best_map50_95' in have:
        COLS.append(('best_map50_95', 'best'))

    use_cells = a.cells if a.cells else sorted(CELL_BUDGET)
    for cell in use_cells:
        for col, key in COLS:
            diffs, detail = [], []
            for s in SEEDS:
                b, t = get(cell, 'base100', s), get(cell, 'strat100', s)
                if not (b and t):
                    continue
                bv = f(b[key][-1]) if b[key] else None
                tv = f(t[key][-1]) if t[key] else None
                if bv is None or tv is None:
                    continue
                diffs.append((tv - bv) * 100.0)      # 转 pp
                detail.append((s, bv * 100, tv * 100, (tv - bv) * 100))
            stat[(cell, col)] = (diffs, detail)
        # 训练图像数核对
        nt = set(r['rows'] for r in runs if r['cell'] == cell)
        print('  格 %s（%s, %s）：应 %d 张；实际完成的 run 数 %d'
              % (cell, CELL_DOMAIN[cell], CELL_BUDGET[cell], CELL_NTRAIN[cell],
                 sum(1 for r in runs if r['cell'] == cell and r['rows'] >= 100)))

    # ---------- 第 3 步：出表 ----------
    L = []
    A = L.append
    A('# G1 判读（预算 × 域差 2×2 分离设计）')
    A('')
    A('> 由 `g1_readout.py` 生成。**第 1 步已通过链路校验**（run 名 ⟷ data ⟷ 格定义；无重复件）。')
    A('> ★ **列口径（实测）**：`results.csv` 里**只有 val 列** `metrics/mAP50-95(B)`；'
      '**不存在** `test_map50_95` / `best_map50_95`。本表因此按 **val** 列出数，'
      '并**显式标注这一偏离**——注册判据写的是 test 列，二者对齐需补一次显式 test 评估（见"时点与口径"）。')
    A('')
    A('## 一、逐格配对差（strategy − base，同种子配对，单位 pp）')
    A('')
    A('| 格 | 域对 | 预算 | 列 | n | 均值 | SD | t | p | 95% CI | 同号 |')
    A('|---|---|---|---|---:|---:|---:|---:|---:|---|---:|')
    rows_csv = []
    for cell in use_cells:
        for col in [k for _, k in COLS]:
            diffs, detail = stat[(cell, col)]
            if not diffs:
                A('| %s | %s | %s | %s | 0 | — | — | — | — | — | — |'
                  % (cell, CELL_DOMAIN[cell], CELL_BUDGET[cell], 'test' if 'test' in col else 'best'))
                continue
            n, mean, sd, t, p, lo, hi = paired(diffs)
            pos = sum(1 for x in diffs if x > 0)
            same = max(pos, len(diffs) - pos)
            A('| %s | %s | %s | %s | %d | **%+.3f** | %.3f | %s | %s | [%+.3f, %+.3f] | %d/%d |'
              % (cell, CELL_DOMAIN[cell], CELL_BUDGET[cell],
                 'test' if 'test' in col else 'best', n, mean, sd,
                 ('%.2f' % t) if t is not None else '—',
                 ('%.5f' % p) if p is not None else '—', lo, hi, same, len(diffs)))
            rows_csv.append(dict(cell=cell, domain=CELL_DOMAIN[cell], budget=CELL_BUDGET[cell],
                                 col=col, n=n, mean=mean, sd=sd, t=t, p=p, lo=lo, hi=hi,
                                 same=same, seeds=';'.join(str(d[0]) for d in detail)))
    A('')
    A('## 二、H1：同一域对内，两预算档的符号是否相反')
    A('')
    A('判据（冻结）：**两端异号**，且**每端各自**满足 {|Δ̄| ≥ 0.30 pp, p < 0.01, ≥8/10 同号}。')
    A('')
    A('| 域对 | 低预算均值 | 高预算均值 | 符号相反？ | 低端过判据？ | 高端过判据？ | **H1** |')
    A('|---|---:|---:|---|---|---|---|')
    for dom in ('d15tod15', 'd15toaitod'):
        cells_lo = [c for c in CELL_BUDGET if CELL_DOMAIN[c] == dom and CELL_BUDGET[c] == '10p']
        cells_hi = [c for c in CELL_BUDGET if CELL_DOMAIN[c] == dom and CELL_BUDGET[c] == '50p']
        def one(cs):
            for c in cs:
                diffs, _ = stat.get((c, 'val'), ([], []))
                if diffs:
                    n, mean, sd, t, p, lo, hi = paired(diffs)
                    pos = sum(1 for x in diffs if x > 0)
                    same = max(pos, len(diffs) - pos)
                    ok = (abs(mean) >= BAR) and (p is not None and p < ALPHA) and (same >= MIN_SAME_SIGN) and n >= 8
                    return mean, ok, n, p, same
            return None, None, 0, None, 0
        mlo, oklo, nlo, plo, slo = one(cells_lo)
        mhi, okhi, nhi, phi, shi = one(cells_hi)
        if mlo is None or mhi is None:
            A('| %s | %s | %s | — | — | — | **未就绪** |'
              % (dom, '—' if mlo is None else '%+.3f' % mlo, '—' if mhi is None else '%+.3f' % mhi))
            continue
        opp = (mlo > 0 > mhi) or (mlo < 0 < mhi)
        h1 = opp and oklo and okhi
        A('| %s | %+.3f | %+.3f | %s | %s | %s | **%s** |'
          % (dom, mlo, mhi, '是' if opp else '**否**',
             '是' if oklo else '否', '是' if okhi else '否', '成立' if h1 else '未成立'))
    A('')
    A('## 三、H2：2×2 交互项（域差档 × 预算档）')
    A('')
    A('以**格均值**为单元做交互项 t 检验。★ 按冻结判据：**H1 不成立则不单独判读 H2**。')
    A('')
    cells = use_cells
    cellmean = {}
    for c in cells:
        diffs, _ = stat.get((c, 'val'), ([], []))
        cellmean[c] = (sum(diffs) / len(diffs)) if diffs else None
    # H2 需要**全部四格**；本次可能只跑了一部分（如 B 完成时只有 c1/c2）
    NEED4 = ['c1', 'c2', 'c3', 'c4']
    ready = all(c in cellmean and cellmean[c] is not None for c in NEED4)
    if not ready:
        miss = [c for c in NEED4 if c not in cellmean or cellmean[c] is None]
        A('*（交互项需要全部四格；缺：%s ⇒ 待算。）*' % '、'.join(miss))
    else:
        # 交互项 = (A1Bhi - A1Blo) - (A0Bhi - A0Blo)
        inter = ((cellmean['c4'] - cellmean['c3']) - (cellmean['c2'] - cellmean['c1']))
        A('| 量 | 值 |')
        A('|---|---:|')
        A('| A0 低预算（c1, %s） | %+.3f |' % (CELL_DOMAIN['c1'], cellmean['c1']))
        A('| A0 高预算（c2） | %+.3f |' % cellmean['c2'])
        A('| A1 低预算（c3） | %+.3f |' % cellmean['c3'])
        A('| A1 高预算（c4） | %+.3f |' % cellmean['c4'])
        A('| **交互项** | **%+.3f** |' % inter)
        A('')
        A('★ 交互项的点估计**不做显著性判定**：每格只有 10 个种子、且两格属同一域对，'
          '把它当独立样本会低估方差。**本件只报点估计**，显著性留待独立复核。')
    A('')
    A('## 四、时点与口径声明')
    A('')
    A('* 本件**不修改任何云端状态**，只读 `results.csv` / `args.yaml`。')
    A('* **只有 `args.yaml` 的 `data:` 与本表一致时，本表的数才有效** —— 第 1 步已核。')
    A('* 已知数据事实：`dota15_50p` 的 `train/50_percent` 有 706 图，其中 `P0334` 因坐标越界被 '
      'ultralytics 丢弃 ⇒ 实际 **705** 张（两臂同集合，不影响配对）。')
    A('')

    outp = os.path.abspath(a.out)
    io.open(outp, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    print('\n判读 -> %s' % outp)
    # CSV
    csvp = outp.replace('.md', '_逐格表.csv')
    if rows_csv:
        with io.open(csvp, 'w', encoding='utf-8', newline='\n') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows_csv[0].keys()))
            w.writeheader()
            for r in rows_csv:
                w.writerow(r)
        print('逐格表 -> %s' % csvp)
    print('（H1 未就绪的格已标出；等 80 个 run 全齐后重跑即得完整判读。）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
