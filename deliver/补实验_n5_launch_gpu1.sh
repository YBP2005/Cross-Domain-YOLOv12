#!/usr/bin/env bash
# 补实验 设计 A（队列 1 / 2，n=5，38 条）—— 自动生成，勿手改
# 用法：bash 补实验_n5_launch_gpu1.sh
# 驱动内 device=0 是硬编码 => 本队列用 CUDA_VISIBLE_DEVICES 只暴露一张卡，
# 使 device=0 落到物理卡 1。不要改驱动去传 --device（会破坏配方一致性）。
set -u
export CUDA_VISIBLE_DEVICES=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY=/usr/local/miniconda3/envs/yolo_arch/bin/python
LOG=/workspace/_supp_n5_gpu1.log
FAIL=/workspace/_supp_failed.log
exec 8>/workspace/_supp_n5_gpu1.lock
flock -n 8 || { echo '已有本队列实例，退出'; exit 0; }
cd /workspace || exit 1

echo "[$(ts)] 2/38 r10_prior_lr005_100ep_3way_s43n" | tee -a "$LOG"
if [ -d /workspace/runs/r10_prior_lr005_100ep_3way_s43n ]; then echo "  SKIP r10_prior_lr005_100ep_3way_s43n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_lr005_100ep_3way_s43n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 43 --lr 0.005 || echo "FAILED r10_prior_lr005_100ep_3way_s43n" >> "$FAIL"; fi
echo "[$(ts)] 4/38 r10_prior_sns_base100ep_3way_s45n" | tee -a "$LOG"
if [ -d /workspace/runs/r10_prior_sns_base100ep_3way_s45n ]; then echo "  SKIP r10_prior_sns_base100ep_3way_s45n"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_base100ep_3way_s45n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 45 --lr 0.001 || echo "FAILED r10_prior_sns_base100ep_3way_s45n" >> "$FAIL"; fi
echo "[$(ts)] 6/38 r10_prior_base100ep_3way_s45n" | tee -a "$LOG"
if [ -d /workspace/runs/r10_prior_base100ep_3way_s45n ]; then echo "  SKIP r10_prior_base100ep_3way_s45n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_base100ep_3way_s45n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 45 --lr 0.001 || echo "FAILED r10_prior_base100ep_3way_s45n" >> "$FAIL"; fi
echo "[$(ts)] 8/38 r10_prior_sns_base100ep_3way_s46n" | tee -a "$LOG"
if [ -d /workspace/runs/r10_prior_sns_base100ep_3way_s46n ]; then echo "  SKIP r10_prior_sns_base100ep_3way_s46n"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_base100ep_3way_s46n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 46 --lr 0.001 || echo "FAILED r10_prior_sns_base100ep_3way_s46n" >> "$FAIL"; fi
echo "[$(ts)] 10/38 r10_prior_base100ep_3way_s46n" | tee -a "$LOG"
if [ -d /workspace/runs/r10_prior_base100ep_3way_s46n ]; then echo "  SKIP r10_prior_base100ep_3way_s46n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_base100ep_3way_s46n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 46 --lr 0.001 || echo "FAILED r10_prior_base100ep_3way_s46n" >> "$FAIL"; fi
echo "[$(ts)] 12/38 mendein_lr005_100ep_s45n" | tee -a "$LOG"
if [ -d /workspace/runs/mendein_lr005_100ep_s45n ]; then echo "  SKIP mendein_lr005_100ep_s45n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mendein_lr005_100ep_s45n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 45 --lr 0.005 || echo "FAILED mendein_lr005_100ep_s45n" >> "$FAIL"; fi
echo "[$(ts)] 14/38 mendein_pws_lr005_100ep_s46n" | tee -a "$LOG"
if [ -d /workspace/runs/mendein_pws_lr005_100ep_s46n ]; then echo "  SKIP mendein_pws_lr005_100ep_s46n"; else $PY /workspace/train_obj.py --loss pws --epochs 100 --name mendein_pws_lr005_100ep_s46n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 46 --lr 0.005 || echo "FAILED mendein_pws_lr005_100ep_s46n" >> "$FAIL"; fi
echo "[$(ts)] 16/38 mendein_lr005_100ep_s46n" | tee -a "$LOG"
if [ -d /workspace/runs/mendein_lr005_100ep_s46n ]; then echo "  SKIP mendein_lr005_100ep_s46n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mendein_lr005_100ep_s46n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 46 --lr 0.005 || echo "FAILED mendein_lr005_100ep_s46n" >> "$FAIL"; fi
echo "[$(ts)] 18/38 mende_sns_lr005_100ep_s43n" | tee -a "$LOG"
if [ -d /workspace/runs/mende_sns_lr005_100ep_s43n ]; then echo "  SKIP mende_sns_lr005_100ep_s43n"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name mende_sns_lr005_100ep_s43n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 43 --lr 0.005 || echo "FAILED mende_sns_lr005_100ep_s43n" >> "$FAIL"; fi
echo "[$(ts)] 20/38 mende_lr005_100ep_s43n" | tee -a "$LOG"
if [ -d /workspace/runs/mende_lr005_100ep_s43n ]; then echo "  SKIP mende_lr005_100ep_s43n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_lr005_100ep_s43n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 43 --lr 0.005 || echo "FAILED mende_lr005_100ep_s43n" >> "$FAIL"; fi
echo "[$(ts)] 22/38 mende_sns_lr005_100ep_s46n" | tee -a "$LOG"
if [ -d /workspace/runs/mende_sns_lr005_100ep_s46n ]; then echo "  SKIP mende_sns_lr005_100ep_s46n"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name mende_sns_lr005_100ep_s46n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 46 --lr 0.005 || echo "FAILED mende_sns_lr005_100ep_s46n" >> "$FAIL"; fi
echo "[$(ts)] 24/38 mende_lr005_100ep_s46n" | tee -a "$LOG"
if [ -d /workspace/runs/mende_lr005_100ep_s46n ]; then echo "  SKIP mende_lr005_100ep_s46n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_lr005_100ep_s46n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 46 --lr 0.005 || echo "FAILED mende_lr005_100ep_s46n" >> "$FAIL"; fi
echo "[$(ts)] 26/38 r15_arch_y11_vistod15_lr005_100ep_s45n" | tee -a "$LOG"
if [ -d /workspace/runs/r15_arch_y11_vistod15_lr005_100ep_s45n ]; then echo "  SKIP r15_arch_y11_vistod15_lr005_100ep_s45n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y11_vistod15_lr005_100ep_s45n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /root/workspace/weights/yolo11n.pt --shuffle-seed 45 --lr 0.005 || echo "FAILED r15_arch_y11_vistod15_lr005_100ep_s45n" >> "$FAIL"; fi
echo "[$(ts)] 28/38 r15_arch_y11_vistod15_lr005_100ep_s46n" | tee -a "$LOG"
if [ -d /workspace/runs/r15_arch_y11_vistod15_lr005_100ep_s46n ]; then echo "  SKIP r15_arch_y11_vistod15_lr005_100ep_s46n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y11_vistod15_lr005_100ep_s46n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /root/workspace/weights/yolo11n.pt --shuffle-seed 46 --lr 0.005 || echo "FAILED r15_arch_y11_vistod15_lr005_100ep_s46n" >> "$FAIL"; fi
echo "[$(ts)] 30/38 r15_arch_y12_vistod15_lr005_100ep_s42n" | tee -a "$LOG"
if [ -d /workspace/runs/r15_arch_y12_vistod15_lr005_100ep_s42n ]; then echo "  SKIP r15_arch_y12_vistod15_lr005_100ep_s42n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_lr005_100ep_s42n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 42 --lr 0.005 || echo "FAILED r15_arch_y12_vistod15_lr005_100ep_s42n" >> "$FAIL"; fi
echo "[$(ts)] 32/38 r15_arch_y12_vistod15_lr005_100ep_s43n" | tee -a "$LOG"
if [ -d /workspace/runs/r15_arch_y12_vistod15_lr005_100ep_s43n ]; then echo "  SKIP r15_arch_y12_vistod15_lr005_100ep_s43n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_lr005_100ep_s43n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 43 --lr 0.005 || echo "FAILED r15_arch_y12_vistod15_lr005_100ep_s43n" >> "$FAIL"; fi
echo "[$(ts)] 34/38 r15_arch_y12_vistod15_lr005_100ep_s44n" | tee -a "$LOG"
if [ -d /workspace/runs/r15_arch_y12_vistod15_lr005_100ep_s44n ]; then echo "  SKIP r15_arch_y12_vistod15_lr005_100ep_s44n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_lr005_100ep_s44n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 44 --lr 0.005 || echo "FAILED r15_arch_y12_vistod15_lr005_100ep_s44n" >> "$FAIL"; fi
echo "[$(ts)] 36/38 r15_arch_y12_vistod15_lr005_100ep_s45n" | tee -a "$LOG"
if [ -d /workspace/runs/r15_arch_y12_vistod15_lr005_100ep_s45n ]; then echo "  SKIP r15_arch_y12_vistod15_lr005_100ep_s45n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_lr005_100ep_s45n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 45 --lr 0.005 || echo "FAILED r15_arch_y12_vistod15_lr005_100ep_s45n" >> "$FAIL"; fi
echo "[$(ts)] 38/38 r15_arch_y12_vistod15_lr005_100ep_s46n" | tee -a "$LOG"
if [ -d /workspace/runs/r15_arch_y12_vistod15_lr005_100ep_s46n ]; then echo "  SKIP r15_arch_y12_vistod15_lr005_100ep_s46n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_lr005_100ep_s46n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 46 --lr 0.005 || echo "FAILED r15_arch_y12_vistod15_lr005_100ep_s46n" >> "$FAIL"; fi
echo "[$(ts)] 设计 A 队列 1 完成" | tee -a "$LOG"
