"""Rol lectora: consulta el Libro sin modelo."""

from __future__ import annotations

from typing import Any

from .libro import Libro


class RolLectora:
    nombre = "lectora"
    necesita_modelo = False

    def __init__(self, libro: Libro):
        self._libro = libro

    def ejecutar(self, entrada: dict[str, Any]) -> dict[str, Any]:
        consulta = str(entrada.get("consulta", "")).strip()
        if not consulta:
            return {"consulta": "", "resultados": []}
        encontrados = self._libro.buscar(
            consulta, int(entrada.get("limite", 3)), bool(entrada.get("solo_verificadas", False))
        )
        return {
            "consulta": consulta,
            "resultados": [
                {"id": f.id, "titulo": f.titulo, "tema": f.tema, "estado": f.estado,
                 "puntuacion": round(p, 4), "procedencia": f.procedencia}
                for f, p in encontrados
            ],
        }
