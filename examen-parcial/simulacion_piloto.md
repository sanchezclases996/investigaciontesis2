# Simulación piloto para la exposición

## Alcance

Se ejecutaron las celdas de `notebooks/06_ab_data_variants.ipynb` y `notebooks/08_optimizacion_hiperparametros.ipynb` dentro del entorno virtual de semana 7. La salida del primer cuaderno se recalculó desde los datos procesados de semana 8; el segundo repitió la búsqueda de hiperparámetros sobre F1. Ambos finalizaron correctamente el 11 de noviembre de 2026.

Esto evalúa la predicción de la etiqueta piloto `candidate_strategy`. No simula respuestas completas del asistente ni mide calidad de generación, latencia extremo a extremo, costo de API, seguridad o éxito de derivación.

## A/B de variables

- 196 consultas, 3 etiquetas (A1=125, A3=27, A5=44).
- Regresión logística balanceada; validación estratificada de 5 pliegues; semilla 42.
- F0: forma de texto, 8 columnas. F1: forma más intención, 17 columnas. F2: F1 más BM25, 22 columnas.

| Variante | F1 macro (media ± DE) | F1 ponderado | Exactitud |
|---|---:|---:|---:|
| F0 | 0.474 ± 0.032 | 0.514 | 0.495 |
| F1 | 0.533 ± 0.046 | 0.622 | 0.602 |
| F2 | 0.511 ± 0.061 | 0.595 | 0.577 |

La extensión F0→F1 sube 0.059 de F1 macro; añadir BM25 en F2 baja 0.022 respecto a F1. Es evidencia piloto, sujeta a revisión de etiquetas, cobertura y partición.

## Búsqueda de hiperparámetros

Random Forest sobre F1; 30 pruebas aleatorias y 30 TPE. F1 macro promedio: baseline 0.553 ± 0.086; mejor aleatorio 0.543 ± 0.048; mejor TPE 0.545 ± 0.059. La regla del notebook conserva baseline porque ninguna búsqueda supera su media.

## Reproducir

Desde la carpeta `examen-parcial` (contiene copias del código y de los datos usados):

```bash
source .venv/bin/activate
jupyter nbconvert --execute --to notebook --inplace notebooks/06_ab_data_variants.ipynb
jupyter nbconvert --execute --to notebook --inplace notebooks/08_optimizacion_hiperparametros.ipynb
```

Los resultados se guardan en `logs/metrics_experimentos.csv`, `logs/metrics_experimentos_folds.csv`, `logs/hpo_runs.csv`, `logs/hpo_resumen.csv` y `logs/hpo_decision.csv`.

## Pendiente para el experimento de tesis

Validación institucional del banco y de las etiquetas; consultas reales anonimizadas; malla oficial; evaluación pareada de las estrategias A0–A4 y políticas R0–R2; respuestas de referencia; y registro de calidad, fidelidad, latencia, costo, seguridad y escalamiento. Las carpetas `experiments/runs` aún no contienen esas corridas.
