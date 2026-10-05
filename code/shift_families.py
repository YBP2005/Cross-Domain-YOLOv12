# -*- coding: utf-8 -*-
"""shift_families.py —— 计算「同一族内各数据集」的域偏移（Wasserstein + s-OTDD）。

协议与已发布表 feature_shift_multi.py **逐项一致**（阳性对照 9/9 已复现，Δ≤5e-5）：
  ResNet18(IMAGENET1K_V1) 去 fc -> 512维 avgpool
  resize 224x224 + ImageNet 归一化
  样本上限 4000，文件名 sorted 后取前 N
  sliced W2: n_slices=200, seed=42 ; sliced W1: n_slices=100, seed=42
  对齐 n = min(len(F1), len(F2)) 后再算
  标签项: 二值(有框/无框) 类频率 x 类中心欧氏距离平方
  s-OTDD = sqrt(W2^2 + 标签项)

两种「同域基线」口径（明确区分，写入输出）：
  A) dir 内    : 该语料自带的 train vs test/val（与已发布表同口径）
  B) 子样本内  : 单目录语料用 seed=42 随机对半分（与 A 篇「子样本距离」同义）

CPU-only，不占 GPU。缓存到 /workspace/otdd_results/feat_<name>.npy（与既有缓存同名空间）。
"""
import os
import sys
import time
import json
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import torch
import torch.nn as nn
import torchvision
from torchvision import transforms
from PIL import Image

OUT = '/workspace/otdd_results'
os.makedirs(OUT, exist_ok=True)
MAX_N = 4000
SEED = 42

D = '/root/datasets_mask'
W = '/root/workspace/data'

# 名称 -> (images 目录, labels 目录, 族)
DATASETS = {
    # ---- helmet 族（安全帽）----
    'shwd':        (W + '/SHWD/images',                          W + '/SHWD/labels', 1),
    'pp':          (W + '/HelmetDetection/images',               W + '/HelmetDetection/labels', 1),
    'sfchd_pool':  (W + '/SFCHD_split/train/50_percent/images',  W + '/SFCHD_split/train/50_percent/labels', 1),
    'sfchd_test':  (W + '/SFCHD_split/test/images',              W + '/SFCHD_split/test/labels', 1),
    'sfchd_cc_tr': (W + '/SFCHD_crosscam/train9555/images',      W + '/SFCHD_crosscam/train9555/labels', 1),
    'sfchd_cc_te': (W + '/SFCHD_crosscam/test2511/images',       W + '/SFCHD_crosscam/test2511/labels', 1),
    'gdut':        (W + '/gdut_hwd/images/train',                W + '/gdut_hwd/labels/train', 1),
    'chv':         (W + '/chv/images/train',                     W + '/chv/labels/train', 1),
    'roboflow':    (W + '/roboflow_hardhat/images/train',        W + '/roboflow_hardhat/labels/train', 1),
    # ---- defect 族（工业缺陷）----
    'pcb':         (D + '/pcb_yolo/images/train',                D + '/pcb_yolo/labels/train', 2),
    'neu':         (W + '/neu_det/images/train',                 W + '/neu_det/labels/train', 2),
    'gc10':        (W + '/gc10_det/images/train',                W + '/gc10_det/labels/train', 2),
    # ---- mask 族（口罩/面罩）----
    'mask_tr':     (D + '/mask_clean/images/train',              D + '/mask_clean/labels/train', 3),
    'mende_tr':    (D + '/mendeley_yolo/images/train',           D + '/mendeley_yolo/labels/train', 3),
    # ---- smoke 族（烟火）----
    'smoke_ker':   (D + '/smoke_keremberke/images/train',        D + '/smoke_keremberke/labels/train', 4),
    'firesmoke_tr':(D + '/firesmoke_clean/images/train',         D + '/firesmoke_clean/labels/train', 4),
}

