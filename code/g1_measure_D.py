# -*- coding: utf-8 -*-
"""G1 的 D（域偏移）测量 —— **复用 shift_families.py 的协议实现，不重写**。

为什么要复用
------------
协议细节（ResNet18 去 fc → 512 维 avgpool、resize 224 + ImageNet 归一化、
样本上限 4000、文件名 sorted 前 N、sliced W2 n_slices=200 seed=42、
对齐 n=min、标签项 = 二值类频率 × 类中心欧氏距离平方、s-OTDD = sqrt(W2²+标签项)）
**任何一处写错都会让 D 不可比**。故本件**不重新实现**，而是：

  1. 读 `/workspace/shift_families.py` 的源码，**截断到 `rows = []` 之前**，
     `exec` 进本命名空间 ⇒ 直接拿到它**同一套** `extract()` / `one()` / `sliced_w2()` / `label_cost_term()`；
  2. 用同一套函数测 G1 的三个对；
  3. **阳性对照**：把已发布 `家族内偏移.csv` 里的两行（`shwd→sfchd_pool`、
     `pcb→neu`）**用同一进程重算**，与发布值逐位对比 ⇒ **Δ 必须很小**，否则本件一切数字作废。

产出
----
  /workspace/otdd_results/G1_D_measurement.csv      三个 G1 对的 D
  /workspace/otdd_results/G1_D_measurement.md       人读版 + 阳性对照表

用法（A 机，CPU-only，与训练并行）：
    /root/yolo_env/bin/python /root/g1_measure_D.py
"""
import io
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np  # noqa: E402

OUT = '/workspace/otdd_results'
SF = '/workspace/shift_families.py'
CSV_PUB = os.path.join(OUT, '家族内偏移.csv')

# ---------- 1) 复用 shift_families.py 的实现（截断到它自己开始算之前） ----------
src = io.open(SF, encoding='utf-8').read()
cut = src.index('rows = []')
head = src[:cut]
NS = {'__name__': '_sf_reuse'}
exec(compile(head, SF, 'exec'), NS)
one, load_ds, DATASETS = NS['one'], NS['load_ds'], NS['DATASETS']
print('已复用 shift_families.py 的实现（截断于 %d 字符）' % cut, flush=True)
print('可用函数：%s' % ', '.join(k for k in ('load_ds', 'one', 'sliced_w1', 'sliced_w2',
                                             'label_cost_term') if k in NS), flush=True)

# ---------- 2) G1 的四个数据集条目（路径已核实在位） ----------
AITOD = '/root/datasets/AI-TOD_yolo'
D15 = '/root/datasets_mask/dota15_yolo'
G1_SETS = {
    'dota15_tr':    (D15 + '/images/train_dota15_20p',  D15 + '/labels/train_dota15_20p', 5),
    'dota15_te':    (D15 + '/images/val',               D15 + '/labels/val',              5),
    'aitod_tr':     (AITOD + '/images/train_aitod_20p', AITOD + '/labels/train_aitod_20p', 6),
    'aitod_te':     (AITOD + '/images/val',             AITOD + '/labels/val',            6),
}
# ★ 把 G1 的四个条目**注入它自己的 DATASETS**，这样 load_ds() 直接可用（协议零改写）
DATASETS.update(G1_SETS)
G1_PAIRS = [
    ('C1/C2 (A0) dota15 -> dota15',  'dota15_tr', 'dota15_te'),
    ('C3/C4 (A1) dota15 -> aitod',   'dota15_tr', 'aitod_tr'),
    ('（参考）aitod 自域',            'aitod_tr',  'aitod_te'),
]
# 阳性对照：已发布值（来自 家族内偏移.csv）
CONTROLS = [
    ('shwd -> sfchd_pool', 'shwd', 'sfchd_pool', 11.2658),
    ('pcb -> neu',          'pcb',  'neu',        23.2931),
]
CACHE = dict(NS.get('cache', {}))


def get(tag):
    r"""走 `shift_families.load_ds()` —— 它自己会先查缓存，缺了才按协议抽并写回缓存。

    ⚠ 第一版我按 `extract(tag, img_d, lbl_d)` 调，但**它没有 extract 这个函数**：
      抽特征的内联逻辑就写在 `load_ds()` 里，且它吃的是 `DATASETS[name]` 三元组。
      ⇒ 改为**把 G1 条目注入 DATASETS，再原样调 load_ds**，一行协议实现都不改。
    """
    F, y, src = load_ds(tag)
    print('      [%s] %s 张（%s）' % (tag, len(F), src), flush=True)
    return F, y


