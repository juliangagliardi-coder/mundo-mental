"""Sistema Nervioso 0.2: tránsito justo, trazable y tolerante a fallos."""

from __future__ import annotations

import heapq
from collections import OrderedDict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _instante(valor: str) -> datetime:
    return datetime.fromisoformat(valor.replace("Z", "+00:00"))


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
    causa: str | None = None
    canal: str = "ordinario"
    caduca: str | None = None
    ruta: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: str(uuid4()))
    momento: str = field(default_factory=_ahora)

    def validar(self) -> None:
        if not self.tipo or not self.origen:
            raise ValueError("Todo impulso necesita tipo y origen")
        if not 0.0 <= self.importancia <= 1.0:
            raise ValueError("La importancia debe estar entre 0 y 1")
        if self.urgencia not in {0, 1, 2, 3}:
            raise ValueError("La urgencia debe estar entre 0 y 3")
        if self.canal not in {"ordinario", "alarma", "reflejo", "interno"}:
            raise ValueError("Canal nervioso desconocido")
        if self.caduca is not None:
            _instante(self.caduca)

    def derivar(self, tipo: str, contenido: Any, origen: str, **cambios: Any) -> "Impulso":
        """Crea una consecuencia conservando correlación, causa y ruta."""
        return Impulso(
            tipo=tipo, contenido=contenido, origen=origen,
            temas=tuple(cambios.pop("temas", self.temas)),
            importancia=float(cambios.pop("importancia", self.importancia)),
            urgencia=int(cambios.pop("urgencia", self.urgencia)),
            destino=cambios.pop("destino", None),
            correlacion=cambios.pop("correlacion", self.correlacion or self.id),
            causa=cambios.pop("causa", self.id),
            canal=cambios.pop("canal", self.canal),
            caduca=cambios.pop("caduca", self.caduca),
            ruta=(*self.ruta, self.origen), **cambios,
        )


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
    caducados: int = 0
    reflejos: int = 0
    fallos_reflejo: int = 0
    fallos_receptor: int = 0
    reintentados: int = 0
    aislados: int = 0


