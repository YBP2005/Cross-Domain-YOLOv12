#!/usr/bin/env bash
# 补实验 B 机 · 队列 4/4（本机卡 1）—— 自动生成，勿手改
# 用法：bash 补实验_n5_B_gpu1.sh
# 驱动内 device=0 是硬编码 => 用 CUDA_VISIBLE_DEVICES 只暴露一张卡，
# 使 device=0 落到本机物理卡 1。不要改驱动去传 --device。
set -u
export CUDA_VISIBLE_DEVICES=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY=/usr/local/miniconda3/envs/yolo_arch/bin/python
LOG=/workspace/_supp_n5_B_gpu1.log
FAIL=/workspace/_supp_n5_B_failed.log
exec 8>/workspace/_supp_n5_B_gpu1.lock
flock -n 8 || { echo '已有本队列实例，退出'; exit 0; }
cd /workspace || exit 1
ts() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
echo "[$(ts)] 队列启动 B 卡1 共 38 条（本队列 9 条）" | tee -a "$LOG"

echo "[$(ts)] 1/9 r10_prior_sns_base100ep_3way_s45n" | tee -a "$LOG"
if [ -d /workspace/runs/r10_prior_sns_base100ep_3way_s45n ]; then echo "  SKIP r10_prior_sns_base100ep_3way_s45n"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_base100ep_3way_s45n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 45 --lr 0.001 || echo "FAILED r10_prior_sns_base100ep_3way_s45n" >> "$FAIL"; fi
echo "[$(ts)] 2/9 r10_prior_sns_base100ep_3way_s46n" | tee -a "$LOG"
if [ -d /workspace/runs/r10_prior_sns_base100ep_3way_s46n ]; then echo "  SKIP r10_prior_sns_base100ep_3way_s46n"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_base100ep_3way_s46n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 46 --lr 0.001 || echo "FAILED r10_prior_sns_base100ep_3way_s46n" >> "$FAIL"; fi
echo "[$(ts)] 3/9 mendein_lr005_100ep_s45n" | tee -a "$LOG"
if [ -d /workspace/runs/mendein_lr005_100ep_s45n ]; then echo "  SKIP mendein_lr005_100ep_s45n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mendein_lr005_100ep_s45n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 45 --lr 0.005 || echo "FAILED mendein_lr005_100ep_s45n" >> "$FAIL"; fi
echo "[$(ts)] 4/9 mendein_lr005_100ep_s46n" | tee -a "$LOG"
if [ -d /workspace/runs/mendein_lr005_100ep_s46n ]; then echo "  SKIP mendein_lr005_100ep_s46n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mendein_lr005_100ep_s46n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 46 --lr 0.005 || echo "FAILED mendein_lr005_100ep_s46n" >> "$FAIL"; fi
echo "[$(ts)] 5/9 mende_lr005_100ep_s43n" | tee -a "$LOG"
if [ -d /workspace/runs/mende_lr005_100ep_s43n ]; then echo "  SKIP mende_lr005_100ep_s43n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_lr005_100ep_s43n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 43 --lr 0.005 || echo "FAILED mende_lr005_100ep_s43n" >> "$FAIL"; fi
echo "[$(ts)] 6/9 mende_lr005_100ep_s46n" | tee -a "$LOG"
if [ -d /workspace/runs/mende_lr005_100ep_s46n ]; then echo "  SKIP mende_lr005_100ep_s46n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_lr005_100ep_s46n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 46 --lr 0.005 || echo "FAILED mende_lr005_100ep_s46n" >> "$FAIL"; fi
echo "[$(ts)] 7/9 r15_arch_y11_vistod15_lr005_100ep_s46n" | tee -a "$LOG"
if [ -d /workspace/runs/r15_arch_y11_vistod15_lr005_100ep_s46n ]; then echo "  SKIP r15_arch_y11_vistod15_lr005_100ep_s46n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y11_vistod15_lr005_100ep_s46n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /root/yolo11n.pt --shuffle-seed 46 --lr 0.005 || echo "FAILED r15_arch_y11_vistod15_lr005_100ep_s46n" >> "$FAIL"; fi
echo "[$(ts)] 8/9 r15_arch_y12_vistod15_lr005_100ep_s43n" | tee -a "$LOG"
if [ -d /workspace/runs/r15_arch_y12_vistod15_lr005_100ep_s43n ]; then echo "  SKIP r15_arch_y12_vistod15_lr005_100ep_s43n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_lr005_100ep_s43n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 43 --lr 0.005 || echo "FAILED r15_arch_y12_vistod15_lr005_100ep_s43n" >> "$FAIL"; fi
echo "[$(ts)] 9/9 r15_arch_y12_vistod15_lr005_100ep_s45n" | tee -a "$LOG"
if [ -d /workspace/runs/r15_arch_y12_vistod15_lr005_100ep_s45n ]; then echo "  SKIP r15_arch_y12_vistod15_lr005_100ep_s45n"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_lr005_100ep_s45n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 45 --lr 0.005 || echo "FAILED r15_arch_y12_vistod15_lr005_100ep_s45n" >> "$FAIL"; fi
echo "[$(ts)] B 队列完成（卡1）" | tee -a "$LOG"
