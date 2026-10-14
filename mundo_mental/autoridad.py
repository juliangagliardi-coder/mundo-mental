"""Autoridad: todo es reversible; solo las zonas protegidas se congelan.

No hay acciones irreversibles. Cada acción se ejecuta con una forma de deshacerla.
Si falla, se revierte y Observación recibe una alarma. Si toca una zona protegida,
el Centinela la bloquea y el Guardián la congela. Los desacuerdos entre Aspectos
no detienen el trabajo: se anotan como deuda y se saldan después.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable
from uuid import uuid4

from .observacion import Alarma, Centinela, Guardian


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


class Autoridad:
    def __init__(self, raiz: str | Path, centinela: Centinela, guardian: Guardian):
        self.ruta = Path(raiz) / "autoridad" / "registro.jsonl"
        self.centinela = centinela
        self.guardian = guardian

    def _anotar(self, evento: dict[str, Any]) -> dict[str, Any]:
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        with self.ruta.open("a", encoding="utf-8") as archivo:
            archivo.write(json.dumps(evento, ensure_ascii=False) + "\n")
        return evento

    def eventos(self) -> list[dict[str, Any]]:
        if not self.ruta.exists():
            return []
        with self.ruta.open(encoding="utf-8") as archivo:
            return [json.loads(linea) for linea in archivo if linea.strip()]

    def actuar(
        self,
        actor: str,
        zona: str,
        accion: str,
        ejecutar: Callable[[], Any],
        deshacer: Callable[[], Any] | None = None,
    ) -> dict[str, Any]:
        base = {"id": str(uuid4()), "momento": _ahora(), "tipo": "decision",
                "actor": actor, "zona": zona, "accion": accion}
        if not self.centinela.comprobar_acceso(actor, zona):
            self.guardian.despertar()
            return self._anotar({**base, "resultado": "bloqueada"})
        try:
            ejecutar()
        except Exception as error:
            revertida = False
            if deshacer is not None:
                try:
                    deshacer()
                    revertida = True
                except Exception:
                    revertida = False
            gravedad = "media" if revertida else "alta"
            self.centinela.buzon.enviar(Alarma(actor, "accion_fallida", zona, gravedad))
            self.guardian.despertar()
            return self._anotar({**base, "resultado": "revertida" if revertida else "fallida",
                                 "error": repr(error)})
        return self._anotar({**base, "resultado": "ejecutada",
                             "con_reversa": deshacer is not None})

    def registrar_desacuerdo(self, actores: Iterable[str], zona: str, motivo: str) -> str:
        deuda_id = str(uuid4())
        self._anotar({"id": deuda_id, "momento": _ahora(), "tipo": "deuda",
                      "actores": list(actores), "zona": zona, "motivo": motivo})
        return deuda_id

    def deudas_abiertas(self) -> list[dict[str, Any]]:
        eventos = self.eventos()
        saldadas = {e["deuda_id"] for e in eventos if e["tipo"] == "saldo"}
        return [e for e in eventos if e["tipo"] == "deuda" and e["id"] not in saldadas]

    def saldar(self, deuda_id: str, nota: str) -> bool:
        if not nota.strip() or deuda_id not in {d["id"] for d in self.deudas_abiertas()}:
            return False
        self._anotar({"id": str(uuid4()), "momento": _ahora(), "tipo": "saldo",
                      "deuda_id": deuda_id, "nota": nota})
        return True
