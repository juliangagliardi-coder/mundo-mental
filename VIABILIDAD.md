# Viabilidad del Palacio Mental

## Principio

Viabilizar no significa aplanar a los Aspectos. El rendimiento computacional y la riqueza de identidad se miden por separado: una mejora no puede borrar voz, memoria autobiográfica, principios, relaciones o tensiones internas.

## Viabilidad 0.1

La primera etapa creó una línea base reproducible y una Biblioteca SQLite/WAL experimental. La implementación estable JSONL se mantuvo intacta para poder comparar ambas rutas.

## Viabilidad 0.2

La segunda etapa incorpora una migración reversible y verificable:

- La Biblioteca de origen nunca se modifica ni se elimina.
- Episodios, identificadores, momentos, metadatos, conceptos y obras conservan su contenido.
- Habilidades, versiones y planos se copian sin sobrescribir conflictos.
- La migración es idempotente: puede repetirse sin duplicar recuerdos u obras.
- Una huella SHA-256 canónica compara origen y destino antes de declarar éxito.
- Biblioteca SQLite incorpora la misma política de depuración que Biblioteca 0.2.
- El Inspector prueba migración, repetición, conservación de identidad y depuración equivalente.

La existencia de esta ruta no promueve todavía SQLite a Biblioteca estable. Primero deben superarse equivalencia funcional, benchmarks repetidos y pruebas de recuperación.

## Siguiente umbral

Viabilidad 0.3 deberá medir varias repeticiones y percentiles, aislar el coste de apertura de conexiones, evaluar ventanas crecientes y probar recuperación tras interrupciones. Ningún resultado será interpretado como mejora de inteligencia: solo como evidencia de coste, escalabilidad y seguridad operacional.
