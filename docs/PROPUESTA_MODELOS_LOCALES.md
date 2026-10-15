# Propuesta: modelos de IA locales opcionales por identidad

Estado: **propuesta pendiente de aprobación del creador** (Constitución, regla 15). Este documento no cambia código ni comportamiento.

## Problema observado

Los Aspectos tienen memoria, identidad y reglas, pero su capacidad de razonar depende solo de recetas fijas. Recordar, transferir y adaptarse (regla 12) no se pueden demostrar sin algo que razone.

## Propuesta

Añadir una **interfaz opcional de razonamiento** (`Razonador`) con dos implementaciones:

- `RazonadorNulo`: valor por defecto; reproduce el comportamiento actual. Sin red, sin dependencias.
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
7. Las pruebas usan un `RazonadorFalso` determinista; ninguna prueba requiere descargar un modelo.

## Hardware (a confirmar con el creador)

Orientación general de fuentes públicas, no medida en esta máquina:

| Memoria disponible | Tamaño de modelo razonable (cuantización Q4) |
|---|---|
| 8 GB | 3B a 8B |
| 16 GB | 4B a 8B con holgura; 12B a 14B ajustado |
| 32 GB o más | modelos de 27B a 35B con cuantización baja |

Pendiente: RAM, tarjeta gráfica y sistema operativo de la laptop.

## Alternativas

- No hacer nada: el proyecto queda como prototipo de infraestructura.
- Un modelo por identidad: más memoria, sin ventaja demostrada.
- API en la nube: rompe el requisito local y la regla de no depender de terceros.

## Plan por fases (cada una, un mensaje o más)

1. Interfaz `Razonador`, `RazonadorNulo` y `RazonadorFalso` con pruebas.
2. `RazonadorOllama` con tiempo máximo, reintentos acotados y degradación segura.
3. Constructor de mensaje de sistema desde la ficha de identidad.
4. Etiquetado de salida como imaginada y paso por Autoridad.
5. Presupuesto de llamadas por Aspecto y registro de auditoría.
6. Banco de tareas repetibles: recuerdo, transferencia y adaptación, con línea base sin modelo.
7. Comparación candidata contra versión anterior antes de adoptar (reglas 3 y 11).

## Beneficio, coste y riesgo

- Beneficio esperado: primera capacidad real de razonar, medible contra una línea base.
- Coste: una dependencia opcional externa (Ollama) y mayor consumo de memoria al usarla.
- Riesgo principal: tratar texto generado como conocimiento. Mitigado por las reglas 1 y 2 de seguridad.
- Efecto sobre identidades: ninguno si se mantiene la ficha como fuente de verdad; se añadirá una prueba de deriva.
- Reversión: eliminar el uso del `RazonadorOllama` devuelve el comportamiento actual.

## Decisión pedida al creador

- ¿Aprobar la fase 1 y 2? (sí / no / cambios)
- ¿Un modelo compartido o uno por identidad?
- Especificaciones de la laptop para elegir el modelo.
