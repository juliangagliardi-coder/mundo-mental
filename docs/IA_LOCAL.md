# IA local para Mundo Mental (Windows)

El razonador (`mundo_mental/razonador.py`) habla con cualquier servidor compatible con la API de chat tipo OpenAI. Con `llama-server` todo corre en el propio ordenador, sin enviar datos fuera.

## 1. Instalar llama.cpp

```
winget install llama.cpp
```

Cierra la ventana de CMD y abre una nueva para que el PATH se actualice.

## 2. Arrancar el servidor

Modelo pequeño (rápido, español flojo):

```
llama-server -hf Qwen/Qwen2.5-3B-Instruct-GGUF:Q4_K_M --port 8080 -c 4096
```

Modelo mediano (más lento, mejor calidad):

```
llama-server -hf Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M --port 8080 -c 4096
```

Si el servidor falla por la tarjeta gráfica, añade `-ngl 0`. Para usar más hilos del procesador, añade `-t 4` (o el número de núcleos reales).

Deja esa ventana abierta mientras uses Mundo Mental.

## 3. Probar la conexión

En otra ventana de CMD, dentro de la carpeta del proyecto:

```
python probar_ia.py
```

Si responde, la conexión funciona. Si falla, el script indica el motivo (`red`, `http_NNN`, `respuesta_invalida` o `presupuesto_agotado`).

## 4. Variables opcionales

| Variable | Valor por defecto |
|---|---|
| `MUNDO_MENTAL_API_URL` | `http://127.0.0.1:8080/v1` |
| `MUNDO_MENTAL_MODELO` | `modelo-local` |
| `MUNDO_MENTAL_API_KEY` | `local` (el servidor local no la comprueba) |

## Límites conocidos

- Los modelos de 3B cometen errores de concordancia y de sentido en español; conviene pedirles tareas cortas y concretas.
- `iniciar.py` es una demostración con reglas fijas y no usa el razonador. El razonador solo se conecta a Tierra al crearla con `crear_tierra(raiz, razonador)`.
- La licencia del modelo es independiente de la de este repositorio; revísala antes de un uso comercial.
