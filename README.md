# Mundo Mental

Un experimento para construir un **palacio mental modular** cuyos Aspectos puedan recordar, investigar, construir, relacionarse y recuperarse sin perder su identidad.

## Abrir la Ciudad

```bash
python mundo.py
```

La Ciudad Mental es un visor gráfico local: muestra los Aspectos, edificios, rutas declaradas y actividad reciente. Puede usarse junto a la demostración de ciclo integrado:

```bash
python iniciar.py
python -m unittest discover -s tests -v
```

## Arquitectura actual

- **Biblioteca 0.2:** memoria episódica, semántica, procedimental y urbanística.
- **Corazón 0.1:** reformas candidatas, inspección y protección de conocimientos.
- **Calles 0.1:** mensajes tipados entre componentes.
- **Curiosidad 0.2:** detecta vacíos, formula preguntas y ejecuta experimentos aislados bajo supervisión.
- **Evidencia validada 0.1:** un validador independiente solo promueve resultados reproducibles y corroborados a Biblioteca.
- **Observación 0.2:** Guardián y Centinela detectan incidencias, aíslan zonas y solo las reanudan mediante señales verificables.
- **Ciudad Mental 0.1:** visor gráfico de la ciudad estable, sus habitantes y su actividad.
- **Viabilidad 0.1:** línea base reproducible de rendimiento; mide sin optimizar.

Consulta [CIUDAD.md](CIUDAD.md), [BIBLIOTECA.md](BIBLIOTECA.md), [CURIOSIDAD.md](CURIOSIDAD.md), [EVIDENCIA.md](EVIDENCIA.md), [OBSERVACION.md](OBSERVACION.md), [IDENTIDAD.md](IDENTIDAD.md), [VIABILIDAD.md](VIABILIDAD.md), [CONSTITUCION.md](CONSTITUCION.md) y [DECISIONES.md](DECISIONES.md).

## Pacto de evolución

Medir, perfilar y detectar problemas está permitido. Antes de implementar cualquier optimización, complejización, modificación de personalidad, cambio de autoridad o alteración de relaciones entre Aspectos se presentará una propuesta al creador. La eficiencia no borrará la personificación: cada Aspecto conservará identidad, perspectiva, principios y memoria de sí.

## Estado honesto

Biblioteca, Corazón, Calles, Casa de Patrones, Curiosidad, Observación, validador de evidencia y Ciudad Mental tienen prototipos ejecutables. Los Universos de Experimentación siguen siendo la próxima ampliación: separados de la Ciudad y sujetos a autorización de Curiosidad.
