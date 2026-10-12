"""Estado visual derivado exclusivamente de eventos del ciclo real."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class EventoVisual:
    actor: str
    accion: str
    detalle: str
    datos: dict[str, Any] = field(default_factory=dict)
    momento: str = field(default_factory=_ahora)


@dataclass
class Presencia:
    nombre: str
    x: int
    y: int
    estado: str
    actividad: str


class MundoVirtual:
    """Proyección visual: no inventa trabajo ni ejecuta lógica del Palacio."""

    ANCHO = 1800
    ALTO = 1200
    CAMINO = ((90, 600), (350, 600), (575, 520), (870, 520), (1120, 650), (1540, 650))

    def __init__(self) -> None:
        self.presencias = {
            "Biblioteca": Presencia("Biblioteca", 480, 575, "en_espera", "Sin eventos todavía"),
            "Curiosidad": Presencia("Curiosidad", 600, 555, "en_espera", "Sin eventos todavía"),
            "Corazón": Presencia("Corazón", 930, 555, "latiente", "Presencia visual; no participa en este ciclo"),
            "Observador": Presencia("Observador", 900, 130, "durmiente", "Espera una alarma real"),
            "Centinela": Presencia("Centinela", 900, 315, "en_guardia", "Custodia bajo el Observador"),
            "Catalogador": Presencia("Catalogador", 315, 720, "en_espera", "No invocado por el ciclo integrado actual"),
        }
        self.eventos: list[EventoVisual] = []
        self.activo: str | None = None
        self.ejecutando = False
        self.ciclos_terminados = 0
        self.ultimo_resultado: dict[str, Any] | None = None

    def comenzar(self) -> None:
        self.ejecutando = True
        self.activo = None

    def detener(self) -> None:
        self.ejecutando = False
        self.activo = None
        self._restablecer_estados()

    def aplicar_evento(
        self,
        actor: str,
        accion: str,
        datos: dict[str, Any],
    ) -> EventoVisual:
        detalle = str(datos.get("detalle", accion))
        evento = EventoVisual(actor, accion, detalle, dict(datos))
        self.eventos.append(evento)
        self.eventos = self.eventos[-120:]
        self._restablecer_estados()
        if actor in self.presencias:
            presencia = self.presencias[actor]
            presencia.estado = "trabajando"
            presencia.actividad = detalle
            self.activo = actor
        else:
            self.activo = None
        return evento

    def completar(self, resultado: dict[str, Any]) -> None:
        self.ciclos_terminados += 1
        self.ultimo_resultado = dict(resultado)
        self.activo = None
        self._restablecer_estados()

    def _restablecer_estados(self) -> None:
        for nombre, presencia in self.presencias.items():
            if nombre == "Corazón":
                presencia.estado = "latiente"
            elif nombre == "Observador":
                presencia.estado = "durmiente"
            elif nombre == "Centinela":
                presencia.estado = "en_guardia"
            else:
                presencia.estado = "en_espera"
