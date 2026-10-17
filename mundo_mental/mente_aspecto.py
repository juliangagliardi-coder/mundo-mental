"""Mente de Aspecto: razonamiento local opcional sobre decisiones dudosas.

El modelo solo puede influir en si un Aspecto atiende un impulso. Nunca altera su identidad,
sus limites ni sus disposiciones: eso sigue pasando por la evolucion reversible de Aspecto.
Si el modelo no responde o responde otra cosa, vale la formula de Aspecto.evaluar_impulso.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Iterable

from .aspecto import Aspecto
from .tierra import Razonador

CANALES_SIN_MODELO = frozenset({"alarma", "reflejo"})
URGENCIA_SIN_MODELO = 3
INSTRUCCION = "Responde solo con una palabra: SI o NO. Debes atender este impulso?"


def interpretar_decision(texto: str) -> bool | None:
    """True para SI, False para NO, None si la respuesta no es una decision clara."""
    if not texto:
        return None
    limpio = unicodedata.normalize("NFD", str(texto).strip().lower())
    limpio = "".join(c for c in limpio if unicodedata.category(c) != "Mn")
    palabra = re.search(r"[a-z]+", limpio)
    if palabra is None:
        return None
    if palabra.group(0) in ("si", "yes"):
        return True
    if palabra.group(0) == "no":
        return False
    return None


class MenteAspecto:
    """Envuelve un Aspecto y consulta al razonador solo cuando la formula esta indecisa."""

    def __init__(self, aspecto: Aspecto, razonador: Razonador, reparto: Any = None, margen: float = 0.12):
        if margen < 0:
            raise ValueError("El margen no puede ser negativo")
        self.aspecto = aspecto
        self.razonador = razonador
        self.reparto = reparto
        self.margen = margen
        self.consultas = 0
        self.cambios = 0
        self.respaldos = 0

    def _contexto(self, impulso: Any, valoracion: Any) -> str:
        i = self.aspecto.identidad
        return "\n".join([
            f"Eres el Aspecto {i.nombre}. Esencia: {i.esencia}",
            f"Proposito: {i.proposito}",
            f"Perspectiva: {i.perspectiva}",
            "Principios: " + "; ".join(i.principios),
            "Limites: " + (", ".join(i.limites) or "ninguno"),
            f"Voz: {i.voz}",
            f"Estado interno: {self.aspecto.estado_interno}",
            f"Necesidades: {self.aspecto.necesidades}",
            f"Impulso: tipo={impulso.tipo}; origen={impulso.origen}; temas={list(impulso.temas)}; "
            f"importancia={impulso.importancia}; contenido={str(impulso.contenido)[:200]}",
            f"Valoracion automatica: interes={valoracion.interes}, umbral={valoracion.umbral}",
        ])

    def _debe_consultar(self, impulso: Any, valoracion: Any) -> bool:
        if impulso.canal in CANALES_SIN_MODELO or impulso.urgencia >= URGENCIA_SIN_MODELO:
            return False
        return abs(valoracion.interes - valoracion.umbral) <= self.margen

    def _pensar(self, impulso: Any, valoracion: Any) -> bool | None:
        if self.reparto is not None and not self.reparto.pedir(self.aspecto.nombre):
            return None
        self.consultas += 1
        try:
            texto = self.razonador.responder(INSTRUCCION, self._contexto(impulso, valoracion))
        except Exception:
            return None
        return interpretar_decision(texto)

    def recibir_impulso(self, impulso: Any) -> dict[str, Any]:
        valoracion = self.aspecto.evaluar_impulso(impulso)
        base = self.aspecto.recibir_impulso(impulso)
        if not self._debe_consultar(impulso, valoracion):
            return base
        decision = self._pensar(impulso, valoracion)
        if decision is None:
            self.respaldos += 1
            return base
        if decision == base["atendido"]:
            return base
        if decision:
            self.aspecto.atendidos += 1
            self.aspecto.ignorados = max(0, self.aspecto.ignorados - 1)
        else:
            self.aspecto.ignorados += 1
            self.aspecto.atendidos = max(0, self.aspecto.atendidos - 1)
        self.cambios += 1
        self.aspecto.narrar("decision_razonada",
                            f"Razone sobre {impulso.tipo} y decidi {'atender' if decision else 'ignorar'}",
                            impulso=impulso.id, formula=base["atendido"], interes=valoracion.interes,
                            umbral=valoracion.umbral)
        self.aspecto._persistir_estado()
        return {**base, "atendido": decision, "detalle": base["detalle"] + ";razonado"}


def conectar_mentes(sistema: Any, aspectos: Iterable[Aspecto], razonador: Razonador,
                    reparto: Any = None, margen: float = 0.12) -> dict[str, MenteAspecto]:
    """Conecta cada Aspecto a traves de su propia mente, conservando sus suscripciones previas."""
    mentes: dict[str, MenteAspecto] = {}
    for aspecto in aspectos:
        mente = MenteAspecto(aspecto, razonador, reparto, margen)
        temas = tuple(sistema.suscripciones.get(aspecto.nombre, ("*",)))
        minima = sistema.importancia_minima.get(aspecto.nombre, 0.0)
        sistema.conectar_receptor(aspecto.nombre, mente.recibir_impulso, temas, minima)
        mentes[aspecto.nombre] = mente
    return mentes
