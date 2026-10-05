#!/usr/bin/env bash
# 补实验启动脚本（设计 B / n=10 / 118 条）—— 自动生成，勿手改
set -u
PY=/usr/local/miniconda3/envs/yolo_arch/bin/python
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd /workspace || exit 1

# mafa→mende20/r10/100ep/sns | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/r10_prior_lr005_100ep_3way_s42n ]; then echo "SKIP r10_prior_lr005_100ep_3way_s42n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_lr005_100ep_3way_s42n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 42 --lr 0.005 || echo "FAILED r10_prior_lr005_100ep_3way_s42n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/r10_prior_lr005_100ep_3way_s43n ]; then echo "SKIP r10_prior_lr005_100ep_3way_s43n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_lr005_100ep_3way_s43n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 43 --lr 0.005 || echo "FAILED r10_prior_lr005_100ep_3way_s43n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/r10_prior_lr005_100ep_3way_s44n ]; then echo "SKIP r10_prior_lr005_100ep_3way_s44n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_lr005_100ep_3way_s44n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 44 --lr 0.005 || echo "FAILED r10_prior_lr005_100ep_3way_s44n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | sns-base 补种子
if [ -d /workspace/runs/r10_prior_sns_base100ep_3way_s45n ]; then echo "SKIP r10_prior_sns_base100ep_3way_s45n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_base100ep_3way_s45n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 45 --lr 0.001 || echo "FAILED r10_prior_sns_base100ep_3way_s45n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | sns-lr005（本格为 0）
if [ -d /workspace/runs/r10_prior_sns_lr005_100ep_3way_s45n ]; then echo "SKIP r10_prior_sns_lr005_100ep_3way_s45n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_lr005_100ep_3way_s45n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 45 --lr 0.005 || echo "FAILED r10_prior_sns_lr005_100ep_3way_s45n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | shapeiou-base 补种子
if [ -d /workspace/runs/r10_prior_base100ep_3way_s45n ]; then echo "SKIP r10_prior_base100ep_3way_s45n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_base100ep_3way_s45n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 45 --lr 0.001 || echo "FAILED r10_prior_base100ep_3way_s45n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/r10_prior_lr005_100ep_3way_s45n ]; then echo "SKIP r10_prior_lr005_100ep_3way_s45n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_lr005_100ep_3way_s45n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 45 --lr 0.005 || echo "FAILED r10_prior_lr005_100ep_3way_s45n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | sns-base 补种子
if [ -d /workspace/runs/r10_prior_sns_base100ep_3way_s46n ]; then echo "SKIP r10_prior_sns_base100ep_3way_s46n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_base100ep_3way_s46n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 46 --lr 0.001 || echo "FAILED r10_prior_sns_base100ep_3way_s46n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | sns-lr005（本格为 0）
if [ -d /workspace/runs/r10_prior_sns_lr005_100ep_3way_s46n ]; then echo "SKIP r10_prior_sns_lr005_100ep_3way_s46n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_lr005_100ep_3way_s46n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 46 --lr 0.005 || echo "FAILED r10_prior_sns_lr005_100ep_3way_s46n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | shapeiou-base 补种子
if [ -d /workspace/runs/r10_prior_base100ep_3way_s46n ]; then echo "SKIP r10_prior_base100ep_3way_s46n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_base100ep_3way_s46n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 46 --lr 0.001 || echo "FAILED r10_prior_base100ep_3way_s46n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/r10_prior_lr005_100ep_3way_s46n ]; then echo "SKIP r10_prior_lr005_100ep_3way_s46n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_lr005_100ep_3way_s46n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 46 --lr 0.005 || echo "FAILED r10_prior_lr005_100ep_3way_s46n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | sns-base 补种子
if [ -d /workspace/runs/r10_prior_sns_base100ep_3way_s47n ]; then echo "SKIP r10_prior_sns_base100ep_3way_s47n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_base100ep_3way_s47n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 47 --lr 0.001 || echo "FAILED r10_prior_sns_base100ep_3way_s47n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | sns-lr005（本格为 0）
if [ -d /workspace/runs/r10_prior_sns_lr005_100ep_3way_s47n ]; then echo "SKIP r10_prior_sns_lr005_100ep_3way_s47n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_lr005_100ep_3way_s47n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 47 --lr 0.005 || echo "FAILED r10_prior_sns_lr005_100ep_3way_s47n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | shapeiou-base 补种子
if [ -d /workspace/runs/r10_prior_base100ep_3way_s47n ]; then echo "SKIP r10_prior_base100ep_3way_s47n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_base100ep_3way_s47n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 47 --lr 0.001 || echo "FAILED r10_prior_base100ep_3way_s47n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/r10_prior_lr005_100ep_3way_s47n ]; then echo "SKIP r10_prior_lr005_100ep_3way_s47n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_lr005_100ep_3way_s47n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 47 --lr 0.005 || echo "FAILED r10_prior_lr005_100ep_3way_s47n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | sns-base 补种子
if [ -d /workspace/runs/r10_prior_sns_base100ep_3way_s48n ]; then echo "SKIP r10_prior_sns_base100ep_3way_s48n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_base100ep_3way_s48n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 48 --lr 0.001 || echo "FAILED r10_prior_sns_base100ep_3way_s48n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | sns-lr005（本格为 0）
if [ -d /workspace/runs/r10_prior_sns_lr005_100ep_3way_s48n ]; then echo "SKIP r10_prior_sns_lr005_100ep_3way_s48n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_lr005_100ep_3way_s48n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 48 --lr 0.005 || echo "FAILED r10_prior_sns_lr005_100ep_3way_s48n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | shapeiou-base 补种子
if [ -d /workspace/runs/r10_prior_base100ep_3way_s48n ]; then echo "SKIP r10_prior_base100ep_3way_s48n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_base100ep_3way_s48n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 48 --lr 0.001 || echo "FAILED r10_prior_base100ep_3way_s48n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/r10_prior_lr005_100ep_3way_s48n ]; then echo "SKIP r10_prior_lr005_100ep_3way_s48n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_lr005_100ep_3way_s48n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 48 --lr 0.005 || echo "FAILED r10_prior_lr005_100ep_3way_s48n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | sns-base 补种子
if [ -d /workspace/runs/r10_prior_sns_base100ep_3way_s49n ]; then echo "SKIP r10_prior_sns_base100ep_3way_s49n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_base100ep_3way_s49n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 49 --lr 0.001 || echo "FAILED r10_prior_sns_base100ep_3way_s49n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | sns-lr005（本格为 0）
if [ -d /workspace/runs/r10_prior_sns_lr005_100ep_3way_s49n ]; then echo "SKIP r10_prior_sns_lr005_100ep_3way_s49n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_lr005_100ep_3way_s49n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 49 --lr 0.005 || echo "FAILED r10_prior_sns_lr005_100ep_3way_s49n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | shapeiou-base 补种子
if [ -d /workspace/runs/r10_prior_base100ep_3way_s49n ]; then echo "SKIP r10_prior_base100ep_3way_s49n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_base100ep_3way_s49n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 49 --lr 0.001 || echo "FAILED r10_prior_base100ep_3way_s49n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/r10_prior_lr005_100ep_3way_s49n ]; then echo "SKIP r10_prior_lr005_100ep_3way_s49n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_lr005_100ep_3way_s49n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 49 --lr 0.005 || echo "FAILED r10_prior_lr005_100ep_3way_s49n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | sns-base 补种子
if [ -d /workspace/runs/r10_prior_sns_base100ep_3way_s50n ]; then echo "SKIP r10_prior_sns_base100ep_3way_s50n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_base100ep_3way_s50n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 50 --lr 0.001 || echo "FAILED r10_prior_sns_base100ep_3way_s50n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | sns-lr005（本格为 0）
if [ -d /workspace/runs/r10_prior_sns_lr005_100ep_3way_s50n ]; then echo "SKIP r10_prior_sns_lr005_100ep_3way_s50n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_lr005_100ep_3way_s50n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 50 --lr 0.005 || echo "FAILED r10_prior_sns_lr005_100ep_3way_s50n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | shapeiou-base 补种子
if [ -d /workspace/runs/r10_prior_base100ep_3way_s50n ]; then echo "SKIP r10_prior_base100ep_3way_s50n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_base100ep_3way_s50n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 50 --lr 0.001 || echo "FAILED r10_prior_base100ep_3way_s50n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/r10_prior_lr005_100ep_3way_s50n ]; then echo "SKIP r10_prior_lr005_100ep_3way_s50n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_lr005_100ep_3way_s50n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 50 --lr 0.005 || echo "FAILED r10_prior_lr005_100ep_3way_s50n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | sns-base 补种子
if [ -d /workspace/runs/r10_prior_sns_base100ep_3way_s51n ]; then echo "SKIP r10_prior_sns_base100ep_3way_s51n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_base100ep_3way_s51n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 51 --lr 0.001 || echo "FAILED r10_prior_sns_base100ep_3way_s51n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | sns-lr005（本格为 0）
if [ -d /workspace/runs/r10_prior_sns_lr005_100ep_3way_s51n ]; then echo "SKIP r10_prior_sns_lr005_100ep_3way_s51n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name r10_prior_sns_lr005_100ep_3way_s51n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 51 --lr 0.005 || echo "FAILED r10_prior_sns_lr005_100ep_3way_s51n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | shapeiou-base 补种子
if [ -d /workspace/runs/r10_prior_base100ep_3way_s51n ]; then echo "SKIP r10_prior_base100ep_3way_s51n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_base100ep_3way_s51n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 51 --lr 0.001 || echo "FAILED r10_prior_base100ep_3way_s51n" >> /workspace/_supp_failed.log; fi

