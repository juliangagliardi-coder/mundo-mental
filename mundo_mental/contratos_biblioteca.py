"""Contratos estables entre la Biblioteca y sus órganos reemplazables."""

from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Protocol


@dataclass(frozen=True)
class LocalizacionCatalogo:
    """Resultado mecánico: señala recuerdos; nunca decide su significado."""

    ids: tuple[str, ...]
    terminos_consultados: int
    coincidencias: int
    version_catalogo: str


@dataclass(frozen=True)
class DiagnosticoBusqueda:
    """Explica cuánto trabajo hizo cada fase de una recuperación."""

    estrategia_solicitada: str
    estrategia_usada: str
    total_episodios: int
    presupuesto_candidatos: int
    candidatos_localizados: int
    candidatos_comprendidos: int
    degradada: bool = False
    motivo: str = ""

    def exportar(self) -> dict[str, Any]:
        return asdict(self)


class PuertoCatalogo(Protocol):
    """Interfaz mínima para cambiar el catálogo sin reescribir la Biblioteca."""

    VERSION: str

    def crear_esquema(self, conexion: sqlite3.Connection) -> None: ...

    def catalogar(self, conexion: sqlite3.Connection, episodio: dict[str, Any]) -> str: ...

    def localizar(
        self,
        conexion: sqlite3.Connection,
        entrada: Iterable[Any],
        limite: int = 128,
        esperado: str | None = None,
    ) -> LocalizacionCatalogo: ...

    def reconstruir(self, conexion: sqlite3.Connection) -> dict[str, int]: ...

    def verificar(self, conexion: sqlite3.Connection) -> dict[str, Any]: ...

    def estado(self, conexion: sqlite3.Connection) -> dict[str, int]: ...
