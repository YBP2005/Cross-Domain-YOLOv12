# IJCV LaTeX 迁移报告（2026-10-17）

## 1 产出（`M3_draft_latex/`）

| 文件 | 说明 |
|---|---|
| `sn-article.tex` | 正文，`sn-jnl` 类 + `sn-mathphys-ay`（author–year，IJCV 惯例） |
| `supplementary.tex` | 补材（22 附录）独立成文 |
| `sn-bibliography.bib` | **38 条**参考文献 |
| `sn-jnl.cls` / `sn-mathphys-ay.bst` | 模板自带，随稿提交 |
| `Makefile` / `build.sh` | pdflatex→bibtex→pdflatex×2 |
| `sn-article.pdf` | ★ **29 页**，0 error |
| `supplementary.pdf` | **74 页**，0 error |

## 2 验收（逐项实测）

| 项 | 结果 |
|---|---|
| 编译 | **两份都过**：`Output written` 存在，**error 0** |
| 未定义引用 / 交叉引用 | **0 / 0** |
| cite↔bib 对账 | ★ **正文 38 个唯一 key，bib 38 条，未定义 0，未使用 0** |
| 页数 | 正文 **29 页**（IJCV 无硬页限，远低于旧的 PR 35 页上限） |
| ★ 数字完整性 | **正文数值 token 丢失 0**；Markdown 有 428 个唯一数值 token，tex 有 369 个，差额 72 个**全部在 `.bib` 中**（参考文献的 DOI 与页码），已逐个核验 |
| 摘要 | ≤250 词 |
| 图 | 两张均已接入（`figures/` 随包） |

## 3 ★ 一个方法论教训（值得记）

我第一轮对账得出"36 个 cite key 未定义、32 条 bib 未使用"，**那是我的解析 bug**（`sed` 没剥掉 `citep{` 前缀，Python 里反斜杠在 heredoc 中被吃掉）。用 `re.escape(chr(92))` 重做后，对账是**完美的 38/38/0/0**。

⇒ **"对账不平"的第一嫌疑应是我自己的解析器，而不是稿子。** 这与本项目此前那条纪律一致：**同一个解析逻辑写两遍就会出错**（`_cells.py` 的教训）。

## 4 迁移后可做的（不阻塞）

- 图片转矢量（`.pdf`/`.eps`）：现为 PNG，模板允许，但 Springer 优先矢量；
- `sn-mathphys-ay` 与 `sn-mathphys-num` 二选一需在投稿系统确认；
- 补材 74 页作为 electronic supplementary 单独提交，不需并入正文。
