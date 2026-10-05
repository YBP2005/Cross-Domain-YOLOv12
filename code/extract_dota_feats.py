
# -*- coding: utf-8 -*-
"""extract_dota_feats.py — 提取 dota 语料的 ResNet-18 特征（补齐 s-OTDD 唯一缺的语料）。

**口径必须与被复用的缓存逐项一致**（否则新旧不可比）——沿 `feature_shift_multi.py`：
  * ResNet-18(IMAGENET1K_V1)，去掉 fc（`nn.Sequential(*list(model.children())[:-1])`）⇒ 512 维 avgpool；
  * `Resize((224,224))` → `ToTensor` → ImageNet 归一化 `[0.485,0.456,0.406]/[0.229,0.224,0.225]`；
  * **CPU**（`DEVICE='cpu'`，与既有做法一致：不抢训练 GPU）；
  * `MAX_N=4000`、文件名 `sorted()` 取前 N、batch 16；
  * 标签 = 「该图 txt 是否存在**任意**目标框」（与 `feature_shift_multi.py` 的 `n_boxes>0` 一致）。

**划分口径（已实测判定）**：既有缓存用的是**完整 `images/train`**，不是 20% 子集 ——
  `feat_dota15_tr(1411)` 对应 `dota15_yolo/images/train(1411)` 而**非** `train_dota15_20p(282)`；
  同理 `visdrone_tr(≤4000)`/`aitod_tr(≤4000)`。⇒ 本脚本对 dota 也用 **`images/train` + `labels/train`**。

★ **自证**：脚本会先对 `dota15_tr` 重算并与磁盘缓存**逐位比对**；不一致就停下不写新文件
  （防止"用一把没人校验过的尺子"）。
"""
import os, sys, time
import numpy as np
import torch
import torch.nn as nn
import torchvision
from torchvision import transforms
from PIL import Image

OUT = '/workspace/otdd_results'
DEVICE = 'cpu'
MAX_N = 4000
BATCH = 16
# 与 feature_shift_multi.py 的 DATASETS 同构
IMG_DIR = '/root/datasets_mask/dota_yolo/images/train'
LBL_DIR = '/root/datasets_mask/dota_yolo/labels/train'
# 自证用的对照语料（磁盘上已有缓存）
CHECK_TAG, CHECK_IMG, CHECK_LBL = ('dota15_tr',
                                   '/root/datasets_mask/dota15_yolo/images/train',
                                   '/root/datasets_mask/dota15_yolo/labels/train')

model = torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.IMAGENET1K_V1)
model = nn.Sequential(*list(model.children())[:-1])
model.eval().to(DEVICE)
tf = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor(),
                         transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])


def list_imgs(d):
    return sorted(f for f in os.listdir(d) if f.lower().endswith(('.jpg', '.jpeg', '.png')))


def extract(img_dir, files, max_n=MAX_N):
    files = files[:max_n]
    feats = []
    t0 = time.time()
    with torch.no_grad():
        for i in range(0, len(files), BATCH):
            batch = []
            for f in files[i:i + BATCH]:
                try:
                    batch.append(tf(Image.open(os.path.join(img_dir, f)).convert('RGB')))
                except Exception:
                    pass
            if not batch:
                continue
            feats.append(model(torch.stack(batch).to(DEVICE)).flatten(1).numpy())
            if (i // BATCH) % 20 == 0:
                print('  %d/%d  %.1f min' % (i, len(files), (time.time() - t0) / 60), flush=True)
    return np.concatenate(feats, 0) if feats else np.zeros((0, 512))


def label_of(lbl_dir, files):
    y = np.zeros(len(files), dtype=np.int64)
    for i, f in enumerate(files):
        lp = os.path.join(lbl_dir, os.path.splitext(f)[0] + '.txt')
        if os.path.exists(lp) and sum(1 for _ in open(lp)) > 0:
            y[i] = 1
    return y


def main():
    # ---- 步骤 0：自证（重算 dota15_tr 并与缓存逐位比对） ----
    print('=== 步骤 0：自证（用同一套参数重算 %s）===' % CHECK_TAG, flush=True)
    cf = list_imgs(CHECK_IMG)
    F = extract(CHECK_IMG, cf)
    y = label_of(CHECK_LBL, cf)
    ref_f = np.load(f'{OUT}/feat_{CHECK_TAG}.npy')
    ref_y = np.load(f'{OUT}/lab_{CHECK_TAG}.npy')
    same_shape = (F.shape == ref_f.shape)
    maxdiff = float(np.abs(F - ref_f).max()) if same_shape else float('nan')
    print('  重算 shape=%s  缓存 shape=%s' % (F.shape, ref_f.shape), flush=True)
    print('  特征最大绝对差 = %.3e    标签一致 = %s' % (maxdiff, bool(np.array_equal(y, ref_y))), flush=True)
    if (not same_shape) or (not np.isfinite(maxdiff)) or maxdiff > 1e-4 or not np.array_equal(y, ref_y):
        print('*** ★自证失败：重算与缓存不一致 ⇒ 口径不同，拒绝提取 dota 特征 ***', flush=True)
        return 1
    print('  ✅ 自证通过（逐位一致）⇒ 参数与既有缓存同源', flush=True)

    # ---- 步骤 1：提取 dota ----
    print('=== 步骤 1：提取 dota（%s）===' % IMG_DIR, flush=True)
    df = list_imgs(IMG_DIR)
    print('  dota train 图数 = %d（取前 %d）' % (len(df), min(len(df), MAX_N)), flush=True)
    Fd = extract(IMG_DIR, df)
    yd = label_of(LBL_DIR, df)
    print('  dota 特征 %s，有目标图 %d/%d (%.1f%%)'
          % (Fd.shape, int(yd.sum()), len(yd), 100.0 * yd.mean()), flush=True)
    np.save(f'{OUT}/feat_dota_tr.npy', Fd)
    np.save(f'{OUT}/lab_dota_tr.npy', yd)
    print('  已写 %s/feat_dota_tr.npy 与 lab_dota_tr.npy' % OUT, flush=True)
    print('DONE', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
