# Evidencia validada

Los resultados de Curiosidad son provisionales. Solo `ValidadorEvidencia`, un componente distinto de Curiosidad y conectado explícitamente a la Biblioteca, puede promover uno a memoria estable.

## Reglas de promoción

- El experimento debe haber terminado con estado `completado`.
- Debe ser reproducible.
- Debe aportarse una corroboración independiente y no nula.
- Toda promoción conserva trazabilidad: identificador de pregunta, nombre del experimento, corroboración y origen `laboratorio_validado`.
- Si una condición falla, se registra un dictamen de rechazo y la Biblioteca no cambia.

La promoción crea un episodio normal de Biblioteca. Por tanto, puede recuperarse, consolidarse y depurarse usando las garantías ya existentes, sin otorgar a Curiosidad permiso directo de escritura.