# mafa→mende20/r10/100ep/sns | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/r10_prior_lr005_100ep_3way_s51n ]; then echo "SKIP r10_prior_lr005_100ep_3way_s51n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r10_prior_lr005_100ep_3way_s51n --data /root/datasets_mask/mendeley_yolo/mende20_3way.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 51 --lr 0.005 || echo "FAILED r10_prior_lr005_100ep_3way_s51n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/mendein_lr005_100ep_s45n ]; then echo "SKIP mendein_lr005_100ep_s45n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mendein_lr005_100ep_s45n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 45 --lr 0.005 || echo "FAILED mendein_lr005_100ep_s45n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | pws-base 补种子
if [ -d /workspace/runs/mendein_pws_base100ep_s46n ]; then echo "SKIP mendein_pws_base100ep_s46n (已存在)"; else $PY /workspace/train_obj.py --loss pws --epochs 100 --name mendein_pws_base100ep_s46n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 46 --lr 0.001 || echo "FAILED mendein_pws_base100ep_s46n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | pws-lr005（本格为 0）
if [ -d /workspace/runs/mendein_pws_lr005_100ep_s46n ]; then echo "SKIP mendein_pws_lr005_100ep_s46n (已存在)"; else $PY /workspace/train_obj.py --loss pws --epochs 100 --name mendein_pws_lr005_100ep_s46n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 46 --lr 0.005 || echo "FAILED mendein_pws_lr005_100ep_s46n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | shapeiou-base 补种子
if [ -d /workspace/runs/mendein_base100ep_s46n ]; then echo "SKIP mendein_base100ep_s46n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mendein_base100ep_s46n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 46 --lr 0.001 || echo "FAILED mendein_base100ep_s46n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/mendein_lr005_100ep_s46n ]; then echo "SKIP mendein_lr005_100ep_s46n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mendein_lr005_100ep_s46n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 46 --lr 0.005 || echo "FAILED mendein_lr005_100ep_s46n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | pws-base 补种子
if [ -d /workspace/runs/mendein_pws_base100ep_s47n ]; then echo "SKIP mendein_pws_base100ep_s47n (已存在)"; else $PY /workspace/train_obj.py --loss pws --epochs 100 --name mendein_pws_base100ep_s47n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 47 --lr 0.001 || echo "FAILED mendein_pws_base100ep_s47n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | pws-lr005（本格为 0）
if [ -d /workspace/runs/mendein_pws_lr005_100ep_s47n ]; then echo "SKIP mendein_pws_lr005_100ep_s47n (已存在)"; else $PY /workspace/train_obj.py --loss pws --epochs 100 --name mendein_pws_lr005_100ep_s47n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 47 --lr 0.005 || echo "FAILED mendein_pws_lr005_100ep_s47n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | shapeiou-base 补种子
if [ -d /workspace/runs/mendein_base100ep_s47n ]; then echo "SKIP mendein_base100ep_s47n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mendein_base100ep_s47n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 47 --lr 0.001 || echo "FAILED mendein_base100ep_s47n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/mendein_lr005_100ep_s47n ]; then echo "SKIP mendein_lr005_100ep_s47n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mendein_lr005_100ep_s47n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 47 --lr 0.005 || echo "FAILED mendein_lr005_100ep_s47n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | pws-base 补种子
if [ -d /workspace/runs/mendein_pws_base100ep_s48n ]; then echo "SKIP mendein_pws_base100ep_s48n (已存在)"; else $PY /workspace/train_obj.py --loss pws --epochs 100 --name mendein_pws_base100ep_s48n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 48 --lr 0.001 || echo "FAILED mendein_pws_base100ep_s48n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | pws-lr005（本格为 0）
if [ -d /workspace/runs/mendein_pws_lr005_100ep_s48n ]; then echo "SKIP mendein_pws_lr005_100ep_s48n (已存在)"; else $PY /workspace/train_obj.py --loss pws --epochs 100 --name mendein_pws_lr005_100ep_s48n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 48 --lr 0.005 || echo "FAILED mendein_pws_lr005_100ep_s48n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | shapeiou-base 补种子
if [ -d /workspace/runs/mendein_base100ep_s48n ]; then echo "SKIP mendein_base100ep_s48n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mendein_base100ep_s48n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 48 --lr 0.001 || echo "FAILED mendein_base100ep_s48n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/mendein_lr005_100ep_s48n ]; then echo "SKIP mendein_lr005_100ep_s48n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mendein_lr005_100ep_s48n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 48 --lr 0.005 || echo "FAILED mendein_lr005_100ep_s48n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | pws-base 补种子
if [ -d /workspace/runs/mendein_pws_base100ep_s49n ]; then echo "SKIP mendein_pws_base100ep_s49n (已存在)"; else $PY /workspace/train_obj.py --loss pws --epochs 100 --name mendein_pws_base100ep_s49n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 49 --lr 0.001 || echo "FAILED mendein_pws_base100ep_s49n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | pws-lr005（本格为 0）
if [ -d /workspace/runs/mendein_pws_lr005_100ep_s49n ]; then echo "SKIP mendein_pws_lr005_100ep_s49n (已存在)"; else $PY /workspace/train_obj.py --loss pws --epochs 100 --name mendein_pws_lr005_100ep_s49n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 49 --lr 0.005 || echo "FAILED mendein_pws_lr005_100ep_s49n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | shapeiou-base 补种子
if [ -d /workspace/runs/mendein_base100ep_s49n ]; then echo "SKIP mendein_base100ep_s49n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mendein_base100ep_s49n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 49 --lr 0.001 || echo "FAILED mendein_base100ep_s49n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/mendein_lr005_100ep_s49n ]; then echo "SKIP mendein_lr005_100ep_s49n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mendein_lr005_100ep_s49n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 49 --lr 0.005 || echo "FAILED mendein_lr005_100ep_s49n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | pws-base 补种子
if [ -d /workspace/runs/mendein_pws_base100ep_s50n ]; then echo "SKIP mendein_pws_base100ep_s50n (已存在)"; else $PY /workspace/train_obj.py --loss pws --epochs 100 --name mendein_pws_base100ep_s50n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 50 --lr 0.001 || echo "FAILED mendein_pws_base100ep_s50n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | pws-lr005（本格为 0）
if [ -d /workspace/runs/mendein_pws_lr005_100ep_s50n ]; then echo "SKIP mendein_pws_lr005_100ep_s50n (已存在)"; else $PY /workspace/train_obj.py --loss pws --epochs 100 --name mendein_pws_lr005_100ep_s50n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 50 --lr 0.005 || echo "FAILED mendein_pws_lr005_100ep_s50n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | shapeiou-base 补种子
if [ -d /workspace/runs/mendein_base100ep_s50n ]; then echo "SKIP mendein_base100ep_s50n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mendein_base100ep_s50n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 50 --lr 0.001 || echo "FAILED mendein_base100ep_s50n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/mendein_lr005_100ep_s50n ]; then echo "SKIP mendein_lr005_100ep_s50n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mendein_lr005_100ep_s50n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 50 --lr 0.005 || echo "FAILED mendein_lr005_100ep_s50n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | pws-base 补种子
if [ -d /workspace/runs/mendein_pws_base100ep_s51n ]; then echo "SKIP mendein_pws_base100ep_s51n (已存在)"; else $PY /workspace/train_obj.py --loss pws --epochs 100 --name mendein_pws_base100ep_s51n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 51 --lr 0.001 || echo "FAILED mendein_pws_base100ep_s51n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | pws-lr005（本格为 0）
if [ -d /workspace/runs/mendein_pws_lr005_100ep_s51n ]; then echo "SKIP mendein_pws_lr005_100ep_s51n (已存在)"; else $PY /workspace/train_obj.py --loss pws --epochs 100 --name mendein_pws_lr005_100ep_s51n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 51 --lr 0.005 || echo "FAILED mendein_pws_lr005_100ep_s51n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | shapeiou-base 补种子
if [ -d /workspace/runs/mendein_base100ep_s51n ]; then echo "SKIP mendein_base100ep_s51n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mendein_base100ep_s51n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 51 --lr 0.001 || echo "FAILED mendein_base100ep_s51n" >> /workspace/_supp_failed.log; fi

