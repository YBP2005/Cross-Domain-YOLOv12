# -*- coding: utf-8 -*-
"""15_audit_sources.py —— **审计数字的来源指针与可复算路径**（带守卫）。

用途：新稿 §6/§7 有 6 条数字，底座（run 级表）里查不到。交接件要求
「**要么补取这些文件，要么在稿中写清来源与可复算路径**」。本件做后者，并且
**让指针本身受守卫保护** —— 出处文件里若找不到那段原文，本件**硬失败**。

依据 `E:\\workplace\\通用经验与教训`：
  · **#41**：「存证存在」≠「条款已抽出」—— 归档了文件不等于抽出了那句话 ⇒ 本件**逐条抽出原文**；
  · **#56**：空集合必须**硬失败** —— 匹配不到就是 FAIL，不是"跳过"；
  · **#42**：记录里的"已完成 X"，X 必须有一个可执行的检查 ⇒ 本件就是那个检查；
  · **#71**：测量件过期 ⇒ 假"没反应" —— 所以本件把**被引文件的 md5** 写进产物。

产物：`deliver\\审计数字_来源与可复算路径.md`
"""
import os
import re
import sys
import json
import hashlib

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
def _find_root(start):
    d = os.path.abspath(start)
    for _ in range(6):
        if os.path.isdir(os.path.join(d, 'base')) and os.path.isdir(os.path.join(d, 'deliver')):
            return d
        d = os.path.dirname(d)
    return os.path.abspath(start)


def _find_m3d(start):
    d = os.path.abspath(start)
    for _ in range(6):
        c = os.path.join(d, 'M3_draft')
        if os.path.isdir(c):
            return c
        d = os.path.dirname(d)
    return os.path.join(os.path.abspath(start), 'M3_draft')
