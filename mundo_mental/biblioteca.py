"""Biblioteca 0.2: memoria episódica, semántica y procedimental."""

from __future__ import annotations

import json
from collections import defaultdict
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
    iguales = sum(x == y for x, y in zip(a, b))
    return iguales / max(len(a), len(b))


def _limitar(valor: float) -> float:
    return round(max(0.0, min(1.0, float(valor))), 6)


class Biblioteca:
    """Recuerda episodios, consolida conceptos y conserva habilidades versionadas."""

    VERSION = "0.2.0"

    def __init__(self, raiz: str | Path = ".mente"):
        self.raiz = Path(raiz)
        self.habilidades = self.raiz / "habilidades"
        self.archivo_habilidades = self.habilidades / "versiones"
        self.planos = self.raiz / "planos"
        self.experiencias = self.raiz / "experiencias.jsonl"
        self.obras = self.raiz / "obras.jsonl"
        self.conceptos = self.raiz / "conceptos.json"
        for sala in (self.habilidades, self.archivo_habilidades, self.planos):
            sala.mkdir(parents=True, exist_ok=True)

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

    @staticmethod
    def _reescribir_jsonl(ruta: Path, registros: list[dict[str, Any]]) -> None:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = ruta.with_suffix(ruta.suffix + ".tmp")
        with temporal.open("w", encoding="utf-8") as archivo:
            for registro in registros:
                archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
        temporal.replace(ruta)

    def recordar(
        self,
        entrada: Iterable[Any],
        respuesta: str,
        esperado: str,
        correcto: bool,
        metadata: dict[str, Any] | None = None,
        importancia: float | None = None,
        protegido: bool = False,
    ) -> str:
        patron = _normalizar(entrada)
        metadata = metadata or {}
        anteriores = self._leer_jsonl(self.experiencias)
        parecido = max((_similitud(patron, x["entrada"]) for x in anteriores), default=0.0)
        novedad = 1.0 - parecido
        confianza = float(metadata.get("confianza", 0.5))
        sorpresa = 1.0 - confianza if correcto else confianza
        if importancia is None:
            importancia = (0.55 if not correcto else 0.20) + 0.30 * novedad + 0.15 * sorpresa
        identidad = str(uuid4())
        self._anexar(
            self.experiencias,
            {
                "id": identidad,
                "momento": _ahora(),
                "entrada": patron,
                "respuesta": respuesta,
                "esperado": esperado,
                "correcto": bool(correcto),
                "importancia": _limitar(importancia),
                "novedad": _limitar(novedad),
                "protegido": bool(protegido),
                "accesos": 0,
                "repeticiones": 1,
                "ultimo_acceso": None,
                "metadata": metadata,
            },
        )
        return identidad

    def buscar_similares(
        self,
        entrada: Iterable[Any],
        limite: int = 5,
        esperado: str | None = None,
        explicar: bool = True,
    ) -> list[dict[str, Any]]:
        objetivo = _normalizar(entrada)
        recuerdos = self._leer_jsonl(self.experiencias)
        candidatos = [x for x in recuerdos if esperado is None or x["esperado"] == esperado]
        for recuerdo in candidatos:
            similitud = _similitud(objetivo, recuerdo["entrada"])
            recuerdo["similitud"] = _limitar(similitud)
            recuerdo["puntuacion_recuperacion"] = _limitar(
                0.70 * similitud + 0.20 * recuerdo.get("importancia", 0.5) + 0.10 * int(recuerdo["correcto"])
            )
            if explicar:
                coincidencias = sum(a == b for a, b in zip(objetivo, recuerdo["entrada"]))
                recuerdo["explicacion"] = (
                    f"Coinciden {coincidencias} de {max(len(objetivo), len(recuerdo['entrada']))} "
                    f"posiciones; importancia {recuerdo.get('importancia', 0.5):.0%}."
                )
        candidatos.sort(
            key=lambda x: (x["puntuacion_recuperacion"], x["momento"]), reverse=True
        )
        elegidos = [dict(recuerdo) for recuerdo in candidatos[: max(0, limite)]]
        ids = {x["id"] for x in elegidos}
        if ids:
            momento = _ahora()
            for recuerdo in recuerdos:
                if recuerdo["id"] in ids:
                    recuerdo["accesos"] = recuerdo.get("accesos", 0) + 1
                    recuerdo["ultimo_acceso"] = momento
            self._reescribir_jsonl(self.experiencias, recuerdos)
        return elegidos

    def consolidar(self, minimo_ejemplos: int = 2) -> dict[str, dict[str, Any]]:
        """Convierte varios episodios en conceptos resumidos sin borrar los originales."""
        grupos: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for recuerdo in self._leer_jsonl(self.experiencias):
            grupos[recuerdo["esperado"]].append(recuerdo)
        conceptos: dict[str, dict[str, Any]] = {}
        for nombre, episodios in grupos.items():
            unicos = {json.dumps(x["entrada"], ensure_ascii=False) for x in episodios}
            if len(unicos) < minimo_ejemplos:
                continue
            longitudes = {len(x["entrada"]) for x in episodios}
            rasgos = []
            if len(longitudes) == 1:
                for posicion in range(next(iter(longitudes))):
                    valores = {x["entrada"][posicion] for x in episodios}
                    rasgos.append(next(iter(valores)) if len(valores) == 1 else "*")
            conceptos[nombre] = {
                "nombre": nombre,
                "episodios": len(episodios),
                "ejemplos_unicos": len(unicos),
                "fiabilidad": _limitar(sum(x["correcto"] for x in episodios) / len(episodios)),
                "rasgos_comunes": rasgos,
                "actualizado": _ahora(),
            }
        temporal = self.conceptos.with_suffix(".tmp")
        temporal.write_text(json.dumps(conceptos, ensure_ascii=False, indent=2), encoding="utf-8")
        temporal.replace(self.conceptos)
        return conceptos

    def cargar_conceptos(self) -> dict[str, dict[str, Any]]:
        if not self.conceptos.exists():
            return {}
        return json.loads(self.conceptos.read_text(encoding="utf-8"))

    def depurar(self, max_recuerdos: int | None = None) -> dict[str, int]:
        """Fusiona duplicados y, opcionalmente, limita recuerdos sin borrar protegidos."""
        recuerdos = self._leer_jsonl(self.experiencias)
        fusionados: dict[tuple[str, str], dict[str, Any]] = {}
        for recuerdo in recuerdos:
            clave = (json.dumps(recuerdo["entrada"], ensure_ascii=False), recuerdo["esperado"])
            if clave not in fusionados:
                fusionados[clave] = recuerdo
                continue
            actual = fusionados[clave]
            actual["repeticiones"] = actual.get("repeticiones", 1) + recuerdo.get("repeticiones", 1)
            actual["accesos"] = actual.get("accesos", 0) + recuerdo.get("accesos", 0)
            actual["protegido"] = actual.get("protegido", False) or recuerdo.get("protegido", False)
            if recuerdo.get("importancia", 0) > actual.get("importancia", 0):
                recuerdo["repeticiones"] = actual["repeticiones"]
                recuerdo["accesos"] = actual["accesos"]
                recuerdo["protegido"] = actual["protegido"]
                fusionados[clave] = recuerdo
        salida = list(fusionados.values())
        if max_recuerdos is not None and len(salida) > max_recuerdos:
            protegidos = [x for x in salida if x.get("protegido")]
            libres = [x for x in salida if not x.get("protegido")]
            libres.sort(
                key=lambda x: (not x["correcto"], x.get("importancia", 0), x.get("accesos", 0)),
                reverse=True,
            )
            salida = protegidos + libres[: max(0, max_recuerdos - len(protegidos))]
        salida.sort(key=lambda x: x["momento"])
        self._reescribir_jsonl(self.experiencias, salida)
        return {"antes": len(recuerdos), "despues": len(salida), "fusionados": len(recuerdos) - len(salida)}

    def guardar_habilidad(self, nombre: str, estado: dict[str, Any]) -> Path:
        ruta = self.habilidades / f"{nombre}.json"
        if ruta.exists():
            version = len(list(self.archivo_habilidades.glob(f"{nombre}-*.json"))) + 1
            copia = self.archivo_habilidades / f"{nombre}-{version:04d}.json"
            copia.write_text(ruta.read_text(encoding="utf-8"), encoding="utf-8")
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

    def consultar_obras(
        self, habilidad: str | None = None, tipo: str | None = None, limite: int = 5
    ) -> list[dict[str, Any]]:
        obras = self.historial_obras()
        obras = [
            x for x in obras
            if (habilidad is None or x.get("habilidad") == habilidad)
            and (tipo is None or x.get("tipo") == tipo)
        ]
        obras.sort(
            key=lambda x: (x.get("aceptada", False), x.get("precision_candidata", 0), x["momento"]),
            reverse=True,
        )
        return obras[: max(0, limite)]

    def estado(self) -> dict[str, Any]:
        recuerdos = self._leer_jsonl(self.experiencias)
        return {
            "version": self.VERSION,
            "episodios": len(recuerdos),
            "conceptos": len(self.cargar_conceptos()),
            "habilidades": len([x for x in self.habilidades.glob("*.json")]),
            "versiones_archivadas": len(list(self.archivo_habilidades.glob("*.json"))),
            "obras": len(self.historial_obras()),
            "recuerdos_protegidos": sum(x.get("protegido", False) for x in recuerdos),
        }
