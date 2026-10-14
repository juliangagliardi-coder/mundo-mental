"""Reformas del Corazón bajo Autoridad: se ejecutan, se registran y se pueden revertir."""

from __future__ import annotations

from typing import Any, Iterable

from .autoridad import Autoridad


def reformar(
    corazon: Any,
    autoridad: Autoridad,
    habilidad: str,
    entrenamiento: Iterable[Any],
    pruebas: Iterable[Any],
    protegidos: Iterable[Any] = (),
    zona: str = "habilidades",
) -> dict[str, Any]:
    """Hace latir al Corazón con reversa: si algo falla, restaura la habilidad anterior.

    La reversa guarda de nuevo el estado previo con `guardar_habilidad`, que archiva
    la versión reemplazada; así nada se pierde ni siquiera al revertir.
    """
    biblioteca = corazon.biblioteca
    anterior = biblioteca.cargar_habilidad(habilidad)
    latido: list[Any] = []

    def ejecutar() -> None:
        latido.append(corazon.latir(habilidad, list(entrenamiento), list(pruebas), list(protegidos)))

    def deshacer() -> None:
        if anterior is not None:
            biblioteca.guardar_habilidad(habilidad, anterior)

    decision = autoridad.actuar("corazon", zona, f"reformar:{habilidad}", ejecutar, deshacer)
    return {**decision, "latido": latido[0] if latido else None}