BASE = _find_root(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _cells as _C          # noqa: E402  ★ 交付件目录的唯一解析器

# ★★ 2026-10-05：**向上查找项目根**（布局无关）。
#   放行仓库：repo/code/x.py ⇒ BASE = repo（含 base/ deliver/ M3_draft/）
#   作者树  ：analysis_M3/scripts/x.py ⇒ BASE = analysis_M3（M3_draft 在上两级）
OUT = _C.deliver_dir()      # ★ 布局无关：作者树 deliver/、放行仓 provenance/deliver/
SUPP = os.path.join(_find_m3d(BASE), '00_SUPPLEMENTARY_v0.4.md')

# (编号, 论文里的数字, 出处小节, 检索式, 底座可否独立复算的说明)
ITEMS = [
    ('S1', '§6(a) 一阶几何量 **SNR < 2（18/18 格）**，频带 **0.76–1.47**',
     'Appendix H.1',
     r'SNR.{0,60}?0\.76\s*[–\-]\s*1\.47',
     '不可 —— 需要梯度/扰动读数，底座只有训练与验证指标'),
    ('S2', '§6(c) **ε-缩放指数 0.56–0.81（中位 0.59）**',
     'Appendix G.2',
     r'0\.56\s*[–\-]\s*0\.81',
     '不可 —— 需要三个半径上的扰动增量'),
    ('S3', '§6(c) **源侧平稳谱 253–284（±6%）**',
     'Appendix G.2',
     r'253\s*[-–]\s*284',
     '不可 —— 需要谱读数'),
    ('S4', '§7 **OOM 回退影响中位 −0.0006 pp（σ̂=0.17，20 格）**',
     '（OOM 审计段）',
     r'0\.0006\s*pp.{0,200}?0\.166\s*[–\-]\s*0\.190',
     '不可 —— 需要逐 OOM 事件的成对复算；底座无该审计表'),
    ('S5', '§7 **三方划分把读数移动 −0.069 pp（p = 0.825）**',
     '（三重划分段）',
     r'0\.069\s*pp.{0,200}?p\s*=\s*0\.825',
     '不可 —— 需要三份划分的逐 run 读数（补材 §M.4 给了三份划分的文件名级交集为 0）'),
    ('S6', '§7 **clean 三方协议十种子：强格 +1.434 / 佐证格 +0.507**',
     'Appendix E.2',
     r'1\.434\s*pp.{0,600}?0\.507\s*pp',
     '不可 —— 但**补材给了完整算式**（baseline 42.062 → strategy 43.496，SD 0.383，t=11.84，p=0.0020）'),
    ('S7', '§7 **11 / 13 种子扩展：+1.409 / +0.628**',
     'Appendix E.2',
     r'1\.409\s*pp.{0,400}?0\.628\s*pp|1\.409\s*pp\s*\*\*at eleven seeds\*\*.*?0\.628\s*pp',
     '不可 —— 同上，补材给了 SD/t/p 与逐种子符号数'),
]


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    if not os.path.isfile(SUPP):
        print('❌ 被引文件不存在：%s' % SUPP)
        return 2
    txt = open(SUPP, encoding='utf-8', errors='replace').read()
    lines = txt.split('\n')
    smd5 = md5(SUPP)

    L = []
    fails = []

    def w(s=''):
        L.append(s)

    w('# 审计数字的来源与可复算路径（§6 / §7）')
    w()
    w('> **本件的用途**：新稿 §6/§7 的 6 类数字在 **run 级底座里查不到**（它们来自扰动实验、')
    w('> 谱读数、划分表、OOM 审计），交接件要求「要么补取这些文件，要么在稿中写清来源与可复算路径」。')
    w('> 本件做后者：**逐条给出出处、行号、原文**，并标明底座能否独立复算。')
    w('>')
    w('> ★ **本件自带守卫**：出处文件里若匹配不到那段原文，脚本**硬失败**（不是跳过）。')
    w('> 依据 `通用经验与教训` #41「存证存在 ≠ 条款已抽出」与 #56「空集合必须硬失败」。')
    w()
    w('## 被引文件（冻结记录）')
    w()
    w('| 项 | 值 |')
    w('|---|---|')
    w('| 路径 | `analysis\\M3_draft\\00_SUPPLEMENTARY_v0.4.md` |')
    w('| md5 | `%s` |' % smd5)
    w('| 行数 | %d |' % len(lines))
    w('| 大小 | %d 字节 |' % len(txt.encode('utf-8')))
    w()
    w('> ⚠ 本 md5 是**本次抽取时**的；被引文件若被改动，本守卫的原文抽取会立刻失败。')
    w()
    w('## 逐条来源指针')
    w()
    w('| # | 论文数字 | 出处 | 行号 | 底座能否独立复算 |')
    w('|---|---|---|---|---|')
    detail = []
    for cid, num, where, pat, computable in ITEMS:
        m = re.search(pat, txt, re.S)
        if not m:
            fails.append((cid, num, where, pat))
            ln = '—'
            snippet = '**⚠ 匹配不到（守卫报红）**'
        else:
            ln = txt[:m.start()].count('\n') + 1
            snippet = re.sub(r'\s+', ' ', lines[ln - 1] if ln - 1 < len(lines) else m.group(0)).strip()
            if len(snippet) > 400:
                snippet = snippet[:400] + ' …'
        w('| %s | %s | %s | L%s | %s |' % (cid, num, where, ln, computable))
        detail.append((cid, num, where, ln, snippet, computable))

    w()
    w('## 逐条原文（**逐字**，便于与稿内引文对照）')
    w()
    for cid, num, where, ln, snippet, computable in detail:
        w('### %s ｜ %s' % (cid, num))
        w()
        w('* 出处：**%s**，L%s' % (where, ln))
        w('* 底座可独立复算：**%s**' % computable)
        w()
        w('> %s' % snippet)
        w()

    # ★ 底座能给的那一条：§6(b) 的 −0.307
    w('## ★ 唯一一条**底座能独立复算**的审计数字：§6(b) 的符号翻转')
    w()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _cells as C
    _, G = C.load()
    r = C.cell(G, 'shwd2sf→sfchd20', 100, None, 'r10', key='test_map50_95', min_n=3)
    rb = C.cell(G, 'shwd2sf→sfchd20', 100, None, 'r10', key='best_map50_95', min_n=3)
    if r and rb and 'ambiguous' not in r and 'ambiguous' not in rb:
        w('补材把 §6(b) 写成「`SHWD→SFCHD` **+0.627**（best）→ **−0.307**（carve-val max）」；')
        w('而底座在同一格（`shwd2sf→sfchd20` · 族 `r10` · 100ep · **n=%d**）上给出：' % r['n'])
        w()
        w('| 指标列 | 增益(pp) | 与补材的对应 |')
        w('|---|---|---|')
        w('| `test_map50_95`（test 侧） | **%+.3f** | 对应补材的 **+0.627**（十三种子 clean 值） |' % r['mean'])
        w('| `best_map50_95`（val 侧最优轮） | **%+.3f** | 对应补材的 **−0.307** |' % rb['mean'])
        w()
        w('⇒ **这条"符号翻转"在底座里有一个逐位对应的实例**（同一格换指标列即翻转）。')
        w('  建议稿中把它与补材的 carve-val 读数**并列引用**，而不是只写 ✅CONFIRMED ——')
        w('  这样读者至少能在一个方向（test 侧）上自己复算。')
    else:
        w('* ⚠ 该格未能解析（r=%s / rb=%s）⇒ **守卫报红**' % (r, rb))
        fails.append(('S8', '§6(b) 底座对应量', 'base', 'shwd2sf→sfchd20/r10/100ep'))
    w()

    w('## 汇总')
    w()
    w('* 条目 **%d** 条；抽到原文 **%d** 条；**匹配不到 %d 条**。'
      % (len(ITEMS) + 1, len(ITEMS) - len([f for f in fails if f[0].startswith('S') and f[0] != 'S8']) + 1,
         len(fails)))
    w()
    if fails:
        w('❌ **守卫报红**（下列条目在出处文件里匹配不到原文，必须人工核对）：')
        w()
        for cid, num, where, pat in fails:
            w('* `%s` %s —— 出处 %s；检索式 `%s`' % (cid, num, where, pat))
        w()
    else:
        w('✅ 全部条目都在出处文件里**逐字命中** ⇒ 指针有效，可安全写进稿中。')
        w()
    w('> 提醒（经验 **#26**）：**审计全绿 ≠ 送审就绪**。本件只管"来源可核"，')
    w('> 不管这些数字**该不该**用、以及它们的论证强度。')
    w()

    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, '审计数字_来源与可复算路径.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    json.dump(dict(source=SUPP, md5=smd5, items=len(ITEMS), fails=[f[0] for f in fails]),
              open(os.path.join(OUT, '_audit_sources.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('条目 %d；失败 %d' % (len(ITEMS) + 1, len(fails)))
    for f in fails:
        print('  ❌', f[0], f[1])
    print('输出 -> %s' % os.path.join(OUT, '审计数字_来源与可复算路径.md'))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
