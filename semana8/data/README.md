# Datos

Organización del corpus y del banco de consultas usado en el análisis exploratorio.

## Flujo

```text
1. Catálogo de fuentes     data/sources/catalog_sources.yaml
2. Descarga pública        data/raw/public_documents/
3. Extracción              data/interim/extracted_text/
4. Inventario              data/processed/corpus/inventario_documental.csv
5. Banco piloto            data/processed/question_bank/consultas_piloto.csv
6. Material sintético/demo data/synthetic/
7. Informes EDA            reports/eda/
```

## Portales UMA

| Portal | URL |
|--------|-----|
| Reglamentos | https://uma.edu.pe/resolucion-reglamentos/ |
| FAQ | https://uma.edu.pe/preguntas-frecuentes/ |
| Transparencia | https://uma.edu.pe/transparencia2026/ |

## Capas de datos

| Capa | Contenido | Ubicación |
|------|-----------|-----------|
| Documental | Reglamentos, tarifario, FAQ | `raw/` → `interim/` → `processed/corpus/` |
| Consultas | Preguntas con referencia documental | `processed/question_bank/` |
| Demo / sintético | Grafo de malla de ejemplo, perfiles demo, borradores FAQ | `synthetic/` |
| Experimental | Resultados A0–A5 | `experiments/results/` (vacío en esta etapa) |

## Regeneración

```bash
source .venv/bin/activate
python -m thesis_routing.pipeline.prepare_data
```

El pipeline lee el catálogo, descarga fuentes públicas, extrae texto, escribe el inventario y genera el banco piloto y los artefactos demo.

## Criterios de registro

- Metadatos medidos del archivo (páginas, hash, tamaño) o tomados de la URL oficial.
- Documentación autorizada no pública en `raw/authorized_documents/` (excluida del control de versiones).
- Respuestas de referencia verificables contra documento o grafo; estado `draft` hasta revisión institucional.
- El grafo en `processed/corpus/malla_demo_grafo.json` es de demostración, no la malla oficial de la facultad.

## Pendientes de origen institucional

- Malla vigente de la Facultad de Ingeniería y Negocios
- Calendario académico del ciclo en curso
- Revisión del banco por personal académico o administrativo
- Consultas reales anonimizadas, si hay autorización
