# Importancia de las variables



## 1. Variable independiente

**Condición de atención** (estrategias A0 a A4; en A4, política de enrutamiento R0, R1 o R2).

Es la variable que se manipula. Permite comparar una misma consulta bajo formas distintas de atención: solo modelo, recuperación documental, recuperación con herramientas, combinación fija, o enrutamiento predictivo. Sin esa variación no se puede contrastar si conviene enrutar o usar siempre la misma estrategia.

## 2. Variables dependientes


| Variable                                       | Por qué importa                                                                                                                                                                                  |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Exactitud                                      | Mide si la respuesta coincide con la respuesta de referencia. Es el criterio básico de calidad.                                                                                                  |
| Fidelidad a fuentes                            | Comprueba que el contenido se sostenga en el documento o dato citado. Evita aceptar respuestas fluidas pero incorrectas.                                                                         |
| Latencia                                       | Tiempo desde que llega la consulta hasta la respuesta. En picos de atención, una mejora de calidad que demora demasiado pierde utilidad.                                                         |
| Costo (USD por consulta)                       | Gasto de uso del modelo. Justifica no enviar todas las consultas por la ruta más cara.                                                                                                           |
| Acierto de ruta                                | En el enrutador: si la estrategia elegida coincide con la esperada para esa consulta. Explica si el ahorro o la calidad vienen de enrutar bien.                                                  |
| Escalamiento correcto                          | Si se deriva al personal administrativo cuando corresponde, y no cuando la consulta podía resolverse en el sistema.                                                                              |
| Bloqueo correcto y falsos positivos del filtro | El filtro previo debe cortar fuera de dominio, manipulación y pedidos no autorizados, sin rechazar de más las consultas válidas. También se observa el efecto del filtro sobre latencia y costo. |


## 3. Relación con el problema

El problema pregunta por el equilibrio entre calidad, latencia y costo. Por eso la exactitud y la fidelidad no bastan solas: hay que reportarlas junto con latencia y costo. El acierto de ruta, el escalamiento y el filtro completan la lectura cuando el sistema decide cómo atender o cuándo no atender en automático.

---



## Señales de la consulta (apoyo al enrutador)

Para elegir la estrategia antes de ejecutar el procedimiento completo se usan señales de la pregunta: longitud y marcas de texto, familia de intención (matrícula, prerrequisitos, pagos, calendario, etc.), si el caso parece personal, y, si ya hubo una búsqueda léxica, la fuerza y el margen del mejor documento.

Esas señales no sustituyen a las variables dependientes de la matriz. Sirven para alimentar la decisión de ruta; lo que se reporta como resultado del estudio sigue siendo exactitud, fidelidad, latencia, costo y, según el caso, acierto de ruta, escalamiento o métricas del filtro.