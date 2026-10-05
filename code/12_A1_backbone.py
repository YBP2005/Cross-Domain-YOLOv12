# -*- coding: utf-8 -*-
"""12_A1_backbone.py —— **run → backbone 映射**（闭合 A1 唯一无法闭合的维度）。

A1 §4 的登记缺口原文：
  > 架构是**从 run 名推断**的（`y11`/`amod` 字面 token），底座的 `model` 列只记**预训练权重**、
  > 不记 backbone ⇒ **架构轴的完整审计需要补一份"run→backbone"映射**，否则只能给下界。

本件把这条链子走通：每个 run 的 `args.yaml` 里都有 `model:`（它微调所依据的权重）；
该权重本身又是**某个本地 run 的产物**，于是可以**递归**直到链子尽头落在一个
`yoloXXn.pt`（COCO 起点）上 —— 那就是 backbone。

产出：
  · `base\\run_backbone_map.csv` —— 逐 run 的 (backbone, 链, 证据, 置信)
  · `analysis\\A1b_架构链映射.md` —— 审计表与缺口
"""
import os
import re
import csv
import sys
import glob
import collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ★ 2026-10-05：可移植（放行布局下 = 仓库根，含 base/ deliver/ M3_draft/）
OUT = os.path.join(BASE, 'analysis')
RAW = os.path.join(BASE, 'raw')
rows = [r for r in csv.DictReader(open(os.path.join(BASE, 'base', 'run_table_canonical.csv'),
                                      encoding='utf-8'))]

# ---------- 1b. 从**日志**抽 (run, backbone)：本件覆盖率最高的证据源 ----------
# 每个训练日志里同时有 `save_dir: /workspace/runs/<run>` 与模型打印
# `YOLOv12n summary (fused): …` / `YOLO11n summary: …` ⇒ **一次给到 run 与 backbone 的绑定**。
LOGDIRS = [os.path.join(BASE, 'raw', 'A_logs_20260929'),
           r"E:\workplace\AB机实验文件夹\B_logs_20260930"]
ANSI = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
RUN_RE = re.compile(r'/workspace/runs/([A-Za-z0-9_.\-]+)')
BB_RE = re.compile(r'\b(YOLOv?\d+[a-z]*|RT-?DETR\w*|yolo\d+[a-z]*)\s+summary', re.I)
MAXB = 40 * 1024 * 1024
LOG_BB = {}
nlog = 0
for d in LOGDIRS:
    if not os.path.isdir(d):
        continue
    for p in glob.glob(os.path.join(d, '**', '*.log'), recursive=True):
        try:
            if os.path.getsize(p) > MAXB:
                continue
            txt = ANSI.sub('', open(p, encoding='utf-8', errors='replace').read().replace('\r', ''))
        except Exception:
            continue
        nlog += 1
        runs = collections.Counter(RUN_RE.findall(txt))
        bbs = collections.Counter(m.group(1).lower() for m in BB_RE.finditer(txt))
        if not runs or not bbs:
            continue
        run = runs.most_common(1)[0][0]
        bb = bbs.most_common(1)[0][0]
        LOG_BB.setdefault(run, set()).add(bb)
print('[logs] 日志 %d 个，给出 (run, backbone) 绑定 %d 个' % (nlog, len(LOG_BB)))

# 归一化日志里拿到的 backbone 名（YOLOv12n -> yolo12n）
def canon_bb(b):
    m = re.match(r'yolov?(\d+)([a-z]*)', b.lower())
    return 'yolo%s%s' % (m.group(1), m.group(2)) if m else b.lower()


ARGS = {}          # run 目录名 -> {key: value}
ARGS_DIRS = [RAW, r"E:\workplace\AB机实验文件夹\B_csv_20260930"]
for _d in ARGS_DIRS:
    if not os.path.isdir(_d):
        continue
    for d in glob.glob(os.path.join(_d, '**', 'args.yaml'), recursive=True):
        name = os.path.basename(os.path.dirname(d))
        kv = {}
        try:
            for line in open(d, encoding='utf-8', errors='replace'):
                m = re.match(r'^([A-Za-z_]+):\s*(.*)$', line.rstrip('\n'))
                if m:
                    kv[m.group(1)] = m.group(2).strip()
        except Exception:
            continue
        ARGS.setdefault(name, kv)
print('[args] 本地 args.yaml 目录 %d 个' % len(ARGS))

# 归一化目录名 → 去 _PARTIAL_ / .incomplete_ / _oomfix 等后缀
SUF = re.compile(r'(_PARTIAL_\d+|\.incomplete_\d+_\d+|_oomfix|_\d{6})$')