# mendein→mende/mendein/100ep/pws | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/mendein_lr005_100ep_s51n ]; then echo "SKIP mendein_lr005_100ep_s51n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mendein_lr005_100ep_s51n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mendein_pretrain.pt --shuffle-seed 51 --lr 0.005 || echo "FAILED mendein_lr005_100ep_s51n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | sns-base 补种子
if [ -d /workspace/runs/mende_sns_base100ep_s43n ]; then echo "SKIP mende_sns_base100ep_s43n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name mende_sns_base100ep_s43n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 43 --lr 0.001 || echo "FAILED mende_sns_base100ep_s43n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | sns-lr005（本格为 0）
if [ -d /workspace/runs/mende_sns_lr005_100ep_s43n ]; then echo "SKIP mende_sns_lr005_100ep_s43n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name mende_sns_lr005_100ep_s43n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 43 --lr 0.005 || echo "FAILED mende_sns_lr005_100ep_s43n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | shapeiou-base 补种子
if [ -d /workspace/runs/mende_base100ep_s43n ]; then echo "SKIP mende_base100ep_s43n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_base100ep_s43n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 43 --lr 0.001 || echo "FAILED mende_base100ep_s43n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/mende_lr005_100ep_s43n ]; then echo "SKIP mende_lr005_100ep_s43n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_lr005_100ep_s43n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 43 --lr 0.005 || echo "FAILED mende_lr005_100ep_s43n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | sns-base 补种子
if [ -d /workspace/runs/mende_sns_base100ep_s46n ]; then echo "SKIP mende_sns_base100ep_s46n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name mende_sns_base100ep_s46n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 46 --lr 0.001 || echo "FAILED mende_sns_base100ep_s46n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | sns-lr005（本格为 0）
if [ -d /workspace/runs/mende_sns_lr005_100ep_s46n ]; then echo "SKIP mende_sns_lr005_100ep_s46n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name mende_sns_lr005_100ep_s46n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 46 --lr 0.005 || echo "FAILED mende_sns_lr005_100ep_s46n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | shapeiou-base 补种子
if [ -d /workspace/runs/mende_base100ep_s46n ]; then echo "SKIP mende_base100ep_s46n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_base100ep_s46n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 46 --lr 0.001 || echo "FAILED mende_base100ep_s46n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/mende_lr005_100ep_s46n ]; then echo "SKIP mende_lr005_100ep_s46n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_lr005_100ep_s46n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 46 --lr 0.005 || echo "FAILED mende_lr005_100ep_s46n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | sns-base 补种子
if [ -d /workspace/runs/mende_sns_base100ep_s47n ]; then echo "SKIP mende_sns_base100ep_s47n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name mende_sns_base100ep_s47n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 47 --lr 0.001 || echo "FAILED mende_sns_base100ep_s47n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | sns-lr005（本格为 0）
if [ -d /workspace/runs/mende_sns_lr005_100ep_s47n ]; then echo "SKIP mende_sns_lr005_100ep_s47n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name mende_sns_lr005_100ep_s47n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 47 --lr 0.005 || echo "FAILED mende_sns_lr005_100ep_s47n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | shapeiou-base 补种子
if [ -d /workspace/runs/mende_base100ep_s47n ]; then echo "SKIP mende_base100ep_s47n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_base100ep_s47n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 47 --lr 0.001 || echo "FAILED mende_base100ep_s47n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/mende_lr005_100ep_s47n ]; then echo "SKIP mende_lr005_100ep_s47n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_lr005_100ep_s47n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 47 --lr 0.005 || echo "FAILED mende_lr005_100ep_s47n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | sns-base 补种子
if [ -d /workspace/runs/mende_sns_base100ep_s48n ]; then echo "SKIP mende_sns_base100ep_s48n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name mende_sns_base100ep_s48n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 48 --lr 0.001 || echo "FAILED mende_sns_base100ep_s48n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | sns-lr005（本格为 0）
if [ -d /workspace/runs/mende_sns_lr005_100ep_s48n ]; then echo "SKIP mende_sns_lr005_100ep_s48n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name mende_sns_lr005_100ep_s48n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 48 --lr 0.005 || echo "FAILED mende_sns_lr005_100ep_s48n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | shapeiou-base 补种子
if [ -d /workspace/runs/mende_base100ep_s48n ]; then echo "SKIP mende_base100ep_s48n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_base100ep_s48n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 48 --lr 0.001 || echo "FAILED mende_base100ep_s48n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/mende_lr005_100ep_s48n ]; then echo "SKIP mende_lr005_100ep_s48n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_lr005_100ep_s48n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 48 --lr 0.005 || echo "FAILED mende_lr005_100ep_s48n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | sns-base 补种子
if [ -d /workspace/runs/mende_sns_base100ep_s49n ]; then echo "SKIP mende_sns_base100ep_s49n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name mende_sns_base100ep_s49n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 49 --lr 0.001 || echo "FAILED mende_sns_base100ep_s49n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | sns-lr005（本格为 0）
if [ -d /workspace/runs/mende_sns_lr005_100ep_s49n ]; then echo "SKIP mende_sns_lr005_100ep_s49n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name mende_sns_lr005_100ep_s49n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 49 --lr 0.005 || echo "FAILED mende_sns_lr005_100ep_s49n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | shapeiou-base 补种子
if [ -d /workspace/runs/mende_base100ep_s49n ]; then echo "SKIP mende_base100ep_s49n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_base100ep_s49n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 49 --lr 0.001 || echo "FAILED mende_base100ep_s49n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/mende_lr005_100ep_s49n ]; then echo "SKIP mende_lr005_100ep_s49n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_lr005_100ep_s49n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 49 --lr 0.005 || echo "FAILED mende_lr005_100ep_s49n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | sns-base 补种子
if [ -d /workspace/runs/mende_sns_base100ep_s50n ]; then echo "SKIP mende_sns_base100ep_s50n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name mende_sns_base100ep_s50n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 50 --lr 0.001 || echo "FAILED mende_sns_base100ep_s50n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | sns-lr005（本格为 0）
if [ -d /workspace/runs/mende_sns_lr005_100ep_s50n ]; then echo "SKIP mende_sns_lr005_100ep_s50n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name mende_sns_lr005_100ep_s50n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 50 --lr 0.005 || echo "FAILED mende_sns_lr005_100ep_s50n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | shapeiou-base 补种子
if [ -d /workspace/runs/mende_base100ep_s50n ]; then echo "SKIP mende_base100ep_s50n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_base100ep_s50n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 50 --lr 0.001 || echo "FAILED mende_base100ep_s50n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/mende_lr005_100ep_s50n ]; then echo "SKIP mende_lr005_100ep_s50n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_lr005_100ep_s50n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 50 --lr 0.005 || echo "FAILED mende_lr005_100ep_s50n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | sns-base 补种子
if [ -d /workspace/runs/mende_sns_base100ep_s51n ]; then echo "SKIP mende_sns_base100ep_s51n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name mende_sns_base100ep_s51n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 51 --lr 0.001 || echo "FAILED mende_sns_base100ep_s51n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | sns-lr005（本格为 0）
if [ -d /workspace/runs/mende_sns_lr005_100ep_s51n ]; then echo "SKIP mende_sns_lr005_100ep_s51n (已存在)"; else $PY /workspace/train_obj.py --loss sns --epochs 100 --name mende_sns_lr005_100ep_s51n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 51 --lr 0.005 || echo "FAILED mende_sns_lr005_100ep_s51n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | shapeiou-base 补种子
if [ -d /workspace/runs/mende_base100ep_s51n ]; then echo "SKIP mende_base100ep_s51n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_base100ep_s51n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 51 --lr 0.001 || echo "FAILED mende_base100ep_s51n" >> /workspace/_supp_failed.log; fi

