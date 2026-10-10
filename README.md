# Mundo Mental

Un experimento para construir un **palacio mental modular** cuyos Aspectos puedan recordar, investigar, construir, relacionarse y recuperarse sin perder su identidad.

## Abrir el Mundo

```bash
python mundo.py
```

Mundo Virtual 0.1 es un reino medieval fantástico local con terreno físico, cámara, habitantes con coordenadas y actividad visible. Consulta [MUNDO.md](MUNDO.md) para los controles.

También puedes ejecutar el ciclo integrado y todas las pruebas:

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
- **Mundo Virtual 0.1:** terreno medieval fantástico, tránsito visible y habitantes con coordenadas.
- **Viabilidad 0.1:** línea base reproducible de rendimiento; mide sin optimizar.

Consulta [MUNDO.md](MUNDO.md), [BIBLIOTECA.md](BIBLIOTECA.md), [CURIOSIDAD.md](CURIOSIDAD.md), [EVIDENCIA.md](EVIDENCIA.md), [OBSERVACION.md](OBSERVACION.md), [IDENTIDAD.md](IDENTIDAD.md), [VIABILIDAD.md](VIABILIDAD.md), [CONSTITUCION.md](CONSTITUCION.md) y [DECISIONES.md](DECISIONES.md).

## Estado honesto

Biblioteca, Corazón, Calles, Casa de Patrones, Curiosidad, Observación, validador de evidencia y Mundo Virtual tienen prototipos ejecutables. Los Universos de Experimentación siguen siendo la próxima ampliación: separados del mundo estable y sujetos a autorización de Curiosidad.
