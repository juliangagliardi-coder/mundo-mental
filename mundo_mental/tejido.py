"""Tejido que coordina Aspectos sin apropiarse de sus decisiones."""

from __future__ import annotations

from typing import Any

from .sistema_nervioso import Impulso, Reaccion, SistemaNervioso


class TejidoMental:
    """Registro y reloj común del Palacio; transporta, pero no interpreta."""

    def __init__(self, sistema: SistemaNervioso | None = None):
        self.sistema = sistema or SistemaNervioso()
        self.aspectos: dict[str, Any] = {}
        self.ciclo = 0

    def incorporar(self, aspecto: Any, temas: tuple[str, ...] = ("*",),
                   importancia_minima: float = 0.0) -> None:
        if aspecto.nombre in self.aspectos and self.aspectos[aspecto.nombre] is not aspecto:
            raise ValueError(f"Ya existe otro Aspecto llamado {aspecto.nombre}")
        self.aspectos[aspecto.nombre] = aspecto
        self.sistema.conectar(aspecto, temas, importancia_minima)

    def retirar(self, nombre: str) -> None:
        self.aspectos.pop(nombre, None)
        self.sistema.desconectar(nombre)

    def emitir(self, origen: str, tipo: str, contenido: Any, **atributos: Any) -> Impulso:
        if origen not in self.aspectos:
            raise KeyError(f"El origen {origen} no pertenece al tejido")
        impulso = Impulso(tipo=tipo, contenido=contenido, origen=origen, **atributos)
        self.sistema.publicar(impulso)
        return impulso

    def responder(self, aspecto: str, causa: Impulso, tipo: str,
                  contenido: Any, **atributos: Any) -> Impulso:
        if aspecto not in self.aspectos:
            raise KeyError(f"El Aspecto {aspecto} no pertenece al tejido")
        respuesta = causa.derivar(tipo, contenido, aspecto, **atributos)
        self.sistema.publicar(respuesta)
        return respuesta

    def latir(self, max_por_aspecto: int = 16) -> list[Reaccion]:
        self.ciclo += 1
        return self.sistema.latir(max_por_aspecto)

    def estado(self) -> dict[str, Any]:
        return {
            "ciclo": self.ciclo,
            "aspectos": {nombre: aspecto.ficha() for nombre, aspecto in self.aspectos.items()},
            "sistema_nervioso": self.sistema.diagnostico(),
        }
