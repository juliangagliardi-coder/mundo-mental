"""Motor de ciclos: reloj con estados, presupuesto y recuperación sobre el Tejido."""

from __future__ import annotations

import json
import os
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .tejido import TejidoMental

ESTADOS = ("despierto", "durmiendo", "pausado")
VERSION_ESTADO = 3


@dataclass(frozen=True)
class ResumenCiclo:
    ciclo: int
    reacciones: int
    atendidas: int


class MotorDeCiclos:
    """Avanza el Tejido con límites explícitos; no decide qué hacen los Aspectos."""

    def __init__(self, tejido: TejidoMental, ruta_estado: str | Path | None = None,
                 presupuesto: int = 100, max_por_aspecto: int = 16, max_historial: int = 256,
                 limite_total: int | None = None, tiempo_max_segundos: float | None = None):
        if presupuesto < 1 or max_por_aspecto < 1 or max_historial < 1:
            raise ValueError("presupuesto, max_por_aspecto y max_historial deben ser positivos")
        if limite_total is not None and limite_total < 1:
            raise ValueError("limite_total debe ser positivo")
        if tiempo_max_segundos is not None and tiempo_max_segundos <= 0:
            raise ValueError("tiempo_max_segundos debe ser positivo")
        self.tejido = tejido
        self.ruta_estado = Path(ruta_estado) if ruta_estado else None
        self.presupuesto = presupuesto
        self.max_por_aspecto = max_por_aspecto
        self.max_historial = max_historial
        self.limite_total = limite_total
        self.tiempo_max_segundos = tiempo_max_segundos
        self.estado = "despierto"
        self.motivo = ""
        self.latidos_totales = 0
        self.historial: list[ResumenCiclo] = []
        self._inicio_sesion = time.monotonic()
        if self.ruta_estado and self.ruta_estado.exists():
            self._cargar()

    def avanzar(self, ciclos: int = 1) -> list[ResumenCiclo]:
        if ciclos < 1:
            raise ValueError("ciclos debe ser positivo")
        if self.estado != "despierto":
            raise RuntimeError(f"El motor está {self.estado}: {self.motivo or 'sin motivo'}")
        hechos: list[ResumenCiclo] = []
        for _ in range(ciclos):
            if self.limite_total is not None and self.latidos_totales >= self.limite_total:
                self.pausar("limite_total")
                break
            if len(hechos) >= self.presupuesto:
                self.pausar("presupuesto_agotado")
                break
            if self._tiempo_agotado():
                self.pausar("tiempo_agotado")
                break
            reacciones = self.tejido.latir(self.max_por_aspecto)
            resumen = ResumenCiclo(self.tejido.ciclo, len(reacciones),
                                   sum(1 for r in reacciones if r.atendido))
            hechos.append(resumen)
            self.latidos_totales += 1
            self.historial.append(resumen)
        del self.historial[:-self.max_historial]
        self._guardar()
        return hechos

    def pausar(self, motivo: str) -> None:
        self._cambiar("pausado", motivo)

    def dormir(self, motivo: str = "descanso") -> None:
        self._cambiar("durmiendo", motivo)

    def despertar(self) -> None:
        self._inicio_sesion = time.monotonic()
        self._cambiar("despierto", "")

    def diagnostico(self) -> dict[str, Any]:
        return {"estado": self.estado, "motivo": self.motivo, "ciclo": self.tejido.ciclo,
                "latidos_totales": self.latidos_totales, "historial": len(self.historial)}

    def _tiempo_agotado(self) -> bool:
        return (self.tiempo_max_segundos is not None
                and time.monotonic() - self._inicio_sesion >= self.tiempo_max_segundos)

    def _cambiar(self, estado: str, motivo: str) -> None:
        if estado not in ESTADOS:
            raise ValueError(f"Estado desconocido: {estado}")
        self.estado, self.motivo = estado, motivo
        self._guardar()

    def _guardar(self) -> None:
        if not self.ruta_estado:
            return
        datos = {"version": VERSION_ESTADO, "estado": self.estado, "motivo": self.motivo,
                 "ciclo": self.tejido.ciclo, "latidos_totales": self.latidos_totales,
                 "historial": [asdict(r) for r in self.historial]}
        self.ruta_estado.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporal = tempfile.mkstemp(dir=self.ruta_estado.parent, suffix=".tmp")
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False)
            os.replace(temporal, self.ruta_estado)
        except BaseException:
            Path(temporal).unlink(missing_ok=True)
            raise

    def _cargar(self) -> None:
        try:
            datos = json.loads(self.ruta_estado.read_text(encoding="utf-8"))
            estado = datos["estado"]
            if estado not in ESTADOS:
                raise ValueError(estado)
            historial = [ResumenCiclo(int(r["ciclo"]), int(r["reacciones"]), int(r["atendidas"]))
                         for r in datos.get("historial", [])]
            self.estado, self.motivo = estado, str(datos.get("motivo", ""))
            self.tejido.ciclo = int(datos["ciclo"])
            self.latidos_totales = int(datos["latidos_totales"])
            self.historial = historial[-self.max_historial:]
            self._inicio_sesion = time.monotonic()
        except (OSError, ValueError, KeyError, TypeError) as error:
            self.estado, self.motivo = "pausado", f"estado_corrupto:{type(error).__name__}"
