# Genoma Vivo

Capa de memoria sobre el Genoma (`mundo_mental/genoma_vivo.py`).

## Memoria por generaciones
- Cada recuerdo tiene categoria, generacion, relevancia, usos y huella (hash del contenido original).
- Una generacion se cierra cada `ciclos_por_generacion` ciclos (`contar_ciclo`) o con `cerrar_generacion`.
- Cada cierre deja un resumen en el Genoma como ancla.

## Que se olvida y que no
- Nunca se olvida: `origen`, `hito`, `biblioteca`, `decision`, `incidente_grave`, `identidad`. Se registran en el Genoma y quedan intactos.
- Se degrada con el tiempo: `incidente`, `contexto`, `detalle`.
  - Tras `generaciones_detalle` (3 por defecto): el contenido pasa a un resumen.
  - Tras `generaciones_olvido` (8 por defecto): el contenido se vacia y solo queda la huella.
- Relevancia: usar (+1) o corroborar (+1.5) un recuerdo lo acerca al umbral de proteccion (3.0). Al alcanzarlo se protege para siempre. Lo no reforzado decae 10% por generacion.

## Autoridad automatica
- `Autoridad` aplica la regla: Observacion veta (bloquea); si permite, Corazon aprueba o rechaza.
- Ante un error de cualquiera de los dos, la propuesta se bloquea. No se consulta a una persona.
- Toda decision queda registrada en el Genoma.

## Vigilante activo
- `VigilanteActivo.vigilar()` audita y repara las replicas.
- Alarma `media` si reparo una replica; `critica` si ninguna replica es recuperable (el Genoma se niega a reconstruir).
- La alarma es un callable: se conecta a Observacion en la integracion siguiente.

## Pendiente
- Conectar `Autoridad` y la alarma a las clases reales de Corazon y Observacion.
- Llamar a `contar_ciclo` desde el motor de ciclos.
- Prueba de larga duracion (miles de ciclos) y tamano del estado del Genoma.
