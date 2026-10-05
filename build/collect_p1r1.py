# -*- coding: utf-8 -*-
"""collect_p1r1.py —— 收 P1 盲审产物：机械抽取 8 维分数 + 四要素 + 自洽核对。

作者口径（2026-10-04）：各模型把评审写进**自己模型名的文件夹**，文件名前缀 `p1r1_review_`。
本脚本把落盘的文件收成两张表：
  · `收稿_原始抽取.json`  —— 逐份的原始抽取（可复核，含未解析到的原因）
  · `收稿_横向对比.md`    —— 横向对比表 + 四要素完整率 + 自洽核对 + 档位分布

★ 纪律（与项目一致）：
  · **解析不到不许静默跳过**：解析失败的格子进 `issues`，并在总表里标红。
  · **四要素缺失 ⇒ 该维不予采信**（按任务书 §2 的规则），本脚本只**标注**，不替作者改分。
  · **各维扣分之和必须 == 100 − 总分**；对不上就把残差算出来，不装作一致。

用法：
  python collect_p1r1.py                  # 收全部并写两张表
  python collect_p1r1.py --root E:\WorkBuddy
  python collect_p1r1.py --json-only      # 只看 JSON
"""
import os
import re
import io
import sys
import json
import glob
import argparse

DIMS = ['新颖性与贡献', '技术严谨性与理论正确性', '实验充分性与消融', '评估公平性与基准协议',
        '可复现性', '评估指标合理性', '统计显著性', '不确定度与误差分析']
MAXES = [15, 15, 15, 10, 10, 15, 10, 10]
FIX = ('WRITING', 'ANALYSIS', 'NEW_RUNS', 'NEW_DATA')
GRADES = ['强烈接受', '接受', '小修', '大修', '拒稿']


def read(path):
    return io.open(path, encoding='utf-8', errors='replace').read()


def cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def num(s, allow_float=True):
    """从一格文本里抽数值。⚠ **必须支持小数** —— 有一份评审给的是 12.0/13.0/12.5…，
    第一版只抽整数，把总分 85.5 抽成 85、并留下一个假的"残差 −1"（已实测）。
    处理三类写法：`**13**`、`**12.5**`、`满分 15 − 实得 10 = 扣 5`。"""
    if s is None:
        return None
    if '实得' in s or '扣' in s:
        m2 = re.search(r'实得\s*\*{0,2}(\d+(?:\.\d+)?)', s)
        if m2:
            return float(m2.group(1)) if allow_float else int(float(m2.group(1)))
    m = (re.search(r'\*\*\s*(\d+(?:\.\d+)?)\s*\*\*', s)
         or re.search(r'(\d+(?:\.\d+)?)', s))
    if not m:
        return None
    v = float(m.group(1))
    if not allow_float and v == int(v):
        return int(v)
    return v


def parse_scores(text):
    """返回 {dim_index: dict(raw=..., score=..., max=..., deducted=..., reason=..., fix=..., after=...)}"""
    out = {}
    for line in text.split('\n'):
        if not line.strip().startswith('|'):
            continue
        cs = cells(line)
        if len(cs) < 5:
            continue
        head = cs[0]
        for k, name in enumerate(DIMS):
            key = name.split('与')[0][:4] if '与' in name else name[:4]
            if (name in head) or (name.replace('性', '') in head) or (key and key in head):
                if k in out:      # 已解析过（表头行会先命中）
                    continue
                d = dict(raw=cs, score=num(cs[1]) if len(cs) > 1 else None,
                         max=num(cs[2]) if len(cs) > 2 else MAXES[k],
                         deducted=(cs[3] if len(cs) > 3 else ''),
                         reason=(cs[4] if len(cs) > 4 else ''),
                         fix=(cs[5] if len(cs) > 5 else ''),
                         after=(cs[6] if len(cs) > 6 else ''))
                out[k] = d
                break
    return out


