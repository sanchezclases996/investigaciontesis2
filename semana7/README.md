# Routing predictivo en consultas académicas-administrativas (UMA)

Semana 7: contenido de la semana 6 más importancia de variables sobre el conjunto F1 adoptado.

## Entrega principal (Glen)

| Artefacto | Ruta |
|-----------|------|
| Notebook importancia | `notebooks/07_importancia_variables.ipynb` |
| Notebook A/B (semana 6) | `notebooks/06_ab_data_variants.ipynb` |
| Figuras | `reports/figures/semana7_importancia_*.png` |
| Logs | `logs/metrics_importancia_variables.csv` |

## Otros archivos de esta carpeta

| Artefacto | Ruta |
|-----------|------|
| Matriz de consistencia (PDF) | `matriz-consistencia/matriz-consistencia.pdf` |
| Matriz (markdown) | `docs/matriz_consistencia.md` |
| Variables del plan de tesis | `docs/importancia_variables.md` |

`docs/importancia_variables.md` habla de variables del experimento de tesis (calidad, latencia, costo). El notebook 07 mide importancia de features del clasificador F1. No son lo mismo.

## Reproducir

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pip install ipykernel jupyter nbconvert
jupyter nbconvert --execute --to notebook --inplace notebooks/07_importancia_variables.ipynb
```
