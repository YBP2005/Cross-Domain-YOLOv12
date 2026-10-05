# -*- coding: utf-8 -*-
"""37_plan_supplement.py —— 生成**补实验方案**（逐 run 清单 + 启动脚本 + run 数）。

回答"需要补多少 run、补哪些"。不做任何估算：每一条缺失 run 都由底座逐格比对得出。

三种设计的取舍：
  · 目标 n：论文自己的种子闸门是 `n≥10`，或 `n≥5 且逐种子全同号`，或 `|t|≥4`。
    故 n=5 为"最小可报"，n=10 为"与全文其余各处一致"。
  · 损失轴挑哪几格/哪几种损失：见下方 LOSS_DESIGN。

产出：
  deliver/补实验方案_损失与架构_20261001.md
  deliver/补实验_run清单.csv
  deliver/补实验_launch.sh
"""
import os
import re
import sys
import csv
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import _cells as C            # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEL = os.path.join(BASE, 'deliver')
SEEDPAT = re.compile(r'_s(\d+)(n?)$')
SEEDS10 = list(range(42, 52))

rows, _ = C.load()


def sd(r):
    m = SEEDPAT.search(r['run'])
    return int(m.group(1)) if m else None


def cellrows(pair, fam, ep):
    return [r for r in rows if C.pair_of(r) == pair and r['family'] == fam
            and C.f(r['epochs_nominal']) and int(C.f(r['epochs_nominal'])) == ep]


# ---------------- 逐格盘点"四象限"现状 ----------------
def quad(pair, fam, ep, loss, seeds=SEEDS10):
    """返回 {(seed, slot): 已有 run 名 or None}；slot ∈ ShB/ShL/LoB/LoL。"""
    out = {}
    cr = cellrows(pair, fam, ep)
    for s in seeds:
        for slot, want in (('ShB', dict(arm='base', loss='shapeiou')),
                           ('ShL', dict(arm='lr005', loss='shapeiou')),
                           ('LoB', dict(arm=None, loss=loss)),
                           ('LoL', dict(arm=None, loss=loss))):
            hit = [r for r in cr if sd(r) == s and (r.get('loss') or '').strip() == want['loss']
                   and (want['arm'] is None or r['lr_arm'] == want['arm'])
                   and (want['arm'] is not None or r['lr0'] == '0.001')]
            out[(s, slot)] = hit[0]['run'] if hit else None
    return out


# ---------------- 设计 ----------------
# 损失轴：每格挑"base 臂覆盖最好"的替代损失
# (配对, 族, 轮数, 替代损失, 数据 yml, pretrain, 容器内 data 路径, run 名前缀, 名字里带 3way 吗)
LOSS_DESIGN = [
    ('mafa→mende20', 'r10', 100, 'sns', 'mende20_3way.yaml', '/workspace/weights/mafa_pretrain.pt',
     '/root/datasets_mask/mendeley_yolo/mende20_3way.yaml', 'r10_prior', '_3way'),
    ('mendein→mende', 'mendein', 100, 'pws', 'mende_20p.yaml', '/workspace/weights/mendein_pretrain.pt',
     '/root/datasets_mask/mendeley_yolo/mende_20p.yaml', 'mendein', ''),
    ('mafa→mende', 'mende', 100, 'sns', 'mende_20p.yaml', '/workspace/weights/mafa_pretrain.pt',
     '/root/datasets_mask/mendeley_yolo/mende_20p.yaml', 'mende', ''),
]

# 架构轴：同目标、同为 COCO 起点、同三方划分，只换 backbone
ARCH_DATA = '/root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml'
# (权重文件名, **A 机上实测存在的完整路径**, run 名前缀)
# ★ 2026-10-02 前置检查实测：`/workspace/weights/yolo11n.pt` **不存在**（在 `/root/workspace/weights/`）；
#   `/workspace` 与 `/root/workspace` 是**两个不同目录**（readlink -f 各自成立）⇒ 路径必须写全。
ARCH = [('yolo11n.pt', '/root/workspace/weights/yolo11n.pt', 'r15_arch_y11_vistod15'),
        ('yolo12n.pt', '/workspace/yolo12n.pt', 'r15_arch_y12_vistod15')]


