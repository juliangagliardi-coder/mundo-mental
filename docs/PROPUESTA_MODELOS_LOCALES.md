# Propuesta: modelos de IA locales opcionales por identidad

Estado: **propuesta pendiente de aprobación del creador** (Constitución, regla 15). Este documento no cambia código ni comportamiento.

## Problema observado

Los Aspectos tienen memoria, identidad y reglas, pero su capacidad de razonar depende solo de recetas fijas. Recordar, transferir y adaptarse (regla 12) no se pueden demostrar sin algo que razone.

## Propuesta

Añadir una **interfaz opcional de razonamiento** (`Razonador`) con tres implementaciones:

- `RazonadorNulo`: valor por defecto; reproduce el comportamiento actual. Sin red, sin dependencias.
- `RazonadorFalso`: determinista, solo para pruebas.
- `RazonadorOllama`: llama a un servidor local de Ollama (`http://localhost:11434/api/chat`, `stream: false`) usando solo la biblioteca estándar de Python.

El proyecto sigue sin requerir librerías externas ni Ollama para ejecutar la demo y las pruebas.

## Un modelo, varias identidades

Se recomienda **un único modelo compartido** y no uno por identidad:

- La identidad vive en la Biblioteca (ficha, principios, memoria autobiográfica), no en los pesos del modelo.
- Cada Aspecto recibe su propio mensaje de sistema construido desde su ficha, y su propio historial.
- Cargar varios modelos a la vez multiplica el uso de memoria y no aporta identidad real.
- Un modelo distinto por Aspecto solo se justificaría si una prueba repetible demuestra que mejora una necesidad declarada (regla 1 y regla 11).

## Reglas de seguridad no negociables

1. La salida del modelo se etiqueta como **imaginada**, nunca como evidencia (regla 22).
2. El modelo propone; no ejecuta. Toda acción pasa por Autoridad con reversa.
3. Solo `localhost`. Sin claves ni modelos en la nube.
4. Tiempo máximo por llamada y número máximo de llamadas por ciclo (regla 9).
5. Si el servidor no responde, el Aspecto vuelve al comportamiento determinista y lo registra.
6. Ningún Aspecto puede modificar la configuración del Razonador, del Guardián ni del Centinela (regla 21).
7. Las pruebas usan `RazonadorFalso`; ninguna prueba requiere descargar un modelo.

## Hardware del creador

Declarado por el creador: Dell Latitude 3550, Windows, procesador i3, 8 GB de RAM. No hay tarjeta gráfica dedicada, así que la inferencia será **solo en CPU**.

Pendiente de confirmar: generación exacta del i3. Existen versiones muy distintas del Latitude 3550 (por ejemplo un i3 de 5.ª generación con 2 núcleos y un i3-1315U con 6 núcleos). Se confirma en Windows con Administrador de tareas > Rendimiento > CPU.

Consecuencias de diseño:

- Modelos de **1B a 3B** parámetros con cuantización Q4. Los de 7B u 8B quedan en el límite o por encima.
- Con 8 GB, Windows y otros programas ocupan una parte importante; conviene cerrar aplicaciones al usar el modelo.
- Velocidad esperada baja (unas pocas decenas de tokens por segundo como mucho, y menos con CPU antigua). Por eso el presupuesto de llamadas por ciclo debe ser estricto y las respuestas cortas.
- Una sola llamada a la vez; los Aspectos comparten el modelo por turnos.

Candidatos iniciales (a probar y medir en la máquina real):

| Modelo | Uso previsto |
|---|---|
| Llama 3.2 3B | Opción principal de calidad dentro del límite de memoria |
| Llama 3.2 1B o Qwen3 1.7B | Opción rápida si el 3B resulta lento |

La elección final se decide con una medición propia (tokens por segundo y memoria usada), no con cifras de terceros.

## Alternativas

- No hacer nada: el proyecto queda como prototipo de infraestructura.
- Un modelo por identidad: más memoria, sin ventaja demostrada, inviable con 8 GB.
- API en la nube: rompe el requisito local y la regla de no depender de terceros.
- Ampliar la RAM: opción de hardware a evaluar más adelante si el cuello de botella es memoria.

## Plan por fases (cada una, un mensaje o más)

1. Interfaz `Razonador`, `RazonadorNulo` y `RazonadorFalso` con pruebas.
2. `RazonadorOllama` con tiempo máximo, reintentos acotados y degradación segura.
3. Script de medición de velocidad y memoria en la laptop del creador.
4. Constructor de mensaje de sistema desde la ficha de identidad.
5. Etiquetado de salida como imaginada y paso por Autoridad.
6. Presupuesto de llamadas por Aspecto y registro de auditoría.
7. Banco de tareas repetibles: recuerdo, transferencia y adaptación, con línea base sin modelo.
8. Comparación candidata contra versión anterior antes de adoptar (reglas 3 y 11).

## Beneficio, coste y riesgo

- Beneficio esperado: primera capacidad real de razonar, medible contra una línea base.
- Coste: una dependencia opcional externa (Ollama), uso de memoria y CPU, y respuestas lentas.
- Riesgo principal: tratar texto generado como conocimiento. Mitigado por las reglas de seguridad 1 y 2.
- Riesgo de hardware: que el 3B sea demasiado lento; se mitiga con el modelo de 1B y con presupuestos estrictos.
- Efecto sobre identidades: ninguno si se mantiene la ficha como fuente de verdad; se añadirá una prueba de deriva.
- Reversión: dejar de usar `RazonadorOllama` devuelve el comportamiento actual.

## Decisión pedida al creador

- ¿Aprobar las fases 1 a 3? (sí / no / cambios)
- ¿Confirmar un modelo compartido?
- Generación exacta del procesador i3 (ver arriba).
