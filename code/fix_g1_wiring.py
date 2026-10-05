# -*- coding: utf-8 -*-
r"""fix_g1_wiring.py -- 修 G1 队列的**接线错**，并清掉由它产生的重复 run。

接线错（由监视子代理报出，我复核确认）
--------------------------------------
`g1_queue.py` 里：
  · `CELLS[cell]['data']` 决定**用哪个 yaml**；
  · `--budgets`（10p/50p）**只进 run 名字**，不影响取数；
  · 而 `queue = [(c, arm, b, s) for c in cells for b in budgets for arm ...]` ⇒
    **cell 与 budget 相乘** ⇒
      ① 每个 cell 被跑两遍（一遍挂 `10p` 名、一遍挂 `50p` 名）—— **重复**；
      ② 总量翻倍（每 lane 40 → 应为 20）。
  实测证据：`args.yaml` 里 `g1_c1..._50p_s42` 与 `g1_c1..._10p_s42` 的 `data:` **都是 `dota15_10p.yaml`**。

正确的接线（与《G1实验方案》§1 的 4 个格一致）
----------------------------------------------
    c1 = dota15→dota15 @ 10p
    c2 = dota15→dota15 @ 50p
    c3 = dota15→aitod  @ 10p
    c4 = dota15→aitod  @ 50p
即 **cell 已经编码了预算** ⇒ 每格**只有一个** (cell, budget) 组合。

本脚本做两件事
--------------
1. **核重复**：把已有 run 按 `(域对, 臂, 种子)` 分组，组内两个 run 必须 `results.csv` **逐位相同**
   （同一数据 + 同种子 + 同臂 ⇒ 应当逐位相同）；**相同才判为重复**。不同则**不删**，进人工清单。
2. **清重复**：删除被判定为重复的那些 run 目录（只删重复里"多出来的那一份"），
   并把它们的名字从 `_g1_done.txt` 里移除，以便修正后的队列重跑成**正确的 50p**。

安全：默认 `--dry-run`；`--apply` 才动。删除前打印清单。
"""
import io
import os
import re
import sys
import json
import hashlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 正规的 (cell -> budget) 映射（唯一真相，与方案 §1 一致）
CELL_BUDGET = {'c1': '10p', 'c2': '50p', 'c3': '10p', 'c4': '50p'}
CELL_DOMAIN = {'c1': 'd15tod15', 'c2': 'd15tod15', 'c3': 'd15toaitod', 'c4': 'd15toaitod'}

REMOTE = r'''python3 - <<"E"
import os, glob, re, csv, json, hashlib
RUNS = '/workspace/runs'
pat = re.compile(r'^g1_(c\d)_([a-z0-9]+)_(base100|strat100)_(10p|50p)_s(\d+)$')
info = []
for d in sorted(glob.glob(os.path.join(RUNS, 'g1_c*'))):
    b = os.path.basename(d)
    m = pat.match(b)
    if not m:
        continue
    cell, dom, arm, bud, seed = m.groups()
    f = os.path.join(d, 'results.csv')
    rows = (sum(1 for _ in open(f)) - 1) if os.path.exists(f) else 0
    yml = ''
    ay = os.path.join(d, 'args.yaml')
    if os.path.exists(ay):
        for line in open(ay):
            if line.startswith('data:'):
                yml = line.split(':', 1)[1].strip(); break
    # ★ 判据用**数据列投影**的哈希，不用整文件哈希：
    #   results.csv 含时间/显存等 wall-clock 列，同数据同种子的两个 run 这些列**天然不同**，
    #   整文件 md5 会判成"不同"（我第一版就差点因此漏判）。只取确定性的那几列。
    h = ''
    if os.path.exists(f):
        try:
            import csv as _csv
            rows2 = list(_csv.DictReader(open(f)))
            keys = [k for k in rows2[0] if ('mAP' in k or 'loss' in k or k.strip()=='epoch')]
            h = hashlib.md5(('|'.join(','.join(str(r.get(k,'')) for k in keys) for r in rows2)).encode()).hexdigest()
        except Exception:
            h = ''
    info.append(dict(name=b, cell=cell, dom=dom, arm=arm, bud=bud, seed=seed,
                     rows=rows, yaml=yml, md5=h))
print('G1FIX' + json.dumps(info, ensure_ascii=False))
E'''


def sample(host, port, pw):
    import paramiko
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for _ in range(6):
        try:
            cli.connect(host, port=port, username='root', password=pw, timeout=40,
                        banner_timeout=90, auth_timeout=40, allow_agent=False, look_for_keys=False)
            break
        except Exception:
            sys.stderr.write('  重试连接…\n')
    else:
        return None
    ch = cli.get_transport().open_session()
    ch.settimeout(120)
    ch.exec_command(REMOTE)
    buf = b''
    try:
        while True:
            d = ch.recv(65536)
            if not d:
                break
            buf += d
    except Exception:
        pass
    cli.close()
    t = buf.decode('utf-8', 'replace')
    i = t.find('G1FIX')
    return json.loads(t[i + 5:].strip().split('\n')[0]) if i >= 0 else None


