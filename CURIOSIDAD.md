# Curiosidad 0.2

Curiosidad convierte vacíos detectables de la Biblioteca en preguntas ordenadas por prioridad. Sus experimentos se ejecutan únicamente en un laboratorio en memoria: sus resultados no escriben ni alteran la Biblioteca, la identidad ni otros Aspectos.

## Ciclo comprobable

1. `observar_conceptos` detecta baja fiabilidad o pocos ejemplos y formula una `Pregunta`.
2. `experimentar` recibe una entrada copiada, por lo que el experimento no puede mutar la entrada de quien lo invoca.
3. Un supervisor opcional decide antes de la ejecución. Si detiene la acción, la función experimental no se invoca.
4. El resultado queda como `ResultadoExperimento` con estado `completado`, `detenido` o `fallido` y se conserva en el laboratorio.
5. La reproducibilidad se comprueba ejecutando de nuevo la función con una copia independiente de la misma entrada.

Un resultado de laboratorio es evidencia provisional, no un recuerdo estable. Cualquier futura promoción a la Biblioteca deberá ser una decisión explícita de otro componente con autoridad para validar conocimiento.