# mafa→mende/mende/100ep/sns | shapeiou-lr005（本格为 0）
if [ -d /workspace/runs/mende_lr005_100ep_s51n ]; then echo "SKIP mende_lr005_100ep_s51n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name mende_lr005_100ep_s51n --data /root/datasets_mask/mendeley_yolo/mende_20p.yaml --pretrain /workspace/weights/mafa_pretrain.pt --shuffle-seed 51 --lr 0.005 || echo "FAILED mende_lr005_100ep_s51n" >> /workspace/_supp_failed.log; fi

# arch/yolo11n.pt/100ep | 架构对照：yolo11n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y11_vistod15_base100_s45n ]; then echo "SKIP r15_arch_y11_vistod15_base100_s45n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y11_vistod15_base100_s45n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /root/workspace/weights/yolo11n.pt --shuffle-seed 45 --lr 0.001 || echo "FAILED r15_arch_y11_vistod15_base100_s45n" >> /workspace/_supp_failed.log; fi

# arch/yolo11n.pt/100ep | 架构对照：yolo11n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y11_vistod15_lr005_100ep_s45n ]; then echo "SKIP r15_arch_y11_vistod15_lr005_100ep_s45n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y11_vistod15_lr005_100ep_s45n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /root/workspace/weights/yolo11n.pt --shuffle-seed 45 --lr 0.005 || echo "FAILED r15_arch_y11_vistod15_lr005_100ep_s45n" >> /workspace/_supp_failed.log; fi

