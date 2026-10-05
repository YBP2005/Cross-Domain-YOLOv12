# -*- coding: utf-8 -*-
"""39b_capture_args_snapshot.py —— **重抓训练协议指纹快照**（写文件；只在机器还在时能跑）。

用法：
    python scripts/39b_capture_args_snapshot.py            # 抓 A + B 活机，合并 raw/ 归档，覆盖快照
    python scripts/39b_capture_args_snapshot.py --dry-run  # 只看会写什么，不落盘

产出：`base/args_protocol_snapshot.csv`（守卫 `39_verify_protocol_fingerprint.py` 的证据）。

为什么单独一件
--------------
快照是**不可再生证据**（pod 是租用的）。但"不可再生"不等于"不可复现"——
只要机器还在，就应该能**一条命令**重抓。本件把那几条临时脚本固化成正式入口，
避免下次再用 `printf` 现敲一个（那次的 heredoc 还被 pwsh 吃掉了一次反斜杠）。

口径（与守卫一致，改这里必须同步改守卫）
----------------------------------------
· 逐 `args.yaml` 记录 `batch / workers / imgsz / epochs` **和字节数**；
· **字节数必须落盘** —— 0 字节 `args.yaml` 在 A 机上真实存在（11 例，
  `/workspace/runs/<name>/` 占位；实体在 `p4_base_weights/` 或 `b_archive/runs/`）。
  只看 `os.path.exists()` 会把 0 字节文件当成"有档案"（已踩）。
· `model` / `data` 取 **basename**：够用于识别外来项目（Sparse-YOLO），又不泄漏长路径。
"""
import os
import csv
import sys
import argparse
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # analysis_M3/
WORK = os.path.dirname(ROOT)                       # analysis/work/（pod_run.py 所在）
OUT = os.path.join(ROOT, 'base', 'args_protocol_snapshot.csv')
LOCAL_TSV = {'A': os.path.join(WORK, '_A_map3.tsv'), 'B': os.path.join(WORK, '_B_map3.tsv')}

# 远端采集脚本：只用标准库；输出 TSV（11 列，与守卫的字段一一对应）
REMOTE = r'''
import os,re
g=lambda t,k,d="?":(re.search(r"^%s:\s*(.*)$"%k,t,re.M).group(1).strip() if re.search(r"^%s:\s*(.*)$"%k,t,re.M) else d)
sz=lambda p:(os.path.getsize(p) if os.path.exists(p) else -1)
for dp,dn,fn in os.walk("/workspace"):
    if "args.yaml" in fn:
        p=os.path.join(dp,"args.yaml")
        try: t=open(p,encoding="utf-8",errors="replace").read()
        except Exception: t=""
        print("%s\t%s\t%s\t%s\t%s\t%d\t%d\t%d\t%s\t%s\t%s"%(dp,g(t,"batch"),g(t,"workers"),g(t,"imgsz"),g(t,"epochs"),
              sz(p),sz(os.path.join(dp,"results.csv")),1 if os.path.isdir(os.path.join(dp,"weights")) else 0,
              os.path.basename(g(t,"model")),os.path.basename(g(t,"data")),g(t,"project")))
'''

HEADER = ['source', 'path', 'name', 'batch', 'workers', 'imgsz', 'epochs',
          'args_bytes', 'results_bytes', 'has_weights', 'model', 'data', 'project']


def _pod(args, timeout=900):
    """调 analysis/work/pod_run.py（不经 pod_retry：重试由调用方按需加）。"""
    return subprocess.run([sys.executable, os.path.join(WORK, 'pod_run.py')] + args,
                          capture_output=True, text=True, encoding='utf-8',
                          errors='replace', timeout=timeout, cwd=WORK)