def plan(n_target):
    """产出一份 (kind, cell, name, loss, pretrain, data, lr, seed, epochs, why) 清单。

    ★ 命名纪律（**必须遵守，否则新 run 归不了格**）——由 `01_build_base.py::norm()` 决定：
      · `family` = 名字的**第一个 token** ⇒ 必须以族名开头（`r10_` / `mendein_` / `r15_...`）；
      · `lr_arm` **只能**从名字解析：含 `lr005` ⇒ lr005 臂；含 `base\\d*` ⇒ base 臂。
        ⚠ 既有换损失跑（`mendein_pws_100ep_s43n`）**不含** `base` ⇒ 臂为空 ⇒ 进不了格图。
        新的换损失跑**必须**写成 `..._pws_base100_...` / `..._pws_lr005_100ep_...`。
      · `epochs_nominal`：`(\\d+)ep` 优先，否则 `base(\\d+)`；
      · 名字**不得**以 `_oomfix` / `_REPB` / `_PARTIAL_` 结尾（会让种子回落 42，见铁律 18）。
      ★ `pair` 不来自名字：它由 **pretrain + dataset** 决定（`_cells.pair_of`）⇒ 配对不会错。
    """
    out = []
    n_use = SEEDS10[:n_target]
    TW = '_3way'
    # ---- 损失轴：补四象限中缺的 ----
    for pair, fam, ep, loss, _yml, pretrain, data, stem, TW in LOSS_DESIGN:
        q = quad(pair, fam, ep, loss, seeds=n_use)
        for (s, slot), have in sorted(q.items()):
            if have:
                continue
            if slot == 'ShB':
                nm, lo, lr, why = '%s_base%dep%s_s%dn' % (stem, ep, TW, s), 'shapeiou', 0.001, 'shapeiou-base 补种子'
            elif slot == 'ShL':
                nm, lo, lr, why = '%s_lr005_%dep%s_s%dn' % (stem, ep, TW, s), 'shapeiou', 0.005, 'shapeiou-lr005（本格为 0）'
            elif slot == 'LoB':
                nm, lo, lr, why = '%s_%s_base%dep%s_s%dn' % (stem, loss, ep, TW, s), loss, 0.001, '%s-base 补种子' % loss
            else:
                nm, lo, lr, why = '%s_%s_lr005_%dep%s_s%dn' % (stem, loss, ep, TW, s), loss, 0.005, '%s-lr005（本格为 0）' % loss
            out.append(dict(kind='L', cell='%s/%s/%dep/%s' % (pair, fam, ep, loss),
                            name=nm, loss=lo, pretrain=pretrain, data=data,
                            lr=lr, seed=s, epochs=ep, why=why))
    # ---- 架构轴：y11 补齐 + y12 全补（命名照抄既有 `r15_arch_y11_vistod15_*`）----
    for w, wpath, prefix in ARCH:
        for s in n_use:
            for arm, lr in (('base', 0.001), ('lr005', 0.005)):
                nm = ('%s_base100_s%dn' % (prefix, s) if arm == 'base'
                      else '%s_lr005_100ep_s%dn' % (prefix, s))
                out.append(dict(kind='A', cell='arch/%s/100ep' % w,
                                name=nm, loss='shapeiou', pretrain=wpath, data=ARCH_DATA,
                                lr=lr, seed=s, epochs=100,
                                why='架构对照：%s（同目标 / 同 COCO 起点 / 同三方划分）' % w))
    return out


def dedup(plan_rows, existing_names):
    """去掉底座里已有的 run（补实验只跑缺的），并去重。"""
    seen = set()
    out = []
    for r in plan_rows:
        if r['name'] in existing_names or r['name'] in seen:
            continue
        seen.add(r['name'])
        out.append(r)
    return out


exists = {r['run'] for r in rows}
L = []


def w(s=''):
    L.append(s)