# arch/yolo11n.pt/100ep | 架构对照：yolo11n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y11_vistod15_base100_s46n ]; then echo "SKIP r15_arch_y11_vistod15_base100_s46n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y11_vistod15_base100_s46n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /root/workspace/weights/yolo11n.pt --shuffle-seed 46 --lr 0.001 || echo "FAILED r15_arch_y11_vistod15_base100_s46n" >> /workspace/_supp_failed.log; fi

# arch/yolo11n.pt/100ep | 架构对照：yolo11n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y11_vistod15_lr005_100ep_s46n ]; then echo "SKIP r15_arch_y11_vistod15_lr005_100ep_s46n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y11_vistod15_lr005_100ep_s46n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /root/workspace/weights/yolo11n.pt --shuffle-seed 46 --lr 0.005 || echo "FAILED r15_arch_y11_vistod15_lr005_100ep_s46n" >> /workspace/_supp_failed.log; fi

# arch/yolo11n.pt/100ep | 架构对照：yolo11n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y11_vistod15_base100_s47n ]; then echo "SKIP r15_arch_y11_vistod15_base100_s47n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y11_vistod15_base100_s47n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /root/workspace/weights/yolo11n.pt --shuffle-seed 47 --lr 0.001 || echo "FAILED r15_arch_y11_vistod15_base100_s47n" >> /workspace/_supp_failed.log; fi

