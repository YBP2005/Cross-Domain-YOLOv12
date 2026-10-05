# -*- coding: utf-8 -*-
"""build_package_p1.py —— 组装 P1 盲审包与 MANIFEST（可复跑，含断言）。

产物：
  E:\\WorkBuddy\\盲审P1\\P1盲审包_全量_<日期>.md
  E:\\WorkBuddy\\盲审P1\\复现仓库\\MANIFEST_sha256.csv
判据（任何一条不成立 ⇒ 非零退出，不写出半成品）：
  · 主稿 / 补材可读且非空；参考条目数 == 预期；引用双向无悬空（复用 build_refs 的检查逻辑）；
  · 包内必须含四个可定位段落（本轮变化块 / 前置说明 / 任务书 / 主稿 / 补材）；
  · MANIFEST 覆盖复现仓库内**除它自身**以外的每个文件。
"""
import os
import re
import io
import csv
import sys
import hashlib
import datetime

ROOT = r'E:\WorkBuddy\盲审P1'
REPO = os.path.join(ROOT, '复现仓库')
DRAFT = os.path.join(REPO, 'M3_draft', 'P1_NewDraft_v1_20260927.md')
SUPP = os.path.join(REPO, 'M3_draft', '00_SUPPLEMENTARY_v0.4.md')
DATE = datetime.date.today().strftime('%Y%m%d')
OUTPKG = os.path.join(ROOT, 'P1盲审包_全量_%s.md' % DATE)
MANIFEST = os.path.join(REPO, 'MANIFEST_sha256.csv')
EXPECT_REFS = 39

