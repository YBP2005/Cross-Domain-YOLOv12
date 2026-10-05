# `theory_B_MDE_diff_by_cell.csv` —— **差值量（成对预算对比）逐格 MDE 表**说明

> 生成日期 **2026-10-06**。只读底座 `base/run_table_canonical.csv`（2 362 run），
> 唯一格解析器 `code/_cells.py`。**本件不修改任何既有文件**（`theory_B_MDE_by_cell.csv`
> 的 sha256 仍为 `9e58dcc80194af97cb9073ad465dc7288018dc8e7d566387285bcdc51f37676f`）。

---

## 1. 口径（**照抄稿内冻结值，未改**）

$$\mathrm{MDE}=\gamma(n)\cdot\hat\sigma,\qquad
\gamma(n)=\frac{t_{1-\alpha/2,\,n-1}+t_{1-\beta,\,n-1}}{\sqrt{n}},\qquad \alpha=0.05,\ \beta=0.80 .$$

本表的“差值量”**不是**单格水平量的同义词，而是**同种子配对的预算对比**：

$$d_s(b)=\big(\text{lr005}_s-\text{base}_s\big)\times 100 \ \ (\text{pp，预算 }b),\qquad
D_s=d_s(\text{to})-d_s(\text{from}),$$

$$\texttt{mean\_diff}=\overline{D},\quad \texttt{sd\_diff}=\mathrm{SD}(D)\ (n-1),\quad
\texttt{mde\_diff}=\gamma(n)\cdot\texttt{sd\_diff},\quad \texttt{resolvable}=|\overline{D}|\ge \texttt{mde\_diff}.$$

* **键**：`(pair, family, label_budget, epoch_budget)`，与水平量表**同一套键**。
  `label_budget`/`epoch_budget` 恒指对比的 **from** 端；to 端写在 `label_budget_to`/`epoch_budget_to`。
  `lb` 无解时写空（与水平表一致）。
* 两条轴：`axis=epoch`（固定 `(pair, family, label_budget)`，比两个轮数预算）、
  `axis=label`（固定 `(pair, family, epoch_budget)`，比两个标注预算）。两条轴的取值都取自
  `dataset` 名（`_cells.budget_of`），桶为 `{10,20,30,40,50,100}`。
* `is_endpoint=True` ⇒ 该组内**最早 → 最晚**那一条（`A9_全域预算轴扫描.md` 与 §4.2 用的就是这一层）。
* 纳入条件：**共享种子数 `n ≥ 3`**；`_pick`/`outcome` 过滤沿用 `_cells.py` 原样。

## 2. γ 表（`scipy.stats.t.ppf` 复算，本表只用到三个 n）

| n | 3 | 5 | 10 |
|---|---|---|---|
| **γ(n)** | **3.096510** | **1.662476** | **0.994714** |

参考值 γ(3)=3.0965、γ(10)=0.9947 —— 逐位吻合（|Δ|<5e-5）。完整抽查：γ(8)=1.1528、γ(9)=1.0650、
γ(11)=0.9369、γ(13)=0.8463、γ(20)=0.6605，与稿内 Appendix P.1 表一致。

## 3. ★ 阳性对照（硬闸；任一不吻合则本表不生成）

| 对照 | 格 | n | sd | **重算 MDE** | 稿内印值 | 偏差 |
|---|---|---|---|---|---|---|
| **PC0**（口径算术） | γ(10)×0.3080 | 10 | 0.3080（给定） | **0.306372** | **0.3064** | 2.8e-05 |
| **PC1**（§4.2 第二行） | `shwd2sf→sfchd` / `b2` / lb=20 / **30→200** | 10 | 0.307997 | **0.306369** | **0.3064** | 3.1e-05 |
| **PC2**（§4.2 同域界） | `dota15→dota15` / `g3` / lb=20 / **100→200** | 5 | 0.137949 | **0.229337** | **0.2293** | 3.7e-05 |

三条**全部在 ±0.0005 内**。附带一致性（与 `A9` 印值对撞）：PC1 `mean_diff=−0.018`、`t=−0.185`
（A9 写 −0.018 / −0.18）；PC2 `mean_diff=−0.066`、`t=−1.070`（A9 写 −0.066 / −1.07）。

