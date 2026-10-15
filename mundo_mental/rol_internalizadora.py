"""Rol internalizadora: convierte una fuente en fichas; solo es verificada la que supera su prueba."""

from __future__ import annotations

import re
from typing import Any

from .libro import Ficha, Libro
from .verificador import Verificador

ENCABEZADO = re.compile(r"^#{1,6}\s+(.*)$")
BLOQUE = re.compile(r"```(?:python|py)?\n(.*?)```", re.DOTALL)


def dividir_secciones(texto: str) -> list[tuple[str, str]]:
    secciones: list[tuple[str, list[str]]] = [("", [])]
    for linea in texto.splitlines():
        coincidencia = ENCABEZADO.match(linea)
        if coincidencia:
            secciones.append((coincidencia.group(1).strip(), []))
        else:
            secciones[-1][1].append(linea)
    return [(titulo, "\n".join(lineas)) for titulo, lineas in secciones]


class RolInternalizadora:
    nombre = "internalizadora"
    necesita_modelo = False

    def __init__(self, libro: Libro, verificador: Verificador | None = None):
        self._libro = libro
        self._verificador = verificador or Verificador()

    def ejecutar(self, entrada: dict[str, Any]) -> dict[str, Any]:
        fuente = entrada.get("fuente") or {}
        titulo = str(fuente.get("titulo", "")).strip()
        texto = str(fuente.get("texto", ""))
        procedencia = str(fuente.get("procedencia", "")).strip()
        licencia = str(fuente.get("licencia", "")).strip()
        if not titulo or not procedencia or not licencia:
            raise ValueError("La fuente necesita título, procedencia y licencia")
        tema = str(entrada.get("tema") or titulo)
        ids, verificadas, imaginadas, rechazadas = [], 0, 0, 0
        for seccion, cuerpo in dividir_secciones(texto):
            bloques = [b.strip() for b in BLOQUE.findall(cuerpo)]
            prosa = BLOQUE.sub("", cuerpo).strip()
            if not bloques and not prosa:
                continue
            ejemplo = bloques[0] if bloques else ""
            prueba = bloques[1] if len(bloques) > 1 else ""
            estado = "imaginado"
            nombre = f"{titulo}: {seccion}" if seccion else titulo
            if ejemplo and prueba:
                resultado = self._verificador.verificar(ejemplo, prueba)
                if resultado.ok:
                    estado = "verificado"
                else:
                    rechazadas += 1
                    self._libro.registrar_fracaso(
                        f"internalizar:{nombre}", resultado.motivo, {"detalle": resultado.detalle}
                    )
            ficha = self._libro.anadir(Ficha(nombre, tema, prosa, ejemplo, prueba, procedencia, licencia, estado))
            ids.append(ficha.id)
            verificadas += ficha.estado == "verificado"
            imaginadas += ficha.estado == "imaginado"
        return {"fichas": ids, "verificadas": verificadas, "imaginadas": imaginadas, "rechazadas": rechazadas}
