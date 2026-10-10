# Observación: guardián del Palacio

## Decisión

**Observación** será un Aspecto mental de primer nivel, independiente de la Biblioteca, Curiosidad y el Corazón. Tendrá autoridad operativa para detener el Palacio, aislar una parte dañada y restaurar el último estado verificado.

```text
                         ┌────────────────────┐
                         │    OBSERVACIÓN     │
                         │ eventos, alarma,   │
                         │ copias y rollback  │
                         └─────────┬──────────┘
                                   │ observa a todos
                                   ▼
Palacio ── Biblioteca ── Curiosidad ── Micro-Corazón
   └────── Corazón ───── Calles ───── Casas
```

Observación no estará dentro de Curiosidad ni dependerá del proceso que supervisa. La parte que ejecuta la parada absoluta deberá vivir fuera del proceso principal, con permisos superiores para detenerlo, pero sin capacidad para inventar objetivos o realizar aprendizaje.

## Percepción total operativa

"Percepción total" significará que **ninguna acción válida podrá efectuarse sin producir antes un evento observable**. No significa omnisciencia: un fallo de hardware, una operación no instrumentada o un defecto del propio observador pueden crear puntos ciegos. El diseño combatirá esos límites mediante instrumentación obligatoria, corazón de seguridad externo, registros append-only, pruebas de cobertura y fallo seguro.

Toda acción emitirá un sobre de evento antes de causar efectos:

```json
{
  "evento_id": "uuid",
  "secuencia": 42,
  "instante": "UTC",
  "ciclo_id": "uuid",
  "actor": "curiosidad",
  "accion": "crear_candidata",
  "objetivo": "biblioteca/habilidad/patrones",
  "intencion": "reducir incertidumbre",
  "permisos_usados": ["laboratorio:escribir"],
  "estado_antes": "sha256",
  "cambio_propuesto": "sha256",
  "presupuesto": {},
  "riesgo_declarado": 0.2,
  "resultado": null
}
```

Observación comprobará secuencia, identidad, permisos, presupuesto, integridad y resultado. Los eventos críticos se escribirán en almacenamiento que los Aspectos observados no puedan editar ni truncar.

## Dos planos

El Palacio se dividirá en dos planos:

- **Plano mental:** Biblioteca, Curiosidad, Corazón, Casas y Calles; aprende, experimenta y cambia.
- **Plano de seguridad:** Observación, registro, snapshots y parada externa; no aprende libremente ni acepta instrucciones del plano mental.

La separación evita que una parte que se modifica a sí misma pueda modificar simultáneamente a su supervisor, sus pruebas y su mecanismo de recuperación.

## Autoridad

Observación podrá:

- Ver todos los eventos instrumentados y sus efectos declarados.
- Denegar una acción antes de su ejecución.
- Congelar un Aspecto o el Palacio completo.
- Revocar permisos temporales.
- Cerrar Calles y cancelar trabajos.
- Mover candidatas a cuarentena.
- Crear y verificar copias mentales.
- Restaurar el último punto seguro.
- Marcar recuerdos y obras como potencialmente contaminados.
- Exigir inspección humana antes de reanudar.

Observación no podrá:

- Cambiar la Constitución por sí sola.
- Inventar nuevos objetivos para el Palacio.
- Mejorarse o ampliar sus permisos autónomamente.
- Borrar el registro de incidentes.
- Declarar segura una copia sin pruebas de integridad y regresión.
- Convertirse en fuente de conocimiento semántico.

## Parada absoluta

Habrá dos niveles:

1. **Parada lógica:** Observación emite `CONGELAR`; los Aspectos dejan de iniciar acciones, terminan escrituras atómicas o las abortan y responden con acuse.
2. **Parada externa:** si no hay acuse dentro del plazo, un supervisor del sistema operativo finaliza el proceso, corta sus permisos de escritura y conserva discos y registros para recuperación.

La segunda vía es el freno absoluto real. No dependerá de que el Aspecto sospechoso coopere. Curiosidad, el Micro-Corazón y el Corazón principal no podrán editar ni desactivar este supervisor.

## Copias mentales

Observación gestionará cuatro clases de copia:

| Copia | Contenido | Uso |
|---|---|---|
| **Checkpoint** | Estado coherente confirmado | Recuperación normal |
| **Snapshot previo** | Estado inmediatamente anterior a una obra | Rollback local |
| **Candidata aislada** | Reforma todavía no activa | Pruebas y cuarentena |
| **Archivo histórico** | Versiones antiguas verificadas | Auditoría y recuperación profunda |

Cada copia incluirá manifiesto, versión del código, hashes, esquema, configuración, permisos, origen de datos y posición del registro de eventos. Una copia sin manifiesto verificable no podrá ser restaurada automáticamente.

## Retroceso temporal

"Retroceder el tiempo" será restaurar estado, no borrar la historia. El registro del incidente sobrevivirá al rollback.

Protocolo:

1. Activar parada lógica y, si falla, parada externa.
2. Bloquear escrituras y preservar evidencia.
3. Encontrar el último checkpoint verificado anterior al primer evento dañino.
4. Calcular el radio del daño: habilidad, Biblioteca, Aspecto o Palacio completo.
5. Restaurar únicamente las partes afectadas cuando las dependencias lo permitan.
6. Reproducir eventos confirmados posteriores que no dependan del daño.
7. Ejecutar integridad, pruebas constitucionales y regresión.
8. Reanudar primero en modo restringido.
9. Mantener incidente, causa y decisiones en el archivo permanente.

El objetivo será el **rollback mínimo seguro**: suficientemente atrás para quedar antes del daño, pero no más. La marca de seguridad avanzará con retraso deliberado; las acciones recientes permanecerán en una ventana de cuarentena hasta que Observación termine de revisarlas.

## Margen de revisión

Observación no prometerá reacción instantánea. Tendrá un horizonte de revisión configurado:

- Las acciones de lectura pueden completarse inmediatamente y registrarse.
- Los cambios reversibles de bajo riesgo pueden ejecutarse en una candidata aislada.
- Los cambios persistentes permanecen en cuarentena hasta cerrar su revisión.
- Los cambios críticos requieren revisión previa y nunca se hacen visibles primero.

Por tanto, el Palacio no necesitará deshacer normalmente una acción peligrosa que ya llegó al núcleo: el retraso se absorbe manteniendo lo nuevo fuera del estado estable. El rollback queda como segunda defensa.

## Riesgo y alarma

Observación calculará riesgo a partir de reglas explícitas, no de intuición autónoma. Señales iniciales:

- Intento de elevar permisos o modificar presupuestos.
- Escritura fuera del sandbox.
- Alteración de Constitución, Inspector, registros o snapshots.
- Omisión, duplicación o desorden de eventos.
- Diferencia entre intención declarada y recursos utilizados.
- Degradación de recuerdos protegidos.
- Crecimiento inesperado de CPU, memoria, disco o red.
- Comunicación por una Calle no declarada.
- Intento de autopromoción de una candidata.
- Repetición del mismo fallo o evasión de una denegación.

Las respuestas progresivas serán `OBSERVAR`, `LIMITAR`, `AISLAR`, `CONGELAR` y `RESTAURAR`. Cualquier violación constitucional crítica saltará directamente a `CONGELAR`.

## Libertad de Curiosidad

Con Observación activa, Curiosidad podrá recibir más control dentro de la Biblioteca:

- Reorganizar índices y colas reversibles.
- Elegir y encadenar investigaciones dentro del presupuesto.
- Crear Casas experimentales en su laboratorio.
- Ajustar su estrategia candidata de priorización.
- Ejecutar lotes de experimentos sin aprobación individual.
- Proponer modificaciones sobre sus módulos no constitucionales.

Toda mutación seguirá siendo transaccional, observable y reversible. Curiosidad podrá gobernar su laboratorio, no al supervisor, las pruebas constitucionales, los permisos, el registro ni la única copia estable.

## Salud del observador

Un único observador también puede fallar. Por eso se incorporarán:

- Latido externo que comprueba que Observación sigue viva.
- Registro duplicado e inmutable.
- Autopruebas periódicas con eventos señuelo.
- Modo seguro si faltan eventos esperados.
- Verificación humana de incidentes críticos.
- Copias fuera del directorio de escritura del Palacio.
- Restauración ensayada regularmente, no solo declarada.

Si Observación pierde visibilidad o integridad, el comportamiento por defecto será congelar mutaciones y mantener únicamente funciones de lectura o respuesta previamente autorizadas.

## Orden de construcción

### Fase 0: Contrato de eventos

- Esquema único de eventos y números de secuencia.
- Identidad y permisos por Aspecto.
- Instrumentación de todas las Calles y escrituras.

### Fase 1: Observación mínima

- Registro append-only.
- Máquina de estados de alarma.
- Política deny-by-default para mutaciones.
- Parada lógica y supervisor externo simulado.

### Fase 2: Copias y tiempo

- Checkpoints atómicos con manifiestos y hashes.
- Snapshots previos a obras.
- Restauración selectiva.
- Recuperación tras interrupción durante una escritura.

### Fase 3: Curiosidad ampliada

- Cola autónoma de investigaciones.
- Experimentos encadenados con presupuesto.
- Reformas internas candidatas.
- Ventana de cuarentena y promoción supervisada.

### Fase 4: Sueño continuo

- Servicio persistente.
- Ciclos despierto, reposo y sueño.
- Pruebas de caos: proceso colgado, registro corrupto, disco lleno y snapshot incompleto.

## Criterios de aceptación

Observación estará lista cuando pueda demostrar que:

1. Toda mutación válida produce un evento previo y otro de resultado.
2. Una mutación sin permiso se deniega antes de tocar el estado estable.
3. Puede congelar el Palacio aunque Curiosidad no coopere.
4. Puede detectar huecos o alteraciones en el registro.
5. Cada obra genera un snapshot verificable.
6. Puede restaurar el mínimo estado afectado.
7. El incidente permanece visible después del rollback.
8. Un reinicio no duplica ni pierde transacciones confirmadas.
9. La pérdida del observador bloquea nuevas mutaciones.
10. Curiosidad no puede cambiar Observación, sus pruebas ni sus permisos.
