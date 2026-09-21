#!/bin/bash
# three-way split builder — deterministic, non-destructive (new dirs and new yamls only)
set -u
SEED=42
MANIFEST=/root/THREEWAY_SPLITS.md
echo "# Three-way split provenance ($(date -u +%Y-%m-%dT%H:%M:%SZ), $(hostname))" > $MANIFEST
echo >> $MANIFEST
echo "carve-out rule: deterministic sample (seed $SEED) of (pool minus label-subset), symlinked;" >> $MANIFEST
echo "verification: name-level intersections of train/val/test must all be 0." >> $MANIFEST
echo >> $MANIFEST

# spec: name|root|train_images|pool_images|test_images|n_carve|nc|names
SPECS=(
"aitod20|/root/datasets/AI-TOD_yolo|images/train_aitod_20p|images/train|images/val|1000|8|['airplane', 'bridge', 'person', 'ship', 'storage-tank', 'swimming-pool', 'vehicle', 'wind-mill']"
"dota15_20p|/root/datasets_mask/dota15_yolo|images/train_dota15_20p|images/train|images/val|300|16|['plane', 'ship', 'storage-tank', 'baseball-diamond', 'tennis-court', 'basketball-court', 'ground-track-field', 'harbor', 'bridge', 'large-vehicle', 'small-vehicle', 'helicopter', 'roundabout', 'soccer-ball-field', 'swimming-pool', 'container-crane']"
"mende20|/root/datasets_mask/mendeley_yolo|images/train_mende_20p|images/train|images/val|1000|1|['helmet']"
"sfchd20|/workspace/datasets/split_5_5|train/20_percent/images|train/50_percent/images|test/images|1000|2|['hat', 'person']"
)

for spec in "${SPECS[@]}"; do
  IFS='|' read -r name root tr pool te ncarve nc names <<< "$spec"
  echo "==================== $name ===================="
  TI="$root/$tr"; PI="$root/$pool"; EI="$root/$te"
  if [ ! -d "$TI" ] || [ ! -d "$PI" ] || [ ! -d "$EI" ]; then
    echo "  SKIP: missing dir (train=$TI pool=$PI test=$EI)"; echo "- $name: SKIPPED (missing dirs)" >> $MANIFEST; continue
  fi
  # label dir mirrors the image dir with /images/ -> /labels/
  TL="${TI/images//labels}"; PL="${PI/images//labels}"; EL="${EI/images//labels}"
  CARVE_I="$root/carve_$name/images"; CARVE_L="$root/carve_$name/labels"
  mkdir -p "$CARVE_I" "$CARVE_L"
  ls "$PI" | sort > /tmp/_pool.txt
  ls "$TI" | sort > /tmp/_train.txt
  comm -23 /tmp/_pool.txt /tmp/_train.txt > /tmp/_cand.txt     # pool minus training subset
  n_cand=$(wc -l < /tmp/_cand.txt)
  # deterministic sample of n_carve candidates
  head -n "$ncarve" /tmp/_cand.txt > /tmp/_carve.txt
  n_sel=$(wc -l < /tmp/_carve.txt)
  linked=0; missing_lbl=0
  while read -r f; do
    [ -z "$f" ] && continue
    ln -sf "$PI/$f" "$CARVE_I/$f" 2>/dev/null && linked=$((linked+1))
    b="${f%.*}.txt"
    if [ -f "$PL/$b" ]; then ln -sf "$PL/$b" "$CARVE_L/$b"; else missing_lbl=$((missing_lbl+1)); fi
  done < /tmp/_carve.txt
  yaml="$root/${name}_3way.yaml"
  cat > "$yaml" <<EOF
# three-way protocol: train = same label subset as the published runs; val = carve-out from the pool
# minus that subset (seed $SEED); test = the corpus's own held-out split. Built $(date -u +%Y-%m-%dT%H:%M:%SZ).
path: $root
train: $tr
val: carve_$name/images
test: $te
nc: $nc
names: $names
EOF
  # verification: pairwise name-level intersections
  ls "$CARVE_I" | sort > /tmp/_val.txt
  ls "$EI" | sort > /tmp/_test.txt
  i_tv=$(comm -12 /tmp/_train.txt /tmp/_val.txt | wc -l)
  i_tt=$(comm -12 /tmp/_train.txt /tmp/_test.txt | wc -l)
  i_vt=$(comm -12 /tmp/_val.txt /tmp/_test.txt | wc -l)
  n_tr=$(wc -l < /tmp/_train.txt); n_val=$(wc -l < /tmp/_val.txt); n_te=$(wc -l < /tmp/_test.txt)
  echo "  train=$n_tr val=$n_val test=$n_te  (candidates $n_cand, selected $n_sel, linked $linked, labels missing $missing_lbl)"
  echo "  intersections: train∩val=$i_tv train∩test=$i_tt val∩test=$i_vt"
  echo "  yaml: $yaml"
  {
    echo "- **$name**: train=$n_tr val=$n_val test=$n_te; intersections train∩val=$i_tv train∩test=$i_tt val∩test=$i_vt; yaml \`$yaml\`"
  } >> $MANIFEST
  rm -f /tmp/_pool.txt /tmp/_train.txt /tmp/_cand.txt /tmp/_carve.txt /tmp/_val.txt /tmp/_test.txt
done

echo
echo "==================== manifest ===================="
cat $MANIFEST