# ---- 任务定义（P1 版；评审者按此逐项作答）----
TASKS = r'''## 任务定义（逐项作答；每一项都要能在包内定位）

### 任务 A：学术判断（最重要）

| # | 问题 |
|---|---|
| **A0** | 用**你自己的话**写出本文的中心主张，**一句话**。然后指出：这个主张与稿内 §1/§10 的自我表述是否一致？若不一致，给出两处原句。 |
| **A1** | 中心主张**新不新**？请分开回答两层：① "预算会改变一个干预的符号"这层；② "把它当作**被测自变量**、在同配对/同流水线/同种子上测**成对增益的符号**"这层。**分别给出你先想到的最接近的先前工作**（有则给题名/出处，无则明说"我想不到"）。 |
| **A2** | §2 的定位是否**守得住**？作者已把 F/G/H 三条主张的定位**自我压了一档**（§2、§4.4、§4.6、§9 各有一句划界）。请判断**这些划界够不够**，以及**有没有哪一条其实还该再收窄**。 |
| **A3** | §6 的"测量层级命题"是**命题**还是**定义**？它在正文里自称"可被推翻"，并给出了证伪条件。请判断该证伪条件**是否真的可被数据推翻**。 |
| **A4** | §8 的"两项描述" $G(B)=U(B)-M(B)$ 在作者自陈 **$U$、$M$ 都未被独立测量**的前提下，**是否还有内容**？作者用同域负格排除了"$M$ 是域失配"这一读法 —— 这个排除**足够**吗？ |
| **A5** | §9 的功效审计把 **43/147** 格判为"功效不足"。这个判据**用在本文结论上是否恰当**（注意：审计覆盖的是**单预算水平量**，而 §4 的结论都在**差值量**上）？ |
| **A6** | §4.3 报出一个**列口径冲突**：第二个独立批次在**声明列**上是零结果（+0.004 pp），只在 test 列上与主批同向。你认为作者这样报**是诚实还是自伤**？对"饱和目标被损伤"这个结论，它剩下多少支撑？ |
| **A7** | §4.5 的留出符号预测（21/25、4/6 家族全同号、7/7）是**正向**结果。请判断：它的**独立单元数**（家族 = 7）是否足以支撑它现在被写成的强度？ |
| **A8** | 若**只能保留一处**贡献，你会保留哪一处？为什么？ |

### 任务 B：投稿目标

| # | 问题 |
|---|---|
| **B1** | 以 **Pattern Recognition** 的标准看，这个稿子的**当前成熟度**处于哪一档？（强烈接受／接受／小修／大修／拒稿）给出你的判断依据。 |
| **B2** | 它是否**更适合别的去处**（例如评测/复现类会议或期刊、TMLR 之类）？若是，请说明**为什么**，以及换去处后**哪些批评会消失、哪些会留下**。 |
| **B3** | 若你是 AC，你会给**几位**审稿人、各自什么专长？一句话说明本文最需要哪种专长的眼睛。 |

### 任务 Q：四个核心问题（请逐条回答，不要合并）

* **Q1 可定位性**：中心主张及其证据链，**能否在第一遍读完后就定位到具体节/表**？给出你**第一次读到时**以为证据在哪、**实际**在哪。
* **Q2 证据强度**：逐条列出你认为**证据强度与措辞不相称**的地方（多报不算错，漏报才是）。每条给：节号 + 原句 + 你认为它现在**实际**能支持到什么程度。
* **Q3 反向证据**：稿内**自己报出的**与结论相反或削弱结论的读数（至少找三条），作者是否都在**原处**做了限定？有没有哪一条**被淡化**了？
* **Q4 最容易被误读的一句**：指出**一句话**，它最可能被读者/审稿人**误读成作者没主张的东西**，并说明你会怎么改。

### 任务 V：送出前必须修的三条（**逐条判定**）

以下是作者自己列出的"送出前必须修"候选。请对**每一条**给出**同意／部分同意／不同意** + 理由 + 可定位位置：

* **V1**：`§4.5` 的留出符号预测**独立单元只有 7 个家族**，而正文写的是"21 of 25 slices"——是否必须把"独立单元是家族"这句提到**结论句之前**？
* **V2**：`§9` 的两条口径句（审计覆盖水平量 / 与种子门问的不同问题）现在放在 Limitations 里——是否**必须**上移到 §7 `Scope of inference`？
* **V3**：补材 N.1 对预注册件的 `FROZEN-HASH` 给出的复算约定（签名线以上文本、LF 归一化、末尾补一个 LF ⇒ 7,175 字节、digest `6a7eee7b…`，与整文件 md5 及字节数一并给出）是否**足够让第三方独立复算**？若不够，是否**必须**补齐（或改为只给整文件 md5 + 字节数 + 冻结时间戳）？

### 任务 C：内部一致性清扫（逐项点名，**允许"未发现"**）

请至少检查并在**未发现**时明说"未发现"：
1. **数字前后一致**：同一量在不同节的取值是否一致（尤其 §4.2 的 0.12 pp 与 0.31 pp、§4.3 的两列、§9 的 43/147 与 §4.5 的 20/45）。
2. **引用编号**：主稿 `[1]`–`[39]` 是否有悬空/错配/重复；某条被引处是否**支持它旁边那句话**。
3. **图与正文**：Fig. 1 的内容与 §3 的描述是否一致；图注里声明的"列约定"是否与 §4 各处用法一致。
4. **节号交叉引用**：正文里指向其它节/附录的指针是否指对（尤其 §9 指的 Appendix P、§10 的 unbuilt 设计）。
5. **补材与主稿**：同一数字在两处的取值与口径是否一致（注意补材的方括号编号是**另一套**）。
6. **表格自身的算术**：逐张表核"行列之和/差值/百分比"是否能自洽。

### 任务 D：必须回答的四个具体问题

* **D1**：`§5` 的注册判据（`p < 0.01` + `≥8/10 同向` + `≥+0.30 pp` + BH q=0.05）与它的结果表（T1-a/b/c）**逐格对得上**吗？T1-b 的表述（"significance 与 direction 都过、只差幅值条"）**准确**吗？
* **D2**：`§7 Scope of inference` 说"**没有任何一条主张同时通过族级校正、功效限定与 clean 协议**"。请**独立核**这句话：从 §4–§9 里能否找到一条主张**同时**满足三者？若找到，那就是作者漏报。
* **D3**：`§6` 的 SNR 门（`18/18 < 2`）与 ε-缩放指数（`0.56–0.81`）是**两个不同性质的障碍**。作者在改稿后把二者拆开写。请判断**拆开是否正确**，以及现在这两句是否**各自站得住**。
* **D4**：`§9` 称"十种子"是 0.30 pp 幅度条在档案中位噪声上**最小可判的整数**，同时明写这是**事后**的账、不是事前规则。**这个自我限定是否足够**？不足则该怎么说？

### 任务 E：收口——单一最大剩余风险

指出**一个**你认为最可能让这篇稿子在 PR 被拒或要求大修的问题，并说明：
① 它在包内的**定位**；② 它是 `WRITING` / `ANALYSIS` / `NEW_RUNS` / `NEW_DATA` 哪一类；
③ 修它**大致要多少工作量**；④ 若不修，**它的代价**是什么。

### 输出位置与文件名（**直接放进你对应的模型文件夹**）

**一句话**：把评审文件**直接放进 `E:\WorkBuddy\` 下你对应的那个模型文件夹**（基本都已经有了）；
**万一确实没有，才自己建一个同名的**。例（若你是 `Hy4 preview`）：

```
E:\WorkBuddy\Hy4 preview\p1r2_review_Hy4 preview_20261005.md
```

1. **目录**：**直接用你对应的那个文件夹**（`E:\WorkBuddy\Hy4 preview\` 之类，同名目录已存在）；
   只有**确实没有**你模型名对应的目录时，才**自己新建一个同名目录**。
   ★ 没有"只能是名单里某一个"的限制：花名册会临时换人（某家额度用尽、由同厂另一版本顶上）
   ⇒ 以**你实际是哪个模型**对应的目录为准。
2. **文件**：前缀 `p1r2_review_` 与日期 `20261005` **请勿改动**（后续按此前缀机械抽取八维分数）；
   中间用你的模型名；**一个评审者一个文件**。
3. **写完就结束**，不需要通知任何人——**作者会自己去各模型目录收**。
4. 只写**自己目录里的这一个文件**：**不要修改别人的目录**，**不要在 `盲审P1\` 目录里写任何东西**；
   你目录里若另有其它任务的残留文件，**忽略即可——不要读、不要动**。

### 输出格式（**必须遵守，便于机械抽取**）

```
## 声明
[是否使用网络；是否看到过任何以前轮次的结论；是否独立]

## 任务 A（A0–A8）
### A0 ...
### A1 ...

## 任务 B（B1–B3）
## 任务 Q（Q1–Q4）
## 任务 V（V1–V3，逐条给"同意/部分同意/不同意 + 理由 + 定位"）
## 任务 C（六项，逐项：发现 或 未发现）
## 任务 D（D1–D4）
## 任务 E（单一最大剩余风险）

## 量化评分（8 维 / 100 分）
| Dimension | Score | Max | Deducted | Reason + location | Fix (class) | Score after fix |
|---|---|---|---|---|---|---|
| 1 新颖性与贡献 | | 15 | | | | |
| 2 技术严谨性与理论正确性 | | 15 | | | | |
| 3 实验充分性与消融 | | 15 | | | | |
| 4 评估公平性与基准协议 | | 10 | | | | |
| 5 可复现性 | | 10 | | | | |
| 6 评估指标合理性 | | 15 | | | | |
| 7 统计显著性 | | 10 | | | | |
| 8 不确定度与误差分析 | | 10 | | | | |
| **Total** | | **100** | | | | |

[自洽核对：各维扣分之和 = 100 − 总分？残差 = ]
[第 6/7/8 三维专项小计 = /35]
[档位 = ；是否触发否决项/降级 = ]
```'''


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def check_draft():
    # ⚠ newline='' —— **禁用换行翻译**：Python 文本模式默认把 CRLF 归一成 LF，
    #   会让包内副本与冻结件**字节不同**（实测差 282 字节 ⇒ md5 不同）。已踩。
    d = io.open(DRAFT, encoding='utf-8', newline='').read()
    fails = []
    if len(d.split()) < 8000:
        fails.append('主稿词数异常（%d）' % len(d.split()))
    try:
        i = d.index('\n## References')
    except ValueError:
        fails.append('主稿缺 `## References`')
        return d, fails
    body = d[:i]
    defs = {int(m.group(1)) for m in re.finditer(r'^\[(?:dataset\]\s*\[)?(\d+)\]', d[i:], re.M)}
    cites = {int(x) for x in re.findall(r'\[(\d+)\]', body)}
    if len(defs) != EXPECT_REFS:
        fails.append('参考文献 %d 条 != 预期 %d' % (len(defs), EXPECT_REFS))
    if cites - defs:
        fails.append('引了没定义：%s' % sorted(cites - defs))
    if defs - cites:
        fails.append('定义了没引：%s' % sorted(defs - cites))
    # 控制字符（本会话踩过的"看不见的损坏"）
    ctrl = [c for c in d if ord(c) < 32 and c not in '\n\t\r']
    if ctrl:
        fails.append('主稿含 %d 个控制字符' % len(ctrl))
    return d, fails


