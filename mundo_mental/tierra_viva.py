"""Tierra viva: bucle continuo que late, reparte razonamiento y ejecuta ciclos de trabajo.

Se detiene al crear el archivo PARAR dentro de la raiz de la mente.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable


class TierraViva:
    def __init__(self, aspecto: Any, sistema: Any, reparto: Any, raiz: str | Path = ".mente",
                 ciclo: Any = None, conceptos: Any = None, tareas: tuple[str, ...] | list[str] = (),
                 presupuesto: int = 100, cada_latidos: int = 10, pausa: float = 5.0,
                 dormir: Callable[[float], None] = time.sleep):
        if cada_latidos < 1 or pausa < 0 or presupuesto < 0:
            raise ValueError("Parametros de vida invalidos")
        self.aspecto = aspecto
        self.sistema = sistema
        self.reparto = reparto
        self.raiz = Path(raiz)
        self.ciclo = ciclo
        self._conceptos = conceptos
        self.tareas = list(tareas)
        self.presupuesto = presupuesto
        self.cada_latidos = cada_latidos
        self.pausa = pausa
        self.dormir = dormir
        self.latidos = 0
        self.ciclos = 0
        self.fallos_ciclo = 0
        self._tranquilos = 0

    def debe_parar(self) -> bool:
        return (self.raiz / "PARAR").exists()

    def _leer_conceptos(self) -> dict[str, Any]:
        if callable(self._conceptos):
            return dict(self._conceptos())
        return dict(self._conceptos or {})

    def un_latido(self) -> dict[str, Any]:
        self.reparto.nuevo_latido()
        reacciones = self.sistema.latir()
        self.latidos += 1
        self._tranquilos = 0 if reacciones else self._tranquilos + 1
        ciclo_ejecutado = False
        if self.ciclo is not None and self._tranquilos >= self.cada_latidos:
            self._tranquilos = 0
            try:
                self.ciclo.ejecutar(self._leer_conceptos(), list(self.tareas), self.presupuesto)
                self.ciclos += 1
                ciclo_ejecutado = True
            except Exception as error:
                self.fallos_ciclo += 1
                self.aspecto.narrar("fallo_ciclo", f"El ciclo fallo: {type(error).__name__}", error=str(error)[:200])
        return {"reacciones": len(reacciones), "ciclo": ciclo_ejecutado}

    def vivir(self, max_latidos: int | None = None) -> int:
        hechos = 0
        while not self.debe_parar() and (max_latidos is None or hechos < max_latidos):
            self.un_latido()
            hechos += 1
            if max_latidos is None or hechos < max_latidos:
                self.dormir(self.pausa)
        if self.debe_parar():
            self.aspecto.narrar("parada", "Me detuve porque existe el archivo PARAR", latidos=hechos)
        return hechos
