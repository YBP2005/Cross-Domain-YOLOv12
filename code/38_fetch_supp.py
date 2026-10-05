# -*- coding: utf-8 -*-
"""38_fetch_supp.py —— 把补实验的结果从 A / B 取回，并重建底座。

为什么单独写一件：这次是**两机同时跑**，各自写自己的 `/workspace/sio_b_results.csv`，
所以取回必须**分开**、再各自并入 `01_build_base.py` 的来源表。

用法：
    python scripts/38_fetch_supp.py --plan          # 只打印将要取的 run 名单与数量
    python scripts/38_fetch_supp.py --fetch A       # 从 A 取（sio + 计划内的 args/results）
    python scripts/38_fetch_supp.py --fetch B
    python scripts/38_fetch_supp.py --rebuild       # 重建底座 + 复核

只取 `args.yaml` 与 `results.csv`（各几 KB）；**不取权重**（5.5 MB × 236 个，分析用不到），
需要权重时加 `--with-weights`。
"""
import argparse
import csv
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
RAW = os.path.join(BASE, 'raw', 'P1_supp_20261002')
POD = os.path.join(os.path.dirname(BASE), 'pod_run.py')


def plan_names():
    p = os.path.join(BASE, 'provenance', 'deliver', '补实验_run清单.csv')
    return [r['name'] for r in csv.DictReader(open(p, encoding='utf-8'))]


def pod(mach, cmd, tries=6):
    """调 pod_run.py，带横幅抖动重试。"""
    import time
    last = ''
    for _ in range(tries):
        pr = subprocess.run([sys.executable, POD, mach, cmd], capture_output=True,
                            text=True, encoding='utf-8', errors='replace', timeout=180)
        out = (pr.stdout or '') + (pr.stderr or '')
        if pr.returncode == 0 and 'Error reading SSH protocol banner' not in out:
            return out
        last = out
        time.sleep(6)
    raise SystemExit('pod_run 失败：\n' + last[-800:])


def fetch(mach, with_weights):
    names = plan_names()
    dst = os.path.join(RAW, mach)
    os.makedirs(dst, exist_ok=True)
    # 1) 汇总文件（两机各自一份）
    pod(mach, 'mkdir -p /workspace/_supp_export')
    pod(mach, 'cp -f /workspace/sio_b_results.csv /workspace/_supp_export/%s_sio_b_results.csv' % mach)
    for remote, local in (('/workspace/_supp_export/%s_sio_b_results.csv' % mach,
                           os.path.join(RAW, '%s_sio_b_results.csv' % mach)),):
        pod(mach, 'echo ok')          # 保持连接节流
        subprocess.run([sys.executable, POD, mach, '--get', remote, local], check=True)
    # 2) 计划内的 run 目录：只取 args.yaml + results.csv（+ 可选 weights）
    want = ' '.join(names)
    pod(mach, 'rm -rf /workspace/_supp_export/runs; mkdir -p /workspace/_supp_export/runs; '
              'for n in %s; do if [ -d /workspace/runs/$n ]; then mkdir -p /workspace/_supp_export/runs/$n; '
              'cp -f /workspace/runs/$n/args.yaml /workspace/_supp_export/runs/$n/ 2>/dev/null; '
              'cp -f /workspace/runs/$n/results.csv /workspace/_supp_export/runs/$n/ 2>/dev/null; '
              '%s fi; done; find /workspace/_supp_export/runs -name results.csv | wc -l'
              % (want, 'mkdir -p /workspace/_supp_export/runs/$n/weights; cp -f /workspace/runs/$n/weights/*.pt /workspace/_supp_export/runs/$n/weights/ 2>/dev/null;' if with_weights else ''))
    pod(mach, 'cd /workspace/_supp_export && tar czf runs_%s.tgz runs && stat -c%%s runs_%s.tgz' % (mach, mach))
    subprocess.run([sys.executable, POD, mach, '--get', '/workspace/_supp_export/runs_%s.tgz' % mach,
                    os.path.join(RAW, 'runs_%s.tgz' % mach)], check=True)
    import tarfile
    with tarfile.open(os.path.join(RAW, 'runs_%s.tgz' % mach)) as tf:
        tf.extractall(dst)
    n = sum(1 for _ in (d for d in os.listdir(os.path.join(dst, 'runs')))) if os.path.isdir(os.path.join(dst, 'runs')) else 0
    print('[%s] 取回 run 目录 %d 个；sio 到 %s' % (mach, n, os.path.join(RAW, '%s_sio_b_results.csv' % mach)))


def rebuild():
    for s in ('01_build_base.py', '14_verify_claims.py', '36_A20_loss_contrast.py', '15_audit_sources.py'):
        print('=== 重跑 %s ===' % s)
        r = subprocess.run([sys.executable, os.path.join(HERE, s)], capture_output=True,
                           text=True, encoding='utf-8', errors='replace')
        print((r.stdout or '')[-1500:])
        if r.returncode:
            print((r.stderr or '')[-800:])
            raise SystemExit('%s 失败' % s)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--plan', action='store_true')
    ap.add_argument('--fetch')
    ap.add_argument('--rebuild', action='store_true')
    ap.add_argument('--with-weights', action='store_true')
    a = ap.parse_args()
    if a.plan:
        n = plan_names()
        print('计划内 run 共 %d 条' % len(n))
        print('前 5:', n[:5])
    if a.fetch:
        fetch(a.fetch, a.with_weights)
    if a.rebuild:
        rebuild()
