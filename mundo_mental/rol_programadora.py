"""Rol programadora: reutiliza el Libro, consulta al razonador y verifica; nunca se aprueba a sí misma."""

from __future__ import annotations

import re
from typing import Any

from .banco_tareas import BancoTareas, Tarea
from .libro import Ficha, Libro
from .tierra import Razonador, RazonadorNulo
from .verificador import Verificador

BLOQUE = re.compile(r"```(?:python|py)?\n(.*?)```", re.DOTALL)


def extraer_codigo(texto: str) -> str:
    coincidencia = BLOQUE.search(texto)
    if coincidencia:
        return coincidencia.group(1).strip()
    return texto.strip() if "def " in texto else ""


class RolProgramadora:
    nombre = "programadora"
    necesita_modelo = True

    def __init__(self, libro: Libro, banco: BancoTareas, razonador: Razonador | None = None,
                 verificador: Verificador | None = None):
        self._libro = libro
        self._banco = banco
        self._razonador = razonador or RazonadorNulo()
        self._verificador = verificador or Verificador()

    def _prompt(self, tarea: Tarea, fichas: list[tuple[Ficha, float]], error: str) -> str:
        partes = [f"Escribe en Python la función {tarea.funcion}.", f"Enunciado: {tarea.enunciado}",
                  "Pruebas visibles:", tarea.visibles]
        for ficha, _ in fichas:
            if ficha.ejemplo:
                partes += [f"Ejemplo verificado ({ficha.titulo}):", ficha.ejemplo]
        if error:
            partes += ["El intento anterior falló:", error]
        partes.append("Responde solo con un bloque ```python.")
        return "\n".join(partes)

    def _cerrar(self, tarea: Tarea, codigo: str, origen: str, historial: list, fuentes: list) -> dict[str, Any]:
        ocultas = self._verificador.verificar(codigo, tarea.ocultas)
        if not ocultas.ok:
            self._libro.registrar_fracaso(f"programar:{tarea.id}", "no_generaliza",
                                          {"origen": origen, "motivo": ocultas.motivo})
        return {"estado": "resuelta" if ocultas.ok else "parcial", "tarea_id": tarea.id, "codigo": codigo,
                "origen": origen, "intentos": historial, "fuentes": fuentes,
                "candidata_lista": ocultas.ok, "adopcion": "requiere_aprobacion_humana"}

    def ejecutar(self, entrada: dict[str, Any]) -> dict[str, Any]:
        tarea = self._banco.obtener(str(entrada["tarea_id"]))
        intentos = max(1, min(8, int(entrada.get("intentos", 3))))
        fichas = self._libro.buscar(f"{tarea.enunciado} {tarea.funcion}", 3, solo_verificadas=True)
        fuentes = [f.id for f, _ in fichas]
        historial: list[dict[str, Any]] = []
        for ficha, _ in fichas:
            if not ficha.ejemplo:
                continue
            r = self._verificador.verificar(ficha.ejemplo, tarea.visibles)
            historial.append({"origen": "libro", "ficha": ficha.id, "motivo": r.motivo})
            if r.ok:
                return self._cerrar(tarea, ficha.ejemplo, "libro", historial, fuentes)
        error = ""
        for numero in range(1, intentos + 1):
            texto = self._razonador.responder(self._prompt(tarea, fichas, error), tarea.id)
            codigo = extraer_codigo(texto)
            if not codigo:
                historial.append({"origen": "modelo", "intento": numero, "motivo": "sin_respuesta"})
                break
            r = self._verificador.verificar(codigo, tarea.visibles)
            historial.append({"origen": "modelo", "intento": numero, "motivo": r.motivo})
            if r.ok:
                return self._cerrar(tarea, codigo, "modelo", historial, fuentes)
            error = f"{r.motivo}: {r.detalle}"
        self._libro.registrar_fracaso(f"programar:{tarea.id}", "sin_solucion", {"intentos": len(historial)})
        return {"estado": "fallida", "tarea_id": tarea.id, "codigo": "", "origen": None,
                "intentos": historial, "fuentes": fuentes, "candidata_lista": False,
                "adopcion": "requiere_aprobacion_humana"}
