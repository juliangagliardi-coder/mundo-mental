"""Mundo virtual jugable, persistente y observable de Mundo Mental."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import hypot
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


@dataclass
class Jugador:
    x: int = 175
    y: int = 600
    rumbo: str = "este"
    brasas: int = 0


class MundoVirtual:
    """Terreno, tránsito y una aventura local sin permisos implícitos."""

    ANCHO = 1800
    ALTO = 1200
    CAMINO = ((90, 600), (350, 600), (575, 520), (870, 520), (1120, 650), (1540, 650))
    BRASAS = ((625, 455), (1040, 710), (1120, 350))
    DESTINO_RITUAL = (925, 585)

    def __init__(self):
        self.seres = {
            "Biblioteca": SerMundo("Biblioteca", 480, 575, actividad="Ordena recuerdos junto a la biblioteca"),
            "Curiosidad": SerMundo("Curiosidad", 560, 555, estado="atenta", actividad="Busca una pregunta nueva"),
            "Corazón": SerMundo("Corazón", 930, 555, estado="latiente", actividad="Late bajo el árbol rojo"),
            "Observador": SerMundo("Observador", 900, 130, estado="durmiente", actividad="Duerme entre las nubes"),
            "Centinela": SerMundo("Centinela", 900, 315, estado="en_guardia", actividad="Guarda el cielo y el camino"),
            "Catalogador": SerMundo("Catalogador", 315, 720, actividad="Clasifica hallazgos en silencio"),
        }
        self.jugador = Jugador()
        self.brasas_disponibles = set(self.BRASAS)
        self.mision_completada = False
        self.eventos: list[EventoMundo] = []
        self.registrar("mundo_despierto", "Mundo", "La ciudad medieval fantástica despierta")
        self.registrar("mision", "Centinela", "Reúne tres brasas de asombro y llévalas al Corazón")

    def registrar(self, tipo: str, actor: str, detalle: str) -> EventoMundo:
        evento = EventoMundo(tipo, actor, detalle)
        self.eventos.append(evento)
        self.eventos = self.eventos[-120:]
        if actor in self.seres:
            self.seres[actor].actividad = detalle
        return evento

    def _valido(self, x: int, y: int) -> bool:
        if not (24 <= x <= self.ANCHO - 24 and 24 <= y <= self.ALTO - 24):
            return False
        rio_centro = 1265 + 50 * __import__("math").sin(y / 130)
        return not (rio_centro - 48 <= x <= rio_centro + 48)

    def mover_jugador(self, dx: int, dy: int) -> bool:
        nx, ny = self.jugador.x + dx, self.jugador.y + dy
        if not self._valido(nx, ny):
            self.registrar("obstaculo", "Viajero", "El río y los límites del reino detienen el paso")
            return False
        self.jugador.rumbo = "este" if dx > 0 else "oeste" if dx < 0 else "sur" if dy > 0 else "norte"
        self.jugador.x, self.jugador.y = nx, ny
        self._recoger_brasas()
        return True

    def _recoger_brasas(self) -> None:
        for brasa in tuple(self.brasas_disponibles):
            if hypot(self.jugador.x - brasa[0], self.jugador.y - brasa[1]) <= 42:
                self.brasas_disponibles.remove(brasa)
                self.jugador.brasas += 1
                self.registrar("hallazgo", "Viajero", f"Encuentra una brasa de asombro ({self.jugador.brasas}/3)")

    def interactuar(self) -> EventoMundo:
        if self.mision_completada:
            return self.registrar("eco", "Corazón", "El Corazón sigue latiendo con las brasas reunidas")
        if self.jugador.brasas == 3 and hypot(self.jugador.x-self.DESTINO_RITUAL[0], self.jugador.y-self.DESTINO_RITUAL[1]) <= 105:
            self.mision_completada = True
            self.seres["Corazón"].actividad = "Arde con las tres brasas de asombro"
            return self.registrar("ritual", "Corazón", "El Corazón recibe las tres brasas: el reino responde con luz")
        cercano = min(self.seres.values(), key=lambda ser: hypot(self.jugador.x-ser.x, self.jugador.y-ser.y))
        if hypot(self.jugador.x-cercano.x, self.jugador.y-cercano.y) <= 100:
            return self.registrar("dialogo", cercano.nombre, cercano.actividad)
        return self.registrar("eco", "Viajero", "Solo el viento responde. Busca una brasa o un habitante")

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
