"""El Corazón reforma en una copia y consulta la experiencia urbanística."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable
from uuid import uuid4

from .biblioteca import Biblioteca
from .casa_patrones import CasaPatrones

Ejemplo = tuple[Iterable[Any], str]


class Corazon:
    def __init__(self, biblioteca: Biblioteca, tolerancia_olvido: float = 0.0):
        self.biblioteca = biblioteca
        self.tolerancia_olvido = tolerancia_olvido

    @staticmethod
    def inspeccionar(casa: CasaPatrones, pruebas: Iterable[Ejemplo]) -> float:
        lote = list(pruebas)
        if not lote:
            return 1.0
        aciertos = sum(casa.predecir(entrada)[0] == esperado for entrada, esperado in lote)
        return aciertos / len(lote)

    def latir(
        self,
        habilidad: str,
        entrenamiento: Iterable[Ejemplo],
        pruebas: Iterable[Ejemplo],
        protegidos: Iterable[Ejemplo] = (),
    ) -> dict[str, Any]:
        entrenamiento, pruebas, protegidos = list(entrenamiento), list(pruebas), list(protegidos)
        antecedentes = self.biblioteca.consultar_obras(habilidad=habilidad, tipo="ampliar_ejemplos")
        estable = CasaPatrones.restaurar(self.biblioteca.cargar_habilidad(habilidad))
        candidata = deepcopy(estable)

        precision_antes = self.inspeccionar(estable, pruebas)
        protegida_antes = self.inspeccionar(estable, protegidos)
        candidata.aprender(entrenamiento)
        precision_candidata = self.inspeccionar(candidata, pruebas)
        protegida_despues = self.inspeccionar(candidata, protegidos)

        mejora = precision_candidata > precision_antes
        conserva = protegida_despues + self.tolerancia_olvido >= protegida_antes
        aceptada = mejora and conserva

        if aceptada:
            self.biblioteca.guardar_habilidad(habilidad, candidata.exportar())
            motivo = "Mejora la tarea nueva y conserva lo protegido."
        elif not mejora:
            motivo = "No demuestra una mejora sobre la ciudad estable."
        else:
            motivo = "Mejora lo nuevo, pero daña conocimiento protegido."

        entradas_protegidas = {tuple(entrada) for entrada, _ in protegidos}
        for entrada, esperado in pruebas:
            respuesta, confianza = candidata.predecir(entrada)
            self.biblioteca.recordar(
                entrada,
                respuesta,
                esperado,
                respuesta == esperado,
                {
                    "habilidad": habilidad,
                    "confianza": confianza,
                    "candidata_aceptada": aceptada,
                },
                protegido=tuple(entrada) in entradas_protegidas,
            )

        obra = {
            "id": str(uuid4()),
            "habilidad": habilidad,
            "tipo": "ampliar_ejemplos",
            "aceptada": aceptada,
            "precision_antes": precision_antes,
            "precision_candidata": precision_candidata,
            "retencion_antes": protegida_antes,
            "retencion": protegida_despues,
            "motivo": motivo,
            "ejemplos_agregados": len(entrenamiento),
            "antecedentes_consultados": len(antecedentes),
        }
        self.biblioteca.registrar_obra(obra)
        self.biblioteca.consolidar()
        return {"obra_id": obra["id"], **{k: v for k, v in obra.items() if k != "id"}}
