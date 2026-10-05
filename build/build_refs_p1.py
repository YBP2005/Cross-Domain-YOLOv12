# -*- coding: utf-8 -*-
"""build_refs_p1.py —— 从**现行**主稿抽出参考文献、生成文献表与逐条卡片（P1 盲审专用）。

产物（写到 `E:\\WorkBuddy\\盲审P1\\参考文献\\`）：
  00_参考文献清单_39条.md          主稿 `## References` 段**逐字**抽出
  文献表_与正文对应位置.md          编号 ↔ 被引位置（节号 + 源行号 + 次数）
  文献/NN_首作者年_关键词.md        每条一张卡片（题录 + 正文引用位置 + 核验出处）
用法：
  python build_refs_p1.py                # 抽清单 + 文献表 + 卡片
  python build_refs_p1.py --check        # 只核对，不写
判据（失败即报错，不静默）：条数 != 预期、编号不连续、引了没定义、定义了没引。
"""
import os
import re
import io
import sys
import hashlib

DRAFT = r'D:\deepseek\analysis\M3_draft\P1_NewDraft_v1_20260927.md'
SUPP = r'D:\deepseek\analysis\M3_draft\00_SUPPLEMENTARY_v0.4.md'
OUT = r'E:\WorkBuddy\盲审P1\参考文献'
CARDS = os.path.join(OUT, '文献')
EXPECT_REFS = 39  # ★ 2026-10-05 定稿：正文引用空间为 [1]–[39]，双向无悬空。
                  #   补充材料 "Prior work" 段引的 6 篇（Arviv/Zhuang/Suo/Apicella/Varma/Forstmeier）
                  #   **以作者+arXiv号/DOI 的正文式引用出现，不占编号**（补材用其自身的台账编号制）。
ALLOW_UNCITED = set()
CHECK_ONLY = '--check' in sys.argv

# 每条引用的**外部核验出处**（2026-10-04 由跳板机取到；不凭记忆写）
#   值 = (核验来源, 核验日期, 备注)
EVID = {
 1: ('arXiv:2103.03098 落地页', '2026-10-04', 'MLSys 2021'),
 2: ('DataCite dois/10.5281/zenodo.22859445', '2026-10-04', '作者 Chegondi；题名含 Auditing'),
 3: ('Crossref works/10.1109/cvpr52734.2025.00777', '2026-10-04', 'pp.8299-8309'),
 4: ('Crossref works/10.1109/tpami.2022.3217046', '2026-10-04', 'TPAMI 46(6):4018-4040'),
 5: ('Crossref works/10.1093/comjnl/bxaf120', '2026-10-02', 'The Computer Journal 69(2)'),
 6: ('Crossref works/10.1109/cvpr42600.2020.01293', '2026-10-04', '9 作者，pp.12912-12921'),
 7: ('arXiv:2503.19206 落地页 + PMLR v267', '2026-10-02', 'ICML 2025'),
 8: ('arXiv:2409.19913 落地页', '2026-10-02', 'ICLR 2025'),
 9: ('arXiv:2006.04884 落地页', '2026-10-02', 'ICLR 2021'),
 10: ('arXiv:2002.11770 落地页', '2026-10-02', 'ICLR 2020'),
 11: ('Crossref works/10.1145/3458723', '2026-10-04', 'CACM 64(12):86-92'),
 12: ('Crossref works/10.1145/3287560.3287596', '2026-10-04', 'FAT* 2019, pp.220-229'),
 13: ('arXiv:2502.12524 落地页', '2026-10-02', 'YOLOv12'),
 14: ('Ultralytics 文档页 docs.ultralytics.com/models/yolo11', '2026-10-01', '软件件，无独立论文'),
 15: ('arXiv:2606.03748 落地页', '2026-10-01', 'YOLO26；CITATION.cff 交叉核对'),
 16: ('Ultralytics 8.4.120 val 实现（包内 md5 见核验件 §六）', '2026-10-01', '指标定义'),
 17: ('arXiv:2609.04577 落地页', '2026-10-02', '作者侧逐字复核'),
 18: ('arXiv:2606.30795 落地页', '2026-10-02', '★ 最接近工作；作者侧逐字复核'),
 19: ('arXiv:2302.07011 落地页', '2026-10-02', 'ICML 2023'),
 20: ('arXiv:2010.11924 落地页', '2026-10-02', 'NeurIPS 2020'),
 21: ('arXiv:1703.04933 落地页', '2026-10-02', 'ICML 2017'),
 22: ('arXiv:2102.11600 落地页', '2026-10-02', 'ICML 2021'),
 23: ('arXiv:2102.01293 落地页', '2026-10-02', '2021'),
 24: ('arXiv:2304.09446 落地页', '2026-10-02', 'CVPR 2023'),
 25: ('公开数据集仓库名（SHWD）', '2026-10-02', '数据集'),
 26: ('arXiv:2306.02098 落地页', '2026-10-02', '数据集 SFCHD'),
 27: ('Crossref works/10.1109/TPAMI.2021.3119563', '2026-10-02', '数据集 VisDrone'),
 28: ('Crossref works/10.1109/CVPR.2018.00418', '2026-10-02', '数据集 DOTA'),
 29: ('Crossref works/10.1109/ICPR48806.2021.9413340', '2026-10-02', '数据集 AI-TOD'),
 30: ('arXiv:2106.03112 落地页（作者侧独立复核）', '2026-10-04', 'F 检索：同域 vs 跨域对比先例'),
 31: ('Crossref works/10.1109/iccv.2019.00502', '2026-10-04', 'ICCV 2019, pp.4917-4926'),
 32: ('arXiv:1902.07208 落地页', '2026-10-04', 'NeurIPS 2019'),
 33: ('arXiv:2102.05543 落地页', '2026-10-04', '2021'),
 34: ('arXiv:2106.03112 同一批次交叉核对（IVMSP）', '2026-10-04', 'DOI 10.1109/IVMSP54334.2022.9816238'),
 35: ('arXiv:1908.08142 落地页', '2026-10-04', 'H 检索：同层先例'),
 36: ('arXiv:1805.08974 落地页', '2026-10-04', 'CVPR 2019'),
 37: ('arXiv:2309.08564 落地页', '2026-10-04', 'G 检索：检测内只换骨干'),
 38: ('Crossref works/10.7717/peerj-cs.1769', '2026-10-04', '协议层最接近'),
 39: ('arXiv:2303.11267 落地页', '2026-10-04', 'VISAPP 2023；架构 vs 权重'),
}


