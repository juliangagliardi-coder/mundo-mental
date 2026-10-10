"""Modelo observable de la Ciudad Mental para la interfaz gráfica."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class EventoCiudad:
    tipo: str
    actor: str
    detalle: str
    destino: str | None = None
    momento: str = field(default_factory=_ahora)


@dataclass
class Habitante:
    nombre: str
    lugar: str
    estado: str = "sereno"
    actividad: str = "En reposo"


class CiudadMental:
    """Estado visual, deliberadamente separado de las decisiones de los Aspectos."""

    LUGARES = {
        "biblioteca": (195, 235),
        "corazon": (505, 250),
        "observacion": (360, 75),
        "calles": (355, 405),
        "portal": (675, 110),
    }

    def __init__(self):
        self.habitantes = {
            "Biblioteca": Habitante("Biblioteca", "biblioteca", "sereno", "Custodia recuerdos"),
            "Curiosidad": Habitante("Curiosidad", "biblioteca", "atenta", "Busca vacíos"),
            "Corazón": Habitante("Corazón", "corazon", "sereno", "Inspecciona obras"),
            "Observación": Habitante("Observación", "observacion", "sereno", "Vigila fronteras"),
            "Calles": Habitante("Calles", "calles", "activa", "Conecta rutas"),
        }
        self.eventos: list[EventoCiudad] = []
        self.rutas = [
            ("biblioteca", "corazon", "antecedentes"),
            ("biblioteca", "observacion", "alarma"),
            ("observacion", "calles", "reanudar"),
            ("biblioteca", "portal", "solicitud_universo"),
        ]
        self.registrar("ciudad_iniciada", "Ciudad", "La ciudad está despierta")

    def registrar(self, tipo: str, actor: str, detalle: str, destino: str | None = None) -> EventoCiudad:
        evento = EventoCiudad(tipo, actor, detalle, destino)
        self.eventos.append(evento)
        self.eventos = self.eventos[-80:]
        if actor in self.habitantes:
            habitante = self.habitantes[actor]
            habitante.actividad = detalle
            habitante.estado = "activa" if tipo not in {"alarma", "incidente"} else "alerta"
        return evento

    def viajar(self, actor: str, destino: str, actividad: str) -> EventoCiudad:
        if actor not in self.habitantes:
            raise KeyError(actor)
        if destino not in self.LUGARES:
            raise KeyError(destino)
        habitante = self.habitantes[actor]
        origen = habitante.lugar
        habitante.lugar = destino
        habitante.actividad = actividad
        habitante.estado = "en_transito"
        return self.registrar("viaje", actor, f"Viaja de {origen} a {destino}: {actividad}", destino)

    def pulso_demo(self) -> tuple[EventoCiudad, ...]:
        pregunta = self.registrar("pregunta", "Curiosidad", "Formula una pregunta sobre un vacío de patrones")
        viaje = self.viajar("Curiosidad", "portal", "Solicita un Universo de Experimentación")
        evidencia = self.registrar("evidencia", "Biblioteca", "Espera validación antes de recordar", "biblioteca")
        vigilancia = self.registrar("vigilancia", "Observación", "Mantiene la ciudad estable", "portal")
        return pregunta, viaje, evidencia, vigilancia

    def ficha(self, nombre: str) -> dict[str, Any]:
        habitante = self.habitantes[nombre]
        relacionados = [evento for evento in self.eventos if evento.actor == nombre][-6:]
        return {
            "nombre": habitante.nombre,
            "lugar": habitante.lugar,
            "estado": habitante.estado,
            "actividad": habitante.actividad,
            "eventos": relacionados,
        }
