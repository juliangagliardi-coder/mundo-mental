"""Calles tipadas para evitar conexiones invisibles entre módulos."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4


@dataclass(frozen=True)
class Mensaje:
    tipo: str
    contenido: Any
    origen: str
    id: str = field(default_factory=lambda: str(uuid4()))
    momento: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Calle:
    id: str
    origen: str
    destino: str
    tipo_aceptado: str
    activa: bool = True
    transportados: int = 0
    rechazados: int = 0

    def transportar(self, mensaje: Mensaje) -> Mensaje:
        if not self.activa:
            self.rechazados += 1
            raise RuntimeError(f"La calle {self.id} está cerrada")
        if mensaje.origen != self.origen or mensaje.tipo != self.tipo_aceptado:
            self.rechazados += 1
            raise ValueError(f"El mensaje no cumple el contrato de {self.id}")
        self.transportados += 1
        return mensaje


class Router:
    def __init__(self):
        self.calles: dict[str, Calle] = {}
        self.destinos: dict[str, Callable[[Mensaje], Any]] = {}

    def registrar_calle(self, calle: Calle) -> None:
        if calle.id in self.calles:
            raise ValueError(f"Ya existe la calle {calle.id}")
        self.calles[calle.id] = calle

    def registrar_destino(self, nombre: str, receptor: Callable[[Mensaje], Any]) -> None:
        self.destinos[nombre] = receptor

    def enviar(self, calle_id: str, mensaje: Mensaje) -> Any:
        calle = self.calles[calle_id]
        entregado = calle.transportar(mensaje)
        if calle.destino not in self.destinos:
            raise KeyError(f"No existe el destino {calle.destino}")
        return self.destinos[calle.destino](entregado)