# 跨数据集对：(标签, A, B, 族号)
CROSS = [
    # ---- helmet：源 -> 目标（战役的轴）----
    ('shwd -> sfchd_pool',      'shwd', 'sfchd_pool', 1),
    ('pp -> sfchd_pool',        'pp', 'sfchd_pool', 1),
    ('gdut -> sfchd_pool',      'gdut', 'sfchd_pool', 1),
    ('chv -> sfchd_pool',       'chv', 'sfchd_pool', 1),
    ('roboflow -> sfchd_pool',  'roboflow', 'sfchd_pool', 1),
    ('sfchd_pool -> shwd',      'sfchd_pool', 'shwd', 1),
    # ---- helmet：源内两半 / 同族其它 ----
    ('shwd -> pp',              'shwd', 'pp', 1),
    ('pp -> shwd',              'pp', 'shwd', 1),
    ('gdut -> chv',             'gdut', 'chv', 1),
    ('chv -> gdut',             'chv', 'gdut', 1),
    ('gdut -> roboflow',        'gdut', 'roboflow', 1),
    ('roboflow -> gdut',        'roboflow', 'gdut', 1),
    # ---- helmet：★ 两套协议的偏移对比（G1 的关键数字）----
    ('[协议] sfchd 随机对半 train->test',      'sfchd_pool', 'sfchd_test', 1),
    ('[协议] sfchd 跨摄像头 train9555->test2511', 'sfchd_cc_tr', 'sfchd_cc_te', 1),
    ('[协议] sfchd 跨摄像头 train9555->随机test', 'sfchd_cc_tr', 'sfchd_test', 1),
    # ---- defect ----
    ('pcb -> neu',   'pcb', 'neu', 2),
    ('neu -> pcb',   'neu', 'pcb', 2),
    ('pcb -> gc10',  'pcb', 'gc10', 2),
    ('gc10 -> pcb',  'gc10', 'pcb', 2),
    ('neu -> gc10',  'neu', 'gc10', 2),
    ('gc10 -> neu',  'gc10', 'neu', 2),
    # ---- mask（补三角形缺边）----
    ('mask_tr -> mende_tr', 'mask_tr', 'mende_tr', 3),
    ('mende_tr -> mask_tr', 'mende_tr', 'mask_tr', 3),
    # ---- smoke（补反向）----
    ('firesmoke_tr -> smoke_ker', 'firesmoke_tr', 'smoke_ker', 4),
]

# dir 内基线：语料自带 train vs test/val
IN_DIR = [
    ('sfchd 随机对半 内',   'sfchd_pool', 'sfchd_test', 1),
    ('mask 内',             'mask_tr', 'mask_tr', 3),   # 占位，下面用 mask test 目录
]
# 上面 mask 的 test 目录不在 DATASETS 里，单独补一个
DATASETS['mask_te'] = (D + '/mask_clean/images/test', D + '/mask_clean/labels/test', 3)
IN_DIR = [('mask 内', 'mask_tr', 'mask_te', 3)]

# 子样本内基线：单目录语料 seed=42 随机对半
SUB = ['shwd', 'pp', 'sfchd_cc_tr', 'sfchd_cc_te', 'gdut', 'chv', 'roboflow',
       'pcb', 'neu', 'gc10', 'mende_tr', 'smoke_ker', 'firesmoke_tr']

model = torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.IMAGENET1K_V1)
model = nn.Sequential(*list(model.children())[:-1])
model.eval()
try:
    torch.set_num_threads(int(os.environ.get('SHIFT_THREADS', '12')))
except Exception:
    pass
tf = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor(),
                         transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])


