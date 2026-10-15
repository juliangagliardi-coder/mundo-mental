from __future__ import annotations

from typing import Any

from .curiosidad import Curiosidad
from .tierra import Razonador, RazonadorNulo

UMBRAL_FIABILIDAD = 0.8
MINIMO_EJEMPLOS = 3


class RolAnalista:
    nombre = "analista"
    necesita_modelo = False

    def __init__(self, razonador: Razonador | None = None):
        self._razonador = razonador or RazonadorNulo()

    def ejecutar(self, entrada: dict[str, Any]) -> dict[str, Any]:
        conceptos = entrada.get("conceptos", {})
        debiles = sorted(n for n, c in conceptos.items() if float(c.get("fiabilidad", 0.0)) < UMBRAL_FIABILIDAD)
        pocos = sorted(n for n, c in conceptos.items()
                       if n not in debiles and int(c.get("ejemplos_unicos", 0)) < MINIMO_EJEMPLOS)
        solidos = sorted(set(conceptos) - set(debiles) - set(pocos))
        resumen: dict[str, Any] = {"total": len(conceptos), "debiles": debiles,
                                   "pocos_ejemplos": pocos, "solidos": solidos}
        texto = self._razonador.responder("Resume el estado de los conceptos.", str(resumen))
        if texto:
            resumen["redaccion"] = texto
        return resumen


class RolControladora:
    nombre = "controladora"
    necesita_modelo = False

    def __init__(self, curiosidad: Curiosidad):
        self._curiosidad = curiosidad

    def _repartir(self, presupuesto: int) -> dict[str, int]:
        preguntas = self._curiosidad.preguntas
        total = sum(p.prioridad for p in preguntas)
        if not preguntas or total <= 0:
            return {}
        reparto = {p.texto: int(presupuesto * p.prioridad / total) for p in preguntas}
        reparto[preguntas[0].texto] += presupuesto - sum(reparto.values())
        return reparto

    def ejecutar(self, entrada: dict[str, Any]) -> dict[str, Any]:
        presupuesto = int(entrada.get("presupuesto", 100))
        if presupuesto < 0:
            raise ValueError("El presupuesto no puede ser negativo")
        conceptos = entrada.get("conceptos", {})
        nuevas = self._curiosidad.observar_conceptos(conceptos) if conceptos else []
        reparto = self._repartir(presupuesto)
        siguiente = self._curiosidad.siguiente_pregunta()
        return {"preguntas_nuevas": [p.texto for p in nuevas],
                "siguiente": siguiente.texto if siguiente else None,
                "siguiente_id": siguiente.id if siguiente else None,
                "pendientes": len(self._curiosidad.preguntas), "reparto": reparto}
