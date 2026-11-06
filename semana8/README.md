# Routing predictivo en consultas académicas-administrativas (UMA)

Semana 8: contenido de la semana 7 más optimización de hiperparámetros del clasificador sobre F1.

## Entrega principal (Glen)

| Artefacto | Ruta |
|-----------|------|
| Notebook HPO | `notebooks/08_optimizacion_hiperparametros.ipynb` |
| Notebook importancia (semana 7) | `notebooks/07_importancia_variables.ipynb` |
| Notebook A/B (semana 6) | `notebooks/06_ab_data_variants.ipynb` |
| Figuras | `reports/figures/semana8_hpo_*.png` |
| Logs | `logs/hpo_runs.csv`, `logs/hpo_resumen.csv`, `logs/hpo_decision.csv` |

## Reproducir

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pip install ipykernel jupyter nbconvert
jupyter nbconvert --execute --to notebook --inplace notebooks/08_optimizacion_hiperparametros.ipynb
```
