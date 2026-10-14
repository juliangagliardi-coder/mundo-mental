"""Planificador: iniciativas limitadas y explicables que conectan Curiosidad con el Motor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .curiosidad import Curiosidad, Pregunta, ResultadoExperimento
from .motor import MotorDeCiclos


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
    """Solo ejecuta experimentos con receta autorizada; toda decisión queda explicada."""

    def __init__(self, curiosidad: Curiosidad, motor: MotorDeCiclos,
                 max_por_ciclo: int = 1, max_total: int = 100,
                 supervisar: Callable[[Pregunta, str, dict[str, Any]], bool] | None = None,
                 max_decisiones: int = 1024):
        if max_por_ciclo < 1 or max_total < 1 or max_decisiones < 1:
            raise ValueError("Los límites del planificador deben ser positivos")
        self.curiosidad = curiosidad
        self.motor = motor
        self.max_por_ciclo = max_por_ciclo
        self.max_total = max_total
        self.supervisar = supervisar
        self.max_decisiones = max_decisiones
        self.recetas: dict[str, Receta] = {}
        self.sin_receta: list[Pregunta] = []
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

    def explicar(self) -> list[Decision]:
        return list(self.decisiones)

    def _anotar(self, pregunta: Pregunta, estado: str, motivo: str) -> None:
        self.decisiones.append(Decision(self.motor.tejido.ciclo, pregunta.texto, estado, motivo))
        del self.decisiones[:-self.max_decisiones]
