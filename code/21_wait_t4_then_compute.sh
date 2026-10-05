#!/usr/bin/env bash
# P1 · T4 收工 → 自动取件 → 重建底座 → 算 s2ae 两条轴 → 跑守卫
#
# 为什么要这个：T4 的验收不只是"两个脚本写 ALL DONE"，而是
# 「**四个端点格都到 n=10，且两条轴能读出符号**」。把这条链自动化，
# 避免"GPU 跑完了但没人取件、结论还停在 n=3"这种**静默停滞**。
#
# 依赖两侧的队列：
#   · A：`/workspace/_P1T4_s2ae_a.log`（T4-A，28 run，默认已收工或正在跑）
#   · B：`/workspace/_P1T4_s2ae_b.log`（T4-B，40 run，~5.5 h）
#
# ★ 注意：T4 的日志/锁是**大写 P**（`_P1s2ae_*`），脚本本体是小写（`_p1s2ae_*.sh`）。
set -u
cd /d/deepseek/analysis/work
export POD_A_HOST=cpod-1u20pv1vhj4v.podtcp.compshare.cn POD_A_PORT=24581 POD_A_USER=root
export POD_B_HOST=cpod-1uearmsfxbj2.podtcp.compshare.cn POD_B_PORT=25046 POD_B_USER=root
export POD_A_PASS POD_B_PASS

poll() {   # $1=机器 $2=日志路径
  local out
  out=$(timeout 55 python pod_run.py "$1" "echo D=\$(grep -ac 'ALL DONE' $2 2>/dev/null); echo E=\$(grep -acE 'GPU. END ' $2 2>/dev/null)" 2>/dev/null)
  local d e
  d=$(echo "$out" | grep -oE '^D=[0-9]+' | head -1 | cut -d= -f2)
  e=$(echo "$out" | grep -oE '^E=[0-9]+' | head -1 | cut -d= -f2)
  echo "${d:-?}:${e:-?}"
}

echo "== 等 T4 两侧收工 =="
# ★ 上限 700 轮 × 2 min ≈ 23.3 h。为什么给这么宽：
#   T4-B 每 lane = 10 个 `10p` run + 10 个 `50p` run，而 `dota15_50p` 有 **706 图** vs `10p` 的 141 图（5.0×）。
#   首批实测全是 10p（~1148s/run）⇒ **08:12 只是下界**。按历史弹性（10p→50p 图数 ×5，30ep 只 ×1.58；
#   20p→40p 图数 ×2，100ep 只 ×1.33 ⇒ 对数弹性 ≈0.4）外推，`50p/100ep` 可能 1800–2400s，
#   于是 T4-B 可能晚到 10:50–13:20。上限 400 轮（~14.7 h）余量不够。
#   ⚠ 该上限只是"停止等待"的门槛，**不是**失败：到点仍会取件并算，只是要按"未全收工"判读。
a_ok=0; b_ok=0
for i in $(seq 1 700); do
  sa=$(poll A /workspace/_P1s2ae_a.log)
  sb=$(poll B /workspace/_P1s2ae_b.log)
  echo "[$i] $(date -u '+%F %T')  T4-A DONE:END=${sa}（期望 1:28）  T4-B DONE:END=${sb}（期望 1:40）"
  [ "${sa%%:*}" = "1" ] && a_ok=1
  [ "${sb%%:*}" = "1" ] && b_ok=1
  if [ "$a_ok" -eq 1 ] && [ "$b_ok" -eq 1 ]; then
    echo "== 两侧均已 ALL DONE =="; break
  fi
  sleep 120
done
if [ "$a_ok" -ne 1 ] || [ "$b_ok" -ne 1 ]; then
  echo "!! 等待超时（700 轮 × 2 min ≈ 23.3 h）—— A_ok=$a_ok B_ok=$b_ok"
  echo "!! 仍继续取件（取到多少算多少），但**不得**把结果当 T4 验收通过。"
fi

echo
echo "== 取件 =="
bash analysis_M3/scripts/19_fetch_ext.sh 2>&1 | tee /d/deepseek/analysis/work/_fetch_last.log | grep -E "\[A\]|\[B\]|WARN|FAIL|清单"
# ★ 过滤只用 ASCII：远端控制台把中文吐成 GBK 乱码，`grep "取到"` **匹配不上**（2026-10-01 实测）。

echo
echo "== 重建底座 =="
cd analysis_M3 && python scripts/01_build_base.py 2>&1 | tail -3
python scripts/12_A1_backbone.py >/dev/null 2>&1

echo
echo "== ★ s2ae 两条轴（T4 验收的核心）=="
python scripts/21_s2ae_axes.py 2>&1

echo
echo "== 守卫 =="
python scripts/14_verify_claims.py 2>&1 | tail -3
python scripts/16_draft_tag_paths.py 2>&1 | grep -E "守卫报红"
echo
echo "===== T4 验收链结束 $(date -u) ====="