# arch/yolo11n.pt/100ep | 架构对照：yolo11n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y11_vistod15_lr005_100ep_s47n ]; then echo "SKIP r15_arch_y11_vistod15_lr005_100ep_s47n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y11_vistod15_lr005_100ep_s47n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /root/workspace/weights/yolo11n.pt --shuffle-seed 47 --lr 0.005 || echo "FAILED r15_arch_y11_vistod15_lr005_100ep_s47n" >> /workspace/_supp_failed.log; fi

# arch/yolo11n.pt/100ep | 架构对照：yolo11n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y11_vistod15_base100_s48n ]; then echo "SKIP r15_arch_y11_vistod15_base100_s48n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y11_vistod15_base100_s48n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /root/workspace/weights/yolo11n.pt --shuffle-seed 48 --lr 0.001 || echo "FAILED r15_arch_y11_vistod15_base100_s48n" >> /workspace/_supp_failed.log; fi

# arch/yolo11n.pt/100ep | 架构对照：yolo11n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y11_vistod15_lr005_100ep_s48n ]; then echo "SKIP r15_arch_y11_vistod15_lr005_100ep_s48n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y11_vistod15_lr005_100ep_s48n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /root/workspace/weights/yolo11n.pt --shuffle-seed 48 --lr 0.005 || echo "FAILED r15_arch_y11_vistod15_lr005_100ep_s48n" >> /workspace/_supp_failed.log; fi

# arch/yolo11n.pt/100ep | 架构对照：yolo11n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y11_vistod15_base100_s49n ]; then echo "SKIP r15_arch_y11_vistod15_base100_s49n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y11_vistod15_base100_s49n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /root/workspace/weights/yolo11n.pt --shuffle-seed 49 --lr 0.001 || echo "FAILED r15_arch_y11_vistod15_base100_s49n" >> /workspace/_supp_failed.log; fi

# arch/yolo11n.pt/100ep | 架构对照：yolo11n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y11_vistod15_lr005_100ep_s49n ]; then echo "SKIP r15_arch_y11_vistod15_lr005_100ep_s49n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y11_vistod15_lr005_100ep_s49n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /root/workspace/weights/yolo11n.pt --shuffle-seed 49 --lr 0.005 || echo "FAILED r15_arch_y11_vistod15_lr005_100ep_s49n" >> /workspace/_supp_failed.log; fi

# arch/yolo11n.pt/100ep | 架构对照：yolo11n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y11_vistod15_base100_s50n ]; then echo "SKIP r15_arch_y11_vistod15_base100_s50n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y11_vistod15_base100_s50n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /root/workspace/weights/yolo11n.pt --shuffle-seed 50 --lr 0.001 || echo "FAILED r15_arch_y11_vistod15_base100_s50n" >> /workspace/_supp_failed.log; fi

# arch/yolo11n.pt/100ep | 架构对照：yolo11n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y11_vistod15_lr005_100ep_s50n ]; then echo "SKIP r15_arch_y11_vistod15_lr005_100ep_s50n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y11_vistod15_lr005_100ep_s50n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /root/workspace/weights/yolo11n.pt --shuffle-seed 50 --lr 0.005 || echo "FAILED r15_arch_y11_vistod15_lr005_100ep_s50n" >> /workspace/_supp_failed.log; fi

# arch/yolo11n.pt/100ep | 架构对照：yolo11n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y11_vistod15_base100_s51n ]; then echo "SKIP r15_arch_y11_vistod15_base100_s51n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y11_vistod15_base100_s51n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /root/workspace/weights/yolo11n.pt --shuffle-seed 51 --lr 0.001 || echo "FAILED r15_arch_y11_vistod15_base100_s51n" >> /workspace/_supp_failed.log; fi

