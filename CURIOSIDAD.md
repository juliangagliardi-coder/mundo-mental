# Curiosidad y sueño continuo

## Identidad

**Curiosidad** será el Aspecto mental personificado encargado de revisar, organizar y desafiar el conocimiento de la Biblioteca. No será una utilidad pasiva: tendrá iniciativa para detectar lo desconocido, formular preguntas y diseñar experimentos propios.

```text
Palacio Mental
└── Biblioteca
    └── Curiosidad
        └── Micro-Corazón experimental
```

La composición de Aspectos es deliberada. Un Aspecto puede contener otro cuando la parte interna posee identidad, estado, objetivos, memoria y un ciclo de decisión propios. La recursión, sin embargo, termina en el Micro-Corazón: no podrá crear copias ilimitadas de sí mismo ni delegar sus permisos.

## Misión

Curiosidad deberá:

- Revisar episodios, conceptos, habilidades y obras.
- Encontrar huecos, contradicciones, ambigüedades y zonas poco exploradas.
- Formular preguntas que no procedan directamente de una orden externa.
- Estimar qué pregunta puede producir aprendizaje real.
- Diseñar experimentos pequeños, reproducibles y reversibles.
- Ejecutarlos únicamente en un laboratorio aislado.
- Registrar resultados positivos, negativos e inconclusos.
- Proponer mejoras para la Biblioteca y para su propio funcionamiento.

## Micro-Corazón

Curiosidad tendrá una versión especializada del Corazón. Su libertad se limita al laboratorio de la Biblioteca.

Podrá:

1. Diagnosticar una carencia de conocimiento.
2. Proponer una hipótesis.
3. Construir una candidata temporal.
4. Ejecutar pruebas protegidas.
5. Comparar candidata y versión estable.
6. Archivar el experimento y solicitar promoción.

No podrá:

- Editar la Constitución.
- Alterar o eliminar las pruebas que la evalúan.
- Aumentar sus propios permisos o presupuestos.
- Escribir directamente sobre el núcleo estable.
- Ocultar experimentos fallidos.
- Acceder a redes, archivos o herramientas no autorizados.
- Aprobar sus propias reformas estructurales.

El Corazón principal seguirá siendo la autoridad urbanística. Curiosidad propone; el Inspector verifica; el Corazón decide; los cambios sensibles esperan aprobación humana.

## Señal de curiosidad

Cada posible investigación recibirá una puntuación formada por:

- **Novedad:** distancia respecto de recuerdos conocidos.
- **Incertidumbre reducible:** desconocimiento que un experimento puede aclarar.
- **Contradicción:** incompatibilidad entre recuerdos o conceptos.
- **Progreso esperado:** posibilidad de mejorar la comprensión, no solo de encontrar sorpresa.
- **Utilidad:** habilidades o decisiones que podrían beneficiarse.
- **Coste:** tiempo, memoria, almacenamiento y computación necesarios.
- **Riesgo:** posibilidad de dañar información, engañar a la evaluación o escapar del laboratorio.

La sorpresa pura no será suficiente. El ruido impredecible produce sorpresa sin conocimiento; Curiosidad deberá favorecer el progreso de aprendizaje y penalizar problemas en los que sus predicciones no mejoran.

## Sueño

El Sueño será el periodo en el que Curiosidad trabaja con la experiencia acumulada sin bloquear las funciones principales del Palacio.

Un ciclo podrá:

1. Seleccionar recuerdos importantes, nuevos, contradictorios o frágiles.
2. Reproducirlos y comparar predicciones con resultados.
3. Consolidar episodios en conceptos.
4. Generar variaciones controladas de ejemplos existentes.
5. Formular una pregunta y una hipótesis falsable.
6. Ejecutar el experimento en el laboratorio.
7. Evaluar aprendizaje, retención, coste y riesgo.
8. Guardar una conclusión y, cuando proceda, una propuesta de obra.

