# 理论补篇：引理证明的推导笔记（2026-10-14 放行）

**为什么放行**：Appendix A 的引理（Lemma 1–8）与 Remark 6 的 PAC-Bayes 项、Appendix B 的各向异性细节，
此前只写"proofs are carried in a theory supplement **available from the authors**；the proofs are **not part of
this release**"。第八轮 **三家评审**（GLM-5.3 −0.5、GLM-5.3-Flash −0.3、qwen-flash −0.4）指出：一篇以
可复现性为卖点的稿子，其依赖的引理证明不应"向作者索取"。本目录即为那些推导。

**内容与状态**（三份均为**推导工作稿**，未经过与正文同等的编辑，放行是为了让依赖可核，不是把它们当作
正文的一部分）：

| 文件 | 含什么 |
|---|---|
| `theory_supplement_draft_E8_E9_E10.md` | Lemma 1–3、Lemma 7 的推导与细化（含 $\|\Delta\|\le\sqrt{4LW_1/\mu_T}$ 这一步的两条路径） |
| `theory_supplement_draft_v2.md` | Lemma 3 的第 3 步、Lemma 7 的逐字迁移与余项、附录 C 的读数选择 |
| `theory_supplement_addendum_proofs.md` | Lemma 3 的 H5→H5′ 替换、Theorem 1 |

**依赖范围**（与正文一致，必须一起读）：正文 §4 的结果**只依赖 Lemma 1、2**（Kantorovich–Rubinstein 对偶
与其梯度形式，均为**教科书标准结果**，可另引文献）；Lemma 3、7 与 Remark 6 **不承载 §4 的任何结论**
（Lemma 7 是为 Appendix B 的各向异性说明与 Appendix J 的诊断保留的）。

**诚实边界**：这三份是**工作稿**，不是定稿的 theory supplement；其中若出现与正文冲突的中间结论，
**以正文为准**。正文与 Appendix A 从未依赖这些笔记里的任何非标准步骤。
