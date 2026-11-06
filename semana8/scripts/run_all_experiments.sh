#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate 2>/dev/null || true
for cfg in configs/experiments/*.yaml; do
  echo "[EXP] $cfg"
  python -m thesis_routing.pipeline.run_experiment || true
done