def four_elements(d):
    """四要素齐备性：① 扣了多少 ② 原因+定位 ③ 改进类别 ④ 改进后预期分。"""
    got = []
    got.append(bool(re.search(r'\d', d.get('deducted', '') or '')) or (d.get('score') is not None and d.get('max')))
    reason = d.get('reason', '') or ''
    got.append(bool(re.search(r'§|L\d|\bAppendix\b|表|节', reason)))
    fix = (d.get('fix', '') or '').upper()
    got.append(any(f in fix for f in FIX))
    got.append(bool(re.search(r'\d', d.get('after', '') or '')))
    return got


def parse_total(text, rows):
    """总分：优先取表里的 Total 行；否则取各维之和（并记录来源）。"""
    for line in text.split('\n'):
        if line.strip().startswith('|') and re.search(r'\bTotal\b|总分|\*\*Total\*\*', line, re.I):
            cs = cells(line)
            for c in cs[1:4]:
                v = num(c)
                if v and 50 <= v <= 100:
                    return v, 'Total 行'
    vals = [r['score'] for r in rows.values() if r.get('score') is not None]
    if len(vals) == 8:
        return sum(vals), '八维之和（表内无 Total 行）'
    return None, '无法确定'


def parse_extra(text):
    """档位、是否用网、是否声明非独立、6/7/8 小计。"""
    ex = {}
    m = re.search(r'档位[^\n]{0,80}', text)
    if m:
        seg = m.group(0)
        ex['grade_raw'] = seg
        for g in GRADES:
            if g in seg:
                ex['grade'] = g
                break
    if 'grade' not in ex:
        for g in GRADES:
            if re.search(r'档位[^\n]{0,40}%s' % g, text) or re.search(r'%s（' % g, text):
                ex['grade'] = g
                break
    m = re.search(r'(6\s*/\s*7\s*/\s*8|第\s*6\s*/\s*7\s*/\s*8|专项小计)[^\n]{0,120}', text)
    if m:
        ex['sub678_raw'] = m.group(0)
        mm = re.search(r'(\d+)\s*(?:/|／)\s*35', m.group(0))
        if mm:
            ex['sub678'] = int(mm.group(1))
    used_net = re.search(r'(使用了网络|未使用网络|已使用联网|没有使用网络|未联网|未使用网络检索)', text)
    ex['net_declared'] = used_net.group(1) if used_net else None
    # ⚠ 第一版在这里报了**7/8 份假警告**：任务书要求"若看到过以前轮次就声明"，
    #   于是**如实写"没有看到过"的那一句**也被关键词命中了 —— 而那正是**独立**的证据。
    #   ⇒ 判据改为：只在**肯定式**声明里flag（"我看到了/我被载入/非独立"），
    #     并对"没有/未/否/无关"等否定式**抑制**。
    # ---- 独立性：**只在声明段里判**（任务书 §2：要求在输出开头第一段声明）----
    #   全文搜索会命中"统计独立性"（非独立重训 / 切片非独立单元），假阳性率 100%（已实测）。
    _head = text
    m_task = re.search(r'^##\s*任务\s*A', text, re.M)
    if m_task:
        _head = text[:m_task.start()]
    else:
        _head = text[:4000]
    ex['independence_scope_chars'] = len(_head)
    ex['independence_flagged'] = False
    ex['independence_note'] = ''
    #   ⓐ 明确自陈"非独立 / 失去独立"，且**不是**在"不存在…非独立"这种否定式里
    for m in re.finditer(r'[^\n]{0,60}(非独立复核|失去独立|无法独立|非独立初审|非独立评审)[^\n]{0,80}', _head):
        seg = m.group(0)
        # ★ 2026-10-04 第二轮修：**双重否定**也要排除。
        #   实测 Kimi-K2.8-Preview 的原话是"**本评审为独立盲审**（非非独立复核）"
        #   —— "非非独立"被我的判据当成"自陈非独立"，是**假阳性**（本会话第 2 次栽在否定式上）。
        if re.search(r'不存在|并非|不是|没有|未|无|否|非非|并不', seg):
            continue
        ex['independence_flagged'] = True
        ex['independence_note'] = seg.strip()[:160]
        break
    #   ⓑ 自陈"看到过 / 被载入过"以前轮次的内容（肯定式）
    if not ex['independence_flagged']:
        pat = ('[^' + chr(92) + 'n]{0,50}(看到了|被载入|载入了|读过)[^' + chr(92) + 'n]{0,40}'
               '(以前|前轮|上一轮|其它评审者|别的模型)[^' + chr(92) + 'n]{0,60}')
        for m in re.finditer(pat, _head):
            seg = m.group(0)
            if re.search(r'没有|未|无|否', seg):
                continue
            ex['independence_flagged'] = True
            ex['independence_note'] = seg.strip()[:160]
            break
    ex['independence_claimed'] = bool(re.search(
        r'(独立盲审|本评审为\*\*独立|没有载入|未被载入|未载入|没有读|没有看过|没有看到过)', text))
    return ex


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=r'E:\WorkBuddy')
    ap.add_argument('--out', default=r'E:\WorkBuddy\盲审P1\收稿')
    ap.add_argument('--json-only', action='store_true')
    a = ap.parse_args()

    files = sorted(glob.glob(os.path.join(a.root, '*', 'p1r1_review_*.md')))
    recs, issues = [], []
    for f in files:
        t = read(f)
        model = os.path.basename(os.path.dirname(f))
        rows = parse_scores(t)
        if len(rows) != 8:
            issues.append('%s：只解析到 %d/8 个维度' % (model, len(rows)))
        total, tsrc = parse_total(t, rows)
        fe = {DIMS[k]: four_elements(v) for k, v in rows.items()}
        deducted = []
        for k, v in rows.items():
            if v.get('score') is not None and v.get('max'):
                deducted.append(v['max'] - v['score'])
        ded_sum = sum(deducted) if len(deducted) == len(rows) == 8 else None
        rec = dict(model=model, path=f, chars=len(t), lines=t.count('\n') + 1,
                   scores={DIMS[k]: rows[k]['score'] for k in sorted(rows)},
                   maxes={DIMS[k]: rows[k]['max'] for k in sorted(rows)},
                   total=total, total_source=tsrc,
                   deduct_sum=ded_sum,
                   closure=((100 - total) - ded_sum) if (total is not None and ded_sum is not None) else None,
                   four_elements={k: v for k, v in fe.items()},
                   four_elements_all=all(all(v) for v in fe.values()) if fe else False,
                   rows={DIMS[k]: rows[k] for k in sorted(rows)},
                   extra=parse_extra(t))
        recs.append(rec)

    os.makedirs(a.out, exist_ok=True)
    jp = os.path.join(a.out, '收稿_原始抽取.json')
    io.open(jp, 'w', encoding='utf-8', newline='').write(
        json.dumps(dict(files=len(files), issues=issues, records=recs), ensure_ascii=False, indent=1))

    # ---- 横向对比表 ----
    L = []
    A = L.append
    A('# P1 第一轮盲审：收稿与横向对比（2026-10-04）')
    A('')
    A('> 由 `复现仓库/build/collect_p1r1.py` 机械抽取。源：`E:\\WorkBuddy\\*\\p1r1_review_*.md`，'
      '**%d 份**。原始抽取（含未解析项）见同目录 `收稿_原始抽取.json`。' % len(files))
    A('> ★ 本表**只做抽取与核对，不改分**；四要素缺失的格子按任务书 §2 的规则标出"该维不予采信"。')
    A('')
    A('## 一、8 维分数横向对比')
    A('')
    A('| 模型 | ' + ' | '.join('%d. %s' % (i + 1, d) for i, d in enumerate(DIMS)) + ' | **总分** |')
    A('|---|' + '---:|' * (len(DIMS) + 1))
    for r in recs:
        cells_ = []
        for d in DIMS:
            v = r['scores'].get(d)
            cells_.append('—' if v is None else str(v))
        A('| **%s** | %s | **%s** |' % (r['model'], ' | '.join(cells_),
                                        '—' if r['total'] is None else r['total']))
    A('')
    A('**满分**：' + '、'.join('%d. %s = %d' % (i + 1, d, m) for i, (d, m) in enumerate(zip(DIMS, MAXES))))
    A('')
    A('## 二、6/7/8 三维专项小计（主战场，满分 35）与档位')
    A('')
    A('| 模型 | 6 指标 | 7 统计 | 8 不确定度 | **小计 /35** | 档位 | 用网声明 | 独立性 |')
    A('|---|---:|---:|---:|---:|---|---|---|')
    for r in recs:
        s = [r['scores'].get(DIMS[5]), r['scores'].get(DIMS[6]), r['scores'].get(DIMS[7])]
        sub = sum(x for x in s if x is not None) if all(x is not None for x in s) else None
        A('| **%s** | %s | %s | %s | **%s** | %s | %s | %s |'
          % (r['model'], s[0], s[1], s[2], '—' if sub is None else sub,
             r['extra'].get('grade', '—'),
             r['extra'].get('net_declared') or '未声明',
             ('⚠ 自陈非独立' if r['extra'].get('independence_flagged')
              else ('✅ 自陈独立' if r['extra'].get('independence_claimed') else '未声明'))))
    A('')
    A('## 三、自洽核对（各维扣分之和 == 100 − 总分）')
    A('')
    A('| 模型 | 总分 | 总分来源 | 各维扣分之和 | 100 − 总分 | **残差** | 判定 |')
    A('|---|---:|---|---:|---:|---:|---|')
    for r in recs:
        res = r['closure']
        ok = (res is not None and abs(res) <= 0.5)   # 有评审用半档小数，总分与扣分和可差 ≤0.5
        A('| %s | %s | %s | %s | %s | %s | %s |'
          % (r['model'], r['total'], r['total_source'], r['deduct_sum'],
             '—' if r['total'] is None else 100 - r['total'],
             '—' if res is None else res, '✅ 自洽' if ok else ('⚠ 有残差' if res is not None else '—')))
    A('')
    A('## 四、四要素完整率（缺任一项 ⇒ 该维不予采信）')
    A('')
    A('| 模型 | 齐备维度 | 不齐备的维度（缺哪一项） |')
    A('|---|---:|---|')
    for r in recs:
        bad = []
        for d, got in r['four_elements'].items():
            if not all(got):
                miss = [n for n, g in zip(['①扣分', '②原因+定位', '③类别', '④改后分'], got) if not g]
                bad.append('%s（缺 %s）' % (d, '、'.join(miss)))
        A('| %s | **%d/8** | %s |' % (r['model'], sum(1 for v in r['four_elements'].values() if all(v)),
                                      '；'.join(bad) if bad else '—'))
    A('')
    A('## 五、解析问题（**不许静默跳过**）')
    A('')
    if issues:
        for i in issues:
            A('* ⚠ %s' % i)
    else:
        A('* ✅ 8 份全部解析到 8 个维度。')
    A('')
    A('---')
    A('')
    A('*生成：`collect_p1r1.py`。原始抽取：`收稿_原始抽取.json`。*')
    mp = os.path.join(a.out, '收稿_横向对比.md')
    if not a.json_only:
        io.open(mp, 'w', encoding='utf-8', newline='').write('\n'.join(L) + '\n')

    print('收稿 %d 份' % len(files))
    for r in recs:
        print('  %-24s 总分 %-4s 残差 %-4s 四要素 %d/8 档位 %s'
              % (r['model'], r['total'], r['closure'],
                 sum(1 for v in r['four_elements'].values() if all(v)), r['extra'].get('grade', '—')))
    if issues:
        print('\n⚠ 解析问题：')
        for i in issues:
            print('  ·', i)
    print('\n输出 -> %s\n        %s' % (jp, mp))
    return 0


if __name__ == '__main__':
    sys.exit(main())