**另做了一次全域对撞**：本表 `column=test_map50_95` 且 `is_endpoint=True` 的 **61 行**（轮数轴 45 + 标签轴 16）
与 `analysis/A9_全域预算轴扫描.md` 的两张表**逐行**比对 `n`、`mean_diff`（±5e-4）、`t`（±6e-3）
与逐种子更低数 `n_lower` —— **61/61 全中，0 处不符**。这 61 行就是审稿意见里点名的
“新发一张 **61 行**差值表”的那个对象。

## 4. 覆盖范围与行数

| 分组 | 行数 |
|---|---|
| `test_map50_95` · 轮数轴 | 62（其中 `is_endpoint` **45**） |
| `test_map50_95` · 标签轴 | 137（其中 `is_endpoint` **16**） |
| **`test_map50_95` 小计** | **199**（endpoint **61** = 45+16） |
| `best_map50_95` · 轮数轴 | 66（endpoint 49） |
| `best_map50_95` · 标签轴 | 137（endpoint 16） |
| **`best_map50_95` 小计** | **203**（endpoint 65） |
| **合计** | **402** |

* 本表**同时给出 val-best 列**（`best_map50_95`）。这正是 §4.3 声明所用而
  `theory_B_MDE_by_cell.csv` 的 147 行**从未覆盖**的那一列（见 §6）。
* `n` 分布：`test` 轮数轴 {3:31, 5:9, 10:22}、标签轴 {3:97, 10:40}；
  61 条 endpoint 上 {3:41, 5:4, 10:16}。
* 本表**含全部预算对**（不只在 endpoint），因为 §4.1 引用的 `30→50 / 50→100 / 100→200`
  是**相邻步**而非端点；只要 `is_endpoint=False` 即可把它们与 `A9` 的 endpoint 层分开。
* **无法复算的格：0 个。** 409 个 `G` 槽里凡两端各自 `n ≥ 3` 且共享种子 `n ≥ 3` 的组合都算出来了；
  被排除的只有两类，都不构成“算不出”：(i) 该 `(pair, family, 预算)` 组只有一个轮数预算（或
  只有一个标注预算）⇒ 无对比可配；(ii) 共享种子 < 3（`n=2` 或 1）。

## 5. `resolvable` 分布

| 集合 | 行数 | `True` | `False` | `False` 占比 |
|---|---|---|---|---|
| `test_map50_95` 全部差值 | 199 | **52** | **147** | 73.9% |
| ↳ 轮数轴 | 62 | 19 | 43 | 69.4% |
| ↳ 标签轴 | 137 | 33 | **104** | 75.9% |
| `test_map50_95` **endpoint**（=A9 的 61） | 61 | **22** | **39** | 63.9% |
| ↳ 轮数轴 endpoint | 45 | 15 | 30 | 66.7% |
| ↳ 标签轴 endpoint | 16 | 7 | 9 | 56.3% |
| `best_map50_95` 全部差值 | 203 | 59 | 144 | 70.9% |
| ↳ endpoint | 65 | 25 | 40 | 61.5% |

* 中位 `|mean_diff| / mde_diff`：`test` **0.4911**、`best` **0.4733** ⇒ **过半差值落在自己的 MDE 之内**。
* ⚠ 与水平量表的 `43/147 = 29.2%` 不可直接相减：两个对象（单格水平 vs 两预算对比）与两个分母都不同。
  可比的只有“同一档案、同一 γ 判据”这层。

## 6. 与水平量表 `theory_B_MDE_by_cell.csv` 的重叠 / 差异

* **水平表仍是 147 行、sha256 未变**（本件只读）。
* 我另把 147 行**从底座逐位重算**了一遍：`n` 全等、`mean_diff` 与水平表 `delta` 偏差 < 5e-4、
  `sd_diff` 与 `sd` 偏差 < 1e-6 ⇒ **147/147 可复现**。
* ★ **口径上的一处关键澄清**：把“差值量”理解成**单格自己的** `(lr005−base)` 逐种子配对差
  （题面字面写法）时，`sd_diff` 与水平表的 `sd`、`mde_diff` 与水平表的 `mde` **是同一个量**，
  那份表会与 `theory_B_MDE_by_cell.csv` 逐位重复（`resolvable` = 104 True / 43 False）。
  真正**不在**已放行表里、而 §4 全部结论所依赖的，是**两个预算之间的对比**（差值之差），
  这才是本表的内容。两处都做了实测，故此处不是措辞之争。