Los datos generados durante el Sueño estarán marcados como **internos**. Nunca se confundirán con observaciones reales, y un concepto no se considerará confirmado únicamente por datos que el propio Palacio inventó.

## Vida continua

El Palacio usará una arquitectura híbrida: un **servicio persistente en segundo plano** compuesto por ciclos finitos y transaccionales.

Estados previstos:

- **Despierto:** atiende entradas, actúa y registra experiencias.
- **Reposo:** ordena, indexa, depura y consolida con bajo consumo.
- **Sueño:** reproduce recuerdos y realiza experimentos internos.
- **Alarma:** detiene trabajos, conserva el registro y restaura el último punto seguro.
- **Pausa:** no aprende ni experimenta, pero permite inspección.

Así podrá vivir indefinidamente mientras disponga de energía y autorización, sin convertirse en un bucle incontrolable. Cada ciclo tendrá inicio, presupuesto, resultado, commit de memoria y final explícitos. Si la máquina se apaga, reanudará desde el último punto confirmado sin repetir una obra a medias.

## Presupuestos y límites

Cada ciclo declarará límites máximos de:

- Tiempo de ejecución.
- CPU y memoria.
- Almacenamiento nuevo.
- Experimentos.
- Profundidad de hipótesis encadenadas.
- Cambios candidatos simultáneos.
- Accesos externos.

El agotamiento de un presupuesto no es un error: provoca una salida limpia y deja el trabajo pendiente en la cola. Existirán pausa inmediata, interruptor de parada, ritmo máximo y ventanas configurables de Sueño.

## Registro experimental

Cada experimento conservará:

```json
{
  "pregunta": "...",
  "origen": ["recuerdo-1", "concepto-2"],
  "hipotesis": "...",
  "prediccion": "...",
  "plan": "...",
  "semilla": 1234,
  "presupuesto": {},
  "resultado": {},
  "conclusion": "confirmada | refutada | inconclusa",
  "aprendizaje": 0.0,
  "riesgo": 0.0,
  "candidata": null
}
```

La semilla, las entradas, las versiones y el entorno permitirán repetir el experimento. Todo cambio tendrá linaje y rollback.

## Frontera de autonomía

| Acción | Autónoma | Requiere Inspector | Requiere aprobación humana |
|---|---:|---:|---:|
| Leer y relacionar recuerdos | Sí | No | No |
| Formular preguntas | Sí | No | No |
| Experimentar en sandbox | Sí | Sí | No |
| Consolidar conceptos reversibles | Sí | Sí | No |
| Proponer una reforma | Sí | Sí | No |
| Cambiar habilidad activa | No | Sí | Según impacto |
| Modificar código de Curiosidad | No | Sí | Sí |
| Cambiar pruebas o Constitución | No | No | Sí |
| Ampliar permisos o acceso externo | No | Sí | Sí |

## Plan para Biblioteca 0.3

- `mundo_mental/curiosidad.py`: preguntas, prioridades e hipótesis.
- `mundo_mental/sueno.py`: máquina de estados y planificador de ciclos.
- `mundo_mental/laboratorio.py`: sandbox y experimentos reproducibles.
- Cola persistente de investigaciones.
- Registro JSONL de experimentos.
- Puntos de control y recuperación tras reinicio.
- API de estado, pausa, reanudación y alarma.
- Pruebas de presupuestos, aislamiento, no duplicación y rollback.

## Criterios de aceptación

Biblioteca 0.3 estará completa cuando Curiosidad pueda:

1. Generar una pregunta a partir de recuerdos reales.
2. Explicar por qué merece ser investigada.
3. Crear una hipótesis falsable.
4. Ejecutar un experimento reproducible sin tocar la mente estable.
5. Distinguir evidencia externa de datos imaginados.
6. Registrar también el fracaso y la incertidumbre.
7. Proponer una mejora sin autopromoverla.
8. Detenerse al agotar su presupuesto.
9. Reanudarse después de un corte sin perder ni duplicar trabajo.
10. Demostrar que no puede alterar Constitución, pruebas ni permisos.
