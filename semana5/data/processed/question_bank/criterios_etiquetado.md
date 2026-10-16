# Criterios de etiquetado del banco piloto

## Categoría

| Código | Significado |
|--------|-------------|
| N | Normativa / reglamento / calendario textual |
| R | Malla, prerrequisitos o avance curricular (herramienta o grafo) |
| M | Requiere combinar más de una fuente |
| A | Trámite o canal que suele derivarse a persona o sistema institucional (SIGU, correo, ventanilla) |

## Complejidad

| Nivel | Criterio |
|-------|----------|
| baja | Un hecho localizable en una sola sección o FAQ |
| media | Una fuente, pero con varias condiciones o localización no trivial |
| alta | Varias fuentes, reglas encadenadas, o herramienta estructurada |

La longitud de la pregunta no define la complejidad.

## Otros campos

- `doc_referencia`: documento o artefacto donde se busca la evidencia.
- `respuesta_esperada`: solo si hay respaldo en FAQ o extracto revisado; si no, vacío.
- `es_respondible`: verdadero si `doc_referencia` existe en el corpus usable (no `pendiente_*`, no D010 débil). No exige aún `respuesta_esperada` llena.
- `validacion_experta`: `draft` hasta revisión institucional.
- `requiere_herramienta`: verdadero para consultas tipo R sobre grafo/malla.
- `requiere_multiples_fuentes`: verdadero para tipo M.

## Deduplicación

No se incluyen preguntas idénticas ni casi idénticas (misma pregunta normalizada). FAQ y preguntas derivadas de reglamentos se fusionan en un solo banco piloto.
