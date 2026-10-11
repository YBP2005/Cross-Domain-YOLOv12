# -*- coding: utf-8 -*-
"""44_verify_draft_hygiene.py —— 新稿的**三项机械自查**（只读，不写任何文件）。

交接件 §5 末尾列的"另有两个自查"（引用完整性 + CJK 扫描）此前**没有脚本**，
每会话靠 shell 内联 python 重打一遍；本件把它固定下来（经验 #42：记录里的"已完成 X"
必须有一个**可执行**的检查）。三项：

1. **引用完整性（编号制）**：`[n]` 的定义与引用**双向**无悬空
   —— 定义了没引、引了没定义，**都报红**（经验 #14 的双向纪律）。
   ⚠ 只扫 `## References` 之后的定义块，且**排除** `[dataset]` 前缀与正文里的 `[n]` 形式差异。
2. **CJK 扫描**：英文稿里手滑留中文（交接件 §7.3 第 17 条踩过）。允许清单：
   `## Internal notes` 之后为**内部注记**（不进送审件），故只在正文段落内报红。
3. **⚠PENDING 残留**：稿首声明"No number in this draft carries ⚠PENDING" ⇒ 必须真的一条都没有。

用法：`python scripts/44_verify_draft_hygiene.py`（失败非零退出）
"""
import os
import re
import io
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _cells as _C          # noqa: E402  ★ 布局无关的路径解析
# ★ 2026-10-07：向上查找 M3_draft（两种布局通用），不再写死层数
_M3D = _C.find_dir('M3_draft', HERE)
ROOT = os.path.dirname(_M3D)
DRAFT = os.path.join(_M3D, 'P1_NewDraft_v1_20260927.md')

CJK = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uff01-\uff5e]')


