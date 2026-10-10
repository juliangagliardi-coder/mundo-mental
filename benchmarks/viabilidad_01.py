"""Viabilidad 0.1: línea base reproducible, sin optimizaciones."""

from __future__ import annotations

import argparse
import json
import platform
import random
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mundo_mental.biblioteca import Biblioteca
from mundo_mental.casa_patrones import CasaPatrones


def _patron(indice: int, longitud: int = 16) -> list[int]:
    return [((indice * 17) + (posicion * 7) + (indice >> (posicion % 5))) % 2 for posicion in range(longitud)]


def _tamano_directorio(ruta: Path) -> int:
    return sum(archivo.stat().st_size for archivo in ruta.rglob("*") if archivo.is_file())


def _medir(funcion: Any) -> tuple[Any, float, int]:
    tracemalloc.start()
    inicio = time.perf_counter()
    resultado = funcion()
    segundos = time.perf_counter() - inicio
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return resultado, segundos, pico


def medir_tamano(tamano: int, semilla: int = 2026) -> dict[str, Any]:
    random.seed(semilla)
    with tempfile.TemporaryDirectory(prefix="palacio-viabilidad-") as temporal:
        raiz = Path(temporal) / ".mente"
        biblioteca = Biblioteca(raiz)

        def incorporar() -> None:
            for indice in range(tamano):
                entrada = _patron(indice)
                esperado = f"concepto-{indice % 8}"
                biblioteca.recordar(
                    entrada,
                    esperado,
                    esperado,
                    True,
                    {"confianza": 0.8, "benchmark": True},
                )

        _, incorporar_s, incorporar_pico = _medir(incorporar)
        _, buscar_s, buscar_pico = _medir(
            lambda: biblioteca.buscar_similares(_patron(tamano // 2), limite=5)
        )
        conceptos, consolidar_s, consolidar_pico = _medir(
            lambda: biblioteca.consolidar(minimo_ejemplos=2)
        )

        casa = CasaPatrones()
        ejemplos = [(_patron(indice), f"concepto-{indice % 8}") for indice in range(tamano)]
        casa.aprender(ejemplos)
        consultas = [_patron(random.randrange(max(1, tamano))) for _ in range(min(100, max(1, tamano)))]
        _, inferir_s, inferir_pico = _medir(lambda: [casa.predecir(x) for x in consultas])

        return {
            "episodios": tamano,
            "conceptos": len(conceptos),
            "incorporar_segundos": incorporar_s,
            "incorporar_por_episodio_ms": incorporar_s * 1000 / max(1, tamano),
            "buscar_segundos": buscar_s,
            "consolidar_segundos": consolidar_s,
            "inferencias": len(consultas),
            "inferir_segundos": inferir_s,
            "pico_bytes": max(incorporar_pico, buscar_pico, consolidar_pico, inferir_pico),
            "persistencia_bytes": _tamano_directorio(raiz),
        }


def ejecutar(tamanos: list[int], semilla: int = 2026) -> dict[str, Any]:
    if not tamanos or any(tamano <= 0 for tamano in tamanos):
        raise ValueError("Todos los tamaños deben ser enteros positivos")
    return {
        "instrumento": "viabilidad-0.1",
        "palacio": "mundo-mental",
        "python": platform.python_version(),
        "plataforma": platform.platform(),
        "semilla": semilla,
        "tamanos": tamanos,
        "resultados": [medir_tamano(tamano, semilla) for tamano in tamanos],
        "advertencia": "Línea base local; no compara inteligencia ni velocidad humana.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Mide la línea base del Palacio Mental")
    parser.add_argument("--sizes", nargs="+", type=int, default=[100, 1000])
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output", type=Path)
    argumentos = parser.parse_args()
    informe = ejecutar(argumentos.sizes, argumentos.seed)
    texto = json.dumps(informe, ensure_ascii=False, indent=2)
    if argumentos.output:
        argumentos.output.parent.mkdir(parents=True, exist_ok=True)
        argumentos.output.write_text(texto + "\n", encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
