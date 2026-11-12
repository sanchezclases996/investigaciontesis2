# Examen parcial: presentación y simulación

Esta carpeta es una copia autocontenida de la presentación, el código y los datos usados para el piloto de clasificación de rutas.

## Contenido

- `ppt_exposicion_simulacion.tex` y `ppt_exposicion_simulacion.pdf`: Beamer y PDF.
- `notebooks/`: cuadernos A/B de variables y búsqueda de hiperparámetros.
- `data/processed/features/consultas_features.csv`: tabla de 196 consultas y variables derivadas utilizada por los cuadernos.
- `logs/`: métricas reproducidas y resultados de búsqueda guardados.
- `reports/figures/`: figuras incorporadas en la presentación; se regeneran al ejecutar los cuadernos.
- `simulacion_piloto.md`: descripción de protocolo, resultados y límites.

## Reproducir la simulación

Desde esta carpeta:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter nbconvert --execute --to notebook --inplace notebooks/06_ab_data_variants.ipynb
jupyter nbconvert --execute --to notebook --inplace notebooks/08_optimizacion_hiperparametros.ipynb
```

Los cuadernos actualizan `logs/` y generan gráficas dentro de `reports/figures/`. Para compilar la presentación desde esta carpeta:

```bash
latexmk -pdf -interaction=nonstopmode ppt_exposicion_simulacion.tex
```

Las etiquetas del banco continúan en borrador y no representan una validación institucional. La simulación evalúa clasificación de etiquetas de ruta, no calidad de respuestas, costos de API ni latencia extremo a extremo.
