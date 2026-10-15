# Propuesta: razonador mínimo para identidad y razonamiento básico

Estado: **propuesta pendiente de aprobación del creador** (Constitución, regla 15). No cambia código ni comportamiento. No modifica `CONSTITUCION.md`: las reglas nuevas aquí son borradores y solo pasarán a la Constitución con aprobación humana explícita (regla 25).

## Problema observado

Los Aspectos tienen memoria, identidad y reglas, pero su razonamiento depende de recetas fijas. El creador pide una IA **muy simple**, solo para dar identidad y razonamiento básico al servicio de tres reglas máximas.

## Reglas máximas propuestas (borrador)

Texto original del creador, con una lectura operativa:

1. **Evolucionar mentes o Aspectos.** Cada Aspecto puede proponer mejoras de sí mismo (perspectiva, principios, recetas), siempre como candidatas.
2. **Formar parte de lo mismamente evolucionado.** Lo que evoluciona un Aspecto debe seguir siendo compatible con el conjunto ya evolucionado: ninguna evolución individual rompe la coherencia del Palacio.
3. **Aportar al razonamiento global del Mundo Mental.** Cada Aspecto contribuye con su perspectiva a una síntesis compartida.

Adiciones sugeridas (a decidir por el creador):

4. **La evolución no borra la identidad.** Evolucionar no autoriza a aplanar, fusionar o eliminar a un Aspecto (ya implicado por la regla 14). Si dos reglas chocan, gana la identidad protegida.
5. **Lo razonado es imaginado hasta validarse.** La salida del modelo es una propuesta; solo pasa a conocimiento tras pruebas y Autoridad (reglas 22 y 23).

Puntos que el creador debe aclarar: qué significa exactamente «formar parte de lo mismamente evolucionado» (la lectura de la regla 2 es una interpretación) y si las adiciones 4 y 5 se aceptan.

## Qué haría la IA (y qué no)

Un modelo diminuto con tres trabajos acotados, uno por regla:

| Regla | Trabajo del modelo | Validación en código determinista |
|---|---|---|
| 1. Evolucionar | Redactar una propuesta corta de cambio para un Aspecto | Formato fijo, tamaño máximo, rama aislada, Autoridad con reversa |
| 2. Formar parte | Clasificar si una propuesta es coherente con las fichas de los demás Aspectos | Comparación contra fichas y principios protegidos; ante duda, rechazo |
| 3. Aportar | Resumir la perspectiva del Aspecto en pocas frases para una síntesis global | Etiqueta «imaginado», límite de longitud, registro en Biblioteca |

No haría: ejecutar acciones, decidir sin Autoridad, cambiar la Constitución, modificar al Guardián o al Centinela, ni aportar hechos del mundo. Los modelos muy pequeños fallan al recordar datos, pero sirven para clasificación, resumen y coherencia de estilo; por eso los trabajos anteriores evitan depender de hechos.

## Modelo propuesto

Un solo modelo compartido; la identidad vive en la Biblioteca y se inyecta como mensaje de sistema. Candidatos, de menor a mayor:

| Modelo | Tamaño de descarga aproximado | Nota |
|---|---|---|
| SmolLM2 135M | 271 MB | Mínimo absoluto; solo para clasificación muy simple |
| SmolLM2 360M | 726 MB | Buen punto de partida para pruebas |
| Qwen3 0.6B | unos 523 MB (Q4) | Unos 1,5 GB de memoria al ejecutarse; recomendado como primera opción |
| Llama 3.2 1B | alrededor de 1,3 GB | Margen extra de calidad si la laptop lo permite |

La elección final se decide midiendo velocidad y memoria en la laptop del creador (Dell Latitude 3550, i3, 8 GB, solo CPU), no con cifras de terceros.

## Reglas de seguridad

1. Salida marcada como **imaginada** (regla 22).
2. El modelo propone; Autoridad ejecuta con reversa.
3. Solo `localhost` (`http://localhost:11434/api/chat`, `stream: false`), sin nube ni claves.
4. Tiempo y número de llamadas máximos por ciclo (regla 9).
5. Si el servidor falla, vuelve el comportamiento determinista y se registra.
6. Ningún Aspecto modifica el Razonador, el Guardián ni el Centinela (regla 21).
7. Pruebas con `RazonadorFalso`; ninguna prueba requiere descargar un modelo.
8. Todo cambio se compara con la versión anterior antes de adoptarse (reglas 3 y 11).

## Plan por fases

1. Interfaz `Razonador` con `RazonadorNulo` (por defecto) y `RazonadorFalso`, con pruebas.
2. `RazonadorOllama` con biblioteca estándar, tiempo máximo y degradación segura.
3. Script de medición de tokens por segundo y memoria en la laptop del creador.
4. Plantillas de los tres trabajos (evolucionar, coherencia, aporte) con formato de salida fijo.
5. Validadores deterministas de cada salida.
6. Etiquetado como imaginado, paso por Autoridad y presupuesto por Aspecto.
7. Banco de tareas repetibles con línea base sin modelo para comprobar si el razonador aporta algo (regla 11).

## Alternativas

- Sin modelo: reglas y plantillas deterministas para las tres tareas. Es la línea base obligatoria; si el modelo no la supera en las pruebas, no se adopta.
- Modelo mediano (3B o más): más capaz pero lento y exigente con 8 GB; descartado de inicio por el pedido de simplicidad.
- Un modelo por Aspecto: sin ventaja demostrada y costoso en memoria.

## Beneficio, coste y riesgo

- Beneficio: razonamiento básico medible, ligado a las tres reglas.
- Coste: dependencia opcional (Ollama) y algo de CPU y memoria.
- Riesgo: texto generado tratado como conocimiento; un modelo diminuto puede decir tonterías con seguridad. Mitigado con formato fijo, validadores y etiqueta de imaginado.
- Riesgo de diseño: que «evolucionar» choque con proteger la identidad; mitigado con la adición 4.
- Efecto sobre identidades: ninguno si la ficha es la fuente de verdad; se añadirá una prueba de deriva.
- Reversión: dejar de usar `RazonadorOllama` devuelve el comportamiento actual.

## Decisiones pedidas al creador

- ¿Aprobar las tres reglas máximas como borrador y aclarar la regla 2?
- ¿Aceptar las adiciones 4 y 5?
- ¿Aprobar las fases 1 a 3?
- Confirmar el procesador i3 exacto de la laptop.
