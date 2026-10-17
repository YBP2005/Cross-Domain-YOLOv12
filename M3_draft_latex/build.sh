#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Build the IJCV submission package.
#
#   ./build.sh            # article + supplement
#   ./build.sh article    # article only
#   ./build.sh supplement # supplement only
#
# Canonical cycle (Springer Nature / IJCV): pdflatex, pdflatex, bibtex,
# pdflatex, pdflatex.  If pdflatex is not on PATH the script falls back to
# Tectonic (which runs an equivalent TeX + BibTeX + TeX cycle internally);
# the engine actually used is printed and recorded in MIGRATION_REPORT.md.
# ---------------------------------------------------------------------------
set -u

cd "$(dirname "$0")"

TARGET="${1:-all}"
JOBS=""
case "$TARGET" in
  all)        DOCS="sn-article supplementary" ;;
  article)    DOCS="sn-article" ;;
  supplement) DOCS="supplementary" ;;
  *)          echo "usage: $0 [all|article|supplement]" >&2; exit 2 ;;
esac

have() { command -v "$1" >/dev/null 2>&1; }

if have pdflatex && have bibtex; then
  ENGINE="pdflatex + bibtex"
  echo "== engine: $ENGINE"
  for doc in $DOCS; do
    echo "--- $doc: pdflatex (1)"
    pdflatex -interaction=nonstopmode -file-line-error "$doc.tex" > "$doc.pass1.out" 2>&1 || true
    echo "--- $doc: pdflatex (2)"
    pdflatex -interaction=nonstopmode -file-line-error "$doc.tex" > "$doc.pass2.out" 2>&1 || true
    echo "--- $doc: bibtex"
    bibtex "$doc" > "$doc.bibtex.out" 2>&1 || true
    echo "--- $doc: pdflatex (3)"
    pdflatex -interaction=nonstopmode -file-line-error "$doc.tex" > "$doc.pass3.out" 2>&1 || true
    echo "--- $doc: pdflatex (4)"
    pdflatex -interaction=nonstopmode -file-line-error "$doc.tex" > "$doc.pass4.out" 2>&1 || true
    if [ -f "$doc.pdf" ]; then
      echo "--- $doc: OK -> $doc.pdf"
    else
      echo "--- $doc: FAILED (no PDF)" >&2
    fi
  done
elif have tectonic; then
  ENGINE="tectonic $(tectonic --version 2>/dev/null | head -1)"
  echo "== engine: $ENGINE (pdflatex not found; Tectonic runs TeX + BibTeX itself)"
  for doc in $DOCS; do
    echo "--- $doc: tectonic"
    tectonic -X compile "$doc.tex" --keep-logs || echo "--- $doc: FAILED" >&2
  done
else
  ENGINE="none"
  echo "No TeX engine found (need pdflatex+bibtex, or tectonic)." >&2
  exit 1
fi

echo
echo "== warnings and errors"
for doc in $DOCS; do
  [ -f "$doc.log" ] || continue
  printf '%s: errors=%s undefined-citations=%s overfull=%s\n' \
    "$doc" \
    "$(grep -c '^!' "$doc.log" 2>/dev/null || echo 0)" \
    "$(grep -ci 'citation .* undefined' "$doc.log" 2>/dev/null || echo 0)" \
    "$(grep -c 'Overfull \\\\hbox' "$doc.log" 2>/dev/null || echo 0)"
done
