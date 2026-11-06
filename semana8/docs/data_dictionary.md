# Diccionario de datos

## QuestionRecord

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | str | Identificador estable |
| question | str | Texto de la consulta |
| category | N/R/M/A | Norma, malla, mixta, trámite→persona |
| source_ref | str | Documento o nodo de grafo |
| reference_answer | str? | Gold verificado |
| validation_status | enum | draft/validated/rejected/no_verifiable_answer |
