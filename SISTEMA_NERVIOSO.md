# Sistema Nervioso 0.2

El Sistema Nervioso es el tejido común que permite que el Palacio comparta hallazgos, coordine Aspectos y contenga fallos sin convertir cada comunicación en alarma ni conceder autoridad al transporte.

## Principios

1. **Difusión no es atención.** El mismo impulso llega a varias identidades, pero cada una explica por qué lo atiende o ignora.
2. **Publicar no espera.** El emisor deposita el impulso; cada receptor trabaja durante latidos con presupuesto finito.
3. **Urgencia no es verdad.** Solo modifica el orden de entrega.
4. **Los reflejos son mínimos y falibles.** Un reflejo defectuoso queda contabilizado y no rompe la publicación.
5. **El fallo se contiene.** Un receptor puede reintentarse y, después del límite, su impulso queda en cuarentena.
6. **La pausa no es olvido.** Un Aspecto puede cerrar temporalmente sus párpados y conservar su bandeja.
7. **La saturación es visible.** Las colas son limitadas y su presión puede inspeccionarse.
8. **El Sistema Nervioso no gobierna.** Transporta, regula y mide; no decide propósitos ni modifica identidades.

## Anatomía

- **Impulso:** unidad inmutable con origen, tipo, temas, importancia, urgencia, canal, destino, causa, correlación, caducidad y ruta.
- **Nervios:** suscripciones que conducen impulsos hacia bandejas independientes.
- **Bandejas:** memoria de trabajo acotada de cada Aspecto.
- **Latido:** turno justo y finito de procesamiento.
- **Atención:** valoración local, explicable y dependiente de identidad.
- **Reflejo:** reacción mínima que no espera interpretación profunda.
- **Cuarentena:** registro de entregas que continuaron fallando después de sus reintentos.
- **Tejido Mental:** registro y reloj que incorpora Aspectos sin interpretar por ellos.

## Flujo

```text
Aspecto publica un impulso
          |
          +--> reflejo aislado, si existe
          |
          +--> bandejas de suscriptores
                         |
                   siguiente latido
                         |
              cada identidad valora
                   /             \
              atiende           ignora
                  |
          puede emitir respuesta
                  |
        conserva causa y correlación
```

## Prioridad y presión

Las bandejas ordenan primero por urgencia, después por importancia y finalmente por antigüedad. Si una bandeja está llena, un impulso nuevo solo desplaza a otro cuando es objetivamente más prioritario. Tanto el desplazamiento como la caducidad se contabilizan.

## Fallos

Los receptores no comparten destino de fallo. Una excepción no detiene a otros Aspectos: el impulso espera al siguiente latido hasta agotar su presupuesto de reintentos y luego entra en cuarentena con metadatos diagnósticos, no con una falsa interpretación.

## Trazabilidad

`Impulso.derivar` conserva causa, correlación y ruta. `SistemaNervioso.trazar` permite reconstruir una conversación causal sin obligar a que todos los Aspectos compartan estado interno.

## Límites actuales

La versión 0.2 sigue siendo determinista y local. La persistencia de bandejas, los procesos separados y la distribución pertenecen a iteraciones posteriores. La identidad mutable de cada Aspecto sí se conserva ya mediante escritura atómica, separada de su autobiografía append-only.
