# -*- coding: utf-8 -*-
"""train_obj_aug.py — A5 控制实验专用训练脚本（= train_obj.py + --aug-seed 增广 RNG 隔离旋钮）

背景（第 9 轮 glm53 A5）：稿件的 σ 只覆盖**数据顺序**这一个噪声源（`--shuffle-seed` 置换 train
im_files），增广 RNG 未变（ultralytics 8.4.120 的 DataLoader generator 固定为
`manual_seed(6148914691236517205 + RANK)`，故 worker 种子确定 → 增广逐轮全同）。本脚本提供
`--aug-seed N`：只把 **worker 进程的 RNG**（random / numpy / torch）改为由 N 导出，
DataLoader generator、sampler、shuffle-seed 置换、初始化种子全部不动 —— 于是数据顺序与初始化
逐位相同，唯一变化的是**增广随机性**。用于量化 σ 中被排除的那个分量。

用法（与 train_obj.py 相同，多一个 --aug-seed）：
  python train_obj_aug.py --loss shapeiou --epochs 100 --name a5_base_aug101_s42n \
      --data /root/sfchd_20p_b.yaml --pretrain /workspace/weights/shwd2sf_pretrain.pt \
      --shuffle-seed 42 --aug-seed 101 [--lr 0.005]
"""
import sys, os, argparse, json, time
sys.path.insert(0, '/workspace/module_sweep')
import modules  # noqa: F401
import losses
from ultralytics import YOLO

PROJECT = '/workspace/runs'


def _install_shuffle_seed(seed):
    """（与 train_obj.py 相同）确定性置换 train split 的 im_files/labels。"""
    from ultralytics.data.dataset import YOLODataset
    _orig_init = YOLODataset.__init__

    def _patched_init(self, *a, **kw):
        _orig_init(self, *a, **kw)
        if getattr(self, 'augment', False) and getattr(self, 'im_files', None):
            import random as _random
            n = len(self.im_files)
            if n > 1:
                rng = _random.Random(seed)
                idx = list(range(n))
                rng.shuffle(idx)
                self.im_files = [self.im_files[i] for i in idx]
                if getattr(self, 'labels', None) is not None:
                    self.labels = [self.labels[i] for i in idx]
                print(f'[shuffle-seed {seed}] permuted {n} train im_files', flush=True)

    YOLODataset.__init__ = _patched_init


def _install_aug_seed(aug_seed):
    """只替换 worker 进程的 RNG 播种：DataLoader generator/sampler 不动。"""
    import numpy as _np
    import random as _random
    import torch as _torch
    import ultralytics.data.build as _build

    def _seed_worker(worker_id):
        ws = (int(aug_seed) * 100003 + int(worker_id)) % 2 ** 32
        _np.random.seed(ws)
        _random.seed(ws)
        _torch.manual_seed(ws)
        print(f'[aug-seed {aug_seed}] worker {worker_id} seeded {ws}', flush=True)

    _build.seed_worker = _seed_worker
    print(f'[aug-seed {aug_seed}] patched ultralytics.data.build.seed_worker', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--loss', required=True)
    ap.add_argument('--epochs', type=int, default=100)
    ap.add_argument('--name', required=True)
    ap.add_argument('--data', required=True)
    ap.add_argument('--pretrain', required=True)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--lr', type=float, default=0.001)
    ap.add_argument('--coslr', action='store_true')
    ap.add_argument('--shuffle-seed', type=int, default=None)
    ap.add_argument('--aug-seed', type=int, required=True)
    ap.add_argument('--optimizer', default='SGD')
    ap.add_argument('--outcsv', default='/workspace/a5_results.csv')
    args = ap.parse_args()

    if args.shuffle_seed is not None:
        _install_shuffle_seed(args.shuffle_seed)
    _install_aug_seed(args.aug_seed)

    losses.patch_loss(args.loss)
    print(f'[loss] patched -> {args.loss}', flush=True)
    m = YOLO(args.pretrain)
    m.train(data=args.data, epochs=args.epochs, batch=32, imgsz=640, device=0, workers=16,
            project=PROJECT, name=args.name, exist_ok=True,
            optimizer=args.optimizer, lr0=args.lr, momentum=0.925, weight_decay=0.0001,
            warmup_epochs=3, seed=args.seed, pretrained=True, amp=False,
            cos_lr=args.coslr, save_period=5, plots=False, verbose=True)
    best = os.path.join(PROJECT, args.name, 'weights', 'best.pt')
    if not os.path.exists(best):
        best = os.path.join(PROJECT, args.name, 'weights', 'last.pt')
    mm = YOLO(best)
    res = mm.val(data=args.data, split='test', batch=32, imgsz=640, device=0, plots=False, verbose=False)
    line = (f'{args.name},{args.loss},{args.epochs},{args.lr},{args.shuffle_seed},{args.aug_seed},'
            f'{res.box.map50:.4f},{res.box.map:.4f},{res.box.mp:.4f},{res.box.mr:.4f}')
    print('RESULT', line, flush=True)
    with open(args.outcsv, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


if __name__ == '__main__':
    main()