w('# 补实验方案：损失轴 × 增益、架构轴（2026-10-01）')
w()
w('> 目的：把 `03_榨干报告` §三 里"现有设计做不到"的两条**变成可做**。')
w('> 本件不做估算 —— 每一条缺失 run 都由 `base/run_table_canonical.csv` **逐格比对**得出。')
w()
w('## 0. 共同配方（必须与既有 run 逐字一致，否则不可比）')
w()
w('| 项 | 值 |')
w('|---|---|')
w('| 驱动 | `/workspace/train_obj.py`（`analysis/work/train_obj.py`，**带 `--shuffle-seed`** 的版本）|')
w('| 固定项 | `batch=32` `imgsz=640` `workers=16` `optimizer=SGD` `momentum=0.925` `weight_decay=1e-4` |')
w('| 固定项 | `warmup_epochs=3` `seed=42`（torch 种子）`pretrained=True` `amp=False` `patience=epochs` `save_period=5` |')
w('| 臂 | `--lr 0.001` = **base**；`--lr 0.005` = **lr005** |')
w('| 种子 | `--shuffle-seed <s>`，s = **数据顺序置换种子**（不是 torch seed）|')
w('| 评测 | 驱动自带：训练后对 `best.pt`（缺则 `last.pt`）调 `val(split=\'test\')`，追加 `/workspace/sio_b_results.csv` |')
w('| 环境 | ultralytics **8.4.120** / torch 2.4.0+cu121 / python 3.10.21 |')
w()
w('## 一、损失轴：补"换损失后的**增益**"（现有数据缺 `{loss}-lr005` 臂）')
w()
w('要回答的是：**把微调损失换掉，`lr005 − base` 这个增益还在不在**。')
w('这需要每个种子下**四格齐全**：`shapeiou-base` / `shapeiou-lr005` / `{loss}-base` / `{loss}-lr005`。')
w()
w('选格原则：挑**三方划分协议**（`*_3way.yaml`）的格优先 —— 它是全稿最干净的口径；')
w('替代损失挑该格 **base 臂覆盖最好**的那一种。')
w()
w('## 二、架构轴：同目标、同 COCO 起点、只换 backbone')
w()
w('为什么现在做不到：**预训练权重决定 backbone** ⇒ backbone 与 (配对, 族) 完全共线，')
w('格内不可能出现两种 backbone。')
w()
w('底座的现状（已实测）：')
w()
w('| 组合 | 现状 |')
w('|---|---|')
w('| `yolo11n.pt → dota15_20p_3way`（族 `r15`） | **base 3 种子 + lr005 3 种子**（其余是 `_PARTIAL_`，按铁律 18 不算独立种子）|')
w('| `yolo12n.pt → dota15_20p_3way` | **不存在** |')
w()
w('⇒ 补 `yolo12n.pt → dota15_20p_3way` 并把两边都推到目标 n，即得**同目标、同为 COCO 起点、')
w('同三方划分、同预算**下的纯架构对照 —— 比 §4.4 现在的"第二个 (源域, backbone) 组合"干净得多。')
w()

for n_target in (5, 10):
    p = dedup(plan(n_target), exists)
    lp = [x for x in p if x['kind'] == 'L']
    ap = [x for x in p if x['kind'] == 'A']
    w('## 设计 %s（目标 n=%d）—— 合计 **%d** run' % ('A' if n_target == 5 else 'B', n_target, len(p)))
    w()
    w('> 两个设计**只差目标种子数**：设计 A 走论文闸门的"n≥5 且逐种子全同号"这条支路，')
    w('> 设计 B 走"n≥10"那条，与全文其余各处一致。**先做 A 也能出结论**，只是判据更严。')
    w()
    w('| 轴 | run 数 |')
    w('|---|---|')
    w('| 损失（四象限补齐） | **%d** |' % len(lp))
    w('| 架构（`yolo11n` 补齐 + `yolo12n` 全补） | **%d** |' % len(ap))
    w('| **合计** | **%d** |' % len(p))
    w()
    bycell = collections.Counter(x['cell'] for x in p)
    w('| 格 | 需补 run |')
    w('|---|---|')
    for k, v in sorted(bycell.items()):
        w('| `%s` | %d |' % (k, v))
    w()
    if n_target == 10:
        # 详细清单只印 n=10 那一版
        w('### 逐 run 清单（n=10 版，共 %d 条）' % len(p))
        w()
        w('| # | 实验 | 格 | 新 run 名 | loss | pretrain | lr | seed | ep | 为什么 |')
        w('|---|---|---|---|---|---|---|---|---|---|')
        for i, x in enumerate(p, 1):
            w('| %d | %s | `%s` | `%s` | `%s` | `%s` | %.3f | %d | %d | %s |'
              % (i, x['kind'], x['cell'], x['name'], x['loss'], x['pretrain'], x['lr'],
                 x['seed'], x['epochs'], x['why']))
        w()

