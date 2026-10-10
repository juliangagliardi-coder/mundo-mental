# Mundo Mental

Un experimento para construir un **palacio mental modular** que pueda recordar experiencias, reutilizar habilidades y ampliar su estructura sin destruir lo aprendido.

Esta versión es pequeña y genérica. No depende de fútbol, imágenes ni lenguaje: trabaja con patrones simples para demostrar el ciclo fundamental del sistema.

## Biblioteca 0.2

La Biblioteca actual separa memoria episódica, semántica y procedimental. Valora recuerdos por novedad, sorpresa e importancia; explica por qué recupera cada experiencia; consolida conceptos; fusiona duplicados; protege recuerdos importantes; archiva habilidades anteriores y ofrece al Corazón el historial de reformas.

Consulta [BIBLIOTECA.md](BIBLIOTECA.md) para conocer sus salas y operaciones.

## Probarlo

Solo necesita Python 3.10 o posterior; no requiere librerías externas.

```bash
python iniciar.py
python -m unittest discover -s tests -v
```

La demostración crea `.mente/` con su propia memoria local. Esa historia no se sube a GitHub.

## Estructura

```text
mundo-mental/
├── CONSTITUCION.md
├── BIBLIOTECA.md
├── PLANO.json
├── iniciar.py
├── mundo_mental/
│   ├── biblioteca.py
│   ├── casa_patrones.py
│   ├── calles.py
│   └── corazon.py
└── tests/
```

## Estado

**Cimiento 0.2:** puede recordar, explicar, consolidar, depurar, versionar habilidades, consultar reformas anteriores y decidir si una ampliación debe conservarse.

Todavía no es una mente general ni consciente. Es una base pequeña, comprobable y preparada para recibir nuevos Aspectos.
