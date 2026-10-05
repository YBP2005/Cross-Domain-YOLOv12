#!/usr/bin/env bash
# P1 · 扩展批次取件（T2 / D2 / T3；**可反复跑、幂等**）
#
# 目的：把新跑的 run 的 `args.yaml` + `results.csv`，以及它们新增的 test 读数行，
#       取回本地放进 `raw/P1_ext_20261001/`，让 `01_build_base.py` 纳入底座。
#
# ★ 三次修订，每次都有实测依据：
#   1) **每台机器只一次 SSH 往返**：初版"每个 run 一次 pod_run.py" ⇒ 164 次握手，太慢。
#      现改为远端一条命令 cat 完所有文件、带分隔符，本机切分。远端**不写任何临时文件**。
#   2) ★★ **落盘必须用 'w' 一次写完，不能用 'a' 追加**：初版用 'a' ⇒ 重复取件把同一文件
#      写两遍（实测 args 232=2x116、results 62=2x31、`epoch,` 表头出现两次）。
#      后果不是"数错了"（best/last 对重复幂等），而是 **`epochs_actual` 翻倍**
#      ⇒ A4/A4c 的 `s/ep` 被对半砍。现在先在内存里攒，最后一次 'w' 落盘。
#   3) ★ **写后断言**（经验 #42/#23：写入不算核对，必须断言目标状态）：
#      results.csv 必须**恰好一个** `epoch,` 表头、首行必须是表头；args.yaml 不得有多个 `name:`。
#      任一失败 ⇒ 非零退出，**不带污染数据去重建底座**。
#
# 未跑完的 run 报 `MISSING` 跳过 ⇒ 收工前跑也没关系，收工后再跑一次即补齐。
# ⚠ **正在训练中**的 run 会被取到（results.csv 只有几行）。底座会把它们标成
#   `interrupted`（不会误判为 complete），但**临时分析必须按 outcome / 行数过滤**。
set -u
cd /d/deepseek/analysis/work
export POD_A_HOST=cpod-1u20pv1vhj4v.podtcp.compshare.cn POD_A_PORT=24581 POD_A_USER=root POD_A_PASS="${POD_A_PASS:?export POD_A_PASS first}"
export POD_B_HOST=cpod-1uearmsfxbj2.podtcp.compshare.cn POD_B_PORT=25046 POD_B_USER=root POD_B_PASS="${POD_B_PASS:?export POD_B_PASS first}"

DEST=/d/deepseek/analysis/work/analysis_M3/raw/P1_ext_20261001
DEST_WIN='D:\deepseek\analysis\work\analysis_M3\raw\P1_ext_20261001'
mkdir -p "$DEST/A/runs" "$DEST/B/runs"

# ---------- 新 run 名清单（**唯一一处**）----------
A_NAMES=""
for p in 10 20 30 40 50; do for e in 30 100; do for a in base lr005; do for s in 45 46 47 48 49 50 51; do
  A_NAMES="$A_NAMES s2df_${p}p_${e}ep_${a}_s${s}n"
done; done; done; done
# ★ T4-A（A 机，`_p1s2ae_a.sh`）：s2ae 端点 2×2 的 30ep 两格补种子 s45–s51（28 run）
#   为什么在这里列：**取件清单是唯一一处**；漏掉这一行 ⇒ GPU 跑完了但结论还停在 n=3（静默停滞）。
for p in 10 50; do for a in base lr005; do for s in 45 46 47 48 49 50 51; do
  A_NAMES="$A_NAMES s2ae_${p}p_30ep_${a}_s${s}n"
done; done; done
# ★ T5-A（A 机，`_p1s2ae_grid_a.sh`）：完整 5×2 网格的 A 侧 70 run
#   · 30ep：20p/30p/40p 补 s45–s51（42 run）  · 100ep：20p/40p 补 s45–s51（28 run）
for p in 20 30 40; do for a in base lr005; do for s in 45 46 47 48 49 50 51; do
  A_NAMES="$A_NAMES s2ae_${p}p_30ep_${a}_s${s}n"