# ---- 写 CSV 与 launch.sh（n=10 版）----
PY = '/usr/local/miniconda3/envs/yolo_arch/bin/python'
def emit(tier, n_target, suffix):
    """把某一 tier 的清单落成 CSV + 单队列脚本 + 双队列脚本。"""
    global final
    final = dedup(plan(n_target), exists)
    with open(os.path.join(DEL, '补实验_run清单%s.csv' % suffix), 'w', newline='', encoding='utf-8') as fh:
        wr = csv.DictWriter(fh, fieldnames=['kind', 'cell', 'name', 'loss', 'pretrain',
                                            'data', 'lr', 'seed', 'epochs', 'why'])
        wr.writeheader()
        for x in final:
            wr.writerow(x)
    sh = ['#!/usr/bin/env bash',
          '# 补实验启动脚本（设计 %s / n=%d / %d 条）—— 自动生成，勿手改' % (tier, n_target, len(final)),
          'set -u',
          'PY=%s' % PY,
          'export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True',
          'cd /workspace || exit 1',
          '']
    for x in final:
        sh.append('# %s | %s' % (x['cell'], x['why']))
        sh.append('if [ -d /workspace/runs/%s ]; then echo "SKIP %s (已存在)"; else $PY /workspace/train_obj.py --loss %s --epochs %d --name %s --data %s --pretrain %s --shuffle-seed %d --lr %s || echo "FAILED %s" >> /workspace/_supp_failed.log; fi'
                  % (x['name'], x['name'], x['loss'], x['epochs'], x['name'], x['data'],
                     x['pretrain'], x['seed'], x['lr'], x['name']))
        sh.append('')
    open(os.path.join(DEL, '补实验%s_launch.sh' % suffix), 'w',
         encoding='utf-8', newline=CHR10).write(CHR10.join(sh) + CHR10)
    for _q in (0, 1):
        qsh = ['#!/usr/bin/env bash',
               '# 补实验 设计 %s（队列 %d / 2，n=%d，%d 条）—— 自动生成，勿手改' % (tier, _q, n_target, len(final)),
               '# 用法：bash 补实验%s_launch_gpu%d.sh' % (suffix, _q),
               '# 驱动内 device=0 是硬编码 => 本队列用 CUDA_VISIBLE_DEVICES 只暴露一张卡，',
               '# 使 device=0 落到物理卡 %d。不要改驱动去传 --device（会破坏配方一致性）。' % _q,
               'set -u',
               'export CUDA_VISIBLE_DEVICES=%d' % _q,
               'export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True',
               'PY=%s' % PY,
               'LOG=/workspace/_supp%s_gpu%d.log' % (suffix, _q),
               'FAIL=/workspace/_supp_failed.log',
               'exec 8>/workspace/_supp%s_gpu%d.lock' % (suffix, _q),
               "flock -n 8 || { echo '已有本队列实例，退出'; exit 0; }",
               'cd /workspace || exit 1',
               '']
        for _i, _x in enumerate(final):
            if _i % 2 != _q:
                continue
            qsh.append('echo "[$(ts)] %d/%d %s" | tee -a "$LOG"' % (_i + 1, len(final), _x['name']))
            # ★ 幂等：目录已存在则跳过（驱动 exist_ok=True 会**覆盖重跑**，故必须自己挡）
            qsh.append('if [ -d /workspace/runs/%s ]; then echo "  SKIP %s"; else $PY /workspace/train_obj.py --loss %s --epochs %d --name %s --data %s --pretrain %s --shuffle-seed %d --lr %s || echo "FAILED %s" >> "$FAIL"; fi'
                       % (_x['name'], _x['name'], _x['loss'], _x['epochs'], _x['name'],
                          _x['data'], _x['pretrain'], _x['seed'], _x['lr'], _x['name']))
        qsh.append('echo "[$(ts)] 设计 %s 队列 %d 完成" | tee -a "$LOG"' % (tier, _q))
        open(os.path.join(DEL, '补实验%s_launch_gpu%d.sh' % (suffix, _q)), 'w',
             encoding='utf-8', newline=CHR10).write(CHR10.join(qsh) + CHR10)
    return final


