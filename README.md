# Mundo Mental

Un experimento para construir un **palacio mental modular** cuyos Aspectos puedan recordar, investigar, construir, relacionarse y recuperarse sin perder su identidad.

## Arquitectura actual

- **Biblioteca 0.2:** memoria episódica, semántica, procedimental y urbanística.
- **Corazón 0.1:** reformas candidatas, inspección y protección de conocimientos.
- **Calles 0.1:** mensajes tipados entre componentes.
- **Curiosidad 0.2:** detecta vacíos, formula preguntas y ejecuta experimentos aislados bajo supervisión.
- **Evidencia validada 0.1:** un validador independiente solo promueve resultados reproducibles y corroborados a Biblioteca.
- **Observación 0.2:** Guardián y Centinela detectan incidencias, aíslan zonas y solo las reanudan mediante señales verificables.
- **Autoridad 0.1:** no existen acciones irreversibles. Cada acción se ejecuta con reversa, las zonas protegidas se bloquean y los desacuerdos entre Aspectos quedan como deuda anotada. Las reformas del Corazón y la validación de evidencia del ciclo integrado pasan por ella.
- **Viabilidad 0.1:** línea base reproducible de rendimiento; mide sin optimizar.
- **Tierra viva:** el primer Aspecto con vida continua. Late sobre el Tejido, razona con un modelo local solo cuando la fórmula de interés está indecisa y, cuando hay calma, trabaja sola resolviendo las tareas del banco bajo Autoridad. Ver docs/TIERRA_VIVA.md.

Consulta BIBLIOTECA.md, CURIOSIDAD.md, EVIDENCIA.md, OBSERVACION.md, IDENTIDAD.md, VIABILIDAD.md, DECISIONES.md, docs/AUTORIDAD.md, docs/TIERRA_VIVA.md, docs/RAZONADOR.md y docs/IA_LOCAL.md.

## Probarlo

La demostración solo necesita Python 3.10 o posterior; no requiere librerías externas.

```
python iniciar.py
python -m unittest discover -s tests -v
```

La demostración crea `.mente/` con memoria local. Esa historia no se sube a GitHub. La CI ejecuta toda la suite descubierta automáticamente en Python 3.10 a 3.13, además de la demo y los benchmarks de humo.

## Lanzar Tierra viva

Tierra usa un modelo local (por ejemplo Qwen2.5-3B con llama.cpp). Solo acepta servidores en `127.0.0.1` o `localhost`.

```
llama-server -hf Qwen/Qwen2.5-3B-Instruct-GGUF:Q4_K_M --port 8080 -c 4096
python arrancar_tierra.py --latidos 60 --margen 3 --pausa 3 --tope-hora 300
```

Para detenerla, crea un archivo vacío `.mente\PARAR` o pulsa Ctrl+C. Con `--sin-modelo` funciona solo con fórmulas, sin servidor, y con `--sin-trabajo` solo reflexiona.

Lo que Tierra aprende queda en `.mente/trabajo/libro.jsonl` (una ficha verificada por cada solución adoptada) y el registro de ciclos en `.mente/trabajo/ciclos.jsonl`.

### Banco de tareas

El banco tiene 20 tareas de programación, cada una con pruebas visibles y ocultas: 5 básicas, 7 extra y 8 difíciles. Tierra solo adopta una solución si pasa las pruebas y no empeora lo ya adoptado. En una ejecución local con Qwen2.5-3B adoptó 19 de las 20 tareas; la que quedó sin resolver fue `fusionar_intervalos`.

## Medir viabilidad

```
python benchmarks/viabilidad_01.py --sizes 100 1000 --output viabilidad.json
```

Para una exploración deliberadamente exigente pueden añadirse tamaños mayores. Los resultados dependen de la máquina y no representan inteligencia ni velocidad humana; comparan versiones del mismo Palacio bajo la misma carga.

## Pacto de evolución

Medir, perfilar y detectar problemas está permitido. Antes de implementar cualquier optimización, complejización, modificación de personalidad, cambio de autoridad o alteración de relaciones entre Aspectos se presentará una propuesta al creador. La eficiencia no borrará la personificación: cada Aspecto conservará identidad, perspectiva, principios y memoria de sí.

## Estado honesto

Biblioteca, Corazón, Calles, Casa de Patrones, Curiosidad, Observación, el validador de evidencia, la Autoridad y Tierra viva tienen prototipos ejecutables. Tierra ya tiene un bucle autónomo con trabajo verificable, pero solo se ha probado en ejecuciones cortas (decenas de latidos): no hay todavía una prueba prolongada de horas. Su único entorno es el banco de tareas; no hay entradas reales del exterior, y solo Tierra está conectada como Aspecto con vida propia. La evolución de código (`--evolucionar`) existe como opción experimental y no se ha usado de forma rutinaria. Viabilidad 0.1 establece una línea base; sus mediciones servirán para proponer cambios concretos, no para introducirlos sin consulta.