def meas(label, a, b):
    F1, y1 = get(a)
    F2, y2 = get(b)
    n, w1, w2, lt, s = one(F1, y1, F2, y2)
    print('  %-32s n=%-5d W1=%.4f W2=%.4f 标签=%.4f  s-OTDD(D)=%.4f'
          % (label, n, w1, w2, lt, s), flush=True)
    return dict(label=label, a=a, b=b, n=n, w1=w1, w2=w2, lt=lt, D=s)


def main():
    t0 = time.time()
    rows, ctrl = [], []

    print('\n=== 阳性对照（与已发布 家族内偏移.csv 对撞）===', flush=True)
    for label, a, b, pub in CONTROLS:
        try:
            r = meas('[对照] ' + label, a, b)
            d = abs(r['D'] - pub)
            r['published'] = pub
            r['delta'] = d
            ctrl.append(r)
            print('      发布值=%.4f  重算=%.4f  Δ=%.4f  %s'
                  % (pub, r['D'], d, 'OK' if d <= 5e-5 else '★超差'), flush=True)
        except Exception as ex:
            print('      [对照] %s 失败：%s' % (label, ex), flush=True)

    print('\n=== G1 的 D ===', flush=True)
    for label, a, b in G1_PAIRS:
        try:
            rows.append(meas(label, a, b))
        except Exception as ex:
            print('      %s 失败：%s' % (label, ex), flush=True)

    # ---- 落盘 ----
    csvp = os.path.join(OUT, 'G1_D_measurement.csv')
    with io.open(csvp, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('类型,对比对,A,B,n,特征W1,特征W2,标签项,sOTDD_D\n')
        for r in ctrl:
            fh.write('阳性对照,%s,%s,%s,%d,%.4f,%.4f,%.4f,%.4f\n'
                     % (r['label'], r['a'], r['b'], r['n'], r['w1'], r['w2'], r['lt'], r['D']))
        for r in rows:
            fh.write('G1,%s,%s,%s,%d,%.4f,%.4f,%.4f,%.4f\n'
                     % (r['label'], r['a'], r['b'], r['n'], r['w1'], r['w2'], r['lt'], r['D']))
    mdp = os.path.join(OUT, 'G1_D_measurement.md')
    with io.open(mdp, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('# G1 的域偏移 D 测量（复用 shift_families.py 协议实现）\n\n')
        fh.write('时间 %.0f s ｜ 协议：ResNet18-512 / resize224+IN归一 / cap4000 / sorted前N / '
                 'sliced W2 200 seed42 / s-OTDD=sqrt(W2^2+标签项)\n\n' % (time.time() - t0))
        fh.write('## 阳性对照（与已发布 `家族内偏移.csv` 对撞）\n\n')
        fh.write('| 对比对 | 发布值 | 本次重算 | Δ | 判定 |\n|---|---:|---:|---:|---|\n')
        for r in ctrl:
            fh.write('| %s | %.4f | %.4f | %.4f | %s |\n'
                     % (r['label'], r['published'], r['D'], r['delta'],
                        'OK' if r['delta'] <= 5e-5 else '**超差**'))
        fh.write('\n## G1 的 D\n\n| 对比对 | A | B | n | 特征W1 | 特征W2 | 标签项 | **D** |\n')
        fh.write('|---|---|---|---:|---:|---:|---:|---:|\n')
        for r in rows:
            fh.write('| %s | %s | %s | %d | %.4f | %.4f | %.4f | **%.4f** |\n'
                     % (r['label'], r['a'], r['b'], r['n'], r['w1'], r['w2'], r['lt'], r['D']))
        fh.write('\n★ **时点声明**：本次测量**晚于训练开跑**（A 机 G1 队列已于同日启动）。\n'
                 '它是 outcome-blind 的（测量过程不看任何训练结果），但**不早于开跑**，'
                 '故在稿内若引用，必须如实标注其时点，不得写成"事前测量"。\n')
    print('\nCSV -> %s\nMD  -> %s' % (csvp, mdp), flush=True)
    print('总用时 %.1f 分钟' % ((time.time() - t0) / 60), flush=True)
    print('G1_D_DONE', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
