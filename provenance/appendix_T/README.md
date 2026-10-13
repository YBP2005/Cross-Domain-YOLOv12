# Appendix T 的原始数据（2026-10-13 放行）

**为什么在这里**：正文 Appendix T 报了三组**评测类**读数（报告上限 `max_det`、面积分层、
逐类分层）。这些数**不是从已放行的底座重算的**，而是**新做的评测**，所以必须把逐 run 结果
一并放行，否则 T 只能靠作者的表格成立。第七轮评审据此扣了分（"附录 T 的原始逐点值未放行"）。

**口径**：全部只用**已训好的** `best.pt`（**无重训**），Ultralytics **8.4.120** / torch 2.4.0+cu121，
`imgsz 640`、`batch 16`、`max_det 300`（除 T1 明确扫的档位）、`split = test`（即语料自带的 held-out 目录）。
跑在两台 4090 上。

## 文件

| 文件 | 行数 | 列 | 说明 |
|---|---:|---|---|
| `T1_maxdet_levels.csv` | 456 | `tag,data,split,max_det,mAP50,mAP50_95,P,R` | T.1：`max_det ∈ {100,300,1000}` 的 Ultralytics val 读数。`tag` 形如 `<cell>_<arm>_<run>` |
| `T2_area_AP.csv` | 240 | `tag,split,max_det,area,AP` | T.2：面积分层 AP，`area ∈ {all,S,M,L}`，阈值按 COCO 约定（S<32²、32²≤M<96²、L≥96²），101 点插值、IoU 0.50:0.05:0.95 |
| `T3_perclass_AP.csv` | 640 | `tag,split,max_det,class_id,class_name,AP50_95` | T.3：逐类 AP，**直接取自评测器的逐类输出**（未自行重算） |

**`tag` 命名**：`<cell>_<arm>_<run>`，其中 `cell ∈ {t1c, mech, d15d15, d15ai, aitodvis}`、
`arm ∈ {base, lr005}`、`run` 是训练时的 run 目录名（含 `_s<NN>n` 种子后缀）。

## 三条必须在读表时知道的限制

1. **`mech` 的 `test` 列不是独立留出读数**：其数据 yaml 里 `val:` 与 `test:` 指向**同一目录**，
   所以同一 run 的 `val` 与 `test` 两行**逐位相同**。正文已就此声明（§Data 前的列口径段与 Appendix R）。
2. **T2 的 AP 是作者自实现的**：评测环境**没有 `pycocotools`**，所以 `T2_area_AP.csv` 的 AP 由
   纯 numpy 按 COCO 定义算得。它**不是**对 Ultralytics 指标的独立复现，两者口径不同
   （例：同格 `all` 本实现 0.1432 vs Ultralytics 0.1156），**不可互相印证**。
3. **T3 的 16 个逐类 t 值未做族校正**，属描述性分解。

## 复跑

驱动与 worker 在 A 机 `/workspace/`（`p1_g0_maxdet_headline.py`、`p1_g2_area_ap.py`、
`p1_g3_perclass_ap.py`、`p1_g4_eval_misc.py`）。**A 机已关机**，故这里是**产物的冻结副本**，
不是可即刻重跑的流水线；要重跑需把权重与数据重新挂上。
