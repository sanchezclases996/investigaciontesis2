# Feature engineering de las consultas

Esta semana convierte cada pregunta del banco piloto en características.
No entrena un enrutador y no asigna la ruta. Las columnas sirven para ver qué se puede medir antes de decidir la estrategia, y qué solo aparece después de una búsqueda.

Fuente: `data/processed/question_bank/consultas_piloto.csv` (196 filas, todas `draft`).

## Tres grupos calculados

| Grupo | Cuándo existe | Qué aporta | Qué no demuestra |
|-------|----------------|------------|------------------|
| Texto | Antes de buscar | Longitud, interrogaciones, negación, condición, comparación, caso personal | Que una pregunta larga sea más difícil |
| Intención por reglas | Antes de buscar | Familia léxica y marcas de cálculo, regla, tiempo o varias fuentes | La categoría N/R/M/A del banco |
| BM25 léxico | Después de una búsqueda inicial | Mejor documento, media del top 3, margen y cuántos documentos superan 0 | Que la respuesta vaya a ser correcta |

La puntuación BM25 no es una probabilidad. Un valor alto no significa 80 % de acierto.

## Catálogo

### Texto

| Característica | Tipo | Definición |
|----------------|------|------------|
| `query_length_chars` | int | Caracteres de la pregunta |
| `query_length_words` | int | Palabras, sin contar tildes como tokens distintos |
| `question_mark_count` | int | Cantidad de `?` |
| `has_multiple_questions` | 0/1 | Más de un `?` |
| `contains_negation` | 0/1 | Palabra `no`, `nunca`, `tampoco`, `sin` o `ni` |
| `contains_condition` | 0/1 | `si` como palabra, `siempre que`, `en caso de`, `aunque`, `mientras` |
| `contains_comparison` | 0/1 | Comparar o pedir una diferencia |
| `contains_personal_case` | 0/1 | `mi`, `mis`, `puedo`, `estoy`, `desaprobé` y formas cercanas |

`si` se busca como palabra. No debe activarse dentro de `asistencia`.

### Intención

| Característica | Tipo | Definición |
|----------------|------|------------|
| `intent_category` | texto | Una familia: prerrequisitos, matrícula, pagos, trámites, horarios, calendario u `otro` |
| `n_intent_families` | int | Cuántas familias léxicas aparecen |
| `requires_multiple_sources_rule` | 0/1 | Dos familias, o un nexo del tipo «además» |
| `requires_personal_context` | 0/1 | La pregunta parece un caso propio (`puedo`, `desaprobé`, `perdí`) |
| `requires_calculation` | 0/1 | Pide cantidad, suma, porcentaje o costo |
| `requires_rule_validation` | 0/1 | Pide saber si se cumple una condición |
| `requires_temporal_reasoning` | 0/1 | Fechas, plazos, «todavía», «cuándo» |
| `contains_academic_entity` | 0/1 | Ciclo, curso, crédito, malla, examen, nota |
| `contains_administrative_entity` | 0/1 | Matrícula, pago, trámite, carné, SIGU, diploma |

Si hay varias familias, se queda la más específica según el orden de la tabla.

### Recuperación léxica

Índice: textos con `estado_extraccion = ok`. D010 queda fuera.

| Característica | Tipo | Definición |
|----------------|------|------------|
| `top1_retrieval_score` | float | BM25 del mejor documento |
| `topk_mean_score` | float | Media de los tres mejores |
| `retrieval_score_margin` | float | Diferencia entre el primero y el segundo |
| `retrieved_document_count` | int | Documentos con puntuación mayor que 0 |
| `retrieved_source_count` | int | Fuentes distintas con puntuación mayor que 0 |
| `top1_doc_id` | texto | Documento en el primer puesto |

No se calculan `source_version_conflict` ni `evidence_coverage`. No hay versiones enfrentadas del mismo reglamento, ni un criterio de cobertura por aspectos de cada pregunta.

## Qué no es una característica

`categoria`, `complejidad`, `candidate_strategy`, `requiere_herramienta` y `doc_referencia` son etiquetas de borrador. Se conservan en la tabla para contrastar. No entran como entrada de un modelo que pretenda predecirlas.

Hay dos usos distintos:

1. Enrutamiento previo: solo texto e intención. La búsqueda todavía no ocurrió.
2. Enrutamiento después de una búsqueda barata: se pueden sumar las columnas BM25 para decidir si hace falta otra estrategia.

Mezclar los dos usos en un solo modelo sería fuga de información.

## Comparación que queda para después

| Conjunto | Columnas | Pregunta |
|----------|----------|----------|
| F0 | Longitud y marcas de texto | ¿Alcanza una línea base superficial? |
| F1 | F0 más intención | ¿La semántica de reglas aporta? |
| F2 | F1 más BM25 | ¿La evidencia recuperada cambia la decisión? |

Eso se mide cuando haya etiquetas revisadas y corridas de calidad, latencia y costo. Esta semana solo comprueba que las columnas se calculan y cómo se distribuyen en el piloto.

## Limitaciones

- Las reglas fallan si el estudiante no usa la palabra esperada. En este banco, 139 de 196 consultas quedan en `otro`.
- `contains_personal_case` se enciende mucho porque la FAQ habla en primera persona (`mi`, `mis`). No significa que la consulta necesite un expediente.
- La longitud no separa la complejidad etiquetada.
- El primer documento BM25 coincide a menudo con D012 porque 128 preguntas salen de la FAQ. Eso no prueba que la búsqueda encuentre el reglamento correcto.
- Casi todas las consultas obtienen puntuación positiva en casi todos los documentos. El conteo de documentos recuperados no discrimina.