CHR10 = chr(10)
# ★ 必须**分别捕获**：`emit()` 会把全局 `final` 指向它自己的返回列表，
#   若直接用 `final` 去比，就成了 A ⊆ A（恒真）—— 这个错当场被看出来了。
FINAL_B = emit('B', 10, '')
FINAL_A = emit('A', 5, '_n5')
def emit_queues(rows_list, suffix, queues):
    """按 (机器, 卡号, 跨机步长序号) 切分成多条队列脚本。

    `queues` = [(标签, 机器, 本机卡号, 步长序号), ...]，步长为 len(queues)。
    ⚠ A 与 B 各自有自己的 `/workspace/sio_b_results.csv`：两机的 RESULT 行分开汇总，
      回收后分别并入底座（与既有 A_sio / B_sio 的约定一致）。
    """
    n = len(queues)
    for _label, _mach, _gpu, _k in queues:
        # ★ 逐机路径替换：两机**权重 md5 逐位一致**，但**存放路径不同**
        #   （实测：yolo11n 在 A 是 /root/workspace/weights/、在 B 是 /root/）。
        _rows = []
        for _x in rows_list:
            _x = dict(_x)
            _x['pretrain'] = MACH_PATH.get(_mach, {}).get(_x['pretrain'], _x['pretrain'])
            _rows.append(_x)
        qsh = ['#!/usr/bin/env bash',
               '# 补实验 %s 机 · 队列 %d/%d（本机卡 %d）—— 自动生成，勿手改' % (_mach, _k + 1, n, _gpu),
               '# 用法：bash %s' % ('补实验%s_%s_gpu%d.sh' % (suffix, _mach, _gpu)),
               '# 驱动内 device=0 是硬编码 => 用 CUDA_VISIBLE_DEVICES 只暴露一张卡，',
               '# 使 device=0 落到本机物理卡 %d。不要改驱动去传 --device。' % _gpu,
               'set -u',
               'export CUDA_VISIBLE_DEVICES=%d' % _gpu,
               'export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True',
               'PY=%s' % PY,
               'LOG=/workspace/_supp%s_%s_gpu%d.log' % (suffix, _mach, _gpu),
               'FAIL=/workspace/_supp%s_%s_failed.log' % (suffix, _mach),
               'exec 8>/workspace/_supp%s_%s_gpu%d.lock' % (suffix, _mach, _gpu),
               "flock -n 8 || { echo '已有本队列实例，退出'; exit 0; }",
               'cd /workspace || exit 1',
               "ts() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }",
               'echo "[$(ts)] 队列启动 %s 卡%d 共 %d 条（本队列 %d 条）" | tee -a "$LOG"' % (_mach, _gpu, len(_rows), (len(_rows) + n - 1 - _k) // n),
               '']
        mine = [x for i, x in enumerate(_rows) if i % n == _k]
        for j, _x in enumerate(mine, 1):
            qsh.append('echo "[$(ts)] %d/%d %s" | tee -a "$LOG"' % (j, len(mine), _x['name']))
            # ★ 幂等：目录已存在则跳过（驱动 exist_ok=True 会覆盖重跑，必须自己挡）
            qsh.append('if [ -d /workspace/runs/%s ]; then echo "  SKIP %s"; else $PY /workspace/train_obj.py --loss %s --epochs %d --name %s --data %s --pretrain %s --shuffle-seed %d --lr %s || echo "FAILED %s" >> "$FAIL"; fi'
                       % (_x['name'], _x['name'], _x['loss'], _x['epochs'], _x['name'],
                          _x['data'], _x['pretrain'], _x['seed'], _x['lr'], _x['name']))
        qsh.append('echo "[$(ts)] %s 队列完成（卡%d）" | tee -a "$LOG"' % (_mach, _gpu))
        open(os.path.join(DEL, '补实验%s_%s_gpu%d.sh' % (suffix, _mach, _gpu)), 'w',
             encoding='utf-8', newline=CHR10).write(CHR10.join(qsh) + CHR10)
    return {m: sum(1 for i in range(len(rows_list)) if i % n == k)
            for _, m, _, k in queues}


# ★ 四队列跨机：A 两张卡 + B 两张卡，步长 4，交替分派
# ★ 逐机 pretrain 路径表（键 = 计划里写的 A 机路径；值 = 该机上的实际路径）
#   依据：2026-10-02 两机前置检查实测 —— 权重 md5 逐位一致，但 yolo11n 存放位置不同。
MACH_PATH = {'B': {'/root/workspace/weights/yolo11n.pt': '/root/yolo11n.pt'}}
Q4 = [('A0', 'A', 0, 0), ('A1', 'A', 1, 1), ('B0', 'B', 0, 2), ('B1', 'B', 1, 3)]
_qA = emit_queues(FINAL_B, '', Q4)
_qA5 = emit_queues(FINAL_A, '_n5', Q4)
print('四队列分派（设计 B，共 %d 条）：' % len(FINAL_B))
for _lbl, _m, _g, _k in Q4:
    _c = sum(1 for i in range(len(FINAL_B)) if i % 4 == _k)
    print('   %s 机 卡%d (队列%d/%d): %d 条' % (_m, _g, _k + 1, 4, _c))
print('四队列分派（设计 A，共 %d 条）：' % len(FINAL_A))
for _lbl, _m, _g, _k in Q4:
    _c = sum(1 for i in range(len(FINAL_A)) if i % 4 == _k)
    print('   %s 机 卡%d (队列%d/%d): %d 条' % (_m, _g, _k + 1, 4, _c))

print('设计 A(n=5) %d 条 是 设计 B(n=10) %d 条 的子集 ? %s  (B 多出 %d 条)'
      % (len(FINAL_A), len(FINAL_B),
         {x['name'] for x in FINAL_A} <= {x['name'] for x in FINAL_B},
         len({x['name'] for x in FINAL_B} - {x['name'] for x in FINAL_A})))
w('## 三、★ 对照怎么定义（两组实验的**统计口径**）')
w()
w('### 3.1 损失轴 —— **同格四象限**')
w()
w('对每个种子 s，四个量同格（同配对/同族/同轮数/同预训练）齐备：')
w()
w('```')
w('增益_shapeiou(s) = lr005@shapeiou(s) − base@shapeiou(s)')
w('增益_loss(s)     = lr005@{loss}(s)   − base@{loss}(s)          # 本实验补出来的')
w('Δ_loss(s)        = 增益_loss(s) − 增益_shapeiou(s)             # 逐种子配对')
w('```')
w()
w('**判据**（用论文自己的闸门）：`Δ_loss` 在 n≥10、或 n≥5 且逐种子全同号、或 |t|≥4 时可报方向；')
w('否则**只报均值与区间，不报方向**。')
w('★ 逐种子配对是必须的：不同臂的种子集若不同，均值相减会混入种子效应。')
w()
w('### 3.2 架构轴 —— **跨格、逐种子配对**（不是格内对照）')
w()
w('⚠ **必须写明**：本对照**不可能**是格内对照 —— 预训练权重决定 backbone，')
w('所以 backbone 永远与 `pair` 共线，格内**永远**只会有一种 backbone（A12 的实测：0 格）。')
w()
w('正确的对照定义是**跨格**，两格只差 backbone：')
w()
w('| | 格 A | 格 B |')
w('|---|---|---|')
w('| pair | `yolo11n→dota15` | `yolo12n→dota15` |')
w('| family | `r15` | `r15` |')
w('| 预算 / 轮数 | 20% / 100ep | 20% / 100ep |')
w('| 协议 | `dota15_20p_3way.yaml` | `dota15_20p_3way.yaml` |')
w('| 种子 | s42–s\{N\} | **同一组** s42–s\{N\} |')
w()
w('```')
w('Δ_arch(s) = 增益_y12(s) − 增益_y11(s)        # 逐种子配对')
w('```')
w()
w('★ 两边都是 **COCO 起点**（无源域预训练）⇒ 架构是**唯一变量**，')
w('这比 §4.4 现在那个"第二个 (源域, backbone) 组合"干净得多。')
w('★ 但也要写明**它失去了什么**：这是"COCO→目标"的迁移，**不含源域预训练**那一环，')
w('所以它能回答"增益是否依赖 backbone"，**不能**回答"增益是否依赖源域预训练"。')
w()
w('## 四、密度轴（**可选**，需先造数据集 —— 与上面两组不是一回事）')
w()
w('密度与配对共线（每个 corpus 对应固定配对），且底座里**没有**同语料的密度变体')
w('（`budget_pct` 是标注比例，**不是**密度）⇒ 这条**要造数据**，不是补 run 就行。')
w()
w('**设计（若要做）**：拿一个密集目标域，按"每图实例数"子采样出 2 个更稀的变体，')
w('其余全固定：')
w()
w('| 项 | 设定 |')
w('|---|---|')
w('| 固定 | 源域预训练权重、目标语料、标注预算、轮数、臂、种子集、三方划分 |')
w('| 变 | **目标集的每图实例数**（`inst/img`）：原样（密集） / 子采样一档 / 子采样两档 |')
w('| 每档 run 数 | 2 臂 × n 种子 |')
w('| n=10 时合计 | **2 档 × 2 臂 × 10 = 40 run**（密集那档已有） |')
w()
w('★ 子采样规则必须**确定且记录**（保留哪些图、按什么阈值），否则不可复现；')
w('★ 子采样会同时改变**图数**，而图数与预算共线 ⇒ 必须**同时固定图数**（按图数下采样后再比），')
w('   否则测到的是"图数效应"不是"密度效应"。**这一点决定了该实验的设计难度，建议单独评估后再决定做不做。**')
w()
w('## 五、机器与准备（请按此上传）')
w()
w('| 需上传 | 说明 |')
w('|---|---|')
w('| `/workspace/train_obj.py` | 用 `analysis/work/train_obj.py`（**带 `--shuffle-seed`**）；`/d/deepseek/train_obj.py` 是旧版，缺该参数 |')
w('| `/workspace/module_sweep/`（`modules.py`+`losses.py`） | 驱动 `sys.path` 依赖；**没有它换损失会直接崩** |')
w('| 权重 | `mafa_pretrain.pt`、`mendein_pretrain.pt`（损失轴）；`yolo11n.pt`、`yolo12n.pt`（架构轴） |')
w('| 数据 | `mendeley_yolo/mende20_3way.yaml`、`mendeley_yolo/mende_20p.yaml`、`dota15_yolo/dota15_20p_3way.yaml` **及其 split 目录** |')
w('| 环境 | ultralytics **8.4.120**（版本不符会改变 baseline，见缺陷记录）|')
w()
w('★ **四队列跨机**（A 两张卡 + B 两张卡）：驱动把 `device=0` 写死 —— **不要**改驱动')
w('   （一改就与既有 run 的配方不再逐字一致）；正确做法是用 `CUDA_VISIBLE_DEVICES`')
w('   让每个队列只看见**本机一张卡**。按步长 4 交替分派，已生成：')
w()
w('   | 脚本 | 机器 | 本机卡 | 设计 B | 设计 A |')
w('   |---|---|---|---|---|')
w('   | `补实验_A_gpu0.sh` | A | 0 | 30 | 10 |')
w('   | `补实验_A_gpu1.sh` | A | 1 | 30 | 10 |')
w('   | `补实验_B_gpu0.sh` | B | 0 | 29 | 9 |')
w('   | `补实验_B_gpu1.sh` | B | 1 | 29 | 9 |')
w()
w('   各自带 `flock` 单实例守卫，且**逐条幂等**（目录已存在则 `SKIP`）。')
w('   ⚠ **A 与 B 各写自己的** `/workspace/sio_b_results.csv` ⇒ 回收时两机 RESULT 行**分开取回**')
w('   （与既有 `A_sio` / `B_sio` 约定一致），再各自并入底座。')
w()
w('★ **B 机放之前必须先做前置检查**：B 的目录布局与 A **不一定相同**')
w('   （A 上 `/workspace` 与 `/root/workspace` 就是两个不同目录）⇒ 先跑 `_precheck_supp.py`，')
w('   路径全过再放；且要确认 B 上**没有别人正在跑**（B 曾交给 P2）。')
w()
w('★ **先跑 1 条冒烟**（任取一条 base 臂），确认：① 日志有 `[loss] patched -> ...`；')
w('② 跑满名义轮数；③ `RESULT` 行写进了 `/workspace/sio_b_results.csv`。三者都对再放全量。')
w()
w('### 5.1 ★ 脚本是**幂等**的')
w()
w('每条命令前都有 `if [ -d /workspace/runs/<name> ]` 判断，已存在则 `SKIP`。')
w('**必须这样**：驱动的 `exist_ok=True` 会直接**覆盖重跑**已有目录 —— 中断后重跑会白烧一遍。')
w('⇒ 中断/补跑都可以直接再执行同一个脚本，已完成的不会重做。')
w()
w('## 五点九、续跑 / 中断处理（照此做，别乱来）')
w()
w('1. **不要覆盖正在运行的脚本**：bash 是**边读边执行**的 —— 往正在跑的 `_supp_*.sh` 上写，')
w('   会读出半个文件。脚本一旦启动就不要再改它；要改先停队列。')
w('2. **停队列**：只杀队列包装那个进程（形如 `bash _supp_A_gpu0.sh`），')
w('   **别杀 `train_obj.py` 本身**，否则当前那条会变成 `.incomplete` 中断件。等当前 run 自然结束再停更稳。')
w('3. **续跑**：把修好的脚本重新上传，再执行同一个脚本 —— 每条都带')
w('   `if [ -d /workspace/runs/<name> ]; then SKIP; fi`，**已完成的不会重做**。')
w('4. ⚠ **`flock` 单实例守卫**：旧实例没退干净时新实例会直接 `exit 0`（日志只一行）。')
w('   先确认 `pgrep -af bash _supp` 为空，再启动。')
w('5. ⚠ **不要**按 `flock` 关键字 pkill —— 会误杀其它合法锁。')
w()
w('> **已知无害瑕疵**：本批启动脚本里写的是 `date -u +%F %T`，shell 会把 `%T` 当成')
w('> 第二个操作数，`date` 报错 ⇒ 日志时间戳显示为 `[]`。**只影响日志可读性，不影响训练**。')
w('> 生成器已改用 `ts()` 包装（输出 ISO8601）；**续跑时换上修好的脚本**即可。')
w()
w('## 六、回收与验收')
w()
w('1. 把新 run 的 `runs/<name>/{args.yaml,results.csv,weights/}` 与 `sio_b_results.csv` 取回；')
w('2. 重跑 `scripts/01_build_base.py`（**必须**，它现在会按短名回退并校验）；')
w('3. 重跑 `scripts/14_verify_claims.py` —— 新增的格必须能在底座里被 `_pick` 选中；')
w('4. 损失轴判定用 `scripts/36_A20_loss_contrast.py` 的同一口径（四象限同种子、同 pretrain）；')
w('5. ⚠ 新 run 名**不要**带 `_oomfix` / `_REPB` / `_PARTIAL_` 后缀（会让种子回落 42，见铁律 18）。')
w()

open(os.path.join(BASE, 'deliver', '补实验方案_损失与架构_20261001.md'),
     'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('n=5 合计:', len(FINAL_A))
print('n=10 合计:', len(FINAL_B))
for k in ('L', 'A'):
    print('  %s: n=5 → %d ; n=10 → %d' % (k, len([x for x in FINAL_A if x['kind'] == k]),
                                          len([x for x in FINAL_B if x['kind'] == k])))
print('输出 -> deliver/补实验方案_损失与架构_20261001.md / 补实验_run清单.csv / 补实验_launch.sh')

# ---------------- ★ 自校验：每条计划名必须被生成器的 norm() 正确解析 ----------------
# 命名错 ⇒ 新 run 落不进目标格 ⇒ 整批白跑。故在**生成方案时**就断言。
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location('_bb', os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                         '01_build_base.py'))
# 不执行整个 builder（它会重建底座）；只把 norm() 抠出来
_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '01_build_base.py'),
            encoding='utf-8').read()
