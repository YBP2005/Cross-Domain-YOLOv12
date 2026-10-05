#!/usr/bin/env bash
# P1 · T5 收工 → 自动取件 → 重建底座 → 算 **完整 5×2 网格** → 跑守卫
#
# 与 `21_wait_t4_then_compute.sh` 同构，只是等的队列与计算件不同：
#   · 等 A 的 `_P1s2ae_grid_a.log`（T5-A，70 run）与 B 的 `_P1s2ae_grid_b.log`（T5-B，20 run）都 ALL DONE；
#   · 算 `22_s2ae_grid.py`（完整网格）而不是 `21_s2ae_axes.py`（端点 2×2）。
#
# ★ 大小写：T5 的脚本是 `_p1s2ae_grid_{a,b}.sh`（小写 p），锁/日志是 `_P1s2ae_grid_{a,b}.lock/.log`（大写 P）。
# ★ 过滤只用 ASCII（远端控制台把中文吐成 GBK 乱码，含中文的 grep 永远匹配不上）。
set -u
cd /d/deepseek/analysis/work
export POD_A_HOST=cpod-1u20pv1vhj4v.podtcp.compshare.cn POD_A_PORT=24581 POD_A_USER=root
export POD_B_HOST=cpod-1uearmsfxbj2.podtcp.compshare.cn POD_B_PORT=25046 POD_B_USER=root
export POD_A_PASS POD_B_PASS

poll() {   # $1=机器 $2=日志路径
  local out d e
  out=$(timeout 55 python pod_run.py "$1" "echo D=\$(grep -ac 'ALL DONE' $2 2>/dev/null); echo E=\$(grep -acE 'GPU. END ' $2 2>/dev/null)" 2>/dev/null)
  d=$(echo "$out" | grep -oE '^D=[0-9]+' | head -1 | cut -d= -f2)
  e=$(echo "$out" | grep -oE '^E=[0-9]+' | head -1 | cut -d= -f2)
  echo "${d:-?}:${e:-?}"
}

echo "== 等 T5 两侧收工 =="
# T5-A 70 run（30ep×42 + 100ep×28，~5.6 h，起点 = T4-A 收工 ~10:00）⇒ ~15:35
# T5-B 20 run（30p/100ep，~2.8 h，起点 = T4-B 收工 10:00–12:10）⇒ ~13:00–15:00
# 上限 700 轮 × 2 min ≈ 23.3 h，从 04:45 起算足够。
a_ok=0; b_ok=0
for i in $(seq 1 700); do
  sa=$(poll A /workspace/_P1s2ae_grid_a.log)
  sb=$(poll B /workspace/_P1s2ae_grid_b.log)
  echo "[$i] $(date -u '+%F %T')  T5-A DONE:END=${sa}（期望 1:70）  T5-B DONE:END=${sb}（期望 1:20）"
  [ "${sa%%:*}" = "1" ] && a_ok=1
  [ "${sb%%:*}" = "1" ] && b_ok=1
  if [ "$a_ok" -eq 1 ] && [ "$b_ok" -eq 1 ]; then echo "== 两侧均已 ALL DONE =="; break; fi
  sleep 120
done
if [ "$a_ok" -ne 1 ] || [ "$b_ok" -ne 1 ]; then
  echo "!! 等待超时 —— A_ok=$a_ok B_ok=$b_ok；仍继续取件，但**不得**当 T5 验收通过。"
fi

echo
echo "== 取件 =="
FETCH_ONLY=A bash analysis_M3/scripts/19_fetch_ext.sh 2>&1 | tee /d/deepseek/analysis/work/_fetch_last.log | grep -E "\[A\]|\[B\]|WARN|FAIL|清单"

echo
echo "== 重建底座 =="
cd analysis_M3 && python scripts/01_build_base.py 2>&1 | tail -3
python scripts/12_A1_backbone.py >/dev/null 2>&1

echo
echo "== ★ 完整 5×2 网格（T5 验收的核心）=="
python scripts/22_s2ae_grid.py 2>&1

echo
echo "== 守卫 =="
python scripts/14_verify_claims.py 2>&1 | tail -3
python scripts/16_draft_tag_paths.py 2>&1 | grep -E "守卫报红"
echo
echo "===== T5 验收链结束 $(date -u) ====="
