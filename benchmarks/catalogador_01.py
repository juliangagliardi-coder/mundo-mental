"""Compara búsqueda exhaustiva y catálogo jerárquico sin declarar ganadores."""

from __future__ import annotations

import argparse
import json
import random
import tempfile
import time
from pathlib import Path

from mundo_mental import BibliotecaSQLite


def patron(indice: int, longitud: int = 24) -> list[int]:
    return [((indice * 17) + posicion * 7 + (indice >> (posicion % 7))) % 2
            for posicion in range(longitud)]


def medir(tamano: int, consultas: int, semilla: int) -> dict:
    random.seed(semilla)
    with tempfile.TemporaryDirectory(prefix="palacio-catalogador-") as carpeta:
        biblioteca = BibliotecaSQLite(carpeta)
        for indice in range(tamano):
            biblioteca.recordar(
                patron(indice), f"respuesta-{indice}", f"concepto-{indice % 32}", True,
                {"origen": f"aspecto-{indice % 5}", "temas": [f"tema-{indice % 13}"]},
            )
        objetivos = [patron(random.randrange(tamano)) for _ in range(consultas)]
        inicio = time.perf_counter()
        catalogadas = [biblioteca.buscar_similares(x, estrategia="catalogo") for x in objetivos]
        catalogo_s = time.perf_counter() - inicio
        inicio = time.perf_counter()
        exhaustivas = [biblioteca.buscar_similares(x, estrategia="exhaustiva") for x in objetivos]
        exhaustiva_s = time.perf_counter() - inicio
        coincidencias = []
        for rapida, completa in zip(catalogadas, exhaustivas):
            ids_rapidos = {x["id"] for x in rapida}
            ids_completos = {x["id"] for x in completa}
            coincidencias.append(len(ids_rapidos & ids_completos) / max(1, len(ids_completos)))
        return {
            "episodios": tamano,
            "consultas": consultas,
            "catalogo_segundos": catalogo_s,
            "exhaustiva_segundos": exhaustiva_s,
            "recall_medio_top5": sum(coincidencias) / max(1, len(coincidencias)),
            "estado_catalogo": biblioteca.estado()["catalogo"],
            "integridad": biblioteca.verificar_catalogo(),
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=1000)
    parser.add_argument("--queries", type=int, default=25)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    resultado = medir(args.size, args.queries, args.seed)
    texto = json.dumps(resultado, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(texto + "\n", encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
