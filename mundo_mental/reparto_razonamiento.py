"""Reparto del razonamiento: Tierra limita cuantos pensamientos del modelo se permiten."""

from __future__ import annotations

import time
from collections import deque
from threading import RLock
from typing import Callable


class RepartoRazonamiento:
    def __init__(self, por_latido: int = 2, por_aspecto: int = 1, por_hora: int = 120,
                 reloj: Callable[[], float] = time.monotonic):
        if por_latido < 0 or por_aspecto < 0 or por_hora < 0:
            raise ValueError("Los presupuestos no pueden ser negativos")
        self.por_latido = por_latido
        self.por_aspecto = por_aspecto
        self.por_hora = por_hora
        self._reloj = reloj
        self._cerrojo = RLock()
        self._latido_total = 0
        self._latido_aspecto: dict[str, int] = {}
        self._recientes: deque[float] = deque()
        self.concedidos = 0
        self.denegados = 0

    def nuevo_latido(self) -> None:
        with self._cerrojo:
            self._latido_total = 0
            self._latido_aspecto = {}

    def pedir(self, nombre: str) -> bool:
        with self._cerrojo:
            ahora = self._reloj()
            while self._recientes and ahora - self._recientes[0] >= 3600:
                self._recientes.popleft()
            if (self._latido_total >= self.por_latido
                    or self._latido_aspecto.get(nombre, 0) >= self.por_aspecto
                    or len(self._recientes) >= self.por_hora):
                self.denegados += 1
                return False
            self._latido_total += 1
            self._latido_aspecto[nombre] = self._latido_aspecto.get(nombre, 0) + 1
            self._recientes.append(ahora)
            self.concedidos += 1
            return True
