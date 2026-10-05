# A1b run → backbone 映射（2026-09-30，闭合 A1 唯一登记缺口）

> A1 §4 登记：底座的 `model` 列只记**预训练权重**、不记 backbone，
> 架构轴只能从 run 名 token 推断 ⇒ 只能给下界。
> 本件把链子走通：递归读 `args.yaml: model`，直到落在 `yoloXXn.pt`（COCO 起点）。

## 1. 方法与覆盖

**两个独立证据源**：

1. **日志模型签名**（主源）：每个训练日志里同时有 `save_dir: /workspace/runs/<run>`
   与 ultralytics 打印的 `YOLOv12n summary (fused): …` ⇒ **一次给到 run 与 backbone 的绑定**。
2. **`args.yaml` 链**（兜底）：递归读 `model:` 直到落在 `yoloXXn.pt`。

| 量 | 值 |
|---|---|
| 扫过的日志 | 711 |
| 日志给到 (run, backbone) 绑定 | **228** |
| 本地 `args.yaml` | 3042 个目录 |
| 底座 run | 2362 |
| **定到具体 backbone** | **2331（99%）** |
| ↳ 其中来自**日志签名** | 270 |
| ↳ 其中来自 **args 链** | 2061 |
| 链断（上游权重没有本地 args.yaml、也无日志） | 0 |
| 只到"未知权重" | 31 |

## 2. backbone 分布

| backbone | run 数 | 说明 |
|---|---|---|
| `yolo12n` | 2241 | COCO 起点，链完整 |
| `yolo11n` | 76 | COCO 起点，链完整 |
| `unknown(epoch80)` | 20 | 链未走通，见 §4 |
| `yolo26n` | 14 | COCO 起点，链完整 |
| `unknown(shapeiou_fusion_best)` | 6 | 链未走通，见 §4 |
| `unknown(best)` | 5 | 链未走通，见 §4 |

## 3. 与 run 名 token 的交叉核对（**这是映射的独立检验**）

凡是 run 名里带 `y11`/`y26` 的、且链子走通的，看两者是否一致：

| 结果 | 数 |
|---|---|
| ✅ 一致 | **88** |
| ❌ 不一致 | 6 |

不一致明细（**这些就是"从 run 名推断"会推断错的 run**）：

| run | 名字暗示 | 链子实测 |
|---|---|---|
| `r15b_y11_aitod_base100_s45n` | `yolo11n` | **`yolo12n`** |
| `r15b_y11_aitod_base100_s46n` | `yolo11n` | **`yolo12n`** |
| `r15b_y11_aitod_base100_s47n` | `yolo11n` | **`yolo12n`** |
| `r15b_y11_aitod_lr005_100ep_s45n` | `yolo11n` | **`yolo12n`** |
| `r15b_y11_aitod_lr005_100ep_s46n` | `yolo11n` | **`yolo12n`** |
| `r15b_y11_aitod_lr005_100ep_s47n` | `yolo11n` | **`yolo12n`** |

## 4. 链子样例（可逐条复核）

* **`yolo12n`** ← ``a0_100_10p_100ep_base_s42n`.`model` = `shwd_pretrain_100ep.pt` → `shwd_pretrain_100ep`.`model` = `yolo12n.pt``
* **`unknown(best)`** ← ``r10_iv_src1_lr005_100ep_3way_s42n`.`model` = `best.pt``
* **`yolo11n`** ← ``r15_arch_y11_vistod15_base100_s42n`.`model` = `yolo11n.pt``
* **`yolo26n`** ← ``_PARTIAL_y26_shwd_pretrain_054939`.`model` = `yolo26n.pt``
* **`unknown(shapeiou_fusion_best)`** ← ``amod_ADown_30ep_s42n`.`model` = `shapeiou_fusion_best.pt``
* **`unknown(epoch80)`** ← ``b2r_shwd2sf_100_ctl81_s42`.`model` = `epoch80.pt``

## 5. 未走通的链（**缺口，逐条列出**）

| 未知/断链的标识 | run 数 | 需要的上游 |
|---|---|---|
| `unknown(epoch80)` | 20 | 该上游权重的 `args.yaml` 不在本次取件内 |
| `unknown(shapeiou_fusion_best)` | 6 | 该上游权重的 `args.yaml` 不在本次取件内 |
| `unknown(best)` | 5 | 该上游权重的 `args.yaml` 不在本次取件内 |

⇒ 这些 run **不能**进入架构轴的结论；它们恰是 A1 §4 原来只能给"下界"的那部分。

## 6. 架构轴（用映射重算，**不再是下界**）

| backbone | run 数 | 目标数据集数 | epochs 分布 |
|---|---|---|---|
| **`yolo12n`** | 2241 | 62 | 100(1188)、30(707)、200(169)、50(110)、400(30) |
| **`yolo11n`** | 76 | 3 | 100(53)、30(21)、20(2) |
| **`yolo26n`** | 14 | 2 | 30(8)、100(6) |

> ⇒ 架构轴现在有**可核的键**：`run_backbone_map.csv`。
> 论文若报"架构对照"（§4.4），应引用该表的 `backbone` 列，而不是 run 名 token。