* **参与度**（按 `test_map50_95`）：

| 量 | 值 |
|---|---|
| 水平表格数（有 `n≥3`） | **147** |
| 在差值表里**作为 from 端**出现过的水平格 | **83** |
| 在差值表里**作为任一端**（from 或 to）出现过的水平格 | **106** |
| **只在水平表、不在任何差值行**里的格 | **41** |
| 只在差值表、不在水平表里的格 | **0**（from 端 0） |

  那 41 格是各 `(pair, family, 预算)` 组里**唯一的轮数预算**（如 `visdrone→dota15/t1c/lb20` 只有
  100 ep、`visdrone→dota15/mech/lb20` 只有 200 ep）⇒ 它们只能进水平表，配不出组内对比。
* **那 41 格的具名清单**（`pair`/`family`/`label_budget`/`epoch_budget`，`label_budget` 为“无预算”
  = `lb=None` 的 `r10`/`g*` 等族）：

  `aitod→aitod20`/`r10`/无预算/30ep · `aitod→dota15`/`a2d15`/20/100ep · `aitod→visdrone`/`aitod`/20/100ep · `aitod→visdrone`/`mech`/20/200ep
  · `aitod→visdrone`/`r10`/20/100ep · `aitod→visdrone`/`t1b`/20/100ep · `chv→gdut_hwd`/`cg`/无预算/30ep · `dota15→aitod`/`t1a`/20/100ep
  · `dota15→aitod20`/`d15`/无预算/100ep · `dota15→aitod20`/`r10`/无预算/100ep · `dota15→aitod20`/`r15b`/无预算/100ep · `dota15→dota15`/`dota15`/20/100ep
  · `dota15→dota15`/`r10`/20/30ep · `dota15→g`/`g1p`/无预算/100ep · `dota15→g2_val_large`/`g2`/无预算/100ep · `dota15→g2_val_small`/`g2`/无预算/100ep
  · `dota→dota`/`r10`/20/30ep · `dota→dota15`/`t1d`/20/100ep · `fsin→firesmoke20`/`r10`/无预算/30ep · `mafa→mende`/`mende`/20/100ep
  · `mafa→mende20`/`r10`/无预算/100ep · `mask→mask20`/`r10`/无预算/30ep · `mask→mende`/`t2`/20/100ep · `mask→mende20`/`r10`/无预算/100ep
  · `mendein→mende20`/`g4`/无预算/100ep · `mendein→mende20`/`r10`/无预算/30ep · `shwd2sf→gdut_hwd`/`sgh`/无预算/30ep · `shwd2sf→roboflow_hardhat`/`srh`/无预算/30ep
  · `shwd2sf→sfchd20`/`r10`/无预算/100ep · `smoke→sfchd`/`smoke2sf`/20/100ep · `smoke→sfchd20`/`r10`/无预算/100ep · `visdrone→data`/`vd15`/无预算/30ep
  · `visdrone→dota15`/`mech`/20/200ep · `visdrone→dota15`/`r10`/20/100ep · `visdrone→dota15`/`t1c`/20/100ep · `visdrone→dota15`/`vis`/20/100ep
  · `visdrone→vhr10`/`vvhr`/无预算/30ep · `visdrone→visdrone`/`r10`/20/30ep · `y11_shwd→sfchd`/`b2`/20/100ep · `yolo11n→dota15`/`r15`/20/100ep
  · `yolo12n→dota15`/`r15`/20/100ep  

* `best_map50_95` 列上 `n≥3` 的格共 **152** 个（比 test 列多 5 个）。

## 7. 列说明与并表方法

必需列（题面点名，顺序照抄）：`pair, family, label_budget, epoch_budget, column, n, mean_diff,
sd_diff, mde_diff, gamma_n, t_stat, resolvable`；
附加列：`axis, label_budget_to, epoch_budget_to, is_endpoint, n_from, n_to, n_lower,
ratio_abs_mean_over_mde, level_mde_from, level_mde_to`。

* `n` = **共享种子数**（对比实际用到的配对数）；`n_from`/`n_to` = 两端各自的配对数（均 ≥3）。
* `n_lower` = `D_s < 0` 的种子数（对应 `A9` 的“更低”列）。
* `level_mde_from` / `level_mde_to` = 两端格**自身**的水平量 MDE（同一 `column` 上按本节公式算）。
  有了这两列，§9“哪些端点**水平**落在受影响带内”这类改法不必再回查另一张表。
