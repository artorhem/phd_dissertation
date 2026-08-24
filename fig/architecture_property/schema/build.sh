#!/bin/bash
# Build all schema diagrams to PDF.
# Usage: ./build.sh          (build all)
#        ./build.sh <name>   (build one, e.g. ./build.sh mode_overview)

set -e
cd "$(dirname "$0")"

FIGS=(
  splitedgekey_embedded
  splitedgekey_columnar
  adjlist_embedded
  adjlist_columnar
  mode_overview
)

build_one() {
  local name="$1"
  echo "  Building ${name}.pdf ..."
  pdflatex -interaction=nonstopmode -halt-on-error "${name}.tex" > /dev/null 2>&1
  # clean aux files
  rm -f "${name}.aux" "${name}.log"
}

if [ -n "$1" ]; then
  build_one "$1"
else
  for fig in "${FIGS[@]}"; do
    build_one "$fig"
  done
  echo "Done. PDFs:"
  ls -1 *.pdf
fi
