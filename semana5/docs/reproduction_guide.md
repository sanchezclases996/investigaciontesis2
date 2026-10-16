# Guía de reproducción

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
make test
bash scripts/reproduce_results.sh
```

Requiere configs en `configs/` y datos documentados en `data/README.md`.
