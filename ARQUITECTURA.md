# Arquitectura del núcleo

Cada pieza tiene una responsabilidad que no comparte con las demás.

| Pieza | Responsabilidad | No hace |
|---|---|---|
| `Calles` / `Router` | Relaciones autorizadas y duraderas entre un origen y un destino, con contrato de tipo | No difunde ni interpreta contenido |
| `SistemaNervioso` | Transporta impulsos: temas, prioridad, urgencia, reflejos, reintentos y cuarentena | No decide qué hacer con ellos |
| `TejidoMental` | Registro común de Aspectos y contador de ciclos | No toma decisiones |
| `MotorDeCiclos` | Reloj con estados (`despierto`, `durmiendo`, `pausado`), presupuesto por llamada, `limite_total` acumulado y recuperación tras reinicio | No decide qué hacen los Aspectos |
| `Planificador` | Une Curiosidad y Motor: ejecuta solo experimentos con `Receta` autorizada, registra cada decisión y pide ayuda a Observación tras fallos repetidos | No inventa experimentos ni reanuda zonas por su cuenta |

## Reglas

1. Las Calles son relaciones explícitas; el Sistema Nervioso son impulsos; el Tejido coordina; el Motor da ritmo; el Planificador limita la iniciativa.
2. Ante un estado persistido ilegible, el motor arranca `pausado`, nunca `despierto`.
3. Agotar el presupuesto pausa el motor con el motivo `presupuesto_agotado`; alcanzar `limite_total`, con `limite_total`.
4. Tras `max_fallos` fallos seguidos en un origen, Curiosidad pide ayuda; Observación congela la zona y el Planificador deja de investigarla. Solo `cerrar_y_reanudar` (diagnóstico, verificación aislada, reproducible y sin alarmas críticas abiertas) la reabre.
5. Cuando dos Aspectos discrepan sin regla constitucional suficiente, Observación bloquea solo lo irreversible; lo reversible continúa con registro. Si el caso no está cubierto, se consulta al propietario.
6. No existe capa visual. Cualquier interfaz futura solo podrá leer el registro real de eventos, nunca simular estados propios.
