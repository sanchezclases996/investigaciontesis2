# Sprint de mejoras: avance y plan del siguiente sprint

**Tesis:** Enrutamiento predictivo de estrategias de atención para consultas académico-administrativas (caso UMA)
**Autor:** Carlos Sánchez Coronel &  Freud Melgar Aliaga
**Fecha:** 27/11/2026

---

## 1. Correcciones aplicadas al plan de tesis

| Observación / problema | Corrección aplicada |
|---|---|
| Solo se decidía la estrategia de atención. | El enrutador decide **dos cosas por consulta**: la estrategia (RAG, RAG con herramientas o abstención) y el nivel de modelo (barato o caro). |
| Faltaban referencias de comparación. | Se agregan un **oráculo** (cota superior de ahorro), un **baseline aleatorio** y la tríada de evaluación RAG (fidelidad, relevancia de la respuesta y relevancia del contexto), con un juez LLM validado contra etiquetas humanas. |
| Objetivos sin umbrales medibles. | El OG y los OE1–OE5 tienen ahora umbrales. Por ejemplo: **exactitud ≥ 95 %** de la mejor configuración fija, con **costo y p95 ≤ 70 %** de la configuración más cara; **abstención correcta ≥ 0,80** con abstención innecesaria ≤ 0,10; un filtro de seguridad que bloquee ≥ 90 % de las entradas adversarias con FP ≤ 5 %. |
| Datos de evaluación sin partición definida. | El **conjunto de referencia** se divide en una partición de calibración (232) y otra de evaluación reservada (100), más un banco adversario aparte para seguridad. |
| Corpus sin delimitar. | El corpus queda formado por unos **24 documentos públicos de la UMA** de cuatro programas, y se congela el 15/12/2026 para que los resultados sean reproducibles. |

## 2. Diagnóstico del repositorio

**Lo que se reutiliza:**

- La extracción de texto y la ingeniería de features.
- La validación cruzada, la ablación y la búsqueda de hiperparámetros. Este pipeline pasa a ser el enrutador aprendido **R1** (regresión logística / random forest).

**Error encontrado y corregido en el diseño:**
- La etiqueta `candidate_strategy` se derivaba directamente de `categoria`. Por eso el macro-F1 de 0,553 medía la reproducción de una regla, no la elección de la ruta más barata aceptable.
- **Corrección:** la etiqueta pasa a ser la *opción más barata que responde correctamente*. Se obtiene ejecutando todas las configuraciones sobre cada consulta del conjunto de referencia y quedándose con la de menor costo que aprueba la evaluación.

**Lo que se retira:** el banco de alumnos, el grafo de demostración y los perfiles sintéticos, porque ya no corresponden al nuevo usuario (el asesor).

**Pendiente en la estructura:** las carpetas `retrieval/`, `models/`, `routing/` y `evaluation/` todavía están vacías y se llenan en el siguiente sprint.

## 3. Plan de mejora para el siguiente sprint

| # | Entregable | Criterio de "terminado" |
|---|---|---|
| S1 | Entorno local reproducible: RAG base (Flowise) + índice vectorial + trazas en LangSmith, cargado con el corpus público de la UMA. | Se levanta desde cero con un solo comando y cada consulta deja una traza. |
| S2 | Script en Python que corre un banco de 20–30 consultas y genera una tabla de resultados. | Corridas repetibles: la misma entrada produce la misma tabla. |
| S3 | **Piloto de 20 consultas** de asesor (unas 4 de abstención) con tres configuraciones: A1-barato, A1-caro y A3-caro. | Tabla con exactitud, costo en USD y latencia p50/p95 por configuración, más el oráculo. |
| S4 | Primera frontera calidad–costo y cálculo del ahorro que capturaría el oráculo. | Gráfico exactitud vs. costo con las configuraciones fijas. |
| S5 | Enrutador por reglas **R0** como primer baseline del router. | R0 comparado contra el aleatorio y el oráculo en el piloto. |

**Métricas registradas por consulta:** configuración usada, costo en USD (por tipo de token, con el juez aparte), latencia p50/p95, número de llamadas a herramientas, calidad (conjunto de referencia + tríada RAG), tipo de abstención y tipología de la consulta.

**Costo estimado del piloto:** menos de US$ 5.

## 4. Próximos pasos después del sprint

1. Ampliar del piloto al conjunto de calibración completo (232) y reentrenar R1 con la etiqueta corregida.
2. Incorporar el enrutador por similitud **R2** (kNN).
3. Agregar el filtro de seguridad (capa 0) y medirlo con el banco adversario.
4. Evaluación final sobre la partición reservada (100), con bootstrap para los intervalos de confianza.
