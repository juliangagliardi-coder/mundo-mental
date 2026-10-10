"""Validación independiente para promover evidencia de laboratorio a la Biblioteca."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .biblioteca import Biblioteca
from .curiosidad import ResultadoExperimento


@dataclass(frozen=True)
class DictamenEvidencia:
    aceptada: bool
    motivo: str
    recuerdo_id: str | None = None


class ValidadorEvidencia:
    """Promueve solo evidencia reproducible y corroborada de forma explícita."""

    def __init__(self, biblioteca: Biblioteca):
        self.biblioteca = biblioteca
        self.dictamenes: list[DictamenEvidencia] = []

    def evaluar(
        self,
        resultado: ResultadoExperimento,
        corroboracion: Any | None,
        entrada: list[Any],
        respuesta: str,
        esperado: str,
        metadata: dict[str, Any] | None = None,
    ) -> DictamenEvidencia:
        if resultado.estado != "completado":
            return self._registrar(False, "experimento_no_completado")
        if not resultado.reproducible:
            return self._registrar(False, "experimento_no_reproducible")
        if corroboracion is None:
            return self._registrar(False, "sin_corrobacion_independiente")

        datos = dict(metadata or {})
        datos.update({
            "origen": "laboratorio_validado",
            "pregunta_id": resultado.pregunta_id,
            "experimento": resultado.nombre,
            "corroboracion": corroboracion,
            "confianza": 0.9,
        })
        recuerdo_id = self.biblioteca.recordar(
            entrada=entrada,
            respuesta=respuesta,
            esperado=esperado,
            correcto=True,
            metadata=datos,
            importancia=0.7,
        )
        return self._registrar(True, "evidencia_validada", recuerdo_id)

    def _registrar(self, aceptada: bool, motivo: str, recuerdo_id: str | None = None) -> DictamenEvidencia:
        dictamen = DictamenEvidencia(aceptada, motivo, recuerdo_id)
        self.dictamenes.append(dictamen)
        return dictamen
