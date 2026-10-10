"""Identidad ejecutable y memoria autobiográfica de los Aspectos."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class IdentidadAspecto:
    nombre: str
    esencia: str
    proposito: str
    perspectiva: str
    principios: tuple[str, ...]
    voz: str
    autoridad: tuple[str, ...] = ()
    limites: tuple[str, ...] = ()
    tensiones: tuple[str, ...] = ()
    relaciones: dict[str, str] = field(default_factory=dict)

    def validar(self) -> None:
        campos = (self.nombre, self.esencia, self.proposito, self.perspectiva, self.voz)
        if any(not valor.strip() for valor in campos):
            raise ValueError("La identidad no puede contener dimensiones esenciales vacías")
        if not self.principios:
            raise ValueError("Todo Aspecto necesita al menos un principio")
        if set(self.autoridad) & set(self.limites):
            raise ValueError("Una capacidad no puede ser autoridad y límite a la vez")

    def huella(self) -> dict[str, Any]:
        self.validar()
        return asdict(self)


class MemoriaAutobiografica:
    def __init__(self, ruta: str | Path):
        self.ruta = Path(ruta)

    def recordar(self, aspecto: str, tipo: str, relato: str, datos: dict[str, Any] | None = None) -> str:
        identidad = str(uuid4())
        registro = {
            "id": identidad,
            "momento": _ahora(),
            "aspecto": aspecto,
            "tipo": tipo,
            "relato": relato,
            "datos": datos or {},
        }
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        with self.ruta.open("a", encoding="utf-8") as archivo:
            archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
        return identidad

    def historia(self, limite: int | None = None) -> list[dict[str, Any]]:
        if not self.ruta.exists():
            return []
        with self.ruta.open(encoding="utf-8") as archivo:
            recuerdos = [json.loads(linea) for linea in archivo if linea.strip()]
        return recuerdos[-limite:] if limite is not None else recuerdos


class Aspecto:
    """Base que une capacidad técnica, identidad y continuidad narrativa."""

    def __init__(self, identidad: IdentidadAspecto, raiz: str | Path = ".mente"):
        identidad.validar()
        self.identidad = identidad
        self.memoria_de_si = MemoriaAutobiografica(
            Path(raiz) / "autobiografias" / f"{identidad.nombre.lower()}.jsonl"
        )
        self.estado_interno = "sereno"

    @property
    def nombre(self) -> str:
        return self.identidad.nombre

    def narrar(self, tipo: str, relato: str, **datos: Any) -> str:
        return self.memoria_de_si.recordar(self.nombre, tipo, relato, datos)

    def cambiar_estado(self, nuevo: str, motivo: str) -> None:
        anterior = self.estado_interno
        self.estado_interno = nuevo
        self.narrar("cambio_de_estado", f"Pasé de {anterior} a {nuevo}: {motivo}", anterior=anterior, nuevo=nuevo)

    def ficha(self) -> dict[str, Any]:
        return {
            "identidad": self.identidad.huella(),
            "estado_interno": self.estado_interno,
            "recuerdos_autobiograficos": len(self.memoria_de_si.historia()),
        }
