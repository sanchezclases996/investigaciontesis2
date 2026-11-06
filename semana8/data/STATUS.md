# Estado de datos

Fecha de preparación: 2026-10-09. Caso: UMA–SJL.

## Pipeline ejecutado

1. Catálogo con URLs → `sources/catalog_sources.yaml`
2. Descarga pública → `raw/public_documents/` (D001–D012)
3. Extracción → `interim/extracted_text/`
4. Inventario → `processed/corpus/inventario_documental.csv`
5. Banco piloto y borradores FAQ → `processed/question_bank/` y `synthetic/`
6. Perfiles y grafo de malla de demostración → `synthetic/` y `processed/corpus/`
7. EDA → `reports/eda/` y `reports/figures/`

## Corpus documental (12 fuentes)

| ID | Documento | Extracción |
|----|-----------|------------|
| D001 | Reglamento académico | ok (16 p.) |
| D002 | Reglamento de matrícula | ok |
| D003 | Reglamento general UMA 2025 | ok |
| D004 | Reglamento económico | ok |
| D005 | Grados y títulos | ok |
| D006 | Admisión pregrado | ok |
| D007 | Becas | ok |
| D008 | Tutoría | ok |
| D009 | Convalidaciones | ok |
| D010 | Proceso de matrícula (guía) | weak_or_scanned |
| D011 | Tarifario 2025 | ok |
| D012 | FAQ HTML | ok |

Portales: [reglamentos](https://uma.edu.pe/resolucion-reglamentos/), [FAQ](https://uma.edu.pe/preguntas-frecuentes/), [transparencia](https://uma.edu.pe/transparencia2026/).

## Banco de consultas

| Archivo | N | Estado |
|---------|---|--------|
| `processed/question_bank/consultas_piloto.csv` | 196 | `validacion_experta=draft`; FAQ + CURATED deduplicado |
| `synthetic/generated_questions/consultas_desde_faq.csv` | 122 | preguntas extraídas de FAQ, sin respuesta de referencia |

El banco piloto no constituye una muestra estadísticamente representativa.

## Material no disponible en esta versión

- Malla vigente de la Facultad de Ingeniería y Negocios
- Calendario académico dedicado del ciclo
- Validación institucional del banco
- Consultas reales anonimizadas
- Grafo de malla oficial (el archivo actual es de demostración)

## Regeneración

```bash
source .venv/bin/activate
python -m thesis_routing.pipeline.prepare_data
python -m thesis_routing.eda.run_eda
```
