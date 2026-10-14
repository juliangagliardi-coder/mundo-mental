# Arquitectura del núcleo

Cada pieza tiene una responsabilidad que no comparte con las demás.

| Pieza | Responsabilidad | No hace |
|---|---|---|
| `Calles` / `Router` | Relaciones autorizadas y duraderas entre un origen y un destino, con contrato de tipo | No difunde ni interpreta contenido |
| `SistemaNervioso` | Transporta impulsos: temas, prioridad, urgencia, reflejos, reintentos y cuarentena | No decide qué hacer con ellos |
| `TejidoMental` | Registro común de Aspectos y contador de ciclos | No toma decisiones |
| `MotorDeCiclos` | Reloj con estados (`despierto`, `durmiendo`, `pausado`), presupuesto y recuperación tras reinicio | No decide qué hacen los Aspectos |

## Reglas

1. Las Calles son relaciones explícitas; el Sistema Nervioso son impulsos; el Tejido coordina; el Motor da ritmo.
2. Ante un estado persistido ilegible, el motor arranca `pausado`, nunca `despierto`.
3. Agotar el presupuesto pausa el motor y lo registra con el motivo `presupuesto_agotado`.
4. Cuando dos Aspectos discrepan sin regla constitucional suficiente, Observación bloquea solo lo irreversible; lo reversible continúa con registro. Si el caso no está cubierto, se consulta al propietario.
5. No existe capa visual. Cualquier interfaz futura solo podrá leer el registro real de eventos, nunca simular estados propios.
