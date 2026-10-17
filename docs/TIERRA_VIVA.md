# Tierra viva

Tierra late de forma continua sobre el `Tejido` y el `MotorDeCiclos`. Cada Aspecto conectado tiene una
`MenteAspecto` que puede razonar con el modelo local, pero solo cuando la formula de interes esta
indecisa. El modelo nunca cambia identidad, limites ni disposiciones.

## Arranque (Windows)

1. Enciende el servidor local:
   `llama-server -hf Qwen/Qwen2.5-3B-Instruct-GGUF:Q4_K_M --port 8080 -c 4096`
2. En otra consola, desde la raiz del repositorio:
   `python arrancar_tierra.py --latidos 5 --margen 1 --pausa 2`
3. Para detenerla: crea un archivo vacio `.mente\PARAR` o pulsa Ctrl+C.

`--sin-modelo` ejecuta todo con las formulas, sin servidor. `--margen 1` consulta al modelo en cada impulso
(mas lento); el valor por defecto (0.12) solo consulta cuando la formula esta cerca del umbral.

## Que hace cada pieza

- `MotorDeCiclos` lleva el reloj, los limites y la persistencia (`.mente/motor.json`).
- `RepartoRazonamiento` limita los pensamientos del modelo: 1 por latido y por aspecto, 120 por hora.
- `ReflexionTierra` hace que Tierra se plantee una pregunta cuando hay calma, para que el modelo tenga algo que decidir.
- El razonador de decisiones usa `max_tokens=8`; el general, 256. Solo se aceptan servidores `http://127.0.0.1` o `localhost`.

## Limites conocidos

- Solo Tierra esta conectada por ahora. Otros Aspectos se anaden con `tejido.incorporar(...)` antes de `conectar_mentes`.
- No se conecta aun `CicloTierra` (necesita Libro y banco de tareas).
- Con 2 nucleos y un modelo de 3B, cada pensamiento puede tardar decenas de segundos.
