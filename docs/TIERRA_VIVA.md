# Tierra viva

Tierra late de forma continua sobre el `Tejido` y el `MotorDeCiclos`. Cada Aspecto conectado tiene una
`MenteAspecto` que puede razonar con el modelo local, pero solo cuando la fórmula de interés está
indecisa. El modelo nunca cambia identidad, límites ni disposiciones.

## Arranque (Windows)

1. Enciende el servidor local:
   `llama-server -hf Qwen/Qwen2.5-3B-Instruct-GGUF:Q4_K_M --port 8080 -c 4096`
2. En otra consola, desde la raíz del repositorio:
   `python arrancar_tierra.py --latidos 60 --margen 3 --pausa 3 --tope-hora 300`
3. Para detenerla: crea un archivo vacío `.mente\PARAR` o pulsa Ctrl+C.

Una tanda de unas decenas de latidos tarda minutos. Una de 500 latidos tardó varias horas con el modelo de 3B, así que conviene empezar con pocos.

## Opciones del lanzador

| Opción | Qué hace |
|---|---|
| `--latidos N` | Número de latidos; 0 (por defecto) = hasta que se cree `PARAR` |
| `--pausa S` | Segundos entre latidos (por defecto 5) |
| `--cada N` | Latidos tranquilos entre ciclos de trabajo (por defecto 3) |
| `--margen M` | 1 = consultar al modelo en cada impulso (más lento); por defecto 0.12, solo cuando la fórmula está cerca del umbral |
| `--tope-hora N` | Máximo de llamadas por hora al modelo para el trabajo autónomo (por defecto 60) |
| `--sin-modelo` | Todo con fórmulas, sin servidor |
| `--sin-trabajo` | Solo reflexión, sin trabajo autónomo |
| `--raiz`, `--url`, `--modelo` | Carpeta de memoria (`.mente`), servidor local y nombre del modelo |
| `--evolucionar RUTA --objetivo "..."` | Opcional y experimental: Tierra pide al modelo un parche y una prueba de mejora para esa ruta, y lo promueve solo si conserva la suite completa y demuestra la mejora |

## Trabajo autónomo

Por defecto, cuando hay calma Tierra lee conceptos de la Biblioteca, intenta resolver las tareas del banco
y adopta lo que mejora sin regresiones, bajo Autoridad y con reversa.

- El banco (`mundo_mental/banco_tareas.py`) tiene 40 tareas con pruebas visibles y ocultas: `TAREAS_BASE` (5),
  `TAREAS_EXTRA` (7), `TAREAS_DIFICILES` (8) y `TAREAS_LOTE2` (20).
- Cada solución adoptada se guarda como ficha verificada en `.mente/trabajo/libro.jsonl`; los ciclos se
  registran en `.mente/trabajo/ciclos.jsonl`.
- Las tareas ya superadas se omiten en los ciclos siguientes; solo se reintentan las pendientes.
- En una ejecución local de 500 latidos con Qwen2.5-3B, Tierra adoptó 36 de las 40 tareas.

## Qué hace cada pieza

- `MotorDeCiclos` lleva el reloj, los límites y la persistencia (`.mente/motor.json`).
- `RepartoRazonamiento` limita los pensamientos del modelo: 1 por latido y por aspecto, 120 por hora.
- `ReflexionTierra` hace que Tierra se plantee una pregunta cuando hay calma, para que el modelo tenga algo que decidir.
- `CicloTierra` ejecuta el trabajo sobre el Libro y el banco de tareas, con Autoridad.
- El razonador de decisiones usa `max_tokens=8`; el general, 256. Solo se aceptan servidores `http://127.0.0.1` o `localhost`.

## Límites conocidos

- Solo Tierra está conectada por ahora. Otros Aspectos se añaden con `tejido.incorporar(...)` antes de `conectar_mentes`.
- Cuando una tarea se le resiste, Tierra repite el mismo intento ciclo tras ciclo: en la prueba de 500 latidos, `fusionar_intervalos`, `segundo_mayor`, `comprimir_texto` y `camel_a_snake` dieron el mismo resultado en los últimos ciclos. No usa el error de la prueba para corregirse ni pasa a otra cosa.
- El registro de ciclos no guarda el código fallido, así que no se puede diagnosticar a posteriori por qué falla una tarea.
- Su único entorno es el banco de tareas: no hay entradas reales del exterior.
- Con un modelo de 3B, cada pensamiento puede tardar decenas de segundos, y las pruebas largas tardan horas.
