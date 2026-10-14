"""Planificador: iniciativas limitadas y explicables que conectan Curiosidad con el Motor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .curiosidad import Curiosidad, Pregunta, ResultadoExperimento
from .motor import MotorDeCiclos
from .observacion import Guardian


@dataclass(frozen=True)
class Receta:
    """Experimento autorizado de antemano para un origen de pregunta."""
    nombre: str
    entrada: dict[str, Any]
    funcion: Callable[[dict[str, Any]], Any]


@dataclass(frozen=True)
class Decision:
    ciclo: int
    pregunta: str
    estado: str
    motivo: str


class Planificador:
    """Solo ejecuta experimentos con receta autorizada; toda decisión queda explicada.

    Tras ``max_fallos`` fallos seguidos en un origen pide ayuda a Observación (si hay
    Guardián conectado) y deja de investigar esa zona hasta que sea reanudada.
    Sin Guardián ni buzón de alarmas, pausa el motor.
    """

    def __init__(self, curiosidad: Curiosidad, motor: MotorDeCiclos,
                 max_por_ciclo: int = 1, max_total: int = 100,
                 supervisar: Callable[[Pregunta, str, dict[str, Any]], bool] | None = None,
                 max_decisiones: int = 1024, guardian: Guardian | None = None,
                 max_fallos: int = 3):
        if max_por_ciclo < 1 or max_total < 1 or max_decisiones < 1 or max_fallos < 1:
            raise ValueError("Los límites del planificador deben ser positivos")
        self.curiosidad = curiosidad
        self.motor = motor
        self.max_por_ciclo = max_por_ciclo
        self.max_total = max_total
        self.supervisar = supervisar
        self.max_decisiones = max_decisiones
        self.guardian = guardian
        self.max_fallos = max_fallos
        self.recetas: dict[str, Receta] = {}
        self.sin_receta: list[Pregunta] = []
        self.bloqueadas: list[Pregunta] = []
        self.fallos_seguidos: dict[str, int] = {}
        self.decisiones: list[Decision] = []
        self.total = 0

    def autorizar(self, origen: str, receta: Receta) -> None:
        if not origen:
            raise ValueError("El origen de la receta no puede estar vacío")
        self.recetas[origen] = receta

    def paso(self) -> list[ResultadoExperimento]:
        resultados: list[ResultadoExperimento] = []
        if self.motor.estado != "despierto":
            return resultados
        for _ in range(self.max_por_ciclo):
            pregunta = self.curiosidad.siguiente_pregunta()
            if pregunta is None:
                break
            if self._zona_aislada(pregunta.origen):
                self.bloqueadas.append(pregunta)
                self._anotar(pregunta, "bloqueada", "zona aislada por Observación")
                continue
            receta = self.recetas.get(pregunta.origen)
            if receta is None:
                self.sin_receta.append(pregunta)
                self._anotar(pregunta, "sin_receta", "No hay receta autorizada para este origen")
                continue
            resultado = self.curiosidad.experimentar(
                pregunta, receta.nombre, dict(receta.entrada), receta.funcion, self.supervisar)
            self.total += 1
            resultados.append(resultado)
            motivo = resultado.motivo or ("reproducible" if resultado.reproducible else "no_reproducible")
            self._anotar(pregunta, resultado.estado, motivo)
            self._registrar_resultado(pregunta.origen, resultado)
            if self.motor.estado != "despierto":
                break
            if self.total >= self.max_total:
                self.motor.pausar("iniciativas_agotadas")
                break
        return resultados

    def avanzar(self, ciclos: int = 1) -> list[ResultadoExperimento]:
        if ciclos < 1:
            raise ValueError("ciclos debe ser positivo")
        resultados: list[ResultadoExperimento] = []
        for _ in range(ciclos):
            if self.motor.estado != "despierto":
                break
            self.motor.avanzar(1)
            resultados.extend(self.paso())
        return resultados

    def reanudar_zona(self, origen: str, diagnostico: str,
                      verificacion_aislada: bool, verificacion_reproducible: bool) -> bool:
        """Pide a Observación cerrar los incidentes de la zona; si todos cierran, la reabre."""
        if self.guardian is None:
            return False
        for incidente in list(self.guardian.incidentes_abiertos(origen)):
            self.guardian.cerrar_y_reanudar(
                incidente["alarma_id"], diagnostico, verificacion_aislada, verificacion_reproducible)
        if self.guardian.incidentes_abiertos(origen):
            return False
        self.fallos_seguidos[origen] = 0
        devueltas = [p for p in self.bloqueadas if p.origen == origen]
        self.bloqueadas = [p for p in self.bloqueadas if p.origen != origen]
        self.curiosidad.preguntas.extend(devueltas)
        self.curiosidad.preguntas.sort(key=lambda x: x.prioridad, reverse=True)
        if not self.guardian.incidentes_abiertos():
            self.guardian.dormir()
        return True

    def explicar(self) -> list[Decision]:
        return list(self.decisiones)

    def _zona_aislada(self, origen: str) -> bool:
        return self.guardian is not None and bool(self.guardian.incidentes_abiertos(origen))

    def _registrar_resultado(self, origen: str, resultado: ResultadoExperimento) -> None:
        fallo = resultado.estado == "fallido" or (
            resultado.estado == "completado" and not resultado.reproducible)
        if resultado.estado == "detenido":
            return
        if not fallo:
            self.fallos_seguidos[origen] = 0
            return
        self.fallos_seguidos[origen] = self.fallos_seguidos.get(origen, 0) + 1
        if self.fallos_seguidos[origen] < self.max_fallos:
            return
        if self.curiosidad.buzon is not None:
            self.curiosidad.pedir_ayuda("fallos_repetidos", origen, "alta")
            if self.guardian is not None:
                self.guardian.despertar()
                return
        self.motor.pausar("fallos_repetidos")

    def _anotar(self, pregunta: Pregunta, estado: str, motivo: str) -> None:
        self.decisiones.append(Decision(self.motor.tejido.ciclo, pregunta.texto, estado, motivo))
        del self.decisiones[:-self.max_decisiones]