done; done; done
for p in 20 40; do for a in base lr005; do for s in 45 46 47 48 49 50 51; do
  A_NAMES="$A_NAMES s2ae_${p}p_100ep_${a}_s${s}n"
done; done; done
# ★ T4-X（机器效应对照，`s2aeX_*`）**已按用户裁定取消**（2026-10-01）：
#   "A 侧 6 run 重跑 B 侧已完成的 10p/100ep 完全是浪费时间" ⇒ 名单里不留 `s2aeX`。
#   跨机/跨时段对"增益"的影响改用 §9 的免费旁证（同格跨日期种子切分），作为**已接受的限制**。

B_NAMES=""
for s in 45 46 47 48 49 50 51; do
  B_NAMES="$B_NAMES y11_sf_base30_s${s}n y11_sf_lr005_30ep_s${s}n"
done
for s in 47 48 49 50 51; do
  B_NAMES="$B_NAMES t2_mask2mende_base100_s${s}n t2_mask2mende_lr005_100ep_s${s}n"
done
# ★ T4-B（B 机，`_p1s2ae_b.sh`）：s2ae 端点 2×2 的 100ep 两格，**整格 10 个种子 s42–s51**（40 run）
for p in 10 50; do for a in base lr005; do for s in 42 43 44 45 46 47 48 49 50 51; do
  B_NAMES="$B_NAMES s2ae_${p}p_100ep_${a}_s${s}n"
done; done; done
# ★ T5-B（B 机，`_p1s2ae_grid_b.sh`）：全空的 `30p/100ep` 格，整 10 个种子（20 run）
for a in base lr005; do for s in 42 43 44 45 46 47 48 49 50 51; do
  B_NAMES="$B_NAMES s2ae_30p_100ep_${a}_s${s}n"
done; done

echo "[清单] A=$(echo $A_NAMES | wc -w) 个（含 T4-A 28）  B=$(echo $B_NAMES | wc -w) 个（含 T4-B 40）"

