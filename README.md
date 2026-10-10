# Mundo Mental

Un experimento para construir un **palacio mental modular** que pueda recordar, investigar, ampliar su estructura y recuperarse sin destruir lo aprendido.

Esta versión es pequeña y genérica. Trabaja con patrones simples para demostrar los mecanismos fundamentales.

## Arquitectura actual

- **Biblioteca 0.2:** memoria episódica, semántica, procedimental y urbanística.
- **Corazón 0.1:** reformas candidatas, inspección y protección de conocimientos.
- **Calles 0.1:** mensajes tipados entre componentes.
- **Curiosidad 0.3-plan:** Aspecto interno que gobernará experimentos y preguntas propias.
- **Observación 0.3-plan:** supervisor independiente con eventos, cuarentena, parada y rollback.

Consulta [BIBLIOTECA.md](BIBLIOTECA.md), [CURIOSIDAD.md](CURIOSIDAD.md), [OBSERVACION.md](OBSERVACION.md), [CONSTITUCION.md](CONSTITUCION.md) y [DECISIONES.md](DECISIONES.md).

## Probarlo

Solo necesita Python 3.10 o posterior; no requiere librerías externas.

```bash
python iniciar.py
python -m unittest discover -s tests -v
```

La demostración crea `.mente/` con memoria local. Esa historia no se sube a GitHub.

## Estado honesto

Biblioteca, Corazón, Calles y la Casa de patrones tienen un primer prototipo ejecutable. Curiosidad y Observación están diseñadas, pero todavía no implementadas. El próximo incremento construirá primero el contrato de eventos y Observación mínima; solo entonces se ampliará la autonomía ejecutable de Curiosidad.
