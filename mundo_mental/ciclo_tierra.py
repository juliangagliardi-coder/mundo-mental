"""Ciclo de Tierra: analista -> controladora -> (lectora -> programadora) por tarea -> adopción -> informe.

Con una Autoridad, las candidatas listas se adoptan solas: se compara el banco antes y después,
se aplica con reversa y se registra. Sin Autoridad, el ciclo solo propone (comportamiento anterior).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .autoridad import Autoridad
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
    ZONA_ADOPCIONES = "adopciones"

    def __init__(self, nucleo: NucleoTierra, banco: BancoTareas, ruta_registro: str | Path,
                 autoridad: Autoridad | None = None, ruta_adoptadas: str | Path | None = None):
        for ruta in (ruta_registro, ruta_adoptadas):
            if ruta is not None and not Path(ruta).is_absolute() and ruta_protegida(str(ruta)):
                raise ValueError("El ciclo no puede escribir en una ruta protegida")
        self.nucleo = nucleo
        self.banco = banco
        self.ruta_registro = Path(ruta_registro)
        self.autoridad = autoridad
        self.ruta_adoptadas = Path(ruta_adoptadas) if ruta_adoptadas else self.ruta_registro.with_name("adoptadas.json")

    def _cargar_adoptadas(self) -> dict[str, str]:
        if not self.ruta_adoptadas.exists():
            return {}
        try:
            datos = json.loads(self.ruta_adoptadas.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        if not isinstance(datos, dict):
            return {}
        return {k: v for k, v in datos.items() if isinstance(k, str) and isinstance(v, str)}

    def _guardar_adoptadas(self, adoptadas: dict[str, str]) -> None:
        self.ruta_adoptadas.parent.mkdir(parents=True, exist_ok=True)
        temporal = self.ruta_adoptadas.with_suffix(".tmp")
        temporal.write_text(json.dumps(adoptadas, ensure_ascii=False, indent=2), encoding="utf-8")
        temporal.replace(self.ruta_adoptadas)

    def _adoptar(self, tarea_id: str, codigo: str) -> dict[str, Any]:
        adoptadas = self._cargar_adoptadas()
        antes = self.banco.evaluar(adoptadas)
        despues = self.banco.evaluar({**adoptadas, tarea_id: codigo})
        comparacion = self.banco.comparar(antes, despues)
        if not comparacion["aceptable"]:
            motivo = "regresion" if comparacion["regresiones"] else "sin_mejora"
            return {"adopcion": "rechazada", "motivo": motivo, "regresiones": comparacion["regresiones"]}

        def ejecutar() -> None:
            self._guardar_adoptadas({**adoptadas, tarea_id: codigo})

        def deshacer() -> None:
            self._guardar_adoptadas(adoptadas)

        decision = self.autoridad.actuar("programadora", self.ZONA_ADOPCIONES, f"adoptar:{tarea_id}",
                                         ejecutar, deshacer)
        resultado = decision["resultado"]
        return {"adopcion": "adoptada" if resultado == "ejecutada" else resultado,
                "motivo": "mejora_sin_regresiones" if resultado == "ejecutada" else resultado,
                "regresiones": []}

    def ejecutar(self, conceptos: dict[str, dict[str, Any]], tareas: list[str], presupuesto: int = 100) -> dict[str, Any]:
        if presupuesto < 0:
            raise ValueError("El presupuesto no puede ser negativo")
        analisis = self.nucleo.ejecutar_rol("analista", {"conceptos": conceptos})
        control = self.nucleo.ejecutar_rol("controladora", {"conceptos": conceptos, "presupuesto": presupuesto})
        omitidas: list[str] = []
        pendientes = list(tareas)
        if self.autoridad is not None:
            previas = self.banco.evaluar(self._cargar_adoptadas())["detalle"]
            omitidas = [t for t in tareas if previas.get(t, {}).get("superada", False)]
            pendientes = [t for t in tareas if t not in omitidas]
        por_tarea = presupuesto // len(pendientes) if pendientes else 0
        intentos = max(1, min(5, por_tarea // 20))
        salida = []
        for tarea_id in pendientes:
            tarea = self.banco.obtener(tarea_id)
            lectura = self.nucleo.ejecutar_rol(
                "lectora", {"consulta": f"{tarea.enunciado} {tarea.funcion}", "limite": 3, "solo_verificadas": True})
            resultado = self.nucleo.ejecutar_rol("programadora", {"tarea_id": tarea_id, "intentos": intentos})
            entrada = {
                "tarea_id": tarea_id, "fichas_consultadas": [r["id"] for r in lectura["resultados"]],
                "estado": resultado["estado"], "origen": resultado["origen"],
                "candidata_lista": resultado["candidata_lista"], "intentos": len(resultado["intentos"]),
            }
            if self.autoridad is not None and resultado["candidata_lista"]:
                entrada.update(self._adoptar(tarea_id, resultado["codigo"]))
            salida.append(entrada)
        resumen = {e: sum(1 for t in salida if t["estado"] == e) for e in ("resuelta", "parcial", "fallida")}
        informe = {
            "momento": datetime.now(timezone.utc).isoformat(), "presupuesto": presupuesto,
            "analisis": analisis,
            "curiosidad": {k: control[k] for k in ("siguiente", "pendientes", "reparto")},
            "tareas": salida, "resumen": resumen, "omitidas": omitidas,
        }
        self.ruta_registro.parent.mkdir(parents=True, exist_ok=True)
        with self.ruta_registro.open("a", encoding="utf-8") as archivo:
            archivo.write(json.dumps(informe, ensure_ascii=False, default=str) + "\n")
        self.nucleo.aspecto.narrar("ciclo", "Completé un ciclo de trabajo", resumen=resumen)
        return informe
