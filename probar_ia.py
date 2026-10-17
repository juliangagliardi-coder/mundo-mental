"""Prueba de conexión con un servidor local compatible con la API de chat tipo OpenAI.

Uso (con llama-server ya en marcha en el puerto 8080):
    python probar_ia.py

Se pueden cambiar los valores con variables de entorno:
    MUNDO_MENTAL_API_URL, MUNDO_MENTAL_MODELO, MUNDO_MENTAL_API_KEY
"""

from __future__ import annotations

import os
import tempfile
import time

from mundo_mental.razonador import RazonadorHTTP, crear_razonador
from mundo_mental.tierra import crear_tierra

PREGUNTA = "Explica en una frase qué es un recuerdo estable."


def entorno_local() -> dict[str, str]:
    return {
        "MUNDO_MENTAL_API_URL": os.environ.get("MUNDO_MENTAL_API_URL", "http://127.0.0.1:8080/v1"),
        "MUNDO_MENTAL_MODELO": os.environ.get("MUNDO_MENTAL_MODELO", "modelo-local"),
        "MUNDO_MENTAL_API_KEY": os.environ.get("MUNDO_MENTAL_API_KEY", "local"),
    }


def main() -> int:
    razonador = crear_razonador(entorno_local(), max_llamadas=5)
    if not isinstance(razonador, RazonadorHTTP):
        print("No se pudo crear el razonador: faltan variables de entorno.")
        return 2

    print(f"Preguntando a {razonador.config.url_base} ...")
    inicio = time.time()
    texto = razonador.responder(PREGUNTA)
    segundos = time.time() - inicio

    if not texto:
        print(f"Falló: {razonador.ultimo_error or 'respuesta vacía'}")
        print("¿Está abierto llama-server en otra ventana?")
        return 1

    print(f"\nRespuesta ({segundos:.1f} s):\n{texto}\n")

    with tempfile.TemporaryDirectory(prefix="mundo-mental-ia-") as carpeta:
        tierra = crear_tierra(carpeta, razonador)
        print(f"Tierra creada con razonador: {type(tierra.razonador).__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
