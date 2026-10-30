# Routing predictivo en consultas académicas-administrativas (UMA)


**Caso de estudio:** Facultad de Ingeniería y Negocios, UMA (San Juan de Lurigancho).

## Entrega principal (Glen)

| Artefacto | Ruta |
|-----------|------|
| **Notebook A/B** | `notebooks/06_ab_data_variants.ipynb` |
| Logs de métricas | `logs/metrics_experimentos.csv` |
| Figura comparativa | `reports/figures/semana6_ab_f1_confusion.png` |

## Cómo reproducir

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pip install ipykernel jupyter nbconvert
jupyter nbconvert --execute --to notebook --inplace notebooks/06_ab_data_variants.ipynb
```

## Diseño del experimento

| ID | Set de features | Cambio único |
|----|-----------------|--------------|
| Baseline_F0 | texto | línea base |
| Var1_F1 | F0 + intención | añade datos de intención |
| Var2_F2 | F1 + BM25 | añade evidencia recuperada |

Modelo fijo: LogisticRegression. Validación: Stratified K-Fold (K=5), seed 42. Métrica central: F1 macro.

Ver también `README_SEMANA.md` y `docs/feature_engineering.md`.
