"""Migración reversible de la Biblioteca 0.2 a la 0.3 experimental."""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .biblioteca import Biblioteca
from .biblioteca_sqlite import BibliotecaSQLite


@dataclass(frozen=True)
class InformeMigracion:
    verificada: bool
    episodios_origen: int
    episodios_destino: int
    obras_origen: int
    obras_destino: int
    conceptos_origen: int
    conceptos_destino: int
    archivos_copiados: int
    huella_origen: str
    huella_destino: str

    def como_dict(self) -> dict[str, Any]:
        return asdict(self)


def _huella(registros: list[dict[str, Any]]) -> str:
    canon = json.dumps(sorted(registros, key=lambda x: x.get("id", "")), ensure_ascii=False,
                       sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _copiar_arbol(origen: Path, destino: Path) -> int:
    if not origen.exists():
        return 0
    copiados = 0
    for archivo in origen.rglob("*"):
        if not archivo.is_file():
            continue
        relativo = archivo.relative_to(origen)
        salida = destino / relativo
        salida.parent.mkdir(parents=True, exist_ok=True)
        if salida.exists() and salida.read_bytes() != archivo.read_bytes():
            raise ValueError(f"Conflicto al migrar {relativo}")
        if not salida.exists():
            shutil.copy2(archivo, salida)
            copiados += 1
    return copiados


def migrar_biblioteca(origen: str | Path, destino: str | Path) -> InformeMigracion:
    """Copia y verifica sin borrar ni modificar la Biblioteca de origen."""
    fuente = Biblioteca(origen)
    nueva = BibliotecaSQLite(destino)
    episodios = fuente._leer_jsonl(fuente.experiencias)
    obras = fuente.historial_obras()
    conceptos = fuente.cargar_conceptos()

    nueva.importar_episodios(episodios)
    nueva.importar_obras(obras)
    nueva.importar_conceptos(conceptos)
    archivos = _copiar_arbol(fuente.habilidades, nueva.habilidades)
    archivos += _copiar_arbol(fuente.planos, nueva.planos)

    episodios_destino = nueva.exportar_episodios()
    obras_destino = nueva.historial_obras()
    huella_origen = _huella(episodios)
    huella_destino = _huella(episodios_destino)
    verificada = (
        huella_origen == huella_destino
        and _huella(obras) == _huella(obras_destino)
        and conceptos == nueva.cargar_conceptos()
        and len(episodios) == len(episodios_destino)
    )
    if not verificada:
        raise ValueError("La copia no es equivalente; el origen permanece intacto")
    return InformeMigracion(
        verificada=True,
        episodios_origen=len(episodios), episodios_destino=len(episodios_destino),
        obras_origen=len(obras), obras_destino=len(obras_destino),
        conceptos_origen=len(conceptos), conceptos_destino=len(nueva.cargar_conceptos()),
        archivos_copiados=archivos, huella_origen=huella_origen, huella_destino=huella_destino,
    )