# arch/yolo11n.pt/100ep | 架构对照：yolo11n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y11_vistod15_lr005_100ep_s51n ]; then echo "SKIP r15_arch_y11_vistod15_lr005_100ep_s51n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y11_vistod15_lr005_100ep_s51n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /root/workspace/weights/yolo11n.pt --shuffle-seed 51 --lr 0.005 || echo "FAILED r15_arch_y11_vistod15_lr005_100ep_s51n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_base100_s42n ]; then echo "SKIP r15_arch_y12_vistod15_base100_s42n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_base100_s42n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 42 --lr 0.001 || echo "FAILED r15_arch_y12_vistod15_base100_s42n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_lr005_100ep_s42n ]; then echo "SKIP r15_arch_y12_vistod15_lr005_100ep_s42n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_lr005_100ep_s42n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 42 --lr 0.005 || echo "FAILED r15_arch_y12_vistod15_lr005_100ep_s42n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_base100_s43n ]; then echo "SKIP r15_arch_y12_vistod15_base100_s43n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_base100_s43n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 43 --lr 0.001 || echo "FAILED r15_arch_y12_vistod15_base100_s43n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_lr005_100ep_s43n ]; then echo "SKIP r15_arch_y12_vistod15_lr005_100ep_s43n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_lr005_100ep_s43n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 43 --lr 0.005 || echo "FAILED r15_arch_y12_vistod15_lr005_100ep_s43n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_base100_s44n ]; then echo "SKIP r15_arch_y12_vistod15_base100_s44n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_base100_s44n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 44 --lr 0.001 || echo "FAILED r15_arch_y12_vistod15_base100_s44n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_lr005_100ep_s44n ]; then echo "SKIP r15_arch_y12_vistod15_lr005_100ep_s44n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_lr005_100ep_s44n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 44 --lr 0.005 || echo "FAILED r15_arch_y12_vistod15_lr005_100ep_s44n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_base100_s45n ]; then echo "SKIP r15_arch_y12_vistod15_base100_s45n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_base100_s45n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 45 --lr 0.001 || echo "FAILED r15_arch_y12_vistod15_base100_s45n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_lr005_100ep_s45n ]; then echo "SKIP r15_arch_y12_vistod15_lr005_100ep_s45n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_lr005_100ep_s45n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 45 --lr 0.005 || echo "FAILED r15_arch_y12_vistod15_lr005_100ep_s45n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_base100_s46n ]; then echo "SKIP r15_arch_y12_vistod15_base100_s46n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_base100_s46n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 46 --lr 0.001 || echo "FAILED r15_arch_y12_vistod15_base100_s46n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_lr005_100ep_s46n ]; then echo "SKIP r15_arch_y12_vistod15_lr005_100ep_s46n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_lr005_100ep_s46n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 46 --lr 0.005 || echo "FAILED r15_arch_y12_vistod15_lr005_100ep_s46n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_base100_s47n ]; then echo "SKIP r15_arch_y12_vistod15_base100_s47n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_base100_s47n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 47 --lr 0.001 || echo "FAILED r15_arch_y12_vistod15_base100_s47n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_lr005_100ep_s47n ]; then echo "SKIP r15_arch_y12_vistod15_lr005_100ep_s47n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_lr005_100ep_s47n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 47 --lr 0.005 || echo "FAILED r15_arch_y12_vistod15_lr005_100ep_s47n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_base100_s48n ]; then echo "SKIP r15_arch_y12_vistod15_base100_s48n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_base100_s48n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 48 --lr 0.001 || echo "FAILED r15_arch_y12_vistod15_base100_s48n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_lr005_100ep_s48n ]; then echo "SKIP r15_arch_y12_vistod15_lr005_100ep_s48n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_lr005_100ep_s48n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 48 --lr 0.005 || echo "FAILED r15_arch_y12_vistod15_lr005_100ep_s48n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_base100_s49n ]; then echo "SKIP r15_arch_y12_vistod15_base100_s49n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_base100_s49n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 49 --lr 0.001 || echo "FAILED r15_arch_y12_vistod15_base100_s49n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_lr005_100ep_s49n ]; then echo "SKIP r15_arch_y12_vistod15_lr005_100ep_s49n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_lr005_100ep_s49n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 49 --lr 0.005 || echo "FAILED r15_arch_y12_vistod15_lr005_100ep_s49n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_base100_s50n ]; then echo "SKIP r15_arch_y12_vistod15_base100_s50n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_base100_s50n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 50 --lr 0.001 || echo "FAILED r15_arch_y12_vistod15_base100_s50n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_lr005_100ep_s50n ]; then echo "SKIP r15_arch_y12_vistod15_lr005_100ep_s50n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_lr005_100ep_s50n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 50 --lr 0.005 || echo "FAILED r15_arch_y12_vistod15_lr005_100ep_s50n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_base100_s51n ]; then echo "SKIP r15_arch_y12_vistod15_base100_s51n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_base100_s51n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 51 --lr 0.001 || echo "FAILED r15_arch_y12_vistod15_base100_s51n" >> /workspace/_supp_failed.log; fi

# arch/yolo12n.pt/100ep | 架构对照：yolo12n.pt（同目标 / 同 COCO 起点 / 同三方划分）
if [ -d /workspace/runs/r15_arch_y12_vistod15_lr005_100ep_s51n ]; then echo "SKIP r15_arch_y12_vistod15_lr005_100ep_s51n (已存在)"; else $PY /workspace/train_obj.py --loss shapeiou --epochs 100 --name r15_arch_y12_vistod15_lr005_100ep_s51n --data /root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml --pretrain /workspace/yolo12n.pt --shuffle-seed 51 --lr 0.005 || echo "FAILED r15_arch_y12_vistod15_lr005_100ep_s51n" >> /workspace/_supp_failed.log; fi

