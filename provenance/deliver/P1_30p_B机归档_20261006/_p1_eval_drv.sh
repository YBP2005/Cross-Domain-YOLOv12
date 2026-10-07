#!/usr/bin/env bash
# _p1_eval_drv.sh —— 为存量 G1 run 补 test 列（只评估，不重训）。
# ★ 评测要把 GPU 占满：**两张卡各起 N 条 lane**（N 由第 2 个参数给，默认 3）。
# ★ 名单**按奇偶切两半**：奇数行→GPU1（若已空立即开跑），偶数行→GPU0（等训练收工后自动接上）。
#   每条 lane 会**等自己那张卡空**，所以现在就能起，不会与训练抢卡。
# 用法：bash _p1_eval_drv.sh A [N]
# 纪律：单实例锁 / 幂等（跳过已有 test_eval.json）/ 只新增 test_eval.json
set -u
M="${1:?用法: bash _p1_eval_drv.sh A|B [lanes_per_gpu]}"
N="${2:-3}"
PY=/usr/local/miniconda3/envs/yolo_arch/bin/python
LOG=/workspace/_p1_eval_test_${M}.log
LOCK=/workspace/_p1_eval_test_${M}.lock
RUNS=/workspace/_p1_eval_${M}_runs.txt
W=/workspace/_p1_eval_${M}_work

exec 9>"$LOCK"
flock -n 9 || { echo "[$(date -u '+%F %T')] 已有实例在跑，退出" >> "$LOG"; exit 0; }
[ -f "$RUNS" ] || { echo "缺 run 名单 $RUNS" >> "$LOG"; exit 1; }
mkdir -p "$W"
# 名单文件是**逗号分隔**；转成一 run 一行，再按奇偶切两半
tr ',' '\n' < "$RUNS" | sed '/^$/d' > "$W/all.txt"
awk 'NR%2==1' "$W/all.txt" > "$W/gpu1.txt"
awk 'NR%2==0' "$W/all.txt" > "$W/gpu0.txt"
n1=$(wc -l < "$W/gpu1.txt"); n0=$(wc -l < "$W/gpu0.txt")
echo "===== P1 test 列评估 ${M} 启动 $(date -u) host=$(hostname) lanes/卡=${N} 名单 ${n1}+${n0} =====" >> "$LOG"

# 两组独立进程：GPU1 组（现在就能占已空的卡）、GPU0 组（等训练收工）
nohup setsid $PY /workspace/p1_eval_test_column.py \
    --runs-file "$W/gpu1.txt" --gpus 1 --lanes-per-gpu "$N" --apply >> "${LOG}.gpu1" 2>&1 &
nohup setsid $PY /workspace/p1_eval_test_column.py \
    --runs-file "$W/gpu0.txt" --gpus 0 --lanes-per-gpu "$N" --apply >> "${LOG}.gpu0" 2>&1 &
echo "[$(date -u '+%F %T')] 已起两组（GPU1×$N = $n1 run 立即 / GPU0×$N = $n0 run 等卡空）" >> "$LOG"
