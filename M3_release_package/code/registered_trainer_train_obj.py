# -*- coding: utf-8 -*-
"""B 篇多对象通用训练 v2（seed 修复版）
用法：python train_obj.py --loss shapeiou --epochs 30 --name mask_pretrain \
      --data xxx.yaml --pretrain xxx.pt [--seed N] [--shuffle-seed N] [--optimizer SGD|AdamW]

v2 新增（seed 机制修复，2026-09-05）：
- --shuffle-seed N：对 train split 的 im_files/labels 做确定性置换（random.Random(N)）。
  绕过 ultralytics 8.4.120 数据管道 RNG 未与 args.seed 挂钩的问题（mende/SFCHD 数据上
  不同 --seed 产生逐 epoch 全同重放）：不同 --shuffle-seed 必产生不同训练序列；
  同 --shuffle-seed 必可复现（同 seed 全同）。默认 None = 行为与 v1 完全一致。
- --optimizer：透传 ultralytics optimizer（默认 SGD，可 AdamW）。
"""
import sys, os, argparse
sys.path.insert(0, '/workspace/module_sweep')
import modules  # noqa: F401
import losses
from ultralytics import YOLO

PROJECT = '/workspace/runs'


def _install_shuffle_seed(seed):
    """Monkey-patch YOLODataset.__init__: deterministically permute train split
    im_files/labels by seed. Val split (augment=False) untouched."""
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--loss', required=True, help='shapeiou/pws/sns/css/jps')
    ap.add_argument('--epochs', type=int, default=100)
    ap.add_argument('--name', required=True)
    ap.add_argument('--data', required=True, help='对象 yaml（含 test split）')
    ap.add_argument('--pretrain', required=True, help='预训练权重（对象自训 / COCO yolo12n.pt）')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--lr', type=float, default=0.001)
    ap.add_argument('--coslr', action='store_true')
    ap.add_argument('--shuffle-seed', type=int, default=None,
                    help='train im_files 确定性置换种子（seed 机制修复；None=不置换）')
    ap.add_argument('--optimizer', default='SGD', help='SGD / AdamW')
    args = ap.parse_args()

    if args.shuffle_seed is not None:
        _install_shuffle_seed(args.shuffle_seed)

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
    line = f'{args.name},{args.loss},{args.epochs},{res.box.map50:.4f},{res.box.map:.4f},{res.box.mp:.4f},{res.box.mr:.4f}'
    print('RESULT', line, flush=True)
    with open('/workspace/sio_b_results.csv', 'a', encoding='utf-8') as f:
        f.write(line + '\n')


if __name__ == '__main__':
    main()
