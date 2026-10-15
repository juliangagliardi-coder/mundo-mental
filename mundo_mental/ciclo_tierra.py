"""Ciclo de Tierra: analista -> controladora -> (lectora -> programadora) por tarea -> informe persistido."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .banco_tareas import BancoTareas
from .curiosidad import Curiosidad
from .libro import Libro
from .rol_internalizadora import RolInternalizadora
from .rol_lectora import RolLectora
from .rol_programadora import RolProgramadora
from .roles_tierra import RolAnalista, RolControladora
from .tierra import NucleoTierra, Razonador, crear_tierra, ruta_protegida
from .verificador import Verificador


def construir_tierra(raiz: str | Path, libro: Libro, banco: BancoTareas, razonador: Razonador | None = None,
                     verificador: Verificador | None = None) -> tuple[NucleoTierra, Curiosidad]:
    verificador = verificador or Verificador()
    nucleo = crear_tierra(raiz, razonador)
    curiosidad = Curiosidad(raiz)
    nucleo.registrar_rol(RolAnalista(nucleo.razonador))
    nucleo.registrar_rol(RolControladora(curiosidad))
    nucleo.registrar_rol(RolLectora(libro))
    nucleo.registrar_rol(RolInternalizadora(libro, verificador))
    nucleo.registrar_rol(RolProgramadora(libro, banco, nucleo.razonador, verificador))
    return nucleo, curiosidad


class CicloTierra:
    def __init__(self, nucleo: NucleoTierra, banco: BancoTareas, ruta_registro: str | Path):
        if not Path(ruta_registro).is_absolute() and ruta_protegida(str(ruta_registro)):
            raise ValueError("El registro del ciclo no puede escribirse en una ruta protegida")
        self.nucleo = nucleo
        self.banco = banco
        self.ruta_registro = Path(ruta_registro)

    def ejecutar(self, conceptos: dict[str, dict[str, Any]], tareas: list[str], presupuesto: int = 100) -> dict[str, Any]:
        if presupuesto < 0:
            raise ValueError("El presupuesto no puede ser negativo")
        analisis = self.nucleo.ejecutar_rol("analista", {"conceptos": conceptos})
        control = self.nucleo.ejecutar_rol("controladora", {"conceptos": conceptos, "presupuesto": presupuesto})
        por_tarea = presupuesto // len(tareas) if tareas else 0
        intentos = max(1, min(5, por_tarea // 20))
        salida = []
        for tarea_id in tareas:
            tarea = self.banco.obtener(tarea_id)
            lectura = self.nucleo.ejecutar_rol(
                "lectora", {"consulta": f"{tarea.enunciado} {tarea.funcion}", "limite": 3, "solo_verificadas": True})
            resultado = self.nucleo.ejecutar_rol("programadora", {"tarea_id": tarea_id, "intentos": intentos})
            salida.append({
                "tarea_id": tarea_id, "fichas_consultadas": [r["id"] for r in lectura["resultados"]],
                "estado": resultado["estado"], "origen": resultado["origen"],
                "candidata_lista": resultado["candidata_lista"], "intentos": len(resultado["intentos"]),
            })
        resumen = {e: sum(1 for t in salida if t["estado"] == e) for e in ("resuelta", "parcial", "fallida")}
        informe = {
            "momento": datetime.now(timezone.utc).isoformat(), "presupuesto": presupuesto,
            "analisis": analisis,
            "curiosidad": {k: control[k] for k in ("siguiente", "pendientes", "reparto")},
            "tareas": salida, "resumen": resumen,
        }
        self.ruta_registro.parent.mkdir(parents=True, exist_ok=True)
        with self.ruta_registro.open("a", encoding="utf-8") as archivo:
            archivo.write(json.dumps(informe, ensure_ascii=False, default=str) + "\n")
        self.nucleo.aspecto.narrar("ciclo", "Completé un ciclo de trabajo", resumen=resumen)
        return informe
