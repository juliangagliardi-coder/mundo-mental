"""Representación gráfica, local y segura del trabajo de los Aspectos."""

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
    hogar_x: int
    hogar_y: int
    rumbo: str = "sur"
    estado: str = "en_espera"
    actividad: str = "Esperando trabajo"


class MundoVirtual:
    """Orquesta una simulación visual sin ejecutar cambios persistentes reales."""

    ANCHO = 1800
    ALTO = 1200
    CAMINO = ((90, 600), (350, 600), (575, 520), (870, 520), (1120, 650), (1540, 650))
    ESTACIONES = {
        "Curiosidad": (650, 500), "Catalogador": (360, 650), "Biblioteca": (500, 545),
        "Corazón": (930, 555), "Centinela": (900, 315),
    }
    FLUJO = (
        ("Curiosidad", "pregunta", "Detecta una pregunta pendiente y la pone en circulación"),
        ("Catalogador", "clasificacion", "Clasifica la tarea y prepara una ficha de trabajo"),
        ("Biblioteca", "traza", "Registra una traza temporal para que el proceso sea observable"),
        ("Corazón", "evaluacion", "Evalúa el resultado como candidato; no lo convierte en memoria"),
        ("Centinela", "auditoria", "Audita el ciclo y confirma que no hubo efectos persistentes"),
    )

    def __init__(self):
        self.seres = {
            "Biblioteca": SerMundo("Biblioteca", 480, 575, 480, 575),
            "Curiosidad": SerMundo("Curiosidad", 560, 555, 560, 555),
            "Corazón": SerMundo("Corazón", 930, 555, 930, 555),
            "Observador": SerMundo("Observador", 900, 130, 900, 130, estado="durmiente", actividad="Observa el ciclo desde el cielo"),
            "Centinela": SerMundo("Centinela", 900, 315, 900, 315, estado="en_guardia", actividad="Vigila el trabajo"),
            "Catalogador": SerMundo("Catalogador", 315, 720, 315, 720),
        }
        self.eventos: list[EventoMundo] = []
        self.ciclo_activo = False
        self.paso = 0
        self.ciclos_terminados = 0
        self.registrar("mundo_despierto", "Mundo", "El reino está listo para mostrar trabajo observable")

    def registrar(self, tipo: str, actor: str, detalle: str) -> EventoMundo:
        evento = EventoMundo(tipo, actor, detalle)
        self.eventos.append(evento)
        self.eventos = self.eventos[-120:]
        if actor in self.seres:
            self.seres[actor].actividad = detalle
        return evento

    def iniciar(self) -> EventoMundo:
        self.ciclo_activo = True
        return self.registrar("ciclo", "Mundo", "El ciclo de trabajo visual comienza")

    def pausar(self) -> EventoMundo:
        self.ciclo_activo = False
        return self.registrar("ciclo", "Mundo", "El ciclo de trabajo visual queda en pausa")

    def avanzar(self) -> EventoMundo:
        actor, tipo, detalle = self.FLUJO[self.paso]
        ser = self.seres[actor]
        destino = self.ESTACIONES[actor]
        ser.x, ser.y = destino
        ser.estado = "trabajando"
        evento = self.registrar(tipo, actor, detalle)
        for nombre, otro in self.seres.items():
            if nombre not in {actor, "Observador"} and otro.estado != "en_guardia":
                otro.estado = "en_espera"
        self.paso += 1
        if self.paso == len(self.FLUJO):
            self.paso = 0
            self.ciclos_terminados += 1
            self.registrar("ciclo_completo", "Mundo", "Ciclo terminado: se descarta la traza temporal y no se escribe memoria persistente")
            for nombre, otro in self.seres.items():
                if nombre != "Observador":
                    otro.x, otro.y = otro.hogar_x, otro.hogar_y
                    otro.estado = "en_espera" if nombre != "Centinela" else "en_guardia"
        return evento

    def paso_siguiente(self) -> str:
        return self.FLUJO[self.paso][0]

    def cercanos(self, x: int, y: int, radio: int) -> Iterable[SerMundo]:
        return (ser for ser in self.seres.values() if (ser.x-x)**2 + (ser.y-y)**2 <= radio**2)
