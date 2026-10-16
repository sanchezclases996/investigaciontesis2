# Routing predictivo en consultas académicas-administrativas (UMA)

Semana 5: la semana 4 más el feature engineering del banco piloto. El cuaderno `notebooks/05_feature_engineering.ipynb` extrae características de texto, de intención por reglas y de una búsqueda BM25. No entrena el enrutador.

Corpus documental público de la Universidad María Auxiliadora, banco piloto de consultas y análisis exploratorio preliminar.

**Caso de estudio:** Facultad de Ingeniería y Negocios, UMA (San Juan de Lurigancho).

**Pregunta de investigación:** ¿el enrutamiento predictivo de estrategias de IA mejora la relación entre calidad, latencia y costo frente a una estrategia fija?

## Contenido principal

| Artefacto | Ruta |
|-----------|------|
| **Feature engineering** | `notebooks/05_feature_engineering.ipynb`, `docs/feature_engineering.md` |
| **EDA principal (revisión)** | `notebooks/01_inventario_documental.ipynb`, `02_eda_corpus.ipynb`, `03_eda_consultas.ipynb` |
| Placeholder resultados | `notebooks/04_eda_resultados.ipynb` |
| Inventario documental | `data/processed/corpus/inventario_documental.csv` |
| Texto extraído | `data/interim/extracted_text/` |
| Fuentes originales | `data/raw/public_documents/` |
| Banco piloto | `data/processed/question_bank/consultas_piloto.csv` |
| Export EDA (markdown/figuras) | `reports/eda/`, `reports/figures/` |
| Estado de datos | `data/STATUS.md` |

## Reproducibilidad

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make data   # catálogo → descarga → extracción → inventario → banco
make eda    # opcional: regenera reports/ vía run_eda.py (export)
jupyter nbconvert --execute --to notebook --inplace notebooks/01_*.ipynb notebooks/02_*.ipynb notebooks/03_*.ipynb
jupyter nbconvert --execute --to notebook --inplace notebooks/05_feature_engineering.ipynb
```

## Alcance de esta etapa

Incluye: inventario de 12 fuentes públicas UMA, extracción de texto, banco piloto etiquetado como `draft`, EDA documental y del banco.

No incluye: malla curricular oficial de la facultad, calendario académico dedicado, gold validado por personal institucional, ni mediciones experimentales de las configuraciones A0–A5.

## Configuraciones previstas (etapas posteriores)

| Código | Descripción |
|--------|-------------|
| A0 | Modelo base |
| A1 | RAG |
| A2 | Fine-tuning (si es viable) |
| A3 | RAG + herramientas de malla |
| A4 | Estrategia compuesta fija |
| A5 | Enrutamiento predictivo |
