"""Memoria episódica y archivo de habilidades del Mundo Mental."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalizar(entrada: Iterable[Any]) -> list[Any]:
    return list(entrada)


def _similitud(a: list[Any], b: list[Any]) -> float:
    if not a or not b:
        return 0.0
    largo = max(len(a), len(b))
    iguales = sum(x == y for x, y in zip(a, b))
    return iguales / largo


class Biblioteca:
    """Guarda recuerdos en formatos sencillos, legibles y versionables."""

    def __init__(self, raiz: str | Path = ".mente"):
        self.raiz = Path(raiz)
        self.habilidades = self.raiz / "habilidades"
        self.planos = self.raiz / "planos"
        self.experiencias = self.raiz / "experiencias.jsonl"
        self.obras = self.raiz / "obras.jsonl"
        self.habilidades.mkdir(parents=True, exist_ok=True)
        self.planos.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _anexar(ruta: Path, registro: dict[str, Any]) -> None:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with ruta.open("a", encoding="utf-8") as archivo:
            archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")

    @staticmethod
    def _leer_jsonl(ruta: Path) -> list[dict[str, Any]]:
        if not ruta.exists():
            return []
        with ruta.open(encoding="utf-8") as archivo:
            return [json.loads(linea) for linea in archivo if linea.strip()]

    def recordar(
        self,
        entrada: Iterable[Any],
        respuesta: str,
        esperado: str,
        correcto: bool,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        identidad = str(uuid4())
        self._anexar(
            self.experiencias,
            {
                "id": identidad,
                "momento": _ahora(),
                "entrada": _normalizar(entrada),
                "respuesta": respuesta,
                "esperado": esperado,
                "correcto": bool(correcto),
                "metadata": metadata or {},
            },
        )
        return identidad

    def buscar_similares(self, entrada: Iterable[Any], limite: int = 5) -> list[dict[str, Any]]:
        objetivo = _normalizar(entrada)
        recuerdos = self._leer_jsonl(self.experiencias)
        for recuerdo in recuerdos:
            recuerdo["similitud"] = _similitud(objetivo, recuerdo["entrada"])
        recuerdos.sort(key=lambda x: (x["similitud"], x["momento"]), reverse=True)
        return recuerdos[: max(0, limite)]

    def guardar_habilidad(self, nombre: str, estado: dict[str, Any]) -> Path:
        ruta = self.habilidades / f"{nombre}.json"
        temporal = ruta.with_suffix(".tmp")
        temporal.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")
        temporal.replace(ruta)
        return ruta

    def cargar_habilidad(self, nombre: str) -> dict[str, Any] | None:
        ruta = self.habilidades / f"{nombre}.json"
        return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else None

    def registrar_obra(self, obra: dict[str, Any]) -> str:
        registro = dict(obra)
        registro.setdefault("id", str(uuid4()))
        registro.setdefault("momento", _ahora())
        self._anexar(self.obras, registro)
        return registro["id"]

    def historial_obras(self) -> list[dict[str, Any]]:
        return self._leer_jsonl(self.obras)
