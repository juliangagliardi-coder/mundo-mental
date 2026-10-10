# Sistema Nervioso 0.1

El Sistema Nervioso es la infraestructura común que permite que el Palacio sienta su propio estado, comparta hallazgos y coordine Aspectos sin convertir cada comunicación en una alarma ni bloquear al emisor.

## Principios

1. **Difusión no es atención.** Un impulso puede llegar a todos, pero cada Aspecto decide desde su identidad si merece atención.
2. **Publicar no espera.** El emisor deposita el impulso y continúa; cada receptor trabaja durante latidos con presupuesto finito.
3. **Los reflejos son mínimos.** Solo acciones simples y previamente registradas pueden ejecutarse inmediatamente.
4. **La urgencia no equivale a verdad.** Afecta al orden de entrega, no a la credibilidad.
5. **La saturación es visible.** Las bandejas son limitadas y contabilizan lo descartado; los impulsos urgentes desplazan los menos valiosos.
6. **Una identidad no es una suscripción.** Los temas filtran el tránsito; la decisión final pertenece al Aspecto.
7. **El sistema nervioso no gobierna.** Transporta, regula y mide; no inventa propósitos.

## Anatomía

- **Impulso:** unidad inmutable con origen, tipo, temas, importancia, urgencia, destino opcional y correlación.
- **Nervios:** suscripciones que conducen impulsos hacia bandejas independientes.
- **Bandejas:** memoria de trabajo acotada de cada Aspecto.
- **Latido:** turno justo y finito de procesamiento.
- **Atención:** valoración local realizada desde perspectiva, disposiciones e intereses del receptor.
- **Reflejo:** reacción mínima que no espera interpretación profunda.
- **Estadísticas:** publicados, duplicados, entregados, atendidos, ignorados, saturación y reflejos.

## Flujo

```text
Aspecto publica un impulso
          |
          +--> reflejo registrado (solo si existe)
          |
          +--> bandejas de suscriptores
                         |
                   siguiente latido
                         |
              cada identidad valora
                   /             \
              atiende           ignora
```

## Coste

La publicación cuesta en función del número de suscriptores, no del tamaño de sus pensamientos. Ningún receptor lento detiene al emisor ni a los demás. Los latidos limitan el trabajo por Aspecto y permiten medir la presión antes de introducir concurrencia real.

## Evolución prevista

La versión 0.1 es deliberadamente determinista y usa memoria local. Futuras capas podrán añadir persistencia, reintentos, grupos de consumo y procesos separados sin cambiar el contrato `Impulso -> atención -> Reacción`. Primero se medirán latencia, saturación, justicia y calidad de atención.
