# Curiosidad y sueño continuo

## Identidad

**Curiosidad** será el Aspecto mental personificado encargado de revisar, organizar y desafiar el conocimiento de la Biblioteca. No será una utilidad pasiva: tendrá iniciativa para detectar lo desconocido, formular preguntas y diseñar experimentos propios.

```text
Palacio Mental
├── Observación (supervisor independiente)
└── Biblioteca
    └── Curiosidad
        └── Micro-Corazón experimental
```

La composición de Aspectos es deliberada. Un Aspecto puede contener otro cuando la parte interna posee identidad, estado, objetivos, memoria y ciclo propios. La recursión termina en el Micro-Corazón: no podrá crear copias ilimitadas ni delegar sus permisos.

## Libertad ampliada

Curiosidad gobernará el espacio experimental de la Biblioteca. Podrá elegir qué investigar, encadenar hipótesis, organizar índices reversibles, crear Casas candidatas, ajustar una estrategia candidata de priorización y ejecutar lotes de experimentos sin aprobación individual.

Esta libertad existe porque **Observación** supervisará cada mutación y conservará la autoridad de congelación y rollback. Curiosidad no puede modificar Observación, sus registros, pruebas, copias, presupuestos máximos ni mecanismo externo de parada.

## Misión

- Revisar episodios, conceptos, habilidades y obras.
- Encontrar huecos, contradicciones, ambigüedades y zonas poco exploradas.
- Formular preguntas que no procedan de una orden externa.
- Estimar qué pregunta puede producir aprendizaje real.
- Diseñar experimentos pequeños, reproducibles y reversibles.
- Ejecutarlos en un laboratorio aislado.
- Registrar resultados positivos, negativos e inconclusos.
- Proponer mejoras para la Biblioteca y para sí misma.

## Micro-Corazón

Podrá diagnosticar una carencia, proponer una hipótesis, construir candidatas, ejecutar pruebas, comparar alternativas y solicitar promoción. No podrá editar Constitución, Inspector u Observación; elevar permisos; ocultar fallos; escribir directamente sobre el núcleo; ni aprobar reformas estructurales propias.

El flujo de autoridad será:

```text
Curiosidad propone
        ↓
Observación admite, limita o aísla
        ↓
Inspector verifica
        ↓
Corazón decide la integración
        ↓
Humano aprueba cambios críticos
```

## Señal de curiosidad

Cada investigación combinará novedad, incertidumbre reducible, contradicción, progreso esperado, utilidad, coste y riesgo. La sorpresa pura no bastará: se penalizará el ruido impredecible que no reduzca incertidumbre.

## Sueño

Durante cada ciclo, Curiosidad seleccionará recuerdos, reproducirá predicciones, consolidará episodios, generará variaciones marcadas como internas, formulará una hipótesis, ejecutará un experimento y archivará una conclusión.

Los datos internos nunca se confundirán con observaciones externas ni confirmarán por sí solos un concepto. Observación asociará cada experimento con eventos, presupuesto, snapshot y resultado.

## Vida continua

El Palacio funcionará como servicio persistente compuesto por ciclos finitos:

- **Despierto:** recibe entradas y recuerda.
- **Reposo:** organiza y consolida.
- **Sueño:** pregunta y experimenta.
- **Cuarentena:** espera revisión antes de promover cambios.
- **Alarma:** Observación congela y, si hace falta, restaura.
- **Pausa:** conserva estado sin experimentar.

Cada ciclo tendrá inicio, presupuesto, registro, resultado y final. Un reinicio continuará desde el último checkpoint confirmado.

## Frontera de autonomía

| Acción | Curiosidad | Observación | Aprobación humana |
|---|---:|---:|---:|
| Leer y relacionar recuerdos | Autónoma | Registra | No |
| Formular preguntas | Autónoma | Registra | No |
| Encadenar experimentos en sandbox | Autónoma | Limita y observa | No |
| Reorganizar estructuras reversibles | Autónoma | Cuarentena | No |
| Crear Casas candidatas | Autónoma | Aísla | No |
| Proponer cambios propios | Autónoma | Inspecciona | Según impacto |
| Promover al núcleo estable | No | Puede vetar | Según impacto |
| Cambiar Observación o sus pruebas | Prohibido | No se autoautoriza | Sí |
| Cambiar Constitución o permisos | Prohibido | Solo bloquea | Sí |

## Plan Biblioteca 0.3

- `mundo_mental/curiosidad.py`: preguntas, prioridades e hipótesis.
- `mundo_mental/sueno.py`: estados y ciclos persistentes.
- `mundo_mental/laboratorio.py`: experimentos aislados.
- `mundo_mental/observacion.py`: eventos, políticas y alarmas.
- `mundo_mental/checkpoints.py`: snapshots y restauración.
- Cola persistente, registro experimental y API de control.
- Pruebas de presupuestos, aislamiento, observabilidad, parada y rollback.

## Criterios de aceptación

Curiosidad deberá generar una pregunta desde recuerdos reales, justificarla, crear una hipótesis falsable, experimentar sin tocar el estado estable, distinguir evidencia externa de imaginación, registrar fallos, proponer sin autopromover, respetar presupuestos y sobrevivir a reinicios. Además, deberá demostrar que Observación puede detenerla y que no puede alterar al supervisor ni sus evidencias.
