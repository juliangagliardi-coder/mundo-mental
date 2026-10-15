# Propuesta de consulta: Aspecto Tierra

Estado: **candidata, solo documentacion**. No cambia ningun comportamiento. Segun la Constitucion (reglas 1, 2, 15 y 25) nada de lo descrito aqui se implementa en codigo hasta que el creador lo apruebe.

## Problema observado

El Mundo Mental no tiene un nucleo que impulse la evolucion de los Aspectos y la suya propia. La IA debe ser el corazon del sistema, pero con hardware limitado (2 nucleos, 8 GB de RAM) y sin depender de servicios externos.

## Propuesta

Crear el Aspecto **Tierra**, con identidad propia, guiado por tres reglas maximas: evolucionar mentes o aspectos, volverse parte de lo evolucionado, y contribuir al razonamiento global del mundo.

Tierra se compone de **roles**, no necesariamente de modelos separados:

| Rol | Funcion | Necesita modelo |
|---|---|---|
| Analista | Resume el estado del mundo | No siempre: reglas y estadisticas; el modelo solo redacta |
| Lectora | Indexa conocimiento de programacion (el Libro) | No: busqueda por texto y significado |
| Internalizadora | Convierte lo leido en fichas verificadas | Parcialmente |
| Programadora | Propone cambios de codigo usando el Libro | Si, con adaptador LoRA periodico |
| Controladora | Orquesta, mide curiosidad y reparte razonamiento a los Aspectos | Si, apoyada en reglas |

La **curiosidad** se mide como senal (novedad, sorpresa, fallos, zonas sin probar); el modelo solo formula la pregunta.

## Motor local

- Programa llama.cpp con binarios ya compilados, escuchando solo en 127.0.0.1.
- Modelo inicial: Qwen2.5-Coder 1.5B (licencia Apache 2.0).
- El motor y los pesos viven fuera del repositorio (limite de 100 MiB por archivo); se documenta como obtenerlos.
- El modelo 3B de la misma familia usa la licencia Qwen-Research (no comercial): queda solo como candidato.
- Los roles quedan tras una misma interfaz para poder cambiar de modelo o usar reglas.

## Alternativas consideradas

1. Varios modelos independientes: no aporta velocidad con 2 nucleos y consume memoria.
2. Entrenar modelos grandes en el equipo: inviable en CPU.
3. Servicios en la nube: descartado por el creador.
4. Ollama: descartado por el creador; se prefiere control directo.

## Beneficio esperado

Un nucleo que trabaja de forma continua en local, reutiliza el Libro y la memoria de fracasos y mejora con cada ciclo sin cuotas ni costes por uso.

## Coste

Memoria (aprox. 1 GB para el modelo), tiempo de CPU compartido por turnos y mantenimiento del Libro. La velocidad real en el equipo del creador esta por medir.

## Riesgos

- Un modelo pequeno puede proponer mal: todo pasa por el verificador.
- Tierra podria favorecerse a si misma: las pruebas protegidas quedan fuera de su alcance (regla 25).
- La licencia Qwen-Research del 3B limita usos comerciales.
- Hay informacion contradictoria sobre cambiar adaptadores LoRA en caliente; se comprobara en la version usada.

## Efecto sobre las identidades

Tierra no modifica la identidad de ningun Aspecto (reglas 13 y 14). Solo propone; los cambios identitarios se consultan al creador (regla 15). Tierra no puede tocar al Guardian, al Centinela ni al freno externo (regla 21).

## Pruebas

- Pruebas de contrato de cada rol y de la interfaz del modelo.
- Banco de tareas pequenas con pruebas ocultas para medir mejora frente a la version anterior (regla 3).
- Comprobacion de procedencia: lo imaginado se separa de la evidencia (regla 22).
- Prueba de que Tierra no puede escribir en pruebas protegidas ni en la Constitucion.

## Reversion

Todo vive en ramas aisladas (regla 19). Descartar la rama deja el Palacio intacto. El motor y los pesos no forman parte del repositorio.

## Fases propuestas

1. Cimientos y contratos de roles, sin modelo.
2. Tierra con reglas deterministas y senal de curiosidad.
3. El Libro: fichas con ejemplo, prueba, procedencia y licencia.
4. Banco de tareas y linea base.
5. Motor local y medicion de velocidad.
6. Tierra con modelo, siempre tras el verificador.
7. Aprendizaje periodico (LoRA) con ejemplos verificados.
8. Autoevolucion acotada con revision humana en las fusiones.

## Decision que se solicita al creador

Aprobar la fase 1 y 2 (sin modelo) como candidata. Las fases siguientes se consultaran al llegar a ellas.
