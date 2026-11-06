#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi
# Análisis principal: ejecutar notebooks/01–03 (pandas/matplotlib en celdas).
# Este script regenera solo el export markdown/JSON vía run_eda.py.
python -m thesis_routing.eda.run_eda
echo "Notebooks (revisión): notebooks/01–03"
echo "Export: reports/eda/  Figuras: reports/figures/"
