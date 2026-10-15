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

Consulta BIBLIOTECA.md, CURIOSIDAD.md, EVIDENCIA.md, OBSERVACION.md, IDENTIDAD.md, VIABILIDAD.md, CONSTITUCION.md, DECISIONES.md y docs/AUTORIDAD.md.

## Probarlo

Solo necesita Python 3.10 o posterior; no requiere librerías externas.

```
python iniciar.py
python -m unittest discover -s tests -v
```

La demostración crea `.mente/` con memoria local. Esa historia no se sube a GitHub. La CI ejecuta toda la suite descubierta automáticamente en Python 3.10 a 3.13, además de la demo y los benchmarks de humo.

## Medir viabilidad

```
python benchmarks/viabilidad_01.py --sizes 100 1000 --output viabilidad.json
```

Para una exploración deliberadamente exigente pueden añadirse tamaños mayores. Los resultados dependen de la máquina y no representan inteligencia ni velocidad humana; comparan versiones del mismo Palacio bajo la misma carga.

## Pacto de evolución

Medir, perfilar y detectar problemas está permitido. Antes de implementar cualquier optimización, complejización, modificación de personalidad, cambio de autoridad o alteración de relaciones entre Aspectos se presentará una propuesta al creador. La eficiencia no borrará la personificación: cada Aspecto conservará identidad, perspectiva, principios y memoria de sí.

## Estado honesto

Biblioteca, Corazón, Calles, Casa de Patrones, Curiosidad, Observación, el validador de evidencia y la Autoridad tienen prototipos ejecutables. No hay todavía un bucle autónomo prolongado ni entradas reales del exterior: el ciclo integrado es una demostración supervisada. Viabilidad 0.1 establece primero una línea base; sus mediciones servirán para proponer cambios concretos, no para introducirlos sin consulta.
