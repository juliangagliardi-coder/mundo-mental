"""Primera Casa: aprende conceptos conservando ejemplos representativos."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable


def _similitud(a: list[Any], b: list[Any]) -> float:
    if not a or not b:
        return 0.0
    return sum(x == y for x, y in zip(a, b)) / max(len(a), len(b))


class CasaPatrones:
    def __init__(self, ejemplos: dict[str, list[list[Any]]] | None = None):
        self.ejemplos: dict[str, list[list[Any]]] = ejemplos or {}

    def aprender(self, experiencias: Iterable[tuple[Iterable[Any], str]]) -> None:
        grupos = defaultdict(list, {k: list(v) for k, v in self.ejemplos.items()})
        for entrada, concepto in experiencias:
            patron = list(entrada)
            if patron not in grupos[concepto]:
                grupos[concepto].append(patron)
        self.ejemplos = dict(grupos)

    def predecir(self, entrada: Iterable[Any]) -> tuple[str, float]:
        patron = list(entrada)
        candidatos: list[tuple[float, str]] = []
        for concepto, ejemplos in self.ejemplos.items():
            mejor = max((_similitud(patron, ejemplo) for ejemplo in ejemplos), default=0.0)
            candidatos.append((mejor, concepto))
        if not candidatos:
            return "desconocido", 0.0
        candidatos.sort(reverse=True)
        mejor_valor, mejor_concepto = candidatos[0]
        if len(candidatos) > 1 and candidatos[1][0] == mejor_valor:
            return "ambiguo", mejor_valor
        return mejor_concepto, mejor_valor

    def exportar(self) -> dict[str, Any]:
        return {"tipo": "casa_patrones", "version": 1, "ejemplos": self.ejemplos}

    @classmethod
    def restaurar(cls, estado: dict[str, Any] | None) -> "CasaPatrones":
        if not estado:
            return cls()
        if estado.get("tipo") != "casa_patrones":
            raise ValueError("El archivo no pertenece a CasaPatrones")
        return cls(ejemplos=estado.get("ejemplos", {}))
