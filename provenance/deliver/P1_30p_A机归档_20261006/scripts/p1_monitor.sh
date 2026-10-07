#!/usr/bin/env bash
# p1_monitor.sh —— A 机 P1（30% 档）队列监控。**只读**，不改任何训练产物。
#
# 用途：一次调用给出队列健康快照 + 必要时打印可执行的补救命令（但**不自动执行**）。
#
# 判据（异常）：① 队列进程不在但未 ALL DONE  ② 卡空超过 grace 期而队列未完成
#              ③ 出现 OOM/降 batch 事件      ④ 某 run 被标 _PARTIAL_
set -u
LOG=/workspace/_p1_30p_A.log
LANE_B=/workspace/_p1_30p_A_lane_base100.tsv
LANE_S=/workspace/_p1_30p_A_lane_strat100.tsv
RUNNER=/workspace/_p1_30p_run_A.sh
TOTAL=$(wc -l < /workspace/_p1_30p_queue.tsv 2>/dev/null || echo 0)
TOTAL=$((TOTAL - 1))
# 本机（A）只负责 dota15→aitod 那一层
MINE=$(awk -F'\t' 'NR>1 && $1=="A"' /workspace/_p1_30p_queue.tsv 2>/dev/null | wc -l)

echo "================ P1 监控 $(date -u '+%F %T') UTC ================"
echo "host=$(hostname)  本机应跑=$MINE run（队列共 $TOTAL）"
echo
echo "--- ① 队列进程"
if pgrep -af "_p1_30p_run_A" | grep -qv pgrep; then
  echo "  [OK] 队列在跑"
  pgrep -af "_p1_30p_run_A" | grep -v pgrep | head -3 | sed 's/^/     /'
else
  echo "  [!!] 队列进程不在"
fi
echo
echo "--- ② 训练进程"
# ★ 2026-10-06（监控子代理建议）：**按 ppid 分组**统计，不做"总数=2"的硬比。
#   原因：train_obj.py 是每个 run 一个**主进程** + 一批 dataloader worker，
#   直接 `pgrep -fc train_obj.py` 会得到 80~90 这种数，每次都被当成假警报。
# 主进程 = train_obj.py 中**其子进程里没有另一个 train_obj.py** 的那些（即 run 的顶层进程）
n_main=$(ps -eo pid=,ppid=,args= 2>/dev/null | grep "[t]rain_obj\.py" | awk '{print $1,$2}' > /tmp/_p1ps.$$; awk 'NR==FNR{pid[$1]=1;next}{if(!($2 in pid))c++}END{print c+0}' /tmp/_p1ps.$$ /tmp/_p1ps.$$; rm -f /tmp/_p1ps.$$)
n_any=$(ps -eo args 2>/dev/null | grep -c "[t]rain_obj\.py" | head -1)
echo "  train_obj.py：**主进程** = ${n_main:-0}（期望 2）｜含 worker 总进程 = ${n_any:-0}"
n_train=${n_main:-0}
pgrep -af "train_obj.py" 2>/dev/null | grep -v pgrep | sed -E 's/.*--name ([^ ]+).*--lr ([^ ]+).*/     \1  lr=\2/' | head -4
echo
echo "--- ③ GPU"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader | sed 's/^/  /'
echo
echo "--- ④ 已完成/失败计数（本机 20 run 计）"
# ★ 完成判据：results.csv 的**数据行数 ≥ 100**（表头另算）；等价地看队列日志的 `END g1_... epochs=100`。
#   起因：先前用 `$(wc -l) - 1 >= 100`，在 yolo 只写 100 行数据（101 行含表头）时得 100 成立，
#   但若它写 100 行总行数则得 99 ⇒ 判据不可靠；现改为**按日志 END 行**为主、行数为辅。
done_n=$(awk -F'	' 'NR>1 && $1=="A"{print $2}' /workspace/_p1_30p_queue.tsv 2>/dev/null | while read -r r; do
  if grep -q "END $r .*epochs=100" "$LOG" 2>/dev/null; then echo ok; continue; fi
  f="/workspace/runs/$r/results.csv"
  if [ -f "$f" ]; then d=$(grep -c '^[0-9]' "$f" 2>/dev/null | head -1); [ "${d:-0}" -ge 100 ] && echo ok; fi
done | grep -c ok)
echo "  完成(≥100ep) = $done_n / $MINE"
echo "  SKIP 次数 = $(grep -c 'SKIP(complete' $LOG 2>/dev/null | head -1)"
echo "  END 次数  = $(grep -c 'END g1_' $LOG 2>/dev/null | head -1)"
echo "  ★ 非零 rc = $(grep -cE 'END g1_.* rc=[^0]' $LOG 2>/dev/null | head -1)"
echo "  ★ OOM 事件 = $(grep -cE 'oom_events=[1-9]' $LOG 2>/dev/null | head -1)"
echo "  _PARTIAL_ 目录 = $(ls -d /workspace/runs/_PARTIAL_* 2>/dev/null | wc -l)"
echo
echo "--- ⑤ 最近 12 条关键行"
grep -E "启动|前置|START g1_|END g1_|SKIP\(|ALL DONE|中止" "$LOG" 2>/dev/null | tail -12 | sed 's/^/  /'
echo
echo "--- ⑥ 当前 run 的进度（从 results.csv 行数看）"
for a in base100 strat100; do
  cur=$(pgrep -af "train_obj.py" | grep -o -- "--name [^ ]*${a}[^ ]*" | head -1 | awk '{print $2}')
  if [ -n "$cur" ]; then
    f="/workspace/runs/$cur/results.csv"
    e=$([ -f "$f" ] && echo $(( $(wc -l < "$f") - 1 )) || echo 0)
    printf '  %-14s %-46s %s/100 ep\n' "$a" "$cur" "$e"
  else
    printf '  %-14s (无)\n' "$a"
  fi
done
echo
echo "--- ⑦ 判定"
alldone=$(grep -c 'ALL DONE' "$LOG" 2>/dev/null | head -1)
if [ "${alldone:-0}" -gt 0 ]; then
  echo "  [DONE] 队列已 ALL DONE（若完成数 < $MINE 需查 rc≠0 的 run）"
elif ! pgrep -af "_p1_30p_run_A" | grep -qv pgrep; then
  echo "  [!!] 队列**不在跑**且未 ALL DONE ⇒ 异常，需重启："
  echo "       cd /workspace && nohup setsid bash $RUNNER > /workspace/_p1_30p_A_nohup.out 2>&1 < /dev/null &"
elif [ "$n_train" -eq 0 ]; then
  echo "  [!!] 队列进程在但**无训练进程** ⇒ 可能卡在等卡空或刚切换 run；再看一次"
else
  echo "  [OK] 正常运行中"
fi
echo "================================================================"
