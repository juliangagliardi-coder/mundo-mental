# Decisiones arquitectónicas

## ADR-001: Biblioteca como memoria estratificada

La Biblioteca separa memoria episódica, semántica, procedimental y urbanística. Las experiencias originales no desaparecen al consolidar conceptos.

## ADR-002: Curiosidad compuesta

Curiosidad es un Aspecto dentro de la Biblioteca y contiene un Micro-Corazón limitado. Puede gobernar su laboratorio y producir propuestas, pero la recursión de Aspectos termina allí.

## ADR-003: Vida continua por ciclos

El Palacio se ejecutará como servicio persistente, pero cada actividad será un ciclo finito, presupuestado, registrado y recuperable.

## ADR-004: Observación independiente

Observación es un Aspecto de primer nivel y un plano de seguridad separado. Recibe eventos de todos los Aspectos, controla cuarentena, copias y rollback, y puede ordenar la parada absoluta mediante un supervisor externo.

## ADR-005: Libertad proporcional a observabilidad

Curiosidad obtiene mayor libertad únicamente cuando sus acciones son aislables, observables y reversibles. La autonomía no incluye modificar al supervisor, la Constitución, las pruebas protegidas ni los permisos máximos.

## ADR-006: Percepción total como propiedad comprobable

No se afirmará omnisciencia. "Total" significa que toda acción válida atraviesa un punto instrumentado y emite un evento previo. La cobertura se comprueba mediante pruebas, eventos señuelo, secuencias y política de fallo seguro.

## ADR-007: El tiempo no se borra

Un rollback restaura el estado del Palacio a un checkpoint, pero conserva la cronología y evidencia del incidente en un registro separado e inmutable.

## ADR-008: Prevención antes que reparación

Las candidatas permanecen en cuarentena durante el margen que Observación necesita para revisarlas. La restauración se reserva para fallos que hayan cruzado defensas anteriores.
