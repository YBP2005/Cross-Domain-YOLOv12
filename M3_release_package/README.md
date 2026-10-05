# Reproducibility package: measurement-and-audit protocol for budgeted fine-tuning

This package accompanies the manuscript *"A measurement-and-audit protocol for budgeted fine-tuning of
lightweight detectors: cell-first rosters, fresh-seed reuse control, and the limits of first-order
diagnostics"* submitted to **Pattern Recognition** (Elsevier).

It is provided **anonymously for review**. Nothing here identifies the authors, and no credentials,
hostnames or cloud-instance identifiers are included.

## What the submission claims, and where each number lives

Every headline number can be recomputed from the CSVs in `data/` without running any training.
`ROLE` is `baseline` (peak lr 0.001) or `strategy` (peak lr 0.005); every value is **mAP50-95 in percent**
on the target corpus's **own held-out test split**, at `ckpt = best`.

| Claim in the manuscript | Where to look | How to recompute |
|---|---|---|
| smoke→SFCHD clean protocol, **+1.434 pp at ten seeds** (42.062 → 43.496; SD 0.383; paired t = 11.84; permutation p = 0.0020) | `data/registered_cells_all_seeds_test-readout.csv` | rows with `cell=smoke→SFCHD`, `ckpt=best`, `seed` 42–51; per-seed `map50_95` difference between `arm=lr005_100ep` and `arm=base100` |
| SHWD→SFCHD clean protocol, **+0.507 pp at ten seeds** (43.559 → 44.066; SD 0.488; t = 3.29; p = 0.0098) | same file | rows with `cell=SHWD→SFCHD`, `ckpt=best`, `seed` 42–51 |
| **Extension**: smoke→SFCHD **+1.408 pp at eleven seeds** (42.110 → 43.517; SD 0.372; t = 12.55; p = 0.000977) and SHWD→SFCHD **+0.627 pp at thirteen seeds** (43.485 → 44.112; SD 0.489; t = 4.63; p = 0.001221) — the readings the roster-wise correction `q = 0.0156` is computed from | same file | same two cells; seeds 42–52 (smoke) and 42–54 (SHWD), `ckpt=best` |
| mAP50 companions: **+0.925 pp** (smoke→SFCHD) and **+0.135 pp** (SHWD→SFCHD) | same file | same rows, column `map50` |
| Two-cell family correction **q = 0.052 and 0.127 at ten seeds**, **q = 0.0156** after the extension | `code/recompute_family_sensitivity.py` | BH over the permutation p-values with m = 26 configurations, the other 24 entering at p = 1 |
| **Third cell**: visdrone→dota15 **+3.650 pp**, 10/10 positive (11.626 → 15.277; SD 0.306; t = 37.75) | `data/clean_threeway_summary.csv` | row `pair=vistod15`, `budget=100`, `ckpt=best` |
| **Architecture control**: YOLO11n (COCO-pretrained) → dota15, **+3.662 pp**, 3/3 (10.578 → 14.240; t = 27.15) | `data/architecture_control_perseed.csv` | difference of `map50_95` between `strategy` and `baseline`, seeds 42/43/44 |
| Within-domain 30-epoch clean census (e.g. aitod20 −1.197, dota −0.850, d15d15 −0.031, visdrone −0.809) | `data/clean_threeway_summary.csv` | rows with `budget=30`, `ckpt=best` |
| MAFA→mendeley **−1.40 pp** over three paired seeds | **not in this package — see "Not included" below** | — |
| Norm-diffusion endpoint norms (SGD and the divergent AdamW arm) | `data/norm2_extra_SGD-endpoint-norms.json`, `data/norm2_adamw_endpoint-norm.json` | direct |

