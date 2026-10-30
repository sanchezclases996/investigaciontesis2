# EDA documental (UMA)

**Caso:** Facultad de Ingeniería y Negocios / UMA–SJL.  
**Fuentes:** documentación pública (reglamentos, tarifario y FAQ).  
**Alcance:** análisis del corpus; no incluye resultados de las configuraciones A0–A5.

## 1. Inventario y cobertura

- Documentos en inventario: **12**.
- Páginas totales (metadato): **102**.
- Palabras extraídas: **48 730**.
- Distribución por dominio: `{'academico': 3, 'admision': 1, 'economico': 3, 'institucional': 1, 'matricula': 2, 'orientacion': 1, 'tramites': 1}`.

Figuras: `reports/figures/eda_docs_por_dominio.png`, `eda_palabras_por_doc.png`.

## 2. Calidad de extracción

- Extracción OK: **11** / 12.
- Extracción débil o posible documento escaneado: **['D010']**.

D010 (guía de proceso de matrícula) aporta poco texto seleccionable.
En el índice de recuperación se deja fuera o se trata aparte hasta disponer de OCR
o de una versión textual usable.

Figuras: `eda_calidad_extraccion.png`, `eda_paginas_vs_palabras.png`.

## 3. Cobertura por aspectos (cuantitativa)

Criterio binario documentado (`cubierto` / `no_cubierto`):
`{'min_hits': 3, 'min_densidad_por_1k': 0.4, 'min_tfidf_cosine': 0.04, 'min_words_doc': 300}`.

Artefactos: `eda_cobertura_hits.csv`, `eda_cobertura_densidad_1k.csv`,
`eda_cobertura_tfidf.csv`, `eda_cobertura_etiqueta.csv`, heatmap TF-IDF.

Los aspectos separan procesos (p. ej. matrícula vs anulación/retiro;
convalidación vs aprobación). La métrica indica evidencia textual medible,
no vigencia jurídica de un artículo.

| Aspecto | Docs cubiertos |
|---------|----------------|
| admision | 5 / 12 |
| anulacion_retiro | 0 / 12 |
| aprobacion_desaprobacion | 6 / 12 |
| asistencia_inasistencia | 4 / 12 |
| becas | 4 / 12 |
| calendario_periodo | 4 / 12 |
| convalidacion | 5 / 12 |
| creditos_academicos | 7 / 12 |
| evaluacion_examenes | 3 / 12 |
| malla_plan_estudios | 7 / 12 |
| matricula_inscripcion | 6 / 12 |
| prerrequisitos | 0 / 12 |
| tarifas_pensiones | 6 / 12 |
| tramites_grados_titulos | 5 / 12 |

## 4. Implicaciones para el diseño experimental

1. **Recuperación documental (A1):** D001–D009, D011 y D012 tienen texto extraíble
   suficiente para un índice RAG normativo y administrativo.
2. **Malla y prerrequisitos (A3):** el corpus público cubre poco la estructura operativa
   de prerrequisitos; las consultas tipo R requieren malla oficial o grafo autorizado.
   El grafo actual es de demostración.
3. **Calendario académico:** no hay documento dedicado en este piloto;
   las consultas centradas en fechas del ciclo tienen cobertura limitada.
4. **FAQ (D012):** concentra preguntas frecuentes; ante divergencia, la referencia son los reglamentos.
5. **Derivación a persona (tipo A):** la FAQ menciona SIGU, correo y ventanilla.

## 5. Limitaciones del corpus

| Limitación | Efecto en la evaluación | Tratamiento |
|------------|-------------------------|-------------|
| Sin malla oficial de la facultad | Consultas tipo R incompletas | Incorporar plan/grafo institucional |
| Sin calendario dedicado | Preguntas de fechas frágiles | Añadir calendario del ciclo |
| D010 con poco texto | Bajo valor en retrieval | OCR o fuente alternativa |
| Banco en estado draft | Sin gold institucional | Revisión por personal de la facultad |
| Sin consultas reales anonimizadas | Menor validez ecológica | Incorporarlas si hay autorización |

## 6. Preparación del corpus para etapas siguientes

- Incluir en el índice RAG: D001–D009, D011, D012.
- Excluir o aislar: D010 mientras la extracción sea débil.
- Mantener la malla en herramientas o grafo, separada del índice de texto normativo.
- Ampliar y validar el banco de consultas antes de las corridas A0–A5.
