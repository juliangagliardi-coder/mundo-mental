# Mundo Mental

Un experimento para construir un **palacio mental modular** que pueda recordar experiencias, reutilizar habilidades y ampliar su estructura sin destruir lo aprendido.

Esta primera versión es deliberadamente pequeña y genérica. No depende de fútbol, imágenes ni lenguaje. Trabaja con patrones simples para demostrar el ciclo esencial:

1. La **Biblioteca** recuerda experiencias, habilidades y reformas.
2. Una **Casa** aprende una capacidad concreta.
3. Las **Calles** transportan mensajes con contratos claros.
4. El **Corazón** crea un candidato, lo inspecciona y solo lo conserva si mejora sin olvidar lo protegido.

## Probarlo

Solo necesita Python 3.10 o posterior; no requiere librerías externas.

```bash
python iniciar.py
python -m unittest discover -s tests -v
```

La demostración crea una carpeta local `.mente/` con la memoria de ejecución. Esa carpeta no se sube a GitHub porque cada mente debe generar su propia historia.

## Estructura

```text
mundo-mental/
├── CONSTITUCION.md        Reglas que ninguna ampliación puede romper
├── PLANO.json             Mapa inicial de Aspectos, Barrios, Casas y Calles
├── iniciar.py             Primera demostración ejecutable
├── mundo_mental/
│   ├── biblioteca.py      Memoria episódica y archivo de habilidades
│   ├── casa_patrones.py   Primera Casa entrenable
│   ├── calles.py          Mensajes, contratos y rutas
│   └── corazon.py         Construcción, inspección y reversión
└── tests/                 Pruebas de memoria y crecimiento seguro
```

## Estado actual

**Cimiento 0.1:** ya puede recordar, buscar experiencias parecidas, guardar una habilidad, proponer una ampliación, medirla, aceptarla o rechazarla y registrar la decisión.

Todavía no es una mente general ni consciente. Es el primer mecanismo comprobable sobre el que podrán crecer nuevos Aspectos.