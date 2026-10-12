# Mundo Mental

Un experimento para construir un **palacio mental modular** cuyos Aspectos puedan recordar, investigar, construir, relacionarse y recuperarse sin perder su identidad.

## Arquitectura actual

- **Biblioteca 0.2:** memoria episódica, semántica, procedimental y urbanística.
- **Corazón 0.1:** reformas candidatas, inspección y protección de conocimientos.
- **Calles 0.1:** mensajes tipados entre componentes.
- **Curiosidad 0.2:** detecta vacíos, formula preguntas y ejecuta experimentos aislados bajo supervisión.
- **Evidencia validada 0.1:** un validador independiente solo promueve resultados reproducibles y corroborados a Biblioteca.
- **Observación 0.2:** Guardián y Centinela detectan incidencias, aíslan zonas y solo las reanudan mediante señales verificables.
- **Monitor gráfico:** representa en un reino medieval fantástico las llamadas reales del ciclo integrado.
- **Viabilidad 0.1:** línea base reproducible de rendimiento; mide sin optimizar.

Consulta [MUNDO.md](MUNDO.md), [BIBLIOTECA.md](BIBLIOTECA.md), [CURIOSIDAD.md](CURIOSIDAD.md), [EVIDENCIA.md](EVIDENCIA.md), [OBSERVACION.md](OBSERVACION.md), [IDENTIDAD.md](IDENTIDAD.md), [VIABILIDAD.md](VIABILIDAD.md), [CONSTITUCION.md](CONSTITUCION.md) y [DECISIONES.md](DECISIONES.md).

## Abrir el monitor gráfico

El archivo está en la rama del PR #8 hasta que el PR se integre en `main`.

```bash
git fetch origin
git switch evolucion/ciudad-visual-01
```

Después, desde la carpeta que contiene `mundo.py`:

```bash
# Windows
py mundo.py

# macOS o Linux
python3 mundo.py
```

Si `python3 -m tkinter` falla en Debian o Ubuntu, instala el paquete del sistema con `sudo apt install python3-tk`. En Windows y macOS, el instalador oficial de Python normalmente incluye Tkinter.

En la ventana, pulsa **Ejecutar un ciclo**. El programa ejecuta `ejecutar_ciclo` de verdad en un directorio temporal y muestra cada llamada recibida; no reproduce una secuencia inventada. **Trabajar continuamente** repite ciclos reales hasta pulsar **Detener**.

## Probarlo

Solo necesita Python 3.10 o posterior; no requiere librerías externas de Python.

```bash
python iniciar.py
python -m unittest discover -s tests -v
```

La demostración crea memoria local temporal. Esa historia no se sube a GitHub.

## Medir viabilidad

```bash
python benchmarks/viabilidad_01.py --sizes 100 1000 --output viabilidad.json
```

Para una exploración deliberadamente exigente pueden añadirse tamaños mayores. Los resultados dependen de la máquina y no representan inteligencia ni velocidad humana; comparan versiones del mismo Palacio bajo la misma carga.

## Pacto de evolución

Medir, perfilar y detectar problemas está permitido. Antes de implementar cualquier optimización, complejización, modificación de personalidad, cambio de autoridad o alteración de relaciones entre Aspectos se presentará una propuesta al creador. La eficiencia no borrará la personificación: cada Aspecto conservará identidad, perspectiva, principios y memoria de sí.

## Estado honesto

Biblioteca, Corazón, Calles, Casa de Patrones, Curiosidad, Observación y el validador de evidencia tienen prototipos ejecutables. El monitor gráfico observa el ciclo integrado existente: no afirma que Catalogador o Corazón hayan trabajado cuando ese ciclo no los invoca.