_ns = {'re': re}
exec(_src[_src.index('def norm('):_src.index('def ', _src.index('def norm(') + 5)], _ns)
_norm = _ns['norm']


def validate(plan_rows):
    bad = []
    for x in plan_rows:
        d = _norm(x['name'])
        want_arm = 'lr005' if x['lr'] == 0.005 else 'base'
        prob = []
        if d['family'] != x['cell'].split('/')[1] and x['kind'] == 'L':
            prob.append('family=%r 期望 %r' % (d['family'], x['cell'].split('/')[1]))
        if d['lr_arm'] != want_arm:
            prob.append('lr_arm=%r 期望 %r' % (d['lr_arm'], want_arm))
        if d['epochs_nominal'] != x['epochs']:
            prob.append('epochs=%r 期望 %d' % (d['epochs_nominal'], x['epochs']))
        if d['seed'] != x['seed'] or d['seed_kind'] != 'shuffle':
            prob.append('seed=%r/%s 期望 %d/shuffle' % (d['seed'], d['seed_kind'], x['seed']))
        if prob:
            bad.append((x['name'], prob))
    return bad


for _n in (5, 10):
    _bad = validate(dedup(plan(_n), exists))
    print('[自校验 n=%d] 名字解析异常 %d 条%s' % (_n, len(_bad), '' if not _bad else ' ❌'))
    for _nm, _pb in _bad[:6]:
        print('    %-52s %s' % (_nm, '; '.join(_pb)))
