# Semana 6

Copia de la semana 5 más el experimento A/B de **variantes de datos (features)**.

- Baseline **F0**: solo features de texto  
- Var1 **F1**: F0 + intención por reglas  
- Var2 **F2**: F1 + BM25  
- Etiqueta: `candidate_strategy`  
- Modelo fijo: LogisticRegression (mismo en las tres corridas)

Cuaderno de entrega: `notebooks/06_ab_data_variants.ipynb`  
Logs: `logs/metrics_experimentos.csv`

```bash
source .venv/bin/activate
jupyter nbconvert --execute --to notebook --inplace notebooks/06_ab_data_variants.ipynb
```
