#!/usr/bin/env bash
# P1 · 等 T3 收工 → 自动取件 → 重建底座 → 算 §4.3 的 n=10
#
# 为什么要有它：T3（§4.3 饱和对照补种子 n=5→10）战线只有 ~35 min，
# 而监视子代理 20 min 才采一次 ⇒ 干等最多浪费 40 min。本作业在后台盯住 `ALL DONE`，
# 一出现就立刻走完"取件 → 重建 → 复算"，把 §4.3 的 n=10 值直接打出来。
set -u
cd /d/deepseek/analysis/work
export POD_A_HOST=cpod-1u20pv1vhj4v.podtcp.compshare.cn POD_A_PORT=24581 POD_A_USER=root POD_A_PASS='vW3M9J2V5f78O4H6'
export POD_B_HOST=cpod-1uearmsfxbj2.podtcp.compshare.cn POD_B_PORT=25046 POD_B_USER=root POD_B_PASS='26jA953OMo708IEX'
export POD_A_PASS POD_B_PASS

echo "== 盯 T3 =="
ok=0
for i in $(seq 1 70); do
  n=$(timeout 55 python pod_run.py B 'grep -ac "ALL DONE" /workspace/_P1T3_t2mende.log' 2>/dev/null | grep -E '^[0-9]+$' | head -1)
  e=$(timeout 55 python pod_run.py B 'grep -acE "GPU. END " /workspace/_P1T3_t2mende.log' 2>/dev/null | grep -E '^[0-9]+$' | head -1)
  echo "[$i] $(date -u '+%F %T')  ALL_DONE=${n:-?}  END=${e:-?}/10"
  if [ "${n:-0}" -ge 1 ]; then ok=1; break; fi
  sleep 60
done
if [ "$ok" -ne 1 ]; then echo "❌ 70 分钟仍未收工，放弃本轮"; exit 1; fi

echo "== T3 已收工，取件 =="
bash analysis_M3/scripts/19_fetch_ext.sh 2>&1 | grep -E "取到|test 读数"

echo "== 重建底座 =="
cd analysis_M3 && python scripts/01_build_base.py 2>&1 | tail -4
python scripts/12_A1_backbone.py >/dev/null 2>&1

echo
echo "== §4.3 的 n=10 结果 =="
cd scripts && python -c "
import sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
import _cells as C
rows,G=C.load()
bb=C.load_backbone()
print('底座行数 =',len(rows))
print('论文 §4.3 = -1.49 pp (t=-4.02, p=0.016, 5/5)  [族 t2 / mende_20p / 100ep / val-best 列]')
for key in ('best_map50_95','test_map50_95'):
    for tag,sd in (('全格',None),('仅 s42-s46（=论文的 5 个）',lambda s: s<=46)):
        c=C.cell(G,'mask→mende',100,None,'t2',key=key,seeds=sd,min_n=3)
        if c is None or 'ambiguous' in c:
            print('  %-15s %-26s -> %s'%(key,tag,c)); continue
        print('  %-15s %-26s n=%2d mean=%+.4f t=%+.3f 更低 %d/%d seeds=%s'%(
            key,tag,c['n'],c['mean'],c['t'],
            sum(1 for v in c['per_seed'].values() if v<0),c['n'],sorted(c['per_seed'])))
print()
for tag,sd in (('全格',None),('仅 s42-s46',lambda s: s<=46)):
    c=C.cell(G,'mask→mende',100,None,'t2',key='best_map50_95',seeds=sd,min_n=3)
    if c and 'ambiguous' not in c:
        print('  逐种子(%s, best 列): %s'%(tag,{('s%d'%k):round(v,3) for k,v in sorted(c['per_seed'].items())}))
"
echo
echo "== 守卫（T3 数据纳入后重跑）=="
# ★ 此处 cwd 已在 analysis_M3/scripts（上面 `cd scripts` 过）⇒ 不能再写 scripts/07_claims.py，
#   否则找 scripts/scripts/07_claims.py。2026-10-01 实际踩到（T3 那轮末尾这一步报了 FileNotFoundError）。
cd .. && python scripts/07_claims.py 2>&1 | tail -2
python scripts/14_verify_claims.py 2>&1 | tail -3
