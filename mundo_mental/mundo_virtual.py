"""Mundo virtual persistente y observable de Mundo Mental.

El mundo describe espacio físico, no autoridad. Las decisiones siguen perteneciendo
al sistema de Aspectos y sus límites constitucionales.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable


@dataclass(frozen=True)
class EventoMundo:
    tipo: str
    actor: str
    detalle: str
    momento: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class SerMundo:
    nombre: str
    x: int
    y: int
    rumbo: str = "sur"
    estado: str = "sereno"
    actividad: str = "En reposo"


class MundoVirtual:
    """Terreno, tránsito y eventos de una ciudad medieval fantástica local."""

    ANCHO = 1800
    ALTO = 1200
    CAMINO = ((90, 600), (350, 600), (575, 520), (870, 520), (1120, 650), (1540, 650))

    def __init__(self):
        self.seres = {
            "Biblioteca": SerMundo("Biblioteca", 480, 575, actividad="Ordena recuerdos junto a la biblioteca"),
            "Curiosidad": SerMundo("Curiosidad", 560, 555, estado="atenta", actividad="Busca una pregunta nueva"),
            "Corazón": SerMundo("Corazón", 930, 555, estado="latiente", actividad="Late bajo el árbol rojo"),
            "Observador": SerMundo("Observador", 900, 130, estado="durmiente", actividad="Duerme entre las nubes"),
            "Centinela": SerMundo("Centinela", 900, 315, estado="en_guardia", actividad="Guarda el cielo y el camino"),
            "Catalogador": SerMundo("Catalogador", 315, 720, actividad="Clasifica hallazgos en silencio"),
        }
        self.eventos: list[EventoMundo] = []
        self.registrar("mundo_despierto", "Mundo", "La ciudad medieval fantástica despierta")

    def registrar(self, tipo: str, actor: str, detalle: str) -> EventoMundo:
        evento = EventoMundo(tipo, actor, detalle)
        self.eventos.append(evento)
        self.eventos = self.eventos[-120:]
        if actor in self.seres:
            self.seres[actor].actividad = detalle
        return evento

    def mover(self, nombre: str, x: int, y: int, actividad: str) -> EventoMundo:
        if nombre not in self.seres:
            raise KeyError(nombre)
        if not (0 <= x <= self.ANCHO and 0 <= y <= self.ALTO):
            raise ValueError("El destino queda fuera del mundo")
        ser = self.seres[nombre]
        ser.rumbo = "este" if x > ser.x else "oeste" if x < ser.x else "sur"
        ser.x, ser.y, ser.actividad = x, y, actividad
        return self.registrar("movimiento", nombre, actividad)

    def pulso_demo(self) -> tuple[EventoMundo, ...]:
        pregunta = self.registrar("pregunta", "Curiosidad", "Detecta un vacío y formula una pregunta")
        viaje = self.mover("Curiosidad", 1450, 620, "Camina hacia la puerta de un Universo de Experimentación")
        registro = self.registrar("registro", "Biblioteca", "Conserva la pregunta como antecedente, sin tratarla como evidencia")
        guardia = self.registrar("vigilancia", "Centinela", "Mantiene guardia bajo el Observador")
        return pregunta, viaje, registro, guardia

    def cercanos(self, x: int, y: int, radio: int) -> Iterable[SerMundo]:
        return (ser for ser in self.seres.values() if (ser.x-x)**2 + (ser.y-y)**2 <= radio**2)