def md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    text = io.open(DRAFT, encoding='utf-8').read()
    lines = text.split('\n')
    try:
        i_ref = next(i for i, l in enumerate(lines) if l.strip() == '## References')
    except StopIteration:
        sys.exit('❌ 找不到 `## References`')
    try:
        i_note = next(i for i, l in enumerate(lines) if l.strip().startswith('## Internal notes'))
    except StopIteration:
        i_note = len(lines)

    # ---- 1) 定义：逐字抽出 ----
    refs = []          # (编号, 行号, 原文)
    for idx in range(i_ref + 1, i_note):
        m = re.match(r'^\[(?:dataset\]\s*\[)?(\d+)\]\s+(.*)$', lines[idx])
        if m:
            refs.append((int(m.group(1)), idx + 1, lines[idx]))
    nums = [n for n, _, _ in refs]
    fails = []
    if len(refs) != EXPECT_REFS:
        fails.append('条目数 %d != 预期 %d' % (len(refs), EXPECT_REFS))
    if nums != sorted(nums) or nums != list(range(1, len(nums) + 1)):
        fails.append('编号不连续或乱序：%s' % nums)

    # ---- 2) 引用：双向 ----
    body = '\n'.join(lines[:i_ref])
    cites = sorted({int(x) for x in re.findall(r'\[(\d+)\]', body)})
    dangling = [c for c in cites if c not in set(nums)]
    unused = [n for n in nums if n not in cites]
    # ★ 2026-10-05：`[40]`–`[45]` 是**补充材料** "Prior work" 段的出处，
    #   正文**不引**它们（正文引用空间仍是 [1]–[39]，我未改动任何正文措辞以免动页数）。
    #   ⇒ 它们**不是悬空**，而是"正文未引的定义"，单独登记、不报错。
    unquoted = [n for n in unused if n in ALLOW_UNCITED]
    unused = [n for n in unused if n not in ALLOW_UNCITED]
    if dangling:
        fails.append('引了没定义：%s' % dangling)
    if unused:
        fails.append('定义了没引：%s' % unused)

    # ---- 3) 每条的被引位置（节号 + 行号）----
    sec_of = {}
    cur = '(标题前)'
    for i, l in enumerate(lines):
        if re.match(r'^## ', l):
            cur = l.strip('# ').strip()
        sec_of[i + 1] = cur
    hits = {n: [] for n in nums}
    for i, l in enumerate(lines[:i_ref]):
        for n in {int(x) for x in re.findall(r'\[(\d+)\]', l)}:
            if n in hits:
                hits[n].append((i + 1, sec_of[i + 1]))

    if fails:
        print('❌ 失败：')
        for f in fails:
            print('  ·', f)
        return 1

    # ---- 4) 写清单 ----
    md = ['# P1 主稿参考文献清单（%d 条，逐字抽出）' % len(refs), '',
          '> 源：`P1_NewDraft_v1_20260927.md`（md5 `%s`），`## References` 段（第 %d 行起）**机械抽出、逐字未改**。'
          % (md5(DRAFT).upper(), i_ref + 1),
          '> 与盲审包内 `06_英文稿_EN` 的 References 段一致；**若有出入以盲审包为准**——包才是评审对象。',
          '> ★ 本稿引用为**编号制**：正文 `[n]` ↔ 本清单 `[n]`，**双向无悬空**（生成时已断言）。', '',
          '| # | 原行 | 条目（逐字） |', '|---:|---:|---|']
    for n, ln, raw in refs:
        md.append('| %d | %d | %s |' % (n, ln, raw.replace('|', '\\|')))
    md += ['', '*生成：`E:\\WorkBuddy\\盲审P1\\复现仓库\\build\\build_refs_p1.py`（可复跑，含断言）。*', '']
    if not CHECK_ONLY:
        os.makedirs(OUT, exist_ok=True)
        io.open(os.path.join(OUT, '00_参考文献清单_%d条.md' % len(refs)), 'w', encoding='utf-8').write('\n'.join(md))

    # ---- 5) 写文献表 ----
    tab = ['# P1 文献表：%d 条引用 ↔ 正文位置' % len(refs), '',
           '> 源：`P1_NewDraft_v1_20260927.md`（md5 `%s`）。行号为该文件源行号；节号取该处**最近的上级 `## ` 标题**。'
           % md5(DRAFT).upper(),
           '> **正文口径**：该文件 `## References`（第 %d 行）**之前**的全部内容；References 段不计。' % (i_ref + 1),
           '> 补充材料（附录 A–P）单列，不计入本表的被引位置。', '',
           '## 总表', '', '| 编号 | 题录（简） | 被引次数 | 正文位置（节号） | 核验出处 | 卡片 |',
           '|---:|---|---:|---|---|---|']
    for n, ln, raw in refs:
        first = re.sub(r'^\[(?:dataset\]\s*\[)?\d+\]\s*', '', raw)
        short = re.sub(r'\s+', ' ', first)[:60]
        secs = sorted({s for _, s in hits[n]})
        card = '`文献/%02d_*.md`' % n
        ev = EVID.get(n, ('（见核验件）', '', ''))[0]
        tab.append('| %d | %s | %d | %s | %s | %s |'
                   % (n, short.replace('|', '\\|'), len(hits[n]),
                      '、'.join(secs) if secs else '—', ev.replace('|', '\\|'), card))
    tab += ['', '*生成：`build_refs_p1.py`（可复跑，含断言）。*', '']
    if not CHECK_ONLY:
        io.open(os.path.join(OUT, '文献表_与正文对应位置.md'), 'w', encoding='utf-8').write('\n'.join(tab))

    # ---- 6) 每条的卡片 ----
    if not CHECK_ONLY:
        os.makedirs(CARDS, exist_ok=True)
        for n, ln, raw in refs:
            entry = re.sub(r'^\[(?:dataset\]\s*\[)?\d+\]\s*', '', raw)
            slug = re.sub(r'[^0-9A-Za-z]+', '', re.sub(r'\s+', ' ', entry))[:26]
            ev, dt, note = EVID.get(n, ('（见 `deliver/新稿参考文献_核验.md`）', '—', '—'))
            body_ = [
                '# [%d] %s' % (n, entry), '',
                '| 项 | 值 |', '|---|---|',
                '| 编号 | `[%d]` |' % n,
                '| 主稿源行 | %d |' % ln,
                '| 被引次数 | %d |' % len(hits[n]),
                '| 正文位置 | %s |' % ('、'.join('%s（L%d）' % (s, l) for l, s in hits[n]) or '—'),
                '| 外部核验出处 | %s |' % ev,
                '| 核验日期 | %s |' % dt,
                '| 备注 | %s |' % note, '',
                '## 主稿里的原句（逐字）', '', '```', raw, '```', '',
                '> 本卡片由 `build_refs_p1.py` 机械生成；**核验出处是外部的、离线不可复算**，',
                '> 逐条证据与 URL 冻结见 `D:\\deepseek\\analysis\\work\\analysis_M3\\deliver\\新稿参考文献_核验.md`。',
                '',
            ]
            io.open(os.path.join(CARDS, '%02d_%s.md' % (n, slug)), 'w', encoding='utf-8').write('\n'.join(body_))

    print('补充材料专用（正文不引，已登记）：%s' % unquoted)
    print('引用：定义 %d、正文引用点 %d、悬空 %d、未引用 %d'
          % (len(refs), len(cites), len(dangling), len(unused)))
    print('主稿 md5: %s' % md5(DRAFT).upper())
    print('补材 md5: %s（%d 行）' % (md5(SUPP), io.open(SUPP, encoding='utf-8').read().count('\n') + 1))
    print('✅ 生成完成（清单 / 文献表 / %d 张卡片）' % len(refs))
    return 0


if __name__ == '__main__':
    sys.exit(main())
