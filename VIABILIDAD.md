# Viabilidad 0.1

## Objetivo

Viabilidad 0.1 crea una línea base reproducible del Palacio actual. Su propósito es descubrir dónde crecen el tiempo, la memoria y el almacenamiento antes de implementar Guardián, Centinela o Curiosidad autónoma.

Esta fase **mide y diagnostica; no optimiza ni complejiza**. Todo cambio de comportamiento derivado de los resultados se propondrá al creador antes de implementarse.

## Qué mide

El banco inicial registra:

- Tiempo para incorporar episodios en la Biblioteca.
- Tiempo para buscar recuerdos similares.
- Tiempo para consolidar conceptos.
- Tiempo de inferencia de una Casa con distintos números de ejemplos.
- Memoria máxima observada por `tracemalloc`.
- Tamaño persistente de la mente temporal.
- Entorno, versión de Python y parámetros usados.

## Qué no afirma

Los resultados no comparan al Palacio con una persona, no miden creatividad y no demuestran escalabilidad futura. Sirven para comparar versiones del mismo código, bajo el mismo protocolo y en hardware conocido.

## Uso

```bash
python benchmarks/viabilidad_01.py --sizes 100 1000 --output viabilidad.json
```

Los tamaños grandes pueden tardar mucho precisamente porque esta versión conserva intencionadamente los algoritmos actuales. El modo de CI utiliza cargas pequeñas y solo comprueba que el instrumento siga funcionando; no establece umbrales de rendimiento dependientes de la máquina.

## Protocolo

Para comparar dos versiones:

1. Usar la misma máquina y versión de Python.
2. Cerrar cargas ajenas importantes.
3. Ejecutar varias veces y conservar todas las mediciones.
4. Comparar medianas, no una única ejecución.
5. Mantener idénticos tamaños y semilla.
6. Registrar cambios de disco, sistema operativo y configuración.
7. No presentar una mejora hasta medir también exactitud, conservación e identidad.

## Hallazgos que buscará

- Crecimiento lineal, cuadrático o inesperado.
- Relecturas y reescrituras completas.
- Picos de memoria.
- Coste de consolidar con frecuencia.
- Umbral a partir del cual una operación deja de ser interactiva.
- Diferencias entre coste temporal y coste persistente.

## Puertas de consulta

Un resultado puede originar propuestas como índices, SQLite/WAL, lotes, cachés, snapshots incrementales, paralelismo o cambios de representación. Ninguna se aplicará automáticamente. Cada propuesta incluirá:

- Evidencia medida.
- Alternativas, incluida no hacer nada.
- Beneficio esperado y criterio de éxito.
- Complejidad añadida.
- Riesgos de seguridad y pérdida de conocimiento.
- Efecto sobre personalidad e identidad de cada Aspecto.
- Plan reversible y pruebas.

## Criterio de terminación

Viabilidad 0.1 termina cuando el banco puede ejecutarse de forma repetible, exporta resultados legibles por máquinas y la integración continua prueba su funcionamiento. La elección e implementación de optimizaciones pertenece a una fase posterior consultada.
