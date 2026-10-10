"""Sistema Nervioso 0.1: impulsos rápidos, atención local y reflejos seguros."""

from __future__ import annotations

import heapq
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Impulso:
    tipo: str
    contenido: Any
    origen: str
    temas: tuple[str, ...] = ()
    importancia: float = 0.5
    urgencia: int = 1
    destino: str | None = None
    correlacion: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    momento: str = field(default_factory=_ahora)

    def validar(self) -> None:
        if not self.tipo or not self.origen:
            raise ValueError("Todo impulso necesita tipo y origen")
        if not 0.0 <= self.importancia <= 1.0:
            raise ValueError("La importancia debe estar entre 0 y 1")
        if self.urgencia not in {0, 1, 2, 3}:
            raise ValueError("La urgencia debe estar entre 0 y 3")


@dataclass(frozen=True)
class Reaccion:
    aspecto: str
    impulso_id: str
    atendido: bool
    interes: float
    detalle: str = ""


@dataclass
class EstadisticasNerviosas:
    publicados: int = 0
    duplicados: int = 0
    entregados: int = 0
    atendidos: int = 0
    ignorados: int = 0
    descartados_saturacion: int = 0
    reflejos: int = 0


class SistemaNervioso:
    """Difunde sin bloquear; los Aspectos conservan su propia atención."""

    def __init__(self, capacidad_por_aspecto: int = 256, memoria_deduplicacion: int = 4096):
        if capacidad_por_aspecto < 1 or memoria_deduplicacion < 1:
            raise ValueError("Las capacidades deben ser positivas")
        self.capacidad = capacidad_por_aspecto
        self.memoria_deduplicacion = memoria_deduplicacion
        self.receptores: dict[str, Callable[[Impulso], Any]] = {}
        self.suscripciones: dict[str, set[str]] = {}
        self.bandejas: dict[str, list[tuple[int, int, Impulso]]] = {}
        self.reflejos: dict[str, list[Callable[[Impulso], Any]]] = {}
        self._vistos: OrderedDict[str, None] = OrderedDict()
        self._secuencia = 0
        self.estadisticas = EstadisticasNerviosas()

    def conectar(self, aspecto: Any, temas: tuple[str, ...] = ("*",)) -> None:
        nombre = aspecto.nombre
        self.receptores[nombre] = aspecto.recibir_impulso
        self.suscripciones[nombre] = set(temas)
        self.bandejas.setdefault(nombre, [])

    def desconectar(self, nombre: str) -> None:
        self.receptores.pop(nombre, None)
        self.suscripciones.pop(nombre, None)
        self.bandejas.pop(nombre, None)

    def registrar_reflejo(self, tipo: str, accion: Callable[[Impulso], Any]) -> None:
        self.reflejos.setdefault(tipo, []).append(accion)

    def publicar(self, impulso: Impulso) -> dict[str, int]:
        impulso.validar()
        if impulso.id in self._vistos:
            self.estadisticas.duplicados += 1
            return {"encolados": 0, "reflejos": 0}
        self._recordar_id(impulso.id)
        self.estadisticas.publicados += 1

        reflejos = 0
        for accion in self.reflejos.get(impulso.tipo, ()):
            accion(impulso)
            reflejos += 1
            self.estadisticas.reflejos += 1

        encolados = 0
        for nombre, temas in self.suscripciones.items():
            if impulso.destino is not None and impulso.destino != nombre:
                continue
            if "*" not in temas and impulso.tipo not in temas and not set(impulso.temas) & temas:
                continue
            self._encolar(nombre, impulso)
            encolados += 1
        return {"encolados": encolados, "reflejos": reflejos}

    def _encolar(self, nombre: str, impulso: Impulso) -> None:
        cola = self.bandejas[nombre]
        self._secuencia += 1
        elemento = (-impulso.urgencia, self._secuencia, impulso)
        if len(cola) < self.capacidad:
            heapq.heappush(cola, elemento)
            return
        menos_valioso = max(range(len(cola)), key=lambda i: (cola[i][0], -cola[i][1]))
        existente = cola[menos_valioso][2]
        if (impulso.urgencia, impulso.importancia) > (existente.urgencia, existente.importancia):
            cola[menos_valioso] = elemento
            heapq.heapify(cola)
        self.estadisticas.descartados_saturacion += 1

    def latir(self, max_por_aspecto: int = 16) -> list[Reaccion]:
        """Un latido finito: procesa presupuestos sin permitir que un receptor monopolice."""
        reacciones: list[Reaccion] = []
        for nombre, receptor in tuple(self.receptores.items()):
            cola = self.bandejas.get(nombre, [])
            for _ in range(min(max_por_aspecto, len(cola))):
                _, _, impulso = heapq.heappop(cola)
                try:
                    resultado = receptor(impulso) or {}
                    atendido = bool(resultado.get("atendido", False))
                    interes = float(resultado.get("interes", 0.0))
                    detalle = str(resultado.get("detalle", ""))
                except Exception as error:
                    atendido, interes, detalle = False, 0.0, f"receptor_fallo:{type(error).__name__}"
                reaccion = Reaccion(nombre, impulso.id, atendido, interes, detalle)
                reacciones.append(reaccion)
                self.estadisticas.entregados += 1
                if atendido:
                    self.estadisticas.atendidos += 1
                else:
                    self.estadisticas.ignorados += 1
        return reacciones

    def pendientes(self, nombre: str | None = None) -> int | dict[str, int]:
        if nombre is not None:
            return len(self.bandejas.get(nombre, ()))
        return {aspecto: len(cola) for aspecto, cola in self.bandejas.items()}

    def _recordar_id(self, identidad: str) -> None:
        self._vistos[identidad] = None
        self._vistos.move_to_end(identidad)
        while len(self._vistos) > self.memoria_deduplicacion:
            self._vistos.popitem(last=False)
