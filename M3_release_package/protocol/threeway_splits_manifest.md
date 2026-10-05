# Three-way split provenance (2026-09-14T07:37:31Z, <cluster>)

carve-out rule: deterministic sample (seed 42) of (pool minus label-subset), symlinked;
verification: name-level intersections of train/val/test must all be 0.

- **aitod20**: train=2243 val=1000 test=2804; intersections train∩val=0 train∩test=0 val∩test=0; yaml `/root/datasets/AI-TOD_yolo/aitod20_3way.yaml`
- **dota15_20p**: train=282 val=300 test=458; intersections train∩val=0 train∩test=0 val∩test=0; yaml `/root/datasets_mask/dota15_yolo/dota15_20p_3way.yaml`
- **mende20**: train=1150 val=1000 test=800; intersections train∩val=0 train∩test=0 val∩test=0; yaml `/root/datasets_mask/mendeley_yolo/mende20_3way.yaml`
- sfchd20: SKIPPED (missing dirs)