def load_ds(name):
    cf = os.path.join(OUT, 'feat_%s.npy' % name)
    cl = os.path.join(OUT, 'lab_%s.npy' % name)
    if os.path.exists(cf) and os.path.exists(cl):
        return np.load(cf), np.load(cl), 'cache'
    img_d, lab_d, _ = DATASETS[name]
    files = sorted(f for f in os.listdir(img_d)
                   if f.lower().endswith(('.jpg', '.jpeg', '.png')))[:MAX_N]
    feats, t0 = [], time.time()
    with torch.no_grad():
        for i in range(0, len(files), 32):
            batch = []
            for f in files[i:i + 32]:
                try:
                    batch.append(tf(Image.open(os.path.join(img_d, f)).convert('RGB')))
                except Exception:
                    pass
            if not batch:
                continue
            feats.append(model(torch.stack(batch)).flatten(1).numpy())
            if (i // 32) % 20 == 0:
                print('  [%s] %d/%d %.1fmin' % (name, i, len(files), (time.time() - t0) / 60), flush=True)
    F = np.concatenate(feats, 0) if feats else np.zeros((0, 512))
    labels = np.zeros(len(files), dtype=np.int64)
    for i, f in enumerate(files):
        lp = os.path.join(lab_d, os.path.splitext(f)[0] + '.txt')
        if os.path.exists(lp):
            labels[i] = 1 if sum(1 for _ in open(lp)) > 0 else 0
    np.save(cf, F)
    np.save(cl, labels)
    print('  [%s] %d 张 -> %s 有目标 %d' % (name, len(files), F.shape, labels.sum()), flush=True)
    return F, labels, 'new'


def sliced_w2(F1, F2, n_slices=200, seed=SEED):
    rng = np.random.default_rng(seed)
    d = F1.shape[1]
    sl = rng.normal(size=(n_slices, d))
    sl /= np.linalg.norm(sl, axis=1, keepdims=True)
    s = 0.0
    for th in sl:
        z1, z2 = F1 @ th, F2 @ th
        s += ((np.sort(z1) - np.sort(z2)) ** 2).mean()
    return np.sqrt(s / n_slices)


def sliced_w1(F1, F2, n_slices=100, seed=SEED):
    rng = np.random.default_rng(seed)
    d = F1.shape[1]
    sl = rng.normal(size=(n_slices, d))
    sl /= np.linalg.norm(sl, axis=1, keepdims=True)
    s = 0.0
    for th in sl:
        z1, z2 = np.sort(F1 @ th), np.sort(F2 @ th)
        s += np.abs(z1 - z2).mean()
    return s / n_slices


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


def one(F1, y1, F2, y2):
    n = min(len(F1), len(F2))
    F1n, F2n, y1n, y2n = F1[:n], F2[:n], y1[:n], y2[:n]
    w1 = sliced_w1(F1n, F2n)
    w2 = sliced_w2(F1n, F2n)
    lt = label_cost_term(y1n, y2n, F1n, F2n)
    return n, w1, w2, lt, float(np.sqrt(w2 ** 2 + lt))


print('===== 阶段1：特征提取 =====', flush=True)
cache = {}
t_all = time.time()
for name in DATASETS:
    try:
        F, y, src = load_ds(name)
        cache[name] = (F, y)
        print('  %-14s n=%-5d %s 有目标=%d' % (name, len(F), src, int(y.sum())), flush=True)
    except Exception as e:
        print('  %-14s FAIL %s' % (name, str(e)[:90]), flush=True)

print('===== 阶段2：配对计算 =====', flush=True)
rows = []


def add(kind, label, fam, A, B, F1, y1, F2, y2):
    n, w1, w2, lt, s = one(F1, y1, F2, y2)
    rows.append((kind, fam, label, A, B, n, w1, w2, lt, s))
    print('  [%s] %-42s n=%-5d W1=%.4f W2=%.4f 标签=%.4f sOTDD=%.4f' %
          (kind, label, n, w1, w2, lt, s), flush=True)


for label, a, b, fam in CROSS:
    if a in cache and b in cache:
        add('跨数据集', label, fam, a, b, cache[a][0], cache[a][1], cache[b][0], cache[b][1])
    else:
        print('  [跨数据集] %s 跳过（缺语料）' % label, flush=True)

for label, a, b, fam in IN_DIR:
    if a in cache and b in cache:
        add('dir内基线', label, fam, a, b, cache[a][0], cache[a][1], cache[b][0], cache[b][1])

for name in SUB:
    if name not in cache:
        continue
    F, y = cache[name]
    if len(F) < 200:
        continue
    rng = np.random.default_rng(SEED)
    idx = rng.permutation(len(F))
    h = len(F) // 2
    i1, i2 = idx[:h], idx[h:2 * h]
    add('子样本内', '%s 子样本(同域基线)' % name, DATASETS[name][2], name, name,
        F[i1], y[i1], F[i2], y[i2])

fam_name = {1: 'helmet', 2: 'defect', 3: 'mask', 4: 'smoke'}
csv = os.path.join(OUT, '家族内偏移.csv')
with open(csv, 'w', encoding='utf-8') as f:
    f.write('类型,族,对比对,n,特征W1,特征W2,标签项,sOTDD\n')
    for kind, fam, label, A, B, n, w1, w2, lt, s in rows:
        f.write('%s,%s,%s,%d,%.4f,%.4f,%.4f,%.4f\n' % (kind, fam_name.get(fam, fam), label, n, w1, w2, lt, s))

md = os.path.join(OUT, '家族内偏移.md')
with open(md, 'w', encoding='utf-8') as f:
    f.write('# 同一族内各数据集的域偏移（ResNet18 特征级，sliced，4000 上限，seed42）\n\n')
    f.write('协议与已发布 `feature_shift_multi.py` 逐项一致（阳性对照 9/9 复现，Δ≤5e-5）。\n')
    f.write('`s-OTDD = sqrt(W2^2 + 标签项)`；`子样本内` = 单目录语料 seed42 随机对半。\n\n')
    f.write('| 类型 | 族 | 对比对 | n | 特征W1 | 特征W2 | 标签项 | s-OTDD |\n|---|---|---|---|---|---|---|---|\n')
    for kind, fam, label, A, B, n, w1, w2, lt, s in rows:
        f.write('| %s | %s | %s | %d | %.4f | %.4f | %.4f | %.4f |\n' %
                (kind, fam_name.get(fam, fam), label, n, w1, w2, lt, s))

print('===== 完成：%d 行，用时 %.1f 分钟 =====' % (len(rows), (time.time() - t_all) / 60), flush=True)
print('CSV ->', csv)
print('MD  ->', md)
print('SHIFT_FAMILIES_DONE')
