"""Rol evolutiva: pide al modelo un parche y su prueba de mejora, y los entrega a Evolucion.

No promueve nada por sí misma: Evolucion decide (suite completa + prueba de mejora + Autoridad).
Solo toca rutas que se le declaran explícitamente al construirla.
"""

from __future__ import annotations

import re
from typing import Any

from .evolucion import Evolucion
from .tierra import Razonador, RazonadorNulo, ruta_protegida

BLOQUES = re.compile(r"```(?:python|py)?\n(.*?)```", re.DOTALL)


def extraer_bloques(texto: str) -> list[str]:
    return [b.strip() for b in BLOQUES.findall(texto) if b.strip()]


class RolEvolutiva:
    nombre = "evolutiva"
    necesita_modelo = True

    def __init__(self, evolucion: Evolucion, razonador: Razonador | None = None,
                 rutas: tuple[str, ...] = (), objetivo: str = "", max_caracteres: int = 12000):
        if not rutas:
            raise ValueError("Hay que declarar al menos una ruta evolucionable")
        if not objetivo.strip():
            raise ValueError("Hay que declarar un objetivo")
        for ruta in rutas:
            if ruta_protegida(ruta):
                raise ValueError(f"Ruta protegida: {ruta}")
        if max_caracteres <= 0:
            raise ValueError("max_caracteres debe ser positivo")
        self.evolucion = evolucion
        self.razonador = razonador or RazonadorNulo()
        self.rutas = tuple(rutas)
        self.objetivo = objetivo.strip()
        self.max_caracteres = max_caracteres
        self._indice = 0

    def _prompt(self, ruta: str, contenido: str) -> str:
        return (
            f"Objetivo: {self.objetivo}\n"
            f"Archivo: {ruta}\n"
            "Contenido actual:\n```python\n" + contenido + "\n```\n"
            "Responde con DOS bloques ```python y nada más: "
            "1) el archivo completo modificado; "
            "2) un script corto de asserts que FALLE con el archivo actual y PASE con tu versión."
        )

    def ejecutar(self, entrada: dict[str, Any] | None = None) -> dict[str, Any]:
        ruta = self.rutas[self._indice % len(self.rutas)]
        self._indice += 1
        try:
            contenido = self.evolucion._ruta(ruta).read_text(encoding="utf-8")
        except (PermissionError, FileNotFoundError) as error:
            return {"estado": "rechazada", "motivo": "ruta", "ruta": ruta, "detalle": str(error)}
        if len(contenido) > self.max_caracteres:
            return {"estado": "omitida", "motivo": "demasiado_grande", "ruta": ruta}
        texto = self.razonador.responder(self._prompt(ruta, contenido), ruta)
        bloques = extraer_bloques(texto)
        if len(bloques) < 2:
            return {"estado": "omitida", "motivo": "sin_propuesta", "ruta": ruta}
        resultado = self.evolucion.proponer(ruta, bloques[0], actor="Tierra", mejora=bloques[1])
        return {"estado": resultado.estado, "motivo": resultado.motivo, "ruta": ruta, "id": resultado.id}
