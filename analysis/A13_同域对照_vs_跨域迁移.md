# A13 同域对照 vs 跨域迁移

> 数据 `base/run_table_canonical.csv`；口径见脚本头。增益 = 逐种子 `(lr005−base)`，pp，`test_map50_95`。

## 一、分类（逐条列出，可复核）

| 配对 | 族 | 源 stem | 目标 stem | 归一后 | 判定 |
|---|---|---|---|---|---|
| `aitod→aitod` | `aitod` | `aitod`(`aitod`) | `aitod`(`aitod`) | 相同 | **同域** |
| `aitod→aitod20` | `r10` | `aitod`(`aitod`) | `aitod20`(`aitod`) | 相同 | **同域** |
| `aitod→dota15` | `a2d15` | `aitod`(`aitod`) | `dota15`(`dota`) | 不同 | **跨域** |
| `aitod→visdrone` | `aitod` | `aitod`(`aitod`) | `visdrone`(`visdrone`) | 不同 | **跨域** |
| `aitod→visdrone` | `mech` | `aitod`(`aitod`) | `visdrone`(`visdrone`) | 不同 | **跨域** |
| `aitod→visdrone` | `r10` | `aitod`(`aitod`) | `visdrone`(`visdrone`) | 不同 | **跨域** |
| `aitod→visdrone` | `t1b` | `aitod`(`aitod`) | `visdrone`(`visdrone`) | 不同 | **跨域** |
| `best→sfchd20_3way_a` | `r10` | `best`(`best`) | `sfchd20_3way_a`(`sfchd20_3way_a`) | 不同 | **跨域** |
| `chv→gdut_hwd` | `cg` | `chv`(`chv`) | `gdut_hwd`(`gdut_hwd`) | 不同 | **跨域** |
| `chv→gdut_hwd` | `s2hv` | `chv`(`chv`) | `gdut_hwd`(`gdut_hwd`) | 不同 | **跨域** |
| `dota15→aitod` | `t1a` | `dota15`(`dota`) | `aitod`(`aitod`) | 不同 | **跨域** |
| `dota15→aitod20` | `d15` | `dota15`(`dota`) | `aitod20`(`aitod`) | 不同 | **跨域** |
| `dota15→aitod20` | `r10` | `dota15`(`dota`) | `aitod20`(`aitod`) | 不同 | **跨域** |
| `dota15→aitod20` | `r15b` | `dota15`(`dota`) | `aitod20`(`aitod`) | 不同 | **跨域** |
| `dota15→dota15` | `dota15` | `dota15`(`dota`) | `dota15`(`dota`) | 相同 | **同域** |
| `dota15→dota15` | `g3` | `dota15`(`dota`) | `dota15`(`dota`) | 相同 | **同域** |
| `dota15→dota15` | `g3clean` | `dota15`(`dota`) | `dota15`(`dota`) | 相同 | **同域** |
| `dota15→dota15` | `g3cleanb` | `dota15`(`dota`) | `dota15`(`dota`) | 相同 | **同域** |
| `dota15→dota15` | `g3ext` | `dota15`(`dota`) | `dota15`(`dota`) | 相同 | **同域** |
| `dota15→dota15` | `r10` | `dota15`(`dota`) | `dota15`(`dota`) | 相同 | **同域** |
| `dota15→g` | `g1p` | `dota15`(`dota`) | `g`(`g`) | 不同 | **跨域** |
| `dota15→g2_val_large` | `g2` | `dota15`(`dota`) | `g2_val_large`(`g2_val_large`) | 不同 | **跨域** |
| `dota15→g2_val_small` | `g2` | `dota15`(`dota`) | `g2_val_small`(`g2_val_small`) | 不同 | **跨域** |
| `dota→data` | `dd15` | `dota`(`dota`) | `data`(`data`) | 不同 | **跨域** |
| `dota→dota` | `dota` | `dota`(`dota`) | `dota`(`dota`) | 相同 | **同域** |
| `dota→dota` | `r10` | `dota`(`dota`) | `dota`(`dota`) | 相同 | **同域** |
| `dota→dota15` | `t1d` | `dota`(`dota`) | `dota15`(`dota`) | 相同 | **同域** |
| `fsin→firesmoke` | `fsin` | `fsin`(`fsin`) | `firesmoke`(`firesmoke`) | 不同 | **跨域** |
| `fsin→firesmoke20` | `r10` | `fsin`(`fsin`) | `firesmoke20`(`firesmoke`) | 不同 | **跨域** |
| `fsin→smoke_keremberke` | `s2sm` | `fsin`(`fsin`) | `smoke_keremberke`(`smoke_keremberke`) | 不同 | **跨域** |
| `mafa→mask` | `base100` | `mafa`(`mafa`) | `mask`(`mask`) | 不同 | **跨域** |
| `mafa→mask` | `base30` | `mafa`(`mafa`) | `mask`(`mask`) | 不同 | **跨域** |
| `mafa→mask` | `lr005` | `mafa`(`mafa`) | `mask`(`mask`) | 不同 | **跨域** |
| `mafa→mask_clean` | `s2mk` | `mafa`(`mafa`) | `mask_clean`(`mask`) | 不同 | **跨域** |
| `mafa→mende` | `mende` | `mafa`(`mafa`) | `mende`(`mende`) | 不同 | **跨域** |
| `mafa→mende20` | `r10` | `mafa`(`mafa`) | `mende20`(`mende`) | 不同 | **跨域** |
| `mask→mask` | `mask` | `mask`(`mask`) | `mask`(`mask`) | 相同 | **同域** |
| `mask→mask20` | `r10` | `mask`(`mask`) | `mask20`(`mask`) | 相同 | **同域** |
| `mask→mende` | `t2` | `mask`(`mask`) | `mende`(`mende`) | 不同 | **跨域** |
| `mask→mende20` | `r10` | `mask`(`mask`) | `mende20`(`mende`) | 不同 | **跨域** |
| `mendein→mende` | `mendein` | `mendein`(`mendein`) | `mende`(`mende`) | 不同 | **跨域** |
| `mendein→mende20` | `g4` | `mendein`(`mendein`) | `mende20`(`mende`) | 不同 | **跨域** |
| `mendein→mende20` | `r10` | `mendein`(`mendein`) | `mende20`(`mende`) | 不同 | **跨域** |
| `pcb→neu_det` | `pn` | `pcb`(`pc`) | `neu_det`(`neu_det`) | 不同 | **跨域** |
| `pcb→neu_det` | `s2df` | `pcb`(`pc`) | `neu_det`(`neu_det`) | 不同 | **跨域** |
| `shapeiou_fusion_best→sfchd` | `amod` | `shapeiou_fusion_best`(`shapeiou_fusion_best`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `shwd2sf→gdut_hwd` | `sgh` | `shwd2sf`(`shwd2sf`) | `gdut_hwd`(`gdut_hwd`) | 不同 | **跨域** |
| `shwd2sf→roboflow_hardhat` | `srh` | `shwd2sf`(`shwd2sf`) | `roboflow_hardhat`(`roboflow_hardhat`) | 不同 | **跨域** |
| `shwd2sf→sfchd` | `a0` | `shwd2sf`(`shwd2sf`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `shwd2sf→sfchd` | `a5` | `shwd2sf`(`shwd2sf`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `shwd2sf→sfchd` | `a5a` | `shwd2sf`(`shwd2sf`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `shwd2sf→sfchd` | `b2` | `shwd2sf`(`shwd2sf`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `shwd2sf→sfchd` | `cal` | `shwd2sf`(`shwd2sf`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `shwd2sf→sfchd` | `calA` | `shwd2sf`(`shwd2sf`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `shwd2sf→sfchd` | `calB` | `shwd2sf`(`shwd2sf`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `shwd2sf→sfchd` | `la` | `shwd2sf`(`shwd2sf`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `shwd2sf→sfchd` | `oldenv` | `shwd2sf`(`shwd2sf`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `shwd2sf→sfchd` | `shwd2sf` | `shwd2sf`(`shwd2sf`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `shwd2sf→sfchd20` | `r10` | `shwd2sf`(`shwd2sf`) | `sfchd20`(`sfchd`) | 不同 | **跨域** |
| `shwd→sfchd` | `a0` | `shwd`(`shwd`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `smoke→firesmoke` | `smokefs` | `smoke`(`smoke`) | `firesmoke`(`firesmoke`) | 不同 | **跨域** |
| `smoke→sfchd` | `a5s` | `smoke`(`smoke`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `smoke→sfchd` | `b2` | `smoke`(`smoke`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `smoke→sfchd` | `calB2` | `smoke`(`smoke`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `smoke→sfchd` | `smoke2sf` | `smoke`(`smoke`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `smoke→sfchd20` | `r10` | `smoke`(`smoke`) | `sfchd20`(`sfchd`) | 不同 | **跨域** |
| `visdrone→data` | `vd15` | `visdrone`(`visdrone`) | `data`(`data`) | 不同 | **跨域** |
| `visdrone→dota15` | `dv` | `visdrone`(`visdrone`) | `dota15`(`dota`) | 不同 | **跨域** |
| `visdrone→dota15` | `mech` | `visdrone`(`visdrone`) | `dota15`(`dota`) | 不同 | **跨域** |
| `visdrone→dota15` | `oldenv` | `visdrone`(`visdrone`) | `dota15`(`dota`) | 不同 | **跨域** |
| `visdrone→dota15` | `r10` | `visdrone`(`visdrone`) | `dota15`(`dota`) | 不同 | **跨域** |
| `visdrone→dota15` | `s2ae` | `visdrone`(`visdrone`) | `dota15`(`dota`) | 不同 | **跨域** |
| `visdrone→dota15` | `t1c` | `visdrone`(`visdrone`) | `dota15`(`dota`) | 不同 | **跨域** |
| `visdrone→dota15` | `vis` | `visdrone`(`visdrone`) | `dota15`(`dota`) | 不同 | **跨域** |
| `visdrone→vhr10` | `vvhr` | `visdrone`(`visdrone`) | `vhr10`(`vhr`) | 不同 | **跨域** |
| `visdrone→visdrone` | `r10` | `visdrone`(`visdrone`) | `visdrone`(`visdrone`) | 相同 | **同域** |
| `visdrone→visdrone` | `visdrone` | `visdrone`(`visdrone`) | `visdrone`(`visdrone`) | 相同 | **同域** |
| `y11_shwd→sfchd` | `b2` | `y11_shwd`(`y11_shwd`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `y11_shwd→sfchd` | `calB2` | `y11_shwd`(`y11_shwd`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `y11_shwd→sfchd` | `y11` | `y11_shwd`(`y11_shwd`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `y26_shwd→sfchd` | `y26` | `y26_shwd`(`y26_shwd`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `yolo11n→dota15` | `r15` | `yolo11n`(`yolo11n`) | `dota15`(`dota`) | 不同 | **跨域** |
| `yolo12n→dota15` | `r15` | `yolo12n`(`yolo12n`) | `dota15`(`dota`) | 不同 | **跨域** |
| `yolo12n→sfchd` | `sfchd` | `yolo12n`(`yolo12n`) | `sfchd`(`sfchd`) | 不同 | **跨域** |
| `→` | `d15` | ``(``) | ``(``) | 相同 | **同域** |

全底座 **85** 个 (配对,族) 组，其中**同域 16 个**、跨域 69 个。

## 二、同域对照

| 配对 | 族 | 预算 | 轮数 | n | 增益(pp) | t |
|---|---|---|---|---|---|---|
| `aitod→aitod20` | `r10` | None | 30 | 10 | **-1.195** | -7.85 |
| `dota15→dota15` | `dota15` | 20 | 100 | 10 | **+1.113** | +40.37 |
| `dota15→dota15` | `g3` | 20 | 100 | 5 | **+1.034** | +17.61 |
| `dota15→dota15` | `g3` | 20 | 200 | 5 | **+0.968** | +10.79 |
| `dota15→dota15` | `g3clean` | 20 | 400 | 5 | **+0.650** | +4.23 |
| `dota15→dota15` | `g3clean` | 20 | 50 | 5 | **+0.572** | +2.96 |
| `dota15→dota15` | `g3clean` | 20 | 100 | 5 | **+1.034** | +17.61 |
| `dota15→dota15` | `g3clean` | 20 | 200 | 5 | **+0.968** | +10.79 |
| `dota15→dota15` | `g3cleanb` | 20 | 400 | 5 | **+0.748** | +7.50 |
| `dota15→dota15` | `g3cleanb` | 20 | 50 | 5 | **+0.476** | +2.96 |
| `dota15→dota15` | `g3ext` | 20 | 400 | 5 | **+0.748** | +7.50 |
| `dota15→dota15` | `g3ext` | 20 | 50 | 5 | **+0.476** | +2.96 |
| `dota15→dota15` | `r10` | 20 | 30 | 10 | **-0.031** | -0.17 |
| `dota→dota` | `r10` | 20 | 30 | 10 | **-0.850** | -4.38 |
| `dota→dota15` | `t1d` | 20 | 100 | 10 | **+0.727** | +18.85 |
| `mask→mask20` | `r10` | None | 30 | 10 | **-2.027** | -5.44 |
| `visdrone→visdrone` | `r10` | 20 | 30 | 10 | **-0.810** | -7.85 |

* 格数 **17**；增益均值 **+0.271 pp**（中位 +0.650）；\|t\|≥2 的格 **16/17**；**负向格 5/17（29%）**

## 三、跨域迁移

| 配对 | 族 | 预算 | 轮数 | n | 增益(pp) | t |
|---|---|---|---|---|---|---|
| `aitod→dota15` | `a2d15` | 20 | 100 | 10 | **+3.540** | +60.36 |
| `aitod→visdrone` | `aitod` | 20 | 100 | 3 | **+0.140** | +1.38 |
| `aitod→visdrone` | `mech` | 20 | 200 | 10 | **-0.055** | -1.23 |
| `aitod→visdrone` | `r10` | 20 | 100 | 10 | **+0.186** | +3.28 |
| `aitod→visdrone` | `t1b` | 20 | 100 | 10 | **+0.168** | +4.46 |
| `chv→gdut_hwd` | `cg` | None | 30 | 3 | **+0.737** | +21.17 |
| `chv→gdut_hwd` | `s2hv` | 10 | 100 | 3 | **-0.290** | -0.87 |
| `chv→gdut_hwd` | `s2hv` | 10 | 30 | 3 | **+2.630** | +9.03 |
| `chv→gdut_hwd` | `s2hv` | 20 | 100 | 3 | **-0.113** | -0.23 |
| `chv→gdut_hwd` | `s2hv` | 20 | 30 | 3 | **+2.220** | +24.77 |
| `chv→gdut_hwd` | `s2hv` | 30 | 100 | 3 | **-1.733** | -4.67 |
| `chv→gdut_hwd` | `s2hv` | 30 | 30 | 3 | **+1.360** | +4.55 |
| `chv→gdut_hwd` | `s2hv` | 40 | 100 | 3 | **-1.003** | -3.53 |
| `chv→gdut_hwd` | `s2hv` | 40 | 30 | 3 | **+0.590** | +1.06 |
| `chv→gdut_hwd` | `s2hv` | 50 | 100 | 3 | **-0.590** | -1.00 |
| `chv→gdut_hwd` | `s2hv` | 50 | 30 | 3 | **+0.410** | +0.77 |
| `dota15→aitod` | `t1a` | 20 | 100 | 10 | **+0.147** | +1.82 |
| `dota15→aitod20` | `d15` | None | 100 | 9 | **+0.278** | +3.62 |
| `dota15→aitod20` | `r10` | None | 100 | 10 | **+0.322** | +2.61 |
| `dota15→aitod20` | `r15b` | None | 100 | 3 | **+0.120** | +3.93 |
| `dota15→g` | `g1p` | None | 100 | 5 | **-4.438** | -7.98 |
| `dota15→g2_val_large` | `g2` | None | 100 | 5 | **+1.096** | +7.60 |
| `dota15→g2_val_small` | `g2` | None | 100 | 5 | **+0.982** | +5.42 |
| `dota→data` | `dd15` | None | 200 | 3 | **+1.743** | +12.51 |
| `dota→data` | `dd15` | None | 30 | 3 | **+2.137** | +13.60 |
| `fsin→firesmoke20` | `r10` | None | 30 | 10 | **-3.939** | -14.81 |
| `fsin→smoke_keremberke` | `s2sm` | 10 | 100 | 3 | **+2.607** | +40.82 |
| `fsin→smoke_keremberke` | `s2sm` | 10 | 30 | 3 | **+1.933** | +12.40 |
| `fsin→smoke_keremberke` | `s2sm` | 20 | 100 | 3 | **+2.620** | +65.50 |
| `fsin→smoke_keremberke` | `s2sm` | 20 | 30 | 3 | **+1.773** | +6.04 |
| `fsin→smoke_keremberke` | `s2sm` | 30 | 100 | 3 | **+2.703** | +11.02 |
| `fsin→smoke_keremberke` | `s2sm` | 30 | 30 | 3 | **+1.537** | +17.73 |
| `fsin→smoke_keremberke` | `s2sm` | 40 | 100 | 3 | **+2.130** | +14.69 |
| `fsin→smoke_keremberke` | `s2sm` | 40 | 30 | 3 | **+1.657** | +17.99 |
| `fsin→smoke_keremberke` | `s2sm` | 50 | 100 | 3 | **+2.007** | +13.46 |
| `fsin→smoke_keremberke` | `s2sm` | 50 | 30 | 3 | **+1.293** | +7.72 |
| `mafa→mask_clean` | `s2mk` | 10 | 100 | 3 | **-0.800** | -1.00 |
| `mafa→mask_clean` | `s2mk` | 10 | 30 | 3 | **-0.857** | -8.02 |
| `mafa→mask_clean` | `s2mk` | 20 | 100 | 3 | **-1.800** | -2.02 |
| `mafa→mask_clean` | `s2mk` | 20 | 30 | 3 | **-2.223** | -4.30 |
| `mafa→mask_clean` | `s2mk` | 30 | 100 | 3 | **-1.387** | -5.36 |
| `mafa→mask_clean` | `s2mk` | 30 | 30 | 3 | **-0.840** | -1.07 |
| `mafa→mask_clean` | `s2mk` | 40 | 100 | 3 | **-0.287** | -1.28 |
| `mafa→mask_clean` | `s2mk` | 40 | 30 | 3 | **-0.793** | -3.48 |
| `mafa→mask_clean` | `s2mk` | 50 | 100 | 3 | **-0.437** | -0.57 |
| `mafa→mask_clean` | `s2mk` | 50 | 30 | 3 | **-0.850** | -2.83 |
| `mafa→mende` | `mende` | 20 | 100 | 10 | **-0.792** | -3.41 |
| `mafa→mende20` | `r10` | None | 100 | 10 | **-1.244** | -3.18 |
| `mask→mende` | `t2` | 20 | 100 | 10 | **-1.156** | -3.03 |
| `mask→mende20` | `r10` | None | 100 | 13 | **-1.170** | -3.39 |
| `mendein→mende` | `mendein` | 20 | 100 | 10 | **-1.768** | -4.74 |
| `mendein→mende` | `mendein` | 20 | 30 | 3 | **-1.387** | -3.17 |
| `mendein→mende20` | `g4` | None | 100 | 13 | **-2.375** | -7.57 |
| `mendein→mende20` | `r10` | None | 30 | 10 | **-2.225** | -3.96 |
| `pcb→neu_det` | `pn` | None | 200 | 3 | **+0.543** | +0.70 |
| `pcb→neu_det` | `pn` | None | 30 | 3 | **+1.687** | +5.00 |
| `pcb→neu_det` | `s2df` | 10 | 100 | 10 | **+2.381** | +4.31 |
| `pcb→neu_det` | `s2df` | 10 | 30 | 10 | **+12.139** | +9.13 |
| `pcb→neu_det` | `s2df` | 20 | 100 | 10 | **+1.060** | +4.07 |
| `pcb→neu_det` | `s2df` | 20 | 30 | 10 | **+8.229** | +11.50 |
| `pcb→neu_det` | `s2df` | 30 | 100 | 10 | **-0.042** | -0.11 |
| `pcb→neu_det` | `s2df` | 30 | 30 | 10 | **+3.299** | +8.87 |
| `pcb→neu_det` | `s2df` | 40 | 100 | 10 | **-0.507** | -1.46 |
| `pcb→neu_det` | `s2df` | 40 | 30 | 10 | **+2.192** | +6.42 |
| `pcb→neu_det` | `s2df` | 50 | 100 | 10 | **-0.010** | -0.03 |
| `pcb→neu_det` | `s2df` | 50 | 30 | 10 | **+1.425** | +5.05 |
| `shwd2sf→gdut_hwd` | `sgh` | None | 30 | 3 | **-0.083** | -0.54 |
| `shwd2sf→roboflow_hardhat` | `srh` | None | 30 | 3 | **+0.440** | +1.52 |
| `shwd2sf→sfchd` | `a0` | 10 | 30 | 3 | **+0.630** | +16.64 |
| `shwd2sf→sfchd` | `a0` | 20 | 100 | 3 | **+0.703** | +5.26 |
| `shwd2sf→sfchd` | `a0` | 20 | 30 | 3 | **+1.023** | +13.31 |
| `shwd2sf→sfchd` | `a0` | 30 | 30 | 3 | **+1.127** | +7.87 |
| `shwd2sf→sfchd` | `a0` | 40 | 100 | 3 | **+1.097** | +9.74 |
| `shwd2sf→sfchd` | `a0` | 40 | 30 | 3 | **+1.000** | +2.98 |
| `shwd2sf→sfchd` | `a0` | 50 | 30 | 3 | **+1.183** | +30.78 |
| `shwd2sf→sfchd` | `b2` | 20 | 100 | 10 | **+0.694** | +11.66 |
| `shwd2sf→sfchd` | `b2` | 20 | 200 | 10 | **+0.794** | +9.58 |
| `shwd2sf→sfchd` | `b2` | 20 | 30 | 10 | **+0.812** | +8.00 |
| `shwd2sf→sfchd` | `b2` | 20 | 50 | 10 | **+0.728** | +7.67 |
| `shwd2sf→sfchd` | `la` | 10 | 100 | 3 | **+0.270** | +1.12 |
| `shwd2sf→sfchd` | `la` | 50 | 100 | 3 | **+1.023** | +9.39 |
| `shwd2sf→sfchd` | `la` | 30 | 100 | 3 | **+1.003** | +10.31 |
| `shwd2sf→sfchd` | `shwd2sf` | 20 | 100 | 10 | **+0.584** | +10.11 |
| `shwd2sf→sfchd` | `shwd2sf` | 20 | 30 | 3 | **+0.920** | +6.13 |
| `shwd2sf→sfchd` | `shwd2sf` | 20 | 50 | 3 | **+0.550** | +4.58 |
| `shwd2sf→sfchd20` | `r10` | None | 100 | 13 | **+0.628** | +4.65 |
| `shwd→sfchd` | `a0` | 10 | 100 | 3 | **+0.067** | +0.45 |
| `shwd→sfchd` | `a0` | 10 | 30 | 3 | **+0.267** | +3.72 |
| `shwd→sfchd` | `a0` | 20 | 100 | 3 | **+0.397** | +7.57 |
| `shwd→sfchd` | `a0` | 20 | 30 | 3 | **+0.780** | +10.39 |
| `shwd→sfchd` | `a0` | 30 | 100 | 3 | **+0.673** | +7.20 |
| `shwd→sfchd` | `a0` | 30 | 30 | 3 | **+0.960** | +12.72 |
| `shwd→sfchd` | `a0` | 40 | 100 | 3 | **+0.917** | +9.77 |
| `shwd→sfchd` | `a0` | 40 | 30 | 3 | **+0.683** | +7.87 |
| `shwd→sfchd` | `a0` | 50 | 100 | 3 | **+0.960** | +8.90 |
| `shwd→sfchd` | `a0` | 50 | 30 | 3 | **+0.633** | +28.97 |
| `smoke→firesmoke` | `smokefs` | 20 | 100 | 3 | **+0.173** | +1.60 |
| `smoke→firesmoke` | `smokefs` | 20 | 30 | 3 | **+0.387** | +1.90 |
| `smoke→sfchd` | `b2` | 20 | 200 | 10 | **+1.495** | +18.66 |
| `smoke→sfchd` | `b2` | 20 | 100 | 10 | **+1.666** | +26.18 |
| `smoke→sfchd` | `b2` | 20 | 30 | 10 | **+3.656** | +26.46 |
| `smoke→sfchd` | `b2` | 20 | 50 | 10 | **+2.674** | +31.45 |
| `smoke→sfchd` | `smoke2sf` | 20 | 100 | 10 | **+1.734** | +20.20 |
| `smoke→sfchd20` | `r10` | None | 100 | 11 | **+1.409** | +12.54 |
| `visdrone→data` | `vd15` | None | 30 | 3 | **+4.117** | +50.89 |
| `visdrone→dota15` | `dv` | 10 | 100 | 3 | **+1.920** | +10.99 |
| `visdrone→dota15` | `dv` | 50 | 100 | 3 | **+3.273** | +38.91 |
| `visdrone→dota15` | `dv` | 30 | 100 | 3 | **+2.413** | +16.37 |
| `visdrone→dota15` | `mech` | 20 | 200 | 10 | **+2.584** | +42.18 |
| `visdrone→dota15` | `r10` | 20 | 100 | 10 | **+3.652** | +37.57 |
| `visdrone→dota15` | `s2ae` | 10 | 30 | 10 | **+1.995** | +23.60 |
| `visdrone→dota15` | `s2ae` | 20 | 100 | 10 | **+2.386** | +36.85 |
| `visdrone→dota15` | `s2ae` | 20 | 30 | 10 | **+3.418** | +32.66 |
| `visdrone→dota15` | `s2ae` | 30 | 30 | 10 | **+3.938** | +67.56 |
| `visdrone→dota15` | `s2ae` | 40 | 100 | 10 | **+2.787** | +32.25 |
| `visdrone→dota15` | `s2ae` | 40 | 30 | 10 | **+4.111** | +47.38 |
| `visdrone→dota15` | `s2ae` | 50 | 30 | 10 | **+3.973** | +50.91 |
| `visdrone→dota15` | `s2ae` | 10 | 100 | 10 | **+1.872** | +33.99 |
| `visdrone→dota15` | `s2ae` | 30 | 100 | 10 | **+2.437** | +34.93 |
| `visdrone→dota15` | `s2ae` | 50 | 100 | 10 | **+3.065** | +51.32 |
| `visdrone→dota15` | `t1c` | 20 | 100 | 10 | **+3.727** | +43.77 |
| `visdrone→dota15` | `vis` | 20 | 100 | 3 | **+3.603** | +12.03 |
| `visdrone→vhr10` | `vvhr` | None | 30 | 3 | **+3.253** | +10.43 |
| `y11_shwd→sfchd` | `b2` | 20 | 100 | 10 | **+0.318** | +3.45 |
| `y11_shwd→sfchd` | `y11` | 20 | 100 | 3 | **+0.010** | +0.19 |
| `y11_shwd→sfchd` | `y11` | 20 | 30 | 10 | **+1.110** | +9.60 |
| `y26_shwd→sfchd` | `y26` | 20 | 100 | 3 | **+1.490** | +19.68 |
| `y26_shwd→sfchd` | `y26` | 20 | 30 | 3 | **+2.660** | +13.03 |
| `yolo11n→dota15` | `r15` | 20 | 100 | 10 | **+3.751** | +50.30 |
| `yolo12n→dota15` | `r15` | 20 | 100 | 10 | **+3.513** | +34.20 |

* 格数 **130**；增益均值 **+1.100 pp**（中位 +0.940）；\|t\|≥2 的格 **107/130**；**负向格 30/130（23%）**

## 四、判读

* 同域组的**增益也是正的** ⇒ "损失平面增益"**不是迁移专有现象**；它是"(形状IoU 损失 vs 基线损失) 在同一数据上的差"，源域是否相同并不决定它的存在。
* ⇒ 这**削弱**了把 §4.x 的增益读成"迁移增益"的说法：真正的对照是"同域也在动"，因此"域差"不是增益的必要条件。
* ⚠ 但要注意**样本极不对称**：同域组集中在 `dota15→dota15`（多个族、轮流数系列）与少数 `r10` 组，且它们多数**不是 30/100ep 网格**，与跨域组的口径不同 ⇒ **只能作定性对照，不得做定量比较**。