def capture(mach, dry=False):
    tmp = os.path.join(WORK, '_argsmap3_capture.py')
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(REMOTE)
    print('  [%s] 上传采集脚本 …' % mach)
    if dry:
        return []
    p = _pod([mach, '--put', '/workspace/_argsmap3.py', '_argsmap3_capture.py'])
    if 'put ' not in (p.stdout or ''):
        raise SystemExit('[%s] 上传失败：%s%s' % (mach, p.stdout, p.stderr))
    # 用 pod_retry 扛 SSH 抖动（本机 pod 约 1/3–1/5 概率 Error reading SSH protocol banner）
    r = subprocess.run([sys.executable, os.path.join(WORK, 'pod_retry.py'), mach,
                        'python3 /workspace/_argsmap3.py'],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=1800, cwd=WORK)
    lines = [ln for ln in (r.stdout or '').splitlines()
             if ln.strip() and not ln.startswith('$') and len(ln.split('\t')) == 11]
    # ★ 远端只打 11 列（不含 `name`，也不剥 `/workspace/` 前缀）；
    #   这里补齐成 13 列 —— **忘了派生 `name` 会让表头与行差一列，
    #   csv 读出来末列 `project` 变成 `None`，守卫当场崩**（已踩，靠端到端复现测试抓到）。
    if not lines:
        raise SystemExit('[%s] 一条都没收到 —— 不要写快照，先查 SSH/路径。stderr=%s'
                         % (mach, (r.stderr or '')[-400:]))
    print('  [%s] 收到 %d 条记录（rc=%d）' % (mach, len(lines), r.returncode))
    out = []
    for ln in lines:
        p, b, w, i, e, ab, rb, nw, md, da, pj = ln.split('\t')
        out.append((mach, p.replace('/workspace/', ''), os.path.basename(p),
                    b, w, i, e, ab, rb, nw, md, da, pj))
    return out


def from_raw():
    """把 raw/ 归档（已从机器删除的历史件）并进来 —— 覆盖面超出活机。"""
    out, base = [], os.path.join(ROOT, 'raw')
    for dp, dn, fn in os.walk(base):
        if 'args.yaml' not in fn:
            continue
        p = os.path.join(dp, 'args.yaml')
        t = open(p, encoding='utf-8', errors='replace').read()

        def g(k):
            import re
            m = re.search(r'^%s:\s*(.*)$' % k, t, re.M)
            return m.group(1).strip() if m else '?'
        rp = os.path.join(dp, 'results.csv')
        out.append(('RAW',
                    os.path.relpath(dp, base).replace(os.sep, '/'),
                    os.path.basename(dp), g('batch'), g('workers'), g('imgsz'), g('epochs'),
                    os.path.getsize(p),
                    os.path.getsize(rp) if os.path.exists(rp) else -1,
                    1 if os.path.isdir(os.path.join(dp, 'weights')) else 0,
                    os.path.basename(g('model')), os.path.basename(g('data')), g('project')))
    print('  [raw/] %d 条（归档件）' % len(out))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    rows = []
    for m in ('A', 'B'):
        try:
            rows += capture(m, dry=a.dry_run)
        except Exception as e:                     # 单机失败不静默：明确报出并整体失败
            raise SystemExit('抓取 %s 失败：%s' % (m, e))
    if a.dry_run:
        print('--dry-run：不落盘。')
        return 0
    rows += from_raw()

    if not rows:
        raise SystemExit('空集合：一条记录都没有，拒绝写快照（否则会覆盖掉好数据）')
    # ★ 写前自检：行宽必须等于表头宽。差一列不会报错，只会让末列读成 `None`
    #   —— 守卫会崩在 `project.startswith`，而**根因在采集端**，很容易看错方向。
    badw = [r for r in rows if len(r) != len(HEADER)]
    if badw:
        raise SystemExit('列数不齐：%d 行的宽度 != 表头 %d 列，样例=%s'
                         % (len(badw), len(HEADER), str(badw[0])[:200]))
    with open(OUT, 'w', newline='\n', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(rows)
    print('写入 %s（%d 条）' % (os.path.relpath(OUT, ROOT), len(rows)))
    print('★ 请紧接着跑守卫：python scripts/39_verify_protocol_fingerprint.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
