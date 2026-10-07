#!/usr/bin/env bash
# P1 补实验（30% 档）—— B 机驾驶脚本。★ 由生成器生成，勿手改。
# 规程：单实例锁 / 等卡空 / 幂等跳过 / 残缺改名留证 / 记墙钟与 OOM / 双 lane
set -u
PY=/usr/local/miniconda3/envs/yolo_arch/bin/python
PRETRAIN=/workspace/weights/dota15_pretrain.pt
EP=100
LOG=/workspace/_p1_30p_B.log
LOCK=/workspace/_p1_30p_B.lock

exec 9>"$LOCK"
flock -n 9 || { echo "[$(date -u '+%F %T')] 已有实例在跑，退出" >> "$LOG"; exit 0; }
echo "===== P1 30p B 启动 $(date -u) host=$(hostname) =====" >> "$LOG"

pre=0
[ -x "$PY" ] || { echo "缺 python: $PY" >> "$LOG"; pre=1; }
[ -f "$PRETRAIN" ] || { echo "缺 pretrain: $PRETRAIN" >> "$LOG"; pre=1; }
[ -f "/workspace/train_obj.py" ] || { echo "缺 /workspace/train_obj.py" >> "$LOG"; pre=1; }
[ -f "/root/datasets_mask/dota15_yolo/dota15_30p.yaml" ] || { echo "缺 data: /root/datasets_mask/dota15_yolo/dota15_30p.yaml" >> "$LOG"; pre=1; }
[ "$pre" -eq 0 ] || { echo "===== 前置检查未过，中止 =====" >> "$LOG"; exit 1; }
echo "[$(date -u '+%F %T')] 前置检查通过" >> "$LOG"

for i in $(seq 1 720); do
  n=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | grep -c . || true)
  [ "${n:-0}" -eq 0 ] && break
  echo "[$(date -u '+%F %T')] 卡上仍有 $n 个进程，等 60s" >> "$LOG"; sleep 60
done
echo "[$(date -u '+%F %T')] 卡已空（或超时），开始" >> "$LOG"

run_one() {
  local dev="$1" name="$2" lr="$3" seed="$4" data="$5"
  local rl="/workspace/runs/$name"
  if [ -f "$rl/results.csv" ]; then
    local done_ep=$(( $(wc -l < "$rl/results.csv") - 1 ))
    if [ "$done_ep" -ge "$EP" ]; then
      echo "[$(date -u '+%F %T')] SKIP(complete ${done_ep}ep) $name" >> "$LOG"; return 0
    fi
  fi
  if [ -d "$rl" ]; then
    mv "$rl" "/workspace/runs/_PARTIAL_${name}_$(date -u +%H%M%S)" 2>/dev/null || true
    echo "[$(date -u '+%F %T')] 旧同名目录残缺，已改名 _PARTIAL_ 留证：$name" >> "$LOG"
  fi
  local l0 t0 t1 n rc oom
  l0=$(wc -l < "$LOG" 2>/dev/null || echo 0); t0=$(date +%s)
  echo "[$(date -u '+%F %T')] GPU$dev START $name ep=$EP lr=$lr seed=$seed" >> "$LOG"
  CUDA_VISIBLE_DEVICES=$dev $PY /workspace/train_obj.py \
      --loss shapeiou --epochs "$EP" --name "$name" --data "$data" \
      --pretrain "$PRETRAIN" --shuffle-seed "$seed" --lr "$lr" >> "$LOG" 2>&1
  rc=$?; t1=$(date +%s)
  n=$(wc -l < "$rl/results.csv" 2>/dev/null || echo 0)
  oom=$(tail -n +$((l0 + 1)) "$LOG" 2>/dev/null | grep -ciE 'out of memory|Reducing to batch|using CPU' || true)
  echo "[$(date -u '+%F %T')] GPU$dev END $name rc=$rc wall=$((t1 - t0))s epochs=$((n - 1)) oom_events=$oom" >> "$LOG"
  if [ "$rc" != 0 ] || [ "$((n - 1))" -lt "$EP" ]; then
    mv "$rl" "/workspace/runs/_PARTIAL_${name}_$(date -u +%H%M%S)" 2>/dev/null || true
    echo "  -> marked _PARTIAL_" >> "$LOG"
  fi
}

lane() {
  local dev="$1" arm="$2"
  while IFS='	' read -r run lr seed data; do
    [ -n "$run" ] || continue
    run_one "$dev" "$run" "$lr" "$seed" "$data"
  done < /workspace/_p1_30p_B_lane_$arm.tsv
}

lane 0 base100 &
lane 1 strat100 &
wait
echo "===== P1 30p B ALL DONE $(date -u) =====" >> "$LOG"