def norm(n):
    prev = None
    while prev != n:
        prev = n
        n = SUF.sub('', n)
    n = re.sub(r'^_PARTIAL_', '', n)
    return n


# 权重名 -> 产出它的 run 名（args.yaml 的 name 字段或目录名）
PRODUCER = {}
for k, kv in ARGS.items():
    nm = norm(kv.get('name') or k)
    PRODUCER.setdefault(nm, k)
    PRODUCER.setdefault(norm(k), k)
for r in rows:
    PRODUCER.setdefault(norm(r['run']), r['run'])

COCO = re.compile(r'(yolo\d+[a-z]*|rtdetr[a-z0-9]*|yolov\d+[a-z]*)\.pt$', re.I)


def backbone_of(runname, depth=0, seen=None):
    """递归走 model 链，返回 (backbone, 链列表, 置信)。"""
    seen = seen or set()
    chain = []
    cur = runname
    while depth < 6:
        if cur in seen:
            return ('cycle', chain, 'low')
        seen.add(cur)
        kv = ARGS.get(cur) or ARGS.get(norm(cur))
        if kv is None:
            for k in ARGS:
                if norm(k) == norm(cur):
                    kv = ARGS[k]
                    cur = k
                    break
        if kv is None:
            return ('no-args', chain, 'none')
        mdl = (kv.get('model') or '').strip()
        chain.append('`%s`.`model` = `%s`' % (cur, os.path.basename(mdl) or '(空)'))
        base = os.path.basename(mdl)
        m = COCO.search(base)
        if m:
            return (m.group(1).lower(), chain, 'high')
        stem = re.sub(r'\.pt$', '', base)
        nxt = PRODUCER.get(norm(stem))
        if nxt is None:
            return ('unknown(%s)' % stem, chain, 'low')
        depth += 1
        cur = nxt
    return ('depth-limit', chain, 'low')


# ---------- 2. 逐 run 定 backbone（日志优先，链子兜底） ----------
mapped = []
for r in rows:
    src = None
    cands = LOG_BB.get(r['run']) or LOG_BB.get(norm(r['run']))
    if cands and len({canon_bb(c) for c in cands}) == 1:
        bb = canon_bb(list(cands)[0])
        chain = ['日志模型签名 `%s summary`（%s）' % (list(cands)[0], r['run'])]
        conf = 'high'
        src = 'log'
    else:
        bb, chain, conf = backbone_of(r['run'])
        src = 'args-chain'
    mapped.append(dict(run=r['run'], machine=r['machine'], family=r['family'],
                       backbone=bb, confidence=conf, chain=' → '.join(chain), source=src))

cnt = collections.Counter(m['backbone'] for m in mapped)
conf = collections.Counter(m['confidence'] for m in mapped)
srcs = collections.Counter(m['source'] for m in mapped)

# 与 run 名 token 交叉核对
def name_token(run):
    if re.search(r'y26|yolo26', run):
        return 'yolo26n'
    if re.search(r'y11|yolo11', run):
        return 'yolo11n'
    return None


agree = dis = 0
disrows = []
for m in mapped:
    t = name_token(m['run'])
    if not t or m['confidence'] != 'high':
        continue
    if t == m['backbone']:
        agree += 1
    else:
        dis += 1
        disrows.append((m['run'], t, m['backbone']))

L = []


def w(s=''):
    L.append(s)
    print(s)


w('# A1b run → backbone 映射（2026-09-30，闭合 A1 唯一登记缺口）')
w()
w('> A1 §4 登记：底座的 `model` 列只记**预训练权重**、不记 backbone，')
w('> 架构轴只能从 run 名 token 推断 ⇒ 只能给下界。')
w('> 本件把链子走通：递归读 `args.yaml: model`，直到落在 `yoloXXn.pt`（COCO 起点）。')
w()
w('## 1. 方法与覆盖')
w()
w('**两个独立证据源**：')
w()
w('1. **日志模型签名**（主源）：每个训练日志里同时有 `save_dir: /workspace/runs/<run>`')
w('   与 ultralytics 打印的 `YOLOv12n summary (fused): …` ⇒ **一次给到 run 与 backbone 的绑定**。')
w('2. **`args.yaml` 链**（兜底）：递归读 `model:` 直到落在 `yoloXXn.pt`。')
w()
w('| 量 | 值 |')
w('|---|---|')
w('| 扫过的日志 | %d |' % nlog)
w('| 日志给到 (run, backbone) 绑定 | **%d** |' % len(LOG_BB))
w('| 本地 `args.yaml` | %d 个目录 |' % len(ARGS))
w('| 底座 run | %d |' % len(rows))
w('| **定到具体 backbone** | **%d（%.0f%%）** |' % (conf['high'], 100.0 * conf['high'] / len(rows)))
w('| ↳ 其中来自**日志签名** | %d |' % srcs.get('log', 0))
w('| ↳ 其中来自 **args 链** | %d |' % (conf['high'] - srcs.get('log', 0)))
w('| 链断（上游权重没有本地 args.yaml、也无日志） | %d |' % conf['none'])
w('| 只到"未知权重" | %d |' % conf['low'])
w()
w('## 2. backbone 分布')
w()
w('| backbone | run 数 | 说明 |')
w('|---|---|---|')
for b, n in cnt.most_common():
    w('| `%s` | %d | %s |' % (b, n,
                              'COCO 起点，链完整' if b in ('yolo11n', 'yolo12n', 'yolo26n')
                              else '链未走通，见 §4'))