* **并表**：`(pair, family, label_budget, epoch_budget)` + `column='test_map50_95'` 即水平表主键，
  可直接 `merge` 逐行并列。
* 数值格式 `%.15g`；`resolvable`/`is_endpoint` 写 `True`/`False`（与水平表一致）；
  UTF-8（无 BOM）+ **CRLF**，与 `theory_B_MDE_by_cell.csv` 相同。

## 8. 口径边界：**不在本表内**的差值量（点名登记）

1. **§4.1/§10 的 `aitod→visdrone` 100→200 变化是跨族对比**：100 ep 落在族 `t1b`、200 ep 落在族 `mech`
   （`(pair, family)` 组内配不出来）。按本表的组内口径它**不进本表**。我单独复算供引用：
   `n=10`、`mean_diff = −0.2230`、`sd_diff = 0.137683`、**`mde_diff = 0.136955`**、`t = −5.122`、
   `n_lower = 9/10`、`|mean|/MDE = 1.63×`（与 §10 印的 *−0.223 pp*、*MDE 0.137*、*1.6×* 逐位吻合）。
   ⚠ 未做全档案的跨族扫描 —— 那会与 `_cells.py` “不许静默合并族”的纪律相抵；
   若稿内要引用它，建议**单点具名**，不要给它一个“全档案跨族分母”。
2. **结构对比**（`lr005` vs `base` 之外的臂、架构/损失轴）**不在本表**：本表的臂差恒为
   `lr005 − base`，与水平表、与 `A9` 完全一致。`analysis/A21`、`A23` 的架构/损失对比另有一套键。
3. 本表**只随 `outcome` 过滤**（`_cells.ok_outcome`），不额外剔格；水平表同。
4. ★ **§4.3 的缺口不是差值量，是 val-best 列的“水平量”，故不在本表**。审稿意见
   （*“147 行审计只覆盖 `test_map50_95` 一列，而 §4.3 的声明列是 val-best ⇒ 那个 −1.4275 pp
   从未进入任何功效审计”*）指向的是**同一格的另一列**，而本表是预算对比，覆盖不到它。
   我把这一格两列都复算了（`mask→mende` / 族 `t2` / lb=20 / 100 ep，`n=10`）：

| `column` | mean (pp) | sd (pp) | **MDE (pp)** | `resolvable` | \|mean\|/MDE |
|---|---|---|---|---|---|
| `test_map50_95`（已放行 147 行里的那一行） | −1.1560 | 1.2054 | 1.1990 | **False** | 0.96 |
| **`best_map50_95`（§4.3 的声明列）** | **−1.4275** | 0.6744 | **0.6708** | **True** | **2.13** |

   ⇒ 该损伤在**它自己的声明列上以 2.13× 过闸**，而不是像 test 列那一行显示的那样落在带内。
   顺带给出 val-best 列的**水平量普查**（同一 γ 判据，口径与 147 行表完全相同）：
   **152** 个格（`n≥3`），`resolvable` = **110 True / 42 False**（test 列为 147 格 / 104 True / 43 False）。
   ⇒ 若要把审计扩到 val-best 列，只差一张 152 行的水平量副本，不需要任何新训练。
   ⚠ 本表**没有**把它写成行，因为它是水平量、不是差值量，混进本表会破坏“同列可并列”的性质。

## 9. 复算路径

```bat
python -c "import sys;sys.path.insert(0,r'D:\deepseek\analysis\work\analysis_M3\scripts');import _cells as C;rows,G=C.load();print(len(rows),len(G))"
```

从 `load()` 出发：`cell_of(pair,fam,lb,ep,key)` → 逐种子 `d_s` → 交集种子 → `D_s = d_s(to) − d_s(from)`
→ `mean_diff/sd_diff/γ(n)·sd_diff`。`γ(n)` 用 `scipy.stats.t.ppf(1−α/2,n−1)+t.ppf(1−β,n−1)` 除以 `√n`。
本件生成时**先过 §3 的三条阳性对照与 §3 的 61 行 `A9` 全表对撞，再落盘**（任一不过则不写文件）。
