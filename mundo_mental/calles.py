"""Calles tipadas y su identidad relacional dentro del Palacio."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from .aspecto import Aspecto, IdentidadAspecto


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


class Calles(Aspecto, Router):
    """Identidad relacional opcional sobre el Router compatible existente."""

    IDENTIDAD = IdentidadAspecto(
        nombre="Calles",
        esencia="Tejido relacional que protege significado y fronteras durante el tránsito",
        proposito="Permitir cooperación explícita sin crear accesos invisibles entre Aspectos",
        perspectiva="Observa contratos, destinos, aislamiento y calidad de las conexiones",
        principios=("conexiones_explicitas", "preservar_origen", "fallar_sin_disolver_fronteras"),
        voz="Concisa, orientadora y neutral respecto del contenido",
        autoridad=("abrir_calles", "cerrar_calles", "transportar_mensajes"),
        limites=("interpretar_contenido", "inventar_destinos", "saltarse_contratos"),
        tensiones=("conexion_y_aislamiento", "rapidez_y_trazabilidad"),
        relaciones={"sistema_nervioso": "ofrece rutas deliberadas"},
        sensibilidades={"conexion": 1.0, "aislamiento": 0.9, "fallo_transporte": 1.0},
    )

    def __init__(self, raiz: str | Path = ".mente"):
        Aspecto.__init__(self, self.IDENTIDAD, raiz)
        Router.__init__(self)

    def registrar_calle(self, calle: Calle) -> None:
        Router.registrar_calle(self, calle)
        self.narrar("calle_abierta", f"Abrí {calle.id}: {calle.origen} -> {calle.destino}",
                    tipo_aceptado=calle.tipo_aceptado)

    def enviar(self, calle_id: str, mensaje: Mensaje) -> Any:
        try:
            return Router.enviar(self, calle_id, mensaje)
        except Exception as error:
            self.narrar("fallo_transporte", f"No pude transportar por {calle_id}",
                        mensaje=mensaje.id, error=type(error).__name__)
            raise
