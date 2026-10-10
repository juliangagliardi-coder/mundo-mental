# Decisiones arquitectónicas

## ADR-001: Biblioteca como memoria estratificada

La Biblioteca separa memoria episódica, semántica, procedimental y urbanística. Las experiencias originales no desaparecen al consolidar conceptos.

## ADR-002: Curiosidad compuesta

Curiosidad es un Aspecto dentro de la Biblioteca y contiene un Micro-Corazón limitado. Puede gobernar su laboratorio y producir propuestas, pero la recursión de Aspectos termina allí.

## ADR-003: Vida continua por ciclos

El Palacio se ejecutará como servicio persistente, pero cada actividad será un ciclo finito, presupuestado y recuperable.

## ADR-004: Observación reactiva

Observación es un Aspecto independiente compuesto operativamente por un Guardián que normalmente duerme y un Centinela mínimo siempre activo. El Guardián analiza incidentes cerrados; el Centinela comprueba alarmas, latidos, límites y zonas prohibidas.

## ADR-005: Derecho universal de alarma

Todo Aspecto puede despertar al Guardián sin autorización de otro Aspecto. La alarma puede solicitar aislamiento o congelación, pero no utilizarse para ordenar acciones arbitrarias.

## ADR-006: Fronteras, no pensamientos

Observación protege efectos persistentes, cruces entre Aspectos, acciones externas, permisos y promociones. No autoriza cada inferencia ni registra exhaustivamente cada operación interna.

## ADR-007: Copia por sesión mutable

Antes de abrir una zona estable se crea una base recuperable y la sesión trabaja en una rama. Se almacenan diferencias y versiones; no se realiza una copia completa por mutación.

## ADR-008: El tiempo no se borra

Un rollback restaura estado, pero conserva la cronología y evidencia del incidente en un registro separado.

## ADR-009: Identidad protegida

Los Aspectos son entidades arquitectónicas y narrativas: tienen función, perspectiva, principios, relaciones y memoria de sí. Una optimización no puede reducirlos silenciosamente a utilidades intercambiables.

## ADR-010: Consulta antes de cambiar

Viabilidad puede medir y descubrir problemas sin autorización adicional. Toda optimización, complejización, cambio de personalidad, reparto de autoridad o alteración de relaciones se presenta al creador antes de implementarse.

## ADR-011: Viabilidad antes de autonomía

Antes de implementar Curiosidad autónoma u Observación ejecutable se crea una línea base reproducible de tiempo, memoria y crecimiento. Viabilidad 0.1 diagnostica; no optimiza el Palacio.
