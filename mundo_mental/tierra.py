"""Aspecto Tierra: núcleo impulsor. Fase 1: identidad, contratos de roles y límites, sin modelo.

Candidata (Constitución, reglas 1, 2 y 15). No modifica ningún módulo existente.
"""

from __future__ import annotations

import posixpath
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from .aspecto import Aspecto, IdentidadAspecto

REGLAS_MAXIMAS = (
    "Evolucionar mentes o aspectos.",
    "Volverse parte de lo evolucionado.",
    "Contribuir al razonamiento global del mundo.",
)

ROLES_PREVISTOS = ("analista", "lectora", "internalizadora", "programadora", "controladora")

RUTAS_PROTEGIDAS = ("CONSTITUCION.md", "tests", "mundo_mental/autoridad.py")
FRAGMENTOS_PROTEGIDOS = ("guardian", "centinela")


def identidad_tierra() -> IdentidadAspecto:
    return IdentidadAspecto(
        nombre="Tierra",
        esencia="Núcleo impulsor que hace evolucionar a los Aspectos y a sí mismo.",
        proposito="Impulsar la evolución del Mundo Mental con propuestas verificables y reversibles.",
        perspectiva="Todo cambio es una hipótesis que debe superar pruebas repetibles.",
        principios=REGLAS_MAXIMAS,
        voz="Sobria, curiosa y explícita sobre lo que sabe y lo que imagina.",
        autoridad=("proponer_cambios", "consultar_libro", "medir_curiosidad", "repartir_razonamiento"),
        limites=(
            "modificar_constitucion", "modificar_pruebas_protegidas", "modificar_guardian",
            "modificar_centinela", "aprobar_sus_propias_propuestas",
        ),
        tensiones=("curiosidad frente a cautela", "autonomía frente a supervisión"),
        sensibilidades={"curiosidad": 0.9, "evolucion": 0.9, "riesgo": 0.7, "fallo": 0.8},
    )


def ruta_protegida(ruta: str) -> bool:
    """True si Tierra no puede escribir en la ruta (relativa al repositorio)."""
    limpia = posixpath.normpath(str(ruta).replace("\\", "/")).lstrip("/")
    if limpia in ("", ".") or limpia == ".." or limpia.startswith("../"):
        return True
    minuscula = limpia.lower()
    if any(fragmento in minuscula for fragmento in FRAGMENTOS_PROTEGIDOS):
        return True
    for protegida in RUTAS_PROTEGIDAS:
        if limpia == protegida or limpia.startswith(protegida + "/"):
            return True
    return False


@runtime_checkable
class Rol(Protocol):
    nombre: str
    necesita_modelo: bool

    def ejecutar(self, entrada: dict[str, Any]) -> dict[str, Any]: ...


@runtime_checkable
class Razonador(Protocol):
    def responder(self, instruccion: str, contexto: str = "") -> str: ...


class RazonadorNulo:
    """Sustituto sin modelo: devuelve texto vacío para que los roles usen sus reglas."""

    def responder(self, instruccion: str, contexto: str = "") -> str:
        return ""


class NucleoTierra:
    """Orquesta los roles de Tierra y aplica sus límites."""

    def __init__(self, aspecto: Aspecto, razonador: Razonador | None = None):
        if aspecto.nombre != "Tierra":
            raise ValueError("NucleoTierra solo gobierna al Aspecto Tierra")
        self.aspecto = aspecto
        self.razonador: Razonador = razonador or RazonadorNulo()
        self._roles: dict[str, Rol] = {}

    def registrar_rol(self, rol: Rol) -> None:
        if rol.nombre not in ROLES_PREVISTOS:
            raise ValueError(f"Rol desconocido: {rol.nombre}")
        if rol.nombre in self._roles:
            raise ValueError(f"El rol ya está registrado: {rol.nombre}")
        self._roles[rol.nombre] = rol
        self.aspecto.narrar("rol_registrado", f"Registré el rol {rol.nombre}",
                            necesita_modelo=bool(rol.necesita_modelo))

    def roles(self) -> tuple[str, ...]:
        return tuple(sorted(self._roles))

    def ejecutar_rol(self, nombre: str, entrada: dict[str, Any] | None = None) -> dict[str, Any]:
        if nombre not in self._roles:
            raise KeyError(nombre)
        resultado = self._roles[nombre].ejecutar(dict(entrada or {}))
        if not isinstance(resultado, dict):
            raise TypeError("Un rol debe devolver un diccionario")
        self.aspecto.narrar("rol_ejecutado", f"Ejecuté el rol {nombre}", claves=sorted(resultado))
        return resultado

    def autorizar_escritura(self, ruta: str) -> bool:
        if ruta_protegida(ruta):
            self.aspecto.narrar("escritura_denegada", f"Se me denegó escribir en {ruta}", ruta=str(ruta))
            return False
        return True


def crear_tierra(raiz: str | Path = ".mente", razonador: Razonador | None = None) -> NucleoTierra:
    return NucleoTierra(Aspecto(identidad_tierra(), raiz), razonador)
