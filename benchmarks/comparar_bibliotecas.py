"""Compara Biblioteca 0.2 JSONL con Biblioteca 0.3 SQLite experimental."""

from __future__ import annotations

import argparse
import json
import platform
import tempfile
import time
import tracemalloc
from pathlib import Path
from typing import Any, Callable

from mundo_mental import Biblioteca, BibliotecaSQLite


def patron(indice: int, longitud: int = 16) -> list[int]:
    return [((indice * 17) + posicion * 7 + (indice >> (posicion % 5))) % 2 for posicion in range(longitud)]


def medir(fabrica: Callable[[Path], Any], tamano: int) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="palacio-comparativa-") as temporal:
        raiz = Path(temporal) / ".mente"
        biblioteca = fabrica(raiz)
        tracemalloc.start()
        inicio = time.perf_counter()
        for indice in range(tamano):
            concepto = f"concepto-{indice % 8}"
            biblioteca.recordar(patron(indice), concepto, concepto, True, {"confianza": 0.8})
        incorporar = time.perf_counter() - inicio
        inicio = time.perf_counter()
        biblioteca.buscar_similares(patron(tamano // 2), limite=5)
        buscar = time.perf_counter() - inicio
        inicio = time.perf_counter()
        biblioteca.consolidar(2)
        consolidar = time.perf_counter() - inicio
        _, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        bytes_disco = sum(x.stat().st_size for x in raiz.rglob("*") if x.is_file())
        return {"incorporar_s": incorporar, "buscar_s": buscar, "consolidar_s": consolidar,
                "pico_bytes": pico, "disco_bytes": bytes_disco}


def comparar(tamanos: list[int]) -> dict[str, Any]:
    return {
        "instrumento": "comparativa-bibliotecas-0.1",
        "python": platform.python_version(),
        "resultados": [
            {"episodios": n, "jsonl": medir(Biblioteca, n),
             "sqlite": medir(lambda ruta: BibliotecaSQLite(ruta), n)} for n in tamanos
        ],
        "nota": "Medición local de implementaciones; no mide inteligencia.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", nargs="+", type=int, default=[100, 1000])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    informe = comparar(args.sizes)
    texto = json.dumps(informe, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(texto + "\n", encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
