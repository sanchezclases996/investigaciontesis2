#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate 2>/dev/null || true
pytest -q
echo "Reproducción completa cuando haya datos + configs congeladas."
