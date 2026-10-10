"""Identidad ejecutable, vida interior y evolución reversible de los Aspectos."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class IdentidadAspecto:
    nombre: str
    esencia: str
    proposito: str
    perspectiva: str
    principios: tuple[str, ...]
    voz: str
    autoridad: tuple[str, ...] = ()
    limites: tuple[str, ...] = ()
    tensiones: tuple[str, ...] = ()
    relaciones: dict[str, str] = field(default_factory=dict)

    def validar(self) -> None:
        campos = (self.nombre, self.esencia, self.proposito, self.perspectiva, self.voz)
        if any(not valor.strip() for valor in campos):
            raise ValueError("La identidad no puede contener dimensiones esenciales vacías")
        if not self.principios:
            raise ValueError("Todo Aspecto necesita al menos un principio")
        if set(self.autoridad) & set(self.limites):
            raise ValueError("Una capacidad no puede ser autoridad y límite a la vez")

    def huella(self) -> dict[str, Any]:
        self.validar()
        return asdict(self)


@dataclass
class Compromiso:
    descripcion: str
    razon: str
    fuerza: float = 0.5
    activo: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))
    creado: str = field(default_factory=_ahora)


@dataclass
class PropuestaEvolucion:
    aspecto: str
    dimension: str
    valor_actual: Any
    valor_candidato: Any
    motivo: str
    evidencia: tuple[str, ...] = ()
    reversible: bool = True
    estado: str = "propuesta"
    id: str = field(default_factory=lambda: str(uuid4()))
    creada: str = field(default_factory=_ahora)


class MemoriaAutobiografica:
    def __init__(self, ruta: str | Path):
        self.ruta = Path(ruta)

    def recordar(self, aspecto: str, tipo: str, relato: str, datos: dict[str, Any] | None = None) -> str:
        identidad = str(uuid4())
        registro = {
            "id": identidad, "momento": _ahora(), "aspecto": aspecto,
            "tipo": tipo, "relato": relato, "datos": datos or {},
        }
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        with self.ruta.open("a", encoding="utf-8") as archivo:
            archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
        return identidad

    def historia(self, limite: int | None = None) -> list[dict[str, Any]]:
        if not self.ruta.exists():
            return []
        with self.ruta.open(encoding="utf-8") as archivo:
            recuerdos = [json.loads(linea) for linea in archivo if linea.strip()]
        return recuerdos[-limite:] if limite is not None else recuerdos


class Aspecto:
    """Ser funcional: núcleo identitario estable y personalidad que puede madurar."""

    def __init__(self, identidad: IdentidadAspecto, raiz: str | Path = ".mente"):
        identidad.validar()
        self.identidad = identidad
        self.memoria_de_si = MemoriaAutobiografica(
            Path(raiz) / "autobiografias" / f"{identidad.nombre.lower()}.jsonl"
        )
        self.estado_interno = "sereno"
        self.necesidades: dict[str, float] = {
            "coherencia": 0.5, "conexion": 0.5, "autonomia": 0.5, "reposo": 0.0,
        }
        self.disposiciones: dict[str, float] = {
            "apertura": 0.5, "cautela": 0.5, "persistencia": 0.5,
        }
        self.compromisos: list[Compromiso] = []
        self.evoluciones: list[PropuestaEvolucion] = []
        self.atendidos = 0
        self.ignorados = 0

    @property
    def nombre(self) -> str:
        return self.identidad.nombre

    def narrar(self, tipo: str, relato: str, **datos: Any) -> str:
        return self.memoria_de_si.recordar(self.nombre, tipo, relato, datos)

    def cambiar_estado(self, nuevo: str, motivo: str) -> None:
        anterior = self.estado_interno
        self.estado_interno = nuevo
        self.narrar("cambio_de_estado", f"Pasé de {anterior} a {nuevo}: {motivo}", anterior=anterior, nuevo=nuevo)

    def sentir(self, necesidad: str, intensidad: float, motivo: str) -> None:
        anterior = self.necesidades.get(necesidad, 0.0)
        valor = max(0.0, min(1.0, intensidad))
        self.necesidades[necesidad] = valor
        if abs(valor - anterior) >= 0.2:
            self.narrar("necesidad", f"{necesidad} cambió por {motivo}", anterior=anterior, nuevo=valor)

    def comprometerse(self, descripcion: str, razon: str, fuerza: float = 0.5) -> Compromiso:
        compromiso = Compromiso(descripcion, razon, max(0.0, min(1.0, fuerza)))
        self.compromisos.append(compromiso)
        self.narrar("compromiso", descripcion, razon=razon, fuerza=compromiso.fuerza, id=compromiso.id)
        return compromiso

    def proponer_evolucion(
        self, dimension: str, valor_candidato: Any, motivo: str,
        evidencia: tuple[str, ...] = (), reversible: bool = True,
    ) -> PropuestaEvolucion:
        if dimension in {"nombre", "esencia", "proposito", "principios", "limites"}:
            raise ValueError("El núcleo identitario no se altera mediante evolución ordinaria")
        if dimension not in self.disposiciones and dimension != "estado_interno":
            raise KeyError(f"Dimensión evolutiva desconocida: {dimension}")
        actual = self.estado_interno if dimension == "estado_interno" else self.disposiciones[dimension]
        propuesta = PropuestaEvolucion(
            self.nombre, dimension, actual, valor_candidato, motivo, evidencia, reversible
        )
        self.evoluciones.append(propuesta)
        self.narrar("propuesta_evolutiva", f"Considero cambiar {dimension}", propuesta=asdict(propuesta))
        return propuesta

    def ensayar_evolucion(self, propuesta_id: str) -> dict[str, Any]:
        propuesta = self._evolucion(propuesta_id)
        propuesta.estado = "en_ensayo"
        return {"dimension": propuesta.dimension, "antes": propuesta.valor_actual,
                "candidato": propuesta.valor_candidato, "reversible": propuesta.reversible}

    def consolidar_evolucion(self, propuesta_id: str, evidencia_resultado: str) -> None:
        propuesta = self._evolucion(propuesta_id)
        if propuesta.estado != "en_ensayo":
            raise RuntimeError("Una evolución debe ensayarse antes de consolidarse")
        if propuesta.dimension == "estado_interno":
            self.estado_interno = str(propuesta.valor_candidato)
        else:
            valor = float(propuesta.valor_candidato)
            self.disposiciones[propuesta.dimension] = max(0.0, min(1.0, valor))
        propuesta.estado = "consolidada"
        self.narrar("evolucion", f"Maduré en {propuesta.dimension}", evidencia=evidencia_resultado,
                    antes=propuesta.valor_actual, despues=propuesta.valor_candidato)

    def revertir_evolucion(self, propuesta_id: str, motivo: str) -> None:
        propuesta = self._evolucion(propuesta_id)
        if not propuesta.reversible:
            raise RuntimeError("La evolución fue declarada irreversible")
        if propuesta.estado == "consolidada":
            if propuesta.dimension == "estado_interno":
                self.estado_interno = str(propuesta.valor_actual)
            else:
                self.disposiciones[propuesta.dimension] = float(propuesta.valor_actual)
        propuesta.estado = "revertida"
        self.narrar("reversion_evolutiva", f"Revertí {propuesta.dimension}: {motivo}", propuesta=propuesta.id)

    def _evolucion(self, propuesta_id: str) -> PropuestaEvolucion:
        for propuesta in self.evoluciones:
            if propuesta.id == propuesta_id:
                return propuesta
        raise KeyError(propuesta_id)

    def valorar_impulso(self, impulso: Any) -> float:
        temas = set(getattr(impulso, "temas", ()))
        afinidad = 0.15
        texto_identidad = " ".join((self.identidad.esencia, self.identidad.proposito,
                                    self.identidad.perspectiva, *self.identidad.principios)).lower()
        afinidad += min(0.45, sum(0.15 for tema in temas if tema.lower() in texto_identidad))
        afinidad += 0.2 * float(getattr(impulso, "importancia", 0.0))
        afinidad += 0.2 * self.disposiciones["apertura"]
        return min(1.0, afinidad)

    def recibir_impulso(self, impulso: Any) -> dict[str, Any]:
        interes = self.valorar_impulso(impulso)
        umbral = 0.65 - 0.25 * self.disposiciones["apertura"]
        atendido = interes >= umbral
        if atendido:
            self.atendidos += 1
            if getattr(impulso, "importancia", 0.0) >= 0.8:
                self.narrar("impulso_significativo", f"Atendí {getattr(impulso, 'tipo', 'impulso')}",
                            impulso=getattr(impulso, "id", None), interes=interes)
        else:
            self.ignorados += 1
        return {"aspecto": self.nombre, "atendido": atendido, "interes": interes}

    def ficha(self) -> dict[str, Any]:
        return {
            "identidad": self.identidad.huella(),
            "estado_interno": self.estado_interno,
            "necesidades": dict(self.necesidades),
            "disposiciones": dict(self.disposiciones),
            "compromisos_activos": len([x for x in self.compromisos if x.activo]),
            "evoluciones": {estado: len([x for x in self.evoluciones if x.estado == estado])
                            for estado in {x.estado for x in self.evoluciones}},
            "atencion": {"atendidos": self.atendidos, "ignorados": self.ignorados},
            "recuerdos_autobiograficos": len(self.memoria_de_si.historia()),
        }