class SistemaNervioso:
    """Difunde sin bloquear y contiene los fallos sin gobernar a los Aspectos."""

    def __init__(self, capacidad_por_aspecto: int = 256, memoria_deduplicacion: int = 4096,
                 max_reintentos: int = 2):
        if capacidad_por_aspecto < 1 or memoria_deduplicacion < 1 or max_reintentos < 0:
            raise ValueError("Las capacidades deben ser positivas y los reintentos no negativos")
        self.capacidad = capacidad_por_aspecto
        self.memoria_deduplicacion = memoria_deduplicacion
        self.max_reintentos = max_reintentos
        self.receptores: dict[str, Callable[[Impulso], Any]] = {}
        self.suscripciones: dict[str, set[str]] = {}
        self.importancia_minima: dict[str, float] = {}
        self.bandejas: dict[str, list[tuple[int, float, int, Impulso]]] = {}
        self.reflejos: dict[str, list[Callable[[Impulso], Any]]] = {}
        self.pausados: set[str] = set()
        self.cuarentena: list[dict[str, Any]] = []
        self._reintentos: dict[tuple[str, str], int] = {}
        self._vistos: OrderedDict[str, None] = OrderedDict()
        self._historial: OrderedDict[str, Impulso] = OrderedDict()
        self._secuencia = 0
        self.estadisticas = EstadisticasNerviosas()

    def conectar(self, aspecto: Any, temas: tuple[str, ...] = ("*",),
                 importancia_minima: float = 0.0) -> None:
        self.conectar_receptor(aspecto.nombre, aspecto.recibir_impulso, temas, importancia_minima)

    def conectar_receptor(self, nombre: str, receptor: Callable[[Impulso], Any],
                           temas: tuple[str, ...] = ("*",),
                           importancia_minima: float = 0.0) -> None:
        if not nombre or not callable(receptor):
            raise ValueError("Un nervio necesita nombre y receptor")
        if not 0.0 <= importancia_minima <= 1.0:
            raise ValueError("La importancia mínima debe estar entre 0 y 1")
        self.receptores[nombre] = receptor
        self.suscripciones[nombre] = set(temas)
        self.importancia_minima[nombre] = importancia_minima
        self.bandejas.setdefault(nombre, [])

    def desconectar(self, nombre: str) -> None:
        self.receptores.pop(nombre, None)
        self.suscripciones.pop(nombre, None)
        self.importancia_minima.pop(nombre, None)
        self.bandejas.pop(nombre, None)
        self.pausados.discard(nombre)

    def pausar(self, nombre: str) -> None:
        if nombre not in self.receptores:
            raise KeyError(nombre)
        self.pausados.add(nombre)

    def reanudar(self, nombre: str) -> None:
        self.pausados.discard(nombre)

    def registrar_reflejo(self, tipo: str, accion: Callable[[Impulso], Any]) -> None:
        if not tipo or not callable(accion):
            raise ValueError("Un reflejo necesita tipo y acción")
        self.reflejos.setdefault(tipo, []).append(accion)

    def publicar(self, impulso: Impulso) -> dict[str, int]:
        impulso.validar()
        if impulso.id in self._vistos:
            self.estadisticas.duplicados += 1
            return {"encolados": 0, "reflejos": 0}
        self._recordar(impulso)
        self.estadisticas.publicados += 1
        if self._caducado(impulso):
            self.estadisticas.caducados += 1
            return {"encolados": 0, "reflejos": 0}

        reflejos = 0
        for accion in self.reflejos.get(impulso.tipo, ()):
            try:
                accion(impulso)
                reflejos += 1
                self.estadisticas.reflejos += 1
            except Exception:
                self.estadisticas.fallos_reflejo += 1

        encolados = 0
        for nombre, temas in tuple(self.suscripciones.items()):
            if impulso.destino is not None and impulso.destino != nombre:
                continue
            if impulso.importancia < self.importancia_minima.get(nombre, 0.0):
                continue
            if "*" not in temas and impulso.tipo not in temas and not set(impulso.temas) & temas:
                continue
            self._encolar(nombre, impulso)
            encolados += 1
        return {"encolados": encolados, "reflejos": reflejos}

    def _elemento(self, impulso: Impulso) -> tuple[int, float, int, Impulso]:
        self._secuencia += 1
        return (-impulso.urgencia, -impulso.importancia, self._secuencia, impulso)

    def _encolar(self, nombre: str, impulso: Impulso) -> bool:
        cola = self.bandejas[nombre]
        elemento = self._elemento(impulso)
        if len(cola) < self.capacidad:
            heapq.heappush(cola, elemento)
            return True
        peor = max(range(len(cola)), key=lambda i: (cola[i][0], cola[i][1], -cola[i][2]))
        existente = cola[peor][3]
        aceptado = (impulso.urgencia, impulso.importancia) > (existente.urgencia, existente.importancia)
        if aceptado:
            cola[peor] = elemento
            heapq.heapify(cola)
        self.estadisticas.descartados_saturacion += 1
        return aceptado

    def latir(self, max_por_aspecto: int = 16) -> list[Reaccion]:
        """Procesa un presupuesto por Aspecto; los reintentos esperan al siguiente latido."""
        if max_por_aspecto < 1:
            raise ValueError("El presupuesto del latido debe ser positivo")
        reacciones: list[Reaccion] = []
        for nombre, receptor in tuple(self.receptores.items()):
            if nombre in self.pausados:
                continue
            cola = self.bandejas.get(nombre, [])
            pendientes_reintento: list[Impulso] = []
            for _ in range(min(max_por_aspecto, len(cola))):
                _, _, _, impulso = heapq.heappop(cola)
                if self._caducado(impulso):
                    self.estadisticas.caducados += 1
                    continue
                try:
                    resultado = receptor(impulso) or {}
                    atendido = bool(resultado.get("atendido", False))
                    interes = float(resultado.get("interes", 0.0))
                    detalle = str(resultado.get("detalle", ""))
                    self._reintentos.pop((nombre, impulso.id), None)
                    self.estadisticas.entregados += 1
                    if atendido:
                        self.estadisticas.atendidos += 1
                    else:
                        self.estadisticas.ignorados += 1
                except Exception as error:
                    atendido, interes = False, 0.0
                    self.estadisticas.fallos_receptor += 1
                    clave = (nombre, impulso.id)
                    intento = self._reintentos.get(clave, 0) + 1
                    self._reintentos[clave] = intento
                    if intento <= self.max_reintentos:
                        pendientes_reintento.append(impulso)
                        self.estadisticas.reintentados += 1
                        detalle = f"reintento:{intento}:{type(error).__name__}"
                    else:
                        detalle = f"aislado:{type(error).__name__}"
                        self.cuarentena.append({
                            "aspecto": nombre, "impulso_id": impulso.id,
                            "tipo": impulso.tipo, "intentos": intento,
                            "error": type(error).__name__, "momento": _ahora(),
                        })
                        self.estadisticas.aislados += 1
                        self._reintentos.pop(clave, None)
                reacciones.append(Reaccion(nombre, impulso.id, atendido, interes, detalle))
            for impulso in pendientes_reintento:
                self._encolar(nombre, impulso)
        return reacciones

    def pendientes(self, nombre: str | None = None) -> int | dict[str, int]:
        if nombre is not None:
            return len(self.bandejas.get(nombre, ()))
        return {aspecto: len(cola) for aspecto, cola in self.bandejas.items()}

    def trazar(self, correlacion_o_id: str) -> list[Impulso]:
        encontrados = [x for x in self._historial.values()
                       if x.id == correlacion_o_id or x.correlacion == correlacion_o_id]
        encontrados.sort(key=lambda x: (x.momento, x.id))
        return encontrados

    def diagnostico(self) -> dict[str, Any]:
        return {
            "estadisticas": asdict(self.estadisticas),
            "pendientes": self.pendientes(),
            "pausados": sorted(self.pausados),
            "cuarentena": list(self.cuarentena),
            "presion": {nombre: round(len(cola) / self.capacidad, 4)
                        for nombre, cola in self.bandejas.items()},
        }

    @staticmethod
    def _caducado(impulso: Impulso) -> bool:
        return impulso.caduca is not None and _instante(impulso.caduca) <= datetime.now(timezone.utc)

    def _recordar(self, impulso: Impulso) -> None:
        self._vistos[impulso.id] = None
        self._historial[impulso.id] = impulso
        self._vistos.move_to_end(impulso.id)
        self._historial.move_to_end(impulso.id)
        while len(self._vistos) > self.memoria_deduplicacion:
            antiguo, _ = self._vistos.popitem(last=False)
            self._historial.pop(antiguo, None)