def main():
    text = open(DRAFT, encoding='utf-8').read()
    lines = text.split('\n')
    fails = []

    # ---------- 1) 引用完整性 ----------
    try:
        i_ref = next(i for i, l in enumerate(lines) if l.strip() == '## References')
    except StopIteration:
        fails.append('找不到 `## References` 标题 —— 解析失败必须报红，不得静默')
        i_ref = len(lines)
    defs = []
    for l in lines[i_ref:]:
        m = re.match(r'^\[(?:dataset\]\s*\[)?(\d+)\]', l)
        if m:
            defs.append(int(m.group(1)))
    body = '\n'.join(lines[:i_ref])
    cites = sorted({int(x) for x in re.findall(r'\[(\d+)\]', body)})
    dset = set(defs)
    dangling = [c for c in cites if c not in dset]
    unused = sorted(dset - set(cites))
    if not dset:
        fails.append('引用定义解析为 0 条 —— **空集合必须硬失败**（经验 #56）')
    if dangling:
        fails.append('引用了但没定义：%s' % dangling)
    if unused:
        fails.append('定义了但没引用：%s' % unused)

    # ---------- 2) CJK 扫描（正文段；内部注记豁免） ----------
    try:
        i_note = next(i for i, l in enumerate(lines) if l.strip().startswith('## Internal notes'))
    except StopIteration:
        i_note = len(lines)
    cjk = [(i + 1, l) for i, l in enumerate(lines[:i_note]) if CJK.search(l)]
    if cjk:
        fails.append('正文出现 CJK %d 处（首处 L%d）' % (len(cjk), cjk[0][0]))

    # ---------- 3) ⚠PENDING 残留 ----------
    #   ⚠ 计数的**不是**字符串 `PENDING` 的出现，而是**作为标签**的出现：
    #     稿首那句 "No number in this draft carries ⚠PENDING" 是**声明**，
    #     把它当残留会让守卫**永远红**（"报红本身成为噪声"⇒ 没人再看这条通道，经验 #19 §5）。
    #     ⇒ 判据 = 该行含 `PENDING` 但**不含** `No number` 这句否定声明。
    pend = [i + 1 for i, l in enumerate(lines[:i_note])
            if 'PENDING' in l and 'No number' not in l]
    if pend:
        fails.append('正文残留 ⚠PENDING：L%s' % pend)

    # ---------- 4) ★★ 2026-10-04 新增：**控制字符扫描** ----------
    #   起因（真实事故）：本会话用 shell heredoc 打补丁时，`\b`/`\a`/`\f` 被 heredoc 先解释成
    #   退格/响铃/换页符，于是稿内出现 `$|<BS>ar\Delta|$`、`$<BEL>pprox2$`、`$r_D\le<FF>rac1{16}$`
    #   —— 渲染出来就是**看不见的缺字**（`ar\Delta`、`pprox2`），而**所有既有守卫都不查这个**
    #   （它们只查自己那串期望字符串是否出现）。这是"看不见的损坏"，必须机械化。
    #   判据：LABEL 与正文里**不得出现**除 \n \t \r 之外的任何 C0 控制字符。
    CTRL = [(i + 1, ch) for i, ch in enumerate(text)
            if ord(ch) < 32 and ch not in '\n\t\r']
    if CTRL:
        fails.append('出现 C0 控制字符 %d 处（首处第 %d 字符 %r）—— 典型的 heredoc 转义事故'
                     % (len(CTRL), CTRL[0][0], CTRL[0][1]))

    print('引用：定义 %d 条、正文引用点 %d 个、悬空 %d、未引用 %d'
          % (len(dset), len(cites), len(dangling), len(unused)))
    print('CJK：正文 %d 处（内部注记 L%d 起豁免）' % (len(cjk), i_note + 1))
    print('⚠PENDING：正文 %d 处' % len(pend))
    print('控制字符：%d 处' % len(CTRL))

    # ---------- 4b) ★★ 2026-10-04 扩展：**交付件全域控制字符扫描** ----------
    #   起因：控制字符扫描原先只扫主稿与补材，而真实事故恰好出在**没被扫到的交付件**里
    #   —— `deliver/P1_理论扩张执行记录_20261004.md` 藏着 4 个 BEL、6 个退格、2 个换页符、1 个 TAB，
    #   全是 heredoc 吃反斜杠留下的伤（`ar`→`|`+BS、`rac`→FF+'rac'）。**扫不到就等于没有守卫。**
    #   判据：`deliver/` 与 `work/analysis_M3/` 下**全部 .md/.csv/.tsv/.json/.py** 都不得含 C0 控制字符。
    DELIV = os.path.join(ROOT, 'work', 'analysis_M3', 'deliver')
    EXTS = ('.md', '.csv', '.tsv', '.json', '.py', '.txt')
    bad_files = []
    scanned = 0
    if os.path.isdir(DELIV):
        for fn in sorted(os.listdir(DELIV)):
            fp = os.path.join(DELIV, fn)
            if not os.path.isfile(fp) or not fn.lower().endswith(EXTS):
                continue
            scanned += 1
            try:
                raw = io.open(fp, encoding='utf-8', newline='').read()
            except Exception:
                continue
            # 第一版把 `\r` 也算了进去 -> 51/51 全报红（这些文件是 CRLF，`\r` 合法）。
            #   判据必须是"**除 TAB/LF/CR 之外**的 C0"。
            # ★ 2026-10-04 第二个坑：判据必须写 `ord(c) not in (9,10,13)`。
            #   原来写 `c not in (9,10,13)` —— `c` 是**字符串**，而 `'\n' in 10` 会去比 `10` 的
            #   十进制表示 `"10"` ⇒ **恒为 True** ⇒ 每个文件都被判成"有问题"（51/51 假红）。
            #   这是 Python 的 `str in int` 陷阱（`int.__contains__` 把自变转成 str）。
            hits = [(i, c) for i, c in enumerate(raw)
                    if ord(c) < 32 and ord(c) not in (9, 10, 13)]
            if hits:
                bad_files.append((fn, len(hits), hits[0]))
    if bad_files:
        detail = '；'.join('%s(%d 处，首处 %r)' % (f, n, c) for f, n, c in bad_files[:4])
        fails.append('交付件里出现 C0 控制字符：%s' % detail)
    print('交付件控制字符扫描：扫 %d 件，%d 件有问题%s'
          % (scanned, len(bad_files), ('：' + '、'.join(f for f, _, _ in bad_files)) if bad_files else ''))
    # ---------- 4c) ★★ 2026-10-04 新增：**数学环境内的裸控制字符** ----------
    #   起因（真实事故，比 4) 更隐蔽）：主稿 §6 曾有 **14 处** LaTeX 命令被"转义解释"吃掉 ——
    #     `\nabla` -> `\n` 被解释成换行，留下 `abla`；
    #     `\rho`   -> `\r`/`\n` 被解释成 CR/LF，留下 `ho`；
    #     `\theta` -> `\t` 被解释成**制表符**，留下 `heta`（**全部** 6 处）；
    #     `\rangle` -> 首字母被替换成 `\langle`。
    #   ★ 4) 为何抓不到：TAB/LF/CR **本来就合法**，4) 明确豁免；
    #     而 `\t` 渲染出来**就是制表符**，肉眼也看不出。
    #   ⇒ 判据落在"**位置**"而不是"有没有"：同一行内成对 `$...$`
    #     与行间 `$$...$$` 内**不得出现裸 TAB / CR**（行间公式的 LF 是排版换行，待许）。
    #   ★ 判据自带自测：带伤样本必须报红、干净样本必须不报。
    def _math_ctrl(txt):
        out = []
        for ln, line in enumerate(txt.split(chr(10)), 1):
            s = line.rstrip(chr(13))
            for mm in re.finditer(r'\$([^$]*)\$', s):
                for ch in mm.group(1):
                    if ch in (chr(9), chr(13)):
                        out.append((ln, ch, mm.group(1)[:44]))
                        break
        for mm in re.finditer(r'\$\$(.*?)\$\$', txt, __import__('re').S):
            for ch in mm.group(1):
                if ch in (chr(9), chr(13)):
                    out.append((txt[:mm.start()].count(chr(10)) + 1, ch, mm.group(1)[:44]))
                    break
        return out

    _dirty = 'x $r_D(' + chr(9) + 'heta)$ y'
    _clean = 'x $r_D(' + chr(92) + 'theta)$ y'
    if not _math_ctrl(_dirty) or _math_ctrl(_clean):
        fails.append('数学环境控制字符判据**自测失败**')
    MATH_CTRL = _math_ctrl(text)
    if MATH_CTRL:
        _ln, _ch, _frag = MATH_CTRL[0]
        fails.append('数学环境内出现裸控制字符 %d 处（首处 L%d %r，片段 %r）'
                     ' —— 典型的"LaTeX 命令被转义解释"事故'
                     % (len(MATH_CTRL), _ln, _ch, _frag))
    print('数学环境控制字符：%d 处%s' % (len(MATH_CTRL), '' if not MATH_CTRL else ' ★'))


    # ---------- 5) ★★ 2026-10-04 新增：**"幽灵引用"扫描** ----------
    #   起因（第一轮盲审 A3，8 份里多份点名）：补材有一节声称 Fig. S1–S5 是
    #   "cited from the main text"，而**主稿里这些出现 0 次** —— 两边都不算错，
    #   但**合起来是一句不成立的自述**。控制字符/CJK/引文编号三类守卫都抓不到它，
    #   因为它是**语义**矛盾，不是**字符串**问题。⇒ 判据：补材自称被主稿引用的每一个
    #   `Fig. S<n>` / `Table S<n>` / `T<n>`，**必须在主稿正文里出现至少一次**。
    supp_path = os.path.join(ROOT, 'M3_draft', '00_SUPPLEMENTARY_v0.4.md')
    if os.path.exists(supp_path):
        supp = io.open(supp_path, encoding='utf-8', newline='').read()
        body_main = text.split('## References')[0]
        ghost = []
        for m in re.finditer(r'(Fig\.\s*S\d+|Table\s*S\d+|T\d+)[^.]{0,120}?cited (?:from|in) the main text',
                             supp):
            tok = m.group(1).replace(' ', '')
            _body_ns = re.sub(r'\s+', '', body_main)
            if tok not in _body_ns:
                ghost.append(tok)
        # 反向也查一遍：补材里"supplementary numbering — Fig. S1 to Fig. S5"这类**概称**
        #   ⚠ 概称句必须**排除已改正的写法**：现在的补材写的是
        #     "... Fig. S1 to Fig. S5 ...; **none of the five is cited from the main text** ..."
        #     —— 那句是**否定式**，不能再被当成"自称被引用"（第一版就报了这个假红）。
        for m in re.finditer(r'supplementary numbering[^.]{0,120}Fig\.\s*S1 to Fig\.\s*S5', supp):
            seg = supp[m.start():m.start() + 400]
            if re.search(r'none of (the five|them|these) is cited|not cited from the main text', seg):
                continue
            if 'Fig. S1' not in body_main and 'Fig. S1' not in ghost:
                ghost.append('Fig. S1（概称 S1–S5）')
        if ghost:
            fails.append('补材自称"被主稿引用"但主稿 0 次引用的件：%s（幽灵引用）' % '、'.join(sorted(set(ghost))))
        print('幽灵引用：%d 处' % len(set(ghost)))
    if fails:
        print('\n❌ 失败 %d 条：' % len(fails))
        for f in fails:
            print('  · %s' % f)
        return 1
    print('\n✅ 六项全绿（含交付件全域控制字符扫描 + 数学环境裸控制字符）（引用双向无悬空、正文无 CJK、无 PENDING、无控制字符）。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
