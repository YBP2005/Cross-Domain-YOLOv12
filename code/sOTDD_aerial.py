
# -*- coding: utf-8 -*-
"""sOTDD_aerial.py — 用**已发布表的同一口径**补算 B 管线四个语料的 s-OTDD。

来源与口径（逐项对齐 `feature_shift_multi.py`，即产出论文 Table S1 那张表的脚本）：
  * 特征：ResNet-18(IMAGENET1K_V1) avgpool 512 维、resize 224、ImageNet 归一化，**已缓存在
    /workspace/otdd_results/feat_*.npy**（本次不重新提特征）；
  * `sliced_w2`：**200 个**随机投影、`seed=42`、投影后排序、`((z1s-z2s)**2).mean()`，
    然后 **sqrt**（即返回的是 W2，不是 W2²）；
  * `label_cost_term`：类频率 × 类中心欧氏距离**平方**（float64，原实现如此，以保持位级可比）；
  * 等权离散测度：两集**截断到 n=min(n1,n2)**（原实现 `n = min(len(F1), len(F2))`）；
  * `s-OTDD = sqrt(W2**2 + label_term)`。

★ 阳性对照（硬闸门）：先算 `MAFA→mask`，**必须复现已发布的 7.1894**（容差 1e-3）。
  复现不上就**拒绝输出任何新数字**。
"""
import os, sys, csv, time
import numpy as np

OUT = '/workspace/otdd_results'
SEED = 42
N_SLICES = 200   # 已发布表的取值（注意：不是 v2 的 500）
TOL = 1e-3
PUBLISHED_VALIDATE = ('mafa', 'mask_train', 7.1894)

PAIRS = [
    # (标签, 源 tag, 目标 tag, 方向说明)
    ('VALIDATE MAFA->mask',        'mafa',        'mask_train'),
    # ---- 先算的 B 管线三对（第三格所在）----
    ('dota15_tr->aitod_tr',        'dota15_tr',   'aitod_tr'),
    ('aitod_tr->visdrone_tr',      'aitod_tr',    'visdrone_tr'),
    ('visdrone_tr->dota15_tr',     'visdrone_tr', 'dota15_tr'),
    ('dota15_val->aitod_tr',       'dota15_val',  'aitod_tr'),
    ('aitod_tr->dota15_tr',        'aitod_tr',    'dota15_tr'),
    ('visdrone_tr->aitod_tr',      'visdrone_tr', 'aitod_tr'),
    ('dota15_val->visdrone_tr',    'dota15_val',  'visdrone_tr'),
    ('visdrone_te->dota15_val',    'visdrone_te', 'dota15_val'),
    # ---- ★ 本轮新增：dota 语料（唯一需新提特征的语料，已自证同源）----
    ('dota_tr->aitod_tr',          'dota_tr',     'aitod_tr'),
    ('dota_tr->visdrone_tr',       'dota_tr',     'visdrone_tr'),
    ('dota_tr->dota15_tr',         'dota_tr',     'dota15_tr'),
    ('dota_tr->aitod_val',         'dota_tr',     'aitod_val'),
    ('dota_tr->dota15_val',        'dota_tr',     'dota15_val'),
]


def load(tag):
    f = np.load(f'{OUT}/feat_{tag}.npy')
    y = None
    for pref in ('lab_', 'label_'):
        p = f'{OUT}/{pref}{tag}.npy'
        if os.path.exists(p):
            y = np.load(p); break
    if y is None:
        raise FileNotFoundError(f'no labels for {tag}')
    return f, y.astype(np.int64)


def sliced_w2(F1, F2, n_slices=N_SLICES, seed=SEED):
    rng = np.random.default_rng(seed)
    d = F1.shape[1]
    slices = rng.normal(size=(n_slices, d))
    slices /= np.linalg.norm(slices, axis=1, keepdims=True)
    n = min(len(F1), len(F2))
    A, B = F1[:n], F2[:n]
    s = 0.0
    for th in slices:
        z1, z2 = A @ th, B @ th
        s += ((np.sort(z1) - np.sort(z2)) ** 2).mean()
    return float(np.sqrt(s / n_slices))


def label_cost_term(y1, y2, F1, F2):
    mu1 = {c: F1[y1 == c].mean(0) for c in np.unique(y1)}
    mu2 = {c: F2[y2 == c].mean(0) for c in np.unique(y2)}
    p1 = np.bincount(y1, minlength=2) / len(y1)
    p2 = np.bincount(y2, minlength=2) / len(y2)
    s = 0.0
    for a in np.unique(y1):
        for b in np.unique(y2):
            s += p1[a] * p2[b] * (np.linalg.norm(mu1[a] - mu2[b]) ** 2)
    return s


def main():
    cache = {}
    rows = []
    for name, a, b in PAIRS:
        for t in (a, b):
            if t not in cache:
                try:
                    cache[t] = load(t)
                except Exception as ex:
                    print(f'MISSING {t}: {ex}', flush=True)
                    cache[t] = None
        if cache[a] is None or cache[b] is None:
            print(f'SKIP {name} (missing features)', flush=True); continue
        F1, y1 = cache[a]; F2, y2 = cache[b]
        t0 = time.time()
        w2 = sliced_w2(F1, F2)
        lt = label_cost_term(y1, y2, F1, F2)
        D = float(np.sqrt(w2 ** 2 + lt))
        rows.append((name, len(F1), len(F2), round(w2, 4), round(lt, 4), round(D, 4)))
        print('%-32s n=%d/%d  W2=%.4f  label=%.4f  s-OTDD=%.4f  (%.1fs)'
              % (name, len(F1), len(F2), w2, lt, D, time.time() - t0), flush=True)

        # ★ 阳性对照：MAFA→mask 必须复现已发布的 7.1894，否则拒绝继续
        if name.startswith('VALIDATE'):
            if abs(D - PUBLISHED_VALIDATE[2]) > TOL:
                print('*** ★POSITIVE CONTROL FAILED: MAFA->mask = %.4f, 已发布值 = %.4f '
                      '(差 %.4f > %.4f) ⇒ 口径不一致，拒绝输出任何新数字 ***'
                      % (D, PUBLISHED_VALIDATE[2], abs(D - PUBLISHED_VALIDATE[2]), TOL), flush=True)
                return 1
            print('== 阳性对照通过：复现已发布 MAFA->mask = %.4f（容差 %g）==' % (D, TOL), flush=True)

    with open(f'{OUT}/sotdd_aerial.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['pair', 'n1', 'n2', 'W2_sliced200', 'label_term', 's_OTDD'])
        w.writerows(rows)
    print('DONE -> %s/sotdd_aerial.csv' % OUT, flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