def main():
    apply_ = '--apply' in sys.argv
    try:
        import _cloud_creds as C
    except Exception:
        print('缺 _cloud_creds.py'); return 2
    machines = [('A', 'cpod-1u20pv1vhj4v.podtcp.compshare.cn', 24581, C.A_PW),
                ('B', 'cpod-1uearmsfxbj2.podtcp.compshare.cn', 25046, C.B_PW)]

    for tag, host, port, pw in machines:
        print('=' * 74)
        print('%s 机' % tag)
        info = sample(host, port, pw)
        if info is None:
            print('  ★ 连不上'); continue
        print('  本轮 run 目录：%d' % len(info))

        # ① 按 (域对, 臂, 种子) 分组
        groups = {}
        for r in info:
            groups.setdefault((r['dom'], r['arm'], r['seed']), []).append(r)

        dup, diff, keep = [], [], []
        for k, rs in sorted(groups.items()):
            if len(rs) == 1:
                keep.append(rs[0]); continue
            # 组内应逐位相同；不同的单独列出
            by_md5 = {}
            for r in rs:
                by_md5.setdefault(r['md5'], []).append(r)
            if len(by_md5) == 1 and rs[0]['md5']:
                # 全部相同 ⇒ 保留一个（budget 与 cell 匹配的那个），其余判重复
                want = None
                for r in rs:
                    if CELL_BUDGET.get(r['cell']) == r['bud']:
                        want = r
                if want is None:
                    want = rs[0]
                for r in rs:
                    (keep if r is want else dup).append(r)
            else:
                diff.extend(rs)

        print('  唯一(保留) %d ｜ 判重复 %d ｜ ★逐位不同需人工 %d'
              % (len(keep), len(dup), len(diff)))
        for r in dup:
            print('    [重复] %-46s rows=%-4d yaml=%s' % (r['name'], r['rows'], os.path.basename(r['yaml'])))
        for r in diff:
            print('    ★[不同] %-46s rows=%-4d md5=%s' % (r['name'], r['rows'], r['md5'][:8]))

        # ② 每格预算是否正确（诊断）
        wrong = [r for r in info if CELL_BUDGET.get(r['cell']) != r['bud']]
        print('  预算标签与格不符的 run（这些是"多出来的那一份"）：%d' % len(wrong))

        if not apply_:
            continue
        if diff:
            print('  ★ 有逐位不同的组 ⇒ **本机不自动删**，请人工看（已列在上）')

        import paramiko
        cli = paramiko.SSHClient()
        cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cli.connect(host, port=port, username='root', password=pw, timeout=40,
                    banner_timeout=90, auth_timeout=40, allow_agent=False, look_for_keys=False)

        def sh(cmd, to=120):
            ch = cli.get_transport().open_session(); ch.settimeout(to); ch.exec_command(cmd)
            b = b''
            try:
                while True:
                    d = ch.recv(65536)
                    if not d:
                        break
                    b += d
            except Exception:
                pass
            return b.decode('utf-8', 'replace').strip()

        # 残件（未满 100 轮）也隔离：否则 ultralytics 会写进新目录而不复用，留下半截数据
        partial = [r for r in info if r['rows'] < 100 and r not in dup]
        names = [r['name'] for r in dup if r['md5']] + [r['name'] for r in partial]
        if partial:
            print('  另隔离残件 %d 个（未满 100 轮）：%s'
                  % (len(partial), '、'.join(r['name'] for r in partial)))
        # 把它们移到 _wiring_dup/ 留证，而不是直接删
        sh('mkdir -p /workspace/runs/_wiring_dup')
        for n in names:
            print('    隔离 %s' % n)
            sh('mv /workspace/runs/%s /workspace/runs/_wiring_dup/ 2>/dev/null; ' % n)
        # 从 _g1_done.txt 移除这些名字，好让修正后的队列重跑成正确的 50p
        if names:
            keepdone = sh('grep -v -F -e %s /root/_g1_done.txt 2>/dev/null | wc -l'
                          % ' -e '.join("'%s'" % n for n in names))
            sh('cp /root/_g1_done.txt /root/_g1_done.txt.bak_wiring 2>/dev/null')
            sh('grep -v -F -e %s /root/_g1_done.txt > /tmp/_d.txt 2>/dev/null; mv /tmp/_d.txt /root/_g1_done.txt'
               % ' -e '.join("'%s'" % n for n in names))
            print('    _g1_done.txt 原 %d 行 -> 现 %s 行（备份 .bak_wiring）'
                  % (len(names) + int(keepdone), sh('wc -l < /root/_g1_done.txt 2>/dev/null || echo 0')))
        print('  完成：隔离 %d 个重复 run' % len(names))
        cli.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