fetch() {   # $1=机器  $2=名字列表  $3=本地根(**Windows 形式**)
  local M="$1" NAMES="$2" ROOTWIN="$3"
  # ★ 路径双形式：bash 与 Windows Python 对 "/tmp" 的解释不同
  #   （bash→C:\Users\...\Temp，Windows Python→<当前盘>:\tmp）⇒ 中转文件用显式 Windows 路径，
  #   并作为**参数**传给 python，避免两处各写一遍。
  local RAWBASH="/d/deepseek/analysis/work/_fetch_$M.raw"
  local RAWWIN='D:\deepseek\analysis\work\_fetch_'"$M"'.raw'
  local cmd="for name in $NAMES; do d=/workspace/runs/\$name; \
if [ -f \$d/results.csv ]; then echo \"===BEGIN \$name\"; cat \$d/args.yaml 2>/dev/null; \
echo \"===MID\"; cat \$d/results.csv; echo \"===END\"; else echo \"===MISSING \$name\"; fi; done"
  echo "[$M] 一次往返取件中（$(echo $NAMES | wc -w) 个 run）…"
  timeout 600 python pod_run.py "$M" "$cmd" > "$RAWBASH" 2>&1
  echo "[$M] DBG cmd长度=${#cmd} raw字节=$(wc -c < "$RAWBASH" 2>/dev/null) begin命中=$(grep -ac '===BEGIN' "$RAWBASH" 2>/dev/null)"
  python - "$M" "$ROOTWIN" "$RAWWIN" <<'PYEOF'
import collections, io, os, sys
M, ROOT, RAW = sys.argv[1], sys.argv[2], sys.argv[3]
CR, LF = chr(13), chr(10)
if not os.path.isfile(RAW):
    print('[' + M + '] ERR 中转文件不存在: ' + RAW)
    sys.exit(1)
txt = io.open(RAW, encoding='utf-8', errors='replace').read().replace(CR, LF)
sys.stderr.write('DBG RAW=' + RAW + ' len=' + str(len(txt)) + ' countBEGIN=' + str(txt.count('===BEGIN')) + LF)

buf = collections.defaultdict(list)
cur = mode = None
got = miss = 0
for line in txt.split(LF):
    if line.startswith('===BEGIN '):
        cur, mode = line[len('===BEGIN '):].strip(), 'a'
        continue
    if line.startswith('===MID'):
        mode = 'r'
        continue
    if line.startswith('===END'):
        cur = mode = None
        got += 1
        continue
    if line.startswith('===MISSING'):
        miss += 1
        cur = mode = None
        continue
    if cur and mode:
        buf[(cur, mode)].append(line)

bad = []
nrun = 0
for (name, mode), lines in sorted(buf.items()):
    d = os.path.join(ROOT, name)
    os.makedirs(d, exist_ok=True)
    fn = 'args.yaml' if mode == 'a' else 'results.csv'
    # ★ 一次 'w' 落盘（不是 'a'）—— 见文件头修订 2
    io.open(os.path.join(d, fn), 'w', encoding='utf-8', newline=LF).write(LF.join(lines) + LF)
    if mode == 'r':
        nrun += 1
        hdr = sum(1 for l in lines if l.startswith('epoch,'))
        if hdr != 1:
            bad.append(name + ': results.csv 的 epoch 表头出现 ' + str(hdr) + ' 次（应为 1）')
        if not (lines and lines[0].startswith('epoch,')):
            bad.append(name + ': results.csv 首行不是 epoch 表头')
    else:
        if sum(1 for l in lines if l.startswith('name: ')) > 1:
            bad.append(name + ': args.yaml 出现多个 name:')

print('[' + M + '] 取到 ' + str(nrun) + ' 个 run，缺 ' + str(miss) + ' 个；写后断言 -> '
      + ('PASS 全部通过' if not bad else 'FAIL ' + str(len(bad)) + ' 条'))
for b in bad[:10]:
    print('    ! ' + b)
sys.exit(1 if bad else 0)
PYEOF
  local rc=$?
  rm -f "$RAWBASH"
  return $rc
}

ONLY="${FETCH_ONLY:-AB}"   # ★ 2026-10-01：B 机已移交 P2 ⇒ 用 FETCH_ONLY=A 只取本侧
if [ "$ONLY" = "AB" ] || [ "$ONLY" = "A" ]; then
  echo "===== A 机（T2/T4-A/T5-A）====="
  fetch A "$A_NAMES" "$DEST_WIN\\A\\runs" || echo "WARN A 机取件断言失败"
fi
if [ "$ONLY" = "AB" ] || [ "$ONLY" = "B" ]; then
  echo "===== B 机（D2/T3/T4-B/T5-B）====="
  fetch B "$B_NAMES" "$DEST_WIN\\B\\runs" || echo "WARN B 机取件断言失败"
fi

# ---------- test 读数（只取新 run 的行）----------
for M in A B; do
  [ "$ONLY" = "AB" ] || [ "$ONLY" = "$M" ] || continue
  if [ "$M" = A ]; then NAMES="$A_NAMES"; else NAMES="$B_NAMES"; fi
  pat=$(echo $NAMES | tr ' ' '|')
  timeout 300 python pod_run.py "$M" "grep -aE '^($pat),' /workspace/sio_b_results.csv" 2>&1 \
    | grep -vE '^(\$|\[exit)' > "$DEST/${M}_sio_b_results.csv"
  echo "[$M] test 读数行 = $(grep -c . "$DEST/${M}_sio_b_results.csv" 2>/dev/null || echo 0)（期望 $(echo $NAMES | wc -w)）"
done

echo
echo "接着跑：cd /d/deepseek/analysis/work/analysis_M3 && python scripts/01_build_base.py"
