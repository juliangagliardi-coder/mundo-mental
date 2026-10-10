# Observación 0.2

Observación protege sin sustituir a los demás Aspectos. El Centinela detecta señales simples y el Guardián abre un incidente de aislamiento o congelación cuando recibe una alarma.

## Reanudación segura

El Guardián solo puede cerrar un incidente y reanudar su zona cuando se cumplen todas estas condiciones, sin excepción por gravedad:

- Hay un diagnóstico escrito.
- Una comprobación aislada confirma que la causa ya no ocurre.
- La comprobación es reproducible.
- No queda ninguna otra alarma crítica o alta sin cerrar en la misma zona.

Cuando falta una condición, el incidente conserva el diagnóstico y las señales evaluadas con estado `aislamiento_mantenido`. Cuando todas se cumplen, queda `cerrado`, conserva la acción final `reanudar` y registra el momento. El Guardián documenta y protege: no crea objetivos ni modifica la Constitución.