w()
w('## 3. 与 run 名 token 的交叉核对（**这是映射的独立检验**）')
w()
w('凡是 run 名里带 `y11`/`y26` 的、且链子走通的，看两者是否一致：')
w()
w('| 结果 | 数 |')
w('|---|---|')
w('| ✅ 一致 | **%d** |' % agree)
w('| ❌ 不一致 | %d |' % dis)
w()
if disrows:
    w('不一致明细（**这些就是"从 run 名推断"会推断错的 run**）：')
    w()
    w('| run | 名字暗示 | 链子实测 |')
    w('|---|---|---|')
    for a, b, c in disrows[:20]:
        w('| `%s` | `%s` | **`%s`** |' % (a, b, c))
    w()
else:
    w('⇒ **零不一致**：名字 token 与链子实测完全吻合 ⇒ 两份独立证据互证。')
    w()
w('## 4. 链子样例（可逐条复核）')
w()
seen_bb = set()
for m in mapped:
    if m['backbone'] in seen_bb or not m['chain']:
        continue
    seen_bb.add(m['backbone'])
    w('* **`%s`** ← `%s`' % (m['backbone'], m['chain']))
w()
w('## 5. 未走通的链（**缺口，逐条列出**）')
w()
bad = [m for m in mapped if m['confidence'] != 'high']
byb = collections.Counter(m['backbone'] for m in bad)
w('| 未知/断链的标识 | run 数 | 需要的上游 |')
w('|---|---|---|')
for b, n in byb.most_common():
    w('| `%s` | %d | %s |' % (b, n, '该上游权重的 `args.yaml` 不在本次取件内' if b != 'no-args' else '该 run 本身无 args.yaml'))
w()
w('⇒ 这些 run **不能**进入架构轴的结论；它们恰是 A1 §4 原来只能给"下界"的那部分。')
w()
w('## 6. 架构轴（用映射重算，**不再是下界**）')
w()
AC = collections.defaultdict(lambda: [0, set(), collections.Counter()])
for m in mapped:
    if m['confidence'] != 'high':
        continue
    a = AC[m['backbone']]
    a[0] += 1
for r, m in zip(rows, mapped):
    if m['confidence'] != 'high':
        continue
    AC[m['backbone']][2][r['epochs_nominal']] += 1
for m, r in zip(mapped, rows):
    if m['confidence'] == 'high':
        AC[m['backbone']][1].add(r['dataset'])
w('| backbone | run 数 | 目标数据集数 | epochs 分布 |')
w('|---|---|---|---|')
for b, (n, ds, ep) in sorted(AC.items(), key=lambda x: -x[1][0]):
    w('| **`%s`** | %d | %d | %s |' % (b, n, len(ds),
                                      '、'.join('%s(%d)' % kv for kv in ep.most_common(5))))
w()
w('> ⇒ 架构轴现在有**可核的键**：`run_backbone_map.csv`。')
w('> 论文若报"架构对照"（§4.4），应引用该表的 `backbone` 列，而不是 run 名 token。')
w()

os.makedirs(os.path.join(BASE, 'base'), exist_ok=True)
with open(os.path.join(BASE, 'base', 'run_backbone_map.csv'), 'w', encoding='utf-8', newline='') as fh:
    wr = csv.DictWriter(fh, fieldnames=['run', 'machine', 'family', 'backbone', 'confidence', 'source', 'chain'])
    wr.writeheader()
    for m in sorted(mapped, key=lambda x: x['run']):
        wr.writerow(m)
open(os.path.join(OUT, 'A1b_架构链映射.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n输出 -> base\\run_backbone_map.csv / analysis\\A1b_架构链映射.md')
