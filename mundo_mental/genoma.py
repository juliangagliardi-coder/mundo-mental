"""Genoma: memoria histórica compacta, verificable y reconstruible por tramos.

No inventa huecos: reconstruye únicamente desde un punto de anclaje y deltas
versionados. Dos réplicas y el Vigilante protegen su integridad.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonico(valor: Any) -> str:
    return json.dumps(valor, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(valor: Any) -> str:
    return sha256(_canonico(valor).encode("utf-8")).hexdigest()


def _mezclar(estado: dict[str, Any], cambio: dict[str, Any]) -> dict[str, Any]:
    """Aplica un delta plano, explícito y determinista sobre un estado serializable."""
    resultado = dict(estado)
    for clave, valor in cambio.items():
        if valor is None:
            resultado.pop(clave, None)
        else:
            resultado[clave] = valor
    return resultado


@dataclass(frozen=True)
class Hito:
    id: str
    zona: str
    tipo: str
    momento: str
    cambio: dict[str, Any]
    ancla: bool
    estado_hash: str
    anterior_hash: str
    motor_version: str = "genoma-01"
    contexto: dict[str, Any] = field(default_factory=dict)
    hash: str = ""

    def con_hash(self) -> "Hito":
        datos = asdict(self)
        datos["hash"] = ""
        return Hito(**{**datos, "hash": _hash(datos)})


class Genoma:
    """Archivo de solo añadir con anclas estratégicas y réplicas verificables."""

    def __init__(self, raiz: str | Path = ".mente", intervalo_anclas: int = 12):
        if intervalo_anclas < 1:
            raise ValueError("El intervalo de anclas debe ser positivo")
        self.raiz = Path(raiz) / "genoma"
        self.intervalo_anclas = intervalo_anclas
        self.rutas = (self.raiz / "primaria.jsonl", self.raiz / "respaldo.jsonl")

    def _leer_ruta(self, ruta: Path) -> list[Hito]:
        if not ruta.exists():
            return []
        with ruta.open(encoding="utf-8") as archivo:
            return [Hito(**json.loads(linea)) for linea in archivo if linea.strip()]

    def hitos(self) -> list[Hito]:
        primaria = self._leer_ruta(self.rutas[0])
        respaldo = self._leer_ruta(self.rutas[1])
        if primaria and self.verificar(primaria):
            return primaria
        if respaldo and self.verificar(respaldo):
            return respaldo
        return primaria or respaldo

    def _escribir_en_ambas(self, hito: Hito) -> None:
        for ruta in self.rutas:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            with ruta.open("a", encoding="utf-8") as archivo:
                archivo.write(_canonico(asdict(hito)) + "\n")

    def registrar(
        self,
        zona: str,
        tipo: str,
        cambio: dict[str, Any],
        *,
        importante: bool = False,
        contexto: dict[str, Any] | None = None,
        motor_version: str = "genoma-01",
    ) -> Hito:
        if not zona or not tipo:
            raise ValueError("Todo hito necesita zona y tipo")
        if not isinstance(cambio, dict):
            raise TypeError("El cambio debe ser un diccionario serializable")
        anteriores = self.hitos()
        estado_anterior = self.reconstruir(anteriores) if anteriores else {}
        estado = _mezclar(estado_anterior, cambio)
        ancla = not anteriores or importante or len(anteriores) % self.intervalo_anclas == 0
        contenido = estado if ancla else cambio
        previo = anteriores[-1].hash if anteriores else "0" * 64
        hito = Hito(
            id=str(uuid4()), zona=zona, tipo=tipo, momento=_ahora(), cambio=contenido,
            ancla=ancla, estado_hash=_hash(estado), anterior_hash=previo,
            motor_version=motor_version, contexto=contexto or {},
        ).con_hash()
        self._escribir_en_ambas(hito)
        return hito

    @staticmethod
    def verificar(hitos: list[Hito]) -> bool:
        estado: dict[str, Any] = {}
        previo = "0" * 64
        for hito in hitos:
            if hito.anterior_hash != previo or hito.con_hash().hash != hito.hash:
                return False
            estado = dict(hito.cambio) if hito.ancla else _mezclar(estado, hito.cambio)
            if _hash(estado) != hito.estado_hash:
                return False
            previo = hito.hash
        return True

    @staticmethod
    def reconstruir(hitos: list[Hito]) -> dict[str, Any]:
        if not hitos:
            return {}
        if not Genoma.verificar(hitos):
            raise ValueError("No se puede reconstruir un Genoma no verificable")
        inicio = max(indice for indice, hito in enumerate(hitos) if hito.ancla)
        estado = dict(hitos[inicio].cambio)
        for hito in hitos[inicio + 1:]:
            estado = _mezclar(estado, hito.cambio)
        return estado

    def auditar(self) -> dict[str, Any]:
        primaria, respaldo = (self._leer_ruta(ruta) for ruta in self.rutas)
        return {
            "primaria_valida": self.verificar(primaria),
            "respaldo_valido": self.verificar(respaldo),
            "replicas_coinciden": [_hash(asdict(x)) for x in primaria] == [_hash(asdict(x)) for x in respaldo],
            "hitos": len(self.hitos()),
        }

    def reparar(self) -> bool:
        primaria, respaldo = (self._leer_ruta(ruta) for ruta in self.rutas)
        fuente = primaria if self.verificar(primaria) else respaldo
        destino = self.rutas[1] if fuente is primaria else self.rutas[0]
        if not self.verificar(fuente):
            return False
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open("w", encoding="utf-8") as archivo:
            for hito in fuente:
                archivo.write(_canonico(asdict(hito)) + "\n")
        return True


class Vigilante:
    """Centinela independiente del Genoma: detecta y repara réplicas dañadas."""

    def __init__(self, genoma: Genoma):
        self.genoma = genoma
        self.revisiones: list[dict[str, Any]] = []

    def revisar(self, reparar: bool = True) -> dict[str, Any]:
        informe = self.genoma.auditar()
        sano = informe["primaria_valida"] and informe["respaldo_valido"] and informe["replicas_coinciden"]
        if not sano and reparar:
            informe["reparado"] = self.genoma.reparar()
            informe.update(self.genoma.auditar())
        else:
            informe["reparado"] = False
        informe["momento"] = _ahora()
        self.revisiones.append(informe)
        return informe