**Reading the two readout files.** The two files use different column conventions, so the arm labels
differ: in `clean_threeway_perseed.csv` the role column is `baseline` / `strategy` for peak lr 0.001 /
0.005, whereas in `registered_cells_all_seeds_test-readout.csv` the arm column is `base100` /
`lr005_100ep` for the same two arms. Both files report mAP50-95 and mAP50 in percent, on the target
corpus's own test split, at the checkpoint named in the `ckpt` column. Values in the released CSV files
are rounded to four decimals, so a mean recomputed from them can differ from a quoted mean in the third
decimal — for example the ten-seed smoke→SFCHD mean recomputes to +1.433 pp from the released rows
against +1.434 pp quoted in the manuscript.

### Not included in this package

Three kinds of reading are **not** in the files above, and are stated here rather than left to be
discovered:

1. **The B-pipeline published-protocol per-seed readings** — including the MAFA→mendeley cross-domain cell
   reported as **−1.40 pp over three paired seeds** (−1.13 / −1.82 / −1.26) and the screening-tier
   readings. The machine that produced them has been decommissioned and its per-seed file is not in this
   archive; it is available from the corresponding author on reasonable request. Note that this reading is
   a *published-protocol* reading, not a clean-protocol one, which is why it does not appear in
   `clean_threeway_*.csv` at all.
2. **Released weights.** The trained checkpoints behind every number are not included because of their
   size; they are available from the corresponding author on reasonable request.
3. **The split archives themselves** (images and labels). The construction rule and the split files are
   included; the corpora are public and are obtained from their own published sources — the reference list
   carries the citations for SHWD, SFCHD, VisDrone, DOTA, AI-TOD and MAFA, and the remaining corpora were
   obtained from public bundles whose provenance is recorded in the released registry.

## Protocol: what the three-way split is, and how to rebuild it

`protocol/threeway_carve_builder.sh` constructs the split for every corpus and
`protocol/threeway_splits_manifest.md` records the sizes and the name-level intersections.
The split is:

* **train** — the same 20 %-label subset as the published runs (so the comparison is same-budget);
* **validation** — a deterministic carve-out (seed 42) taken from the remaining training pool, used for
  checkpoint selection;
* **test** — the corpus's own held-out split; **this is the only split any reported number comes from**,
  so no checkpoint selection can touch the reported split.

`protocol/splits/*.yaml` are the per-corpus data files as used. They contain the original machine's
absolute paths; set them to your own data root (the layout is `<root>/<corpus>/{train,carve_*,test}`).

## Code

| File | Role |
|---|---|
| `code/registered_trainer_train_obj.py` | the registered training entry point (two-stage protocol; `--loss`, `--epochs`, `--pretrain`, `--lr`); the registered seed is a `--shuffle-seed` data-order permutation |
| `code/recompute_family_sensitivity.py` | recomputes every BH family variant quoted in the manuscript, under one stated convention |
| `code/bh_family26.py` | the m = 26 roster-wise correction itself |
| `code/selection_premium.py` | the published-protocol vs clean-protocol level comparison |
| `code/null_exceedance.py` | expected false-pass counts and P(≥1) under the frozen screening rule |
| `code/account_runs.py` | run accounting from the archive |
| `code/enumerate_family_cellfirst.py` | the cell-first roster enumeration |
| `code/fresh7_seed_analysis.py` | the reuse-free seven seeds |
| `code/conditional_and_power.py` | the conditional/power statements |

Scripts carry the original authors' working-language comments; they are released **as used**, not
rewritten, so that the released code is the code that produced the numbers.

## Provenance

`provenance/run_manifest_R15.csv` lists the runs of the seed-extension batch with their epochs, learning
rate, initialisation, data file, and the md5 of each run's `results.csv`.
`MANIFEST_sha256.csv` carries the sha256 of **every file in this package**, so the whole package can be
integrity-checked with one command.

## Notes on scope

* Two cells share one target corpus (SFCHD), and the two papers in this line of work share a training
  recipe and training set for the registered replication cells while each computes its readings under its
  own selection and endpoint rule. Neither paper describes that relationship as cross-implementation
  replication.
* The architecture control changes **both** the architecture and the initialisation (COCO rather than a
  VisDrone source pretrain); the two are not separated, and it covers one cell only.
* Released weights are available from the corresponding author on reasonable request.