def main():
    d, fails = check_draft()
    s = io.open(SUPP, encoding='utf-8', newline='').read()
    if len(s.split()) < 4000:
        fails.append('补材词数异常（%d）' % len(s.split()))
    if '## References' not in d:
        fails.append('包内缺少主稿 References 段')
    # 包内必须含的四段（**在拼好的包里查**，不是在源文件里查 —— 第一版查错了对象，报了四条假警告）
    headfile0 = os.path.join(REPO, 'build', '_pack_head.md')
    _hb = io.open(headfile0, encoding='utf-8', newline='').read() if os.path.exists(headfile0) else ''
    combined = '\n'.join([_hb, TASKS, d, s])
    for need, what in ((r'^## 任务定义', '任务定义（A/B/Q/V/C/D/E）'),
                       (r'^## 四条前置说明', '四条前置说明'),
                       (r'^### 4 评分细则本体', '评分细则本体（8 维）'),
                       (r'^【本轮送审材料】', '材料自述块')):
        if not re.search(need, combined, re.M):
            fails.append('包内缺少「%s」段' % what)
    if fails:
        print('❌ 组装中止：')
        for f in fails:
            print('  ·', f)
        return 1

    md5d = hashlib.md5(d.encode('utf-8')).hexdigest().upper()
    md5s = hashlib.md5(s.encode('utf-8')).hexdigest().upper()

    # ---- 包首：自述块 + 前置说明 + 任务书（由 build_head_p1.py 现测生成）----
    headfile = os.path.join(REPO, 'build', '_pack_head.md')
    if os.path.exists(headfile):
        headblock = io.open(headfile, encoding='utf-8', newline='').read()
    else:
        headblock = ''
        print('⚠ 未找到 %s —— 请先跑 build_head_p1.py' % headfile)

    taskblock = TASKS

    head = [
        '# P1 盲审包（全量）—— %s' % datetime.date.today().isoformat(),
        '',
        '> 本包是**自足**的盲审材料。包内依次是：**材料自述块**、**四条前置说明**、**任务书与评分细则**、',
        '> **`06_英文稿_EN`**（主稿全文）、**`08_英文补充材料_Supplementary`**（附录 A、A-bis、B–P 全文）。',
        '> 两份材料的 md5 一并冻结：主稿 `%s`，补材 `%s`。' % (md5d, md5s),
        '> 同目录另有两份**旁证**材料（`复现仓库\\`、`参考文献\\`），**不是评审对象**，用法见任务书 §0a。',
        '',
        '---',
        '',
        headblock.rstrip(),
        '',
        '---',
        '',
        taskblock.rstrip(),
        '',
    ]
    body = [
        '',
        '---',
        '',
        '# 06_英文稿_EN',
        '',
        '> 主稿全文（送审件）。md5 `%s`。' % md5d,
        '',
        d.rstrip(),
        '',
        '---',
        '',
        '# 08_英文补充材料_Supplementary',
        '',
        '> 补充材料全文（附录 A、A-bis、B–P）。md5 `%s`。' % md5s,
        '> ⚠ **重要**：补材内部出现的方括号编号（`[1]`–`[74]`）属于**上一版稿子的台账编号**，',
        '> **与主稿的 `[1]`–`[39]` 不是同一套**，不得互相引用；补材文首已有状态说明。',
        '',
        s.rstrip(),
        '',
        '---',
        '',
        '*包尾。评分细则见本包「任务书与评分细则」段；输出格式见同目录 `P1盲审任务_说明与输出格式_%s.md`。*' % DATE,
        '',
    ]
    txt = '\n'.join(head) + '\n'.join(body)
    if len(txt) < 100000:
        print('❌ 组装结果过小（%d 字符），中止' % len(txt))
        return 1
    io.open(OUTPKG, 'w', encoding='utf-8', newline='').write(txt)

    # ---- MANIFEST ----
    rows = []
    # ★★ 2026-10-04：**哈希边界收紧**。
    #   这 4 件是 `15_audit_sources.py` / `16_draft_tag_paths.py` 的**自写报告**，
    #   每次重跑内容即变（其中 `_audit_sources.json` 还把**本机绝对路径**写进内容），
    #   ⇒ **逐机逐字节复现在设计上不可能**，把它们的 sha256 当验收项会制造永久性假红。
    #   实测：169 项清单里恰好这 4 条 sha256 不符，而**字节数全都相同**。
    #   处置：**移出 MANIFEST**（README 里写明被有意排除），
    #   而不是放宽整张清单的判据 —— 其余文件的逐字节校验必须保持严格。
    MANIFEST_EXCLUDE = set(['_audit_sources.json', '审计数字_来源与可复算路径.md', '新稿_逐句脚注表.md', '新稿标签_可复算路径.md'])
    for dirpath, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d != '.git']   # ★ 2026-10-05：仓库已成 git 仓库，清单不收录 .git/
        for fn in files:
            fp = os.path.join(dirpath, fn)
            if os.path.abspath(fp) == os.path.abspath(MANIFEST):
                continue
            if os.path.basename(fp) in MANIFEST_EXCLUDE:
                continue
            rel = os.path.relpath(fp, REPO).replace('\\', '/')
            rows.append((rel, os.path.getsize(fp), sha256(fp)))
    rows.sort()
    with io.open(MANIFEST, 'w', encoding='utf-8', newline='') as fh:
        wr = csv.writer(fh)
        wr.writerow(['path', 'bytes', 'sha256'])
        wr.writerows(rows)

    print('✅ 盲审包: %s' % OUTPKG)
    print('   字符数 %d / 字节数 %d' % (len(txt), len(txt.encode('utf-8'))))
    print('   主稿 md5 %s / 补材 md5 %s' % (md5d, md5s))
    print('✅ MANIFEST: %d 个文件（不含 MANIFEST 自身）' % len(rows))
    return 0


if __name__ == '__main__':
    sys.exit(main())
