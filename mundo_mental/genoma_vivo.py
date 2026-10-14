"""Genoma Vivo: memoria por generaciones con olvido gradual, autoridad automatica y Vigilante activo.

Lo fundamental no se olvida nunca: origen, hitos, conocimiento de Biblioteca, decisiones,
incidentes graves e identidad. Los detalles menores pierden precision con las generaciones,
salvo que se usen o corroboren. Del olvido solo queda una huella verificable.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from .genoma import Genoma, Vigilante, _ahora, _hash

PROTEGIDAS = frozenset({"origen", "hito", "biblioteca", "decision", "incidente_grave", "identidad"})
FUNDACIONALES = frozenset({"origen", "hito", "identidad"})
RELEVANCIA_BASE = {"incidente": 1.0, "contexto": 0.5, "detalle": 0.2}
CATEGORIAS = PROTEGIDAS | set(RELEVANCIA_BASE)


@dataclass
class Recuerdo:
    id: str
    categoria: str
    generacion: int
    momento: str
    contenido: dict[str, Any]
    huella: str
    nivel: int = 0
    relevancia: float = 0.0
    usos: int = 0
    protegido: bool = False


def _resumir(contenido: dict[str, Any]) -> dict[str, Any]:
    resumen = {k: str(contenido[k])[:60] for k in sorted(contenido)[:3]}
    resumen["_resumido"] = True
    return resumen


class MemoriaViva:
    """Recuerdos clasificados por generacion con olvido progresivo y protecciones."""

    def __init__(self, raiz: str | Path = ".mente", genoma: Genoma | None = None, *,
                 generaciones_detalle: int = 3, generaciones_olvido: int = 8,
                 umbral_proteccion: float = 3.0, ciclos_por_generacion: int = 100,
                 decaimiento: float = 0.9):
        if not 0 < generaciones_detalle < generaciones_olvido:
            raise ValueError("Se requiere 0 < generaciones_detalle < generaciones_olvido")
        if ciclos_por_generacion < 1 or not 0 < decaimiento <= 1:
            raise ValueError("Parametros de generacion o decaimiento invalidos")
        self.ruta = Path(raiz) / "memoria" / "recuerdos.json"
        self.genoma = genoma or Genoma(raiz)
        self.generaciones_detalle = generaciones_detalle
        self.generaciones_olvido = generaciones_olvido
        self.umbral_proteccion = umbral_proteccion
        self.ciclos_por_generacion = ciclos_por_generacion
        self.decaimiento = decaimiento
        self.generacion = 0
        self.ciclos = 0
        self.recuerdos: dict[str, Recuerdo] = {}
        self._cargar()

    def _cargar(self) -> None:
        if not self.ruta.exists():
            return
        datos = json.loads(self.ruta.read_text(encoding="utf-8"))
        self.generacion, self.ciclos = datos["generacion"], datos["ciclos"]
        self.recuerdos = {r["id"]: Recuerdo(**r) for r in datos["recuerdos"]}

    def _guardar(self) -> None:
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = self.ruta.with_suffix(".tmp")
        datos = {"generacion": self.generacion, "ciclos": self.ciclos,
                 "recuerdos": [asdict(r) for r in self.recuerdos.values()]}
        temporal.write_text(json.dumps(datos, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        os.replace(temporal, self.ruta)

    def recordar(self, categoria: str, contenido: dict[str, Any], relevancia: float | None = None) -> Recuerdo:
        if categoria not in CATEGORIAS:
            raise ValueError(f"Categoria desconocida: {categoria}")
        if not isinstance(contenido, dict):
            raise TypeError("El contenido debe ser un diccionario serializable")
        protegido = categoria in PROTEGIDAS
        base = RELEVANCIA_BASE.get(categoria, self.umbral_proteccion) if relevancia is None else relevancia
        recuerdo = Recuerdo(id=str(uuid4()), categoria=categoria, generacion=self.generacion,
                            momento=_ahora(), contenido=dict(contenido), huella=_hash(contenido),
                            relevancia=base, protegido=protegido or base >= self.umbral_proteccion)
        self.recuerdos[recuerdo.id] = recuerdo
        if protegido:
            self.genoma.registrar("memoria", categoria, {f"recuerdo.{recuerdo.id}": recuerdo.huella},
                                  importante=categoria in FUNDACIONALES,
                                  contexto={"generacion": self.generacion})
        self._guardar()
        return recuerdo

    def _reforzar(self, id: str, puntos: float) -> Recuerdo:
        recuerdo = self.recuerdos[id]
        recuerdo.relevancia += puntos
        recuerdo.usos += 1
        if recuerdo.relevancia >= self.umbral_proteccion:
            recuerdo.protegido = True
        self._guardar()
        return recuerdo

    def usar(self, id: str) -> Recuerdo:
        return self._reforzar(id, 1.0)

    def corroborar(self, id: str) -> Recuerdo:
        return self._reforzar(id, 1.5)

    def consultar(self, categoria: str | None = None) -> list[Recuerdo]:
        return [r for r in self.recuerdos.values() if categoria is None or r.categoria == categoria]

    def olvidar(self) -> dict[str, int]:
        resumidos = olvidados = 0
        for recuerdo in self.recuerdos.values():
            if recuerdo.protegido:
                continue
            recuerdo.relevancia *= self.decaimiento
            edad = self.generacion - recuerdo.generacion
            if edad >= self.generaciones_olvido and recuerdo.nivel < 2:
                recuerdo.contenido, recuerdo.nivel = {}, 2
                olvidados += 1
            elif edad >= self.generaciones_detalle and recuerdo.nivel < 1:
                recuerdo.contenido, recuerdo.nivel = _resumir(recuerdo.contenido), 1
                resumidos += 1
        return {"resumidos": resumidos, "olvidados": olvidados}

    def cerrar_generacion(self) -> dict[str, Any]:
        self.generacion += 1
        olvido = self.olvidar()
        niveles = [r.nivel for r in self.recuerdos.values()]
        resumen = {"generacion": self.generacion, "recuerdos": len(niveles),
                   "completos": niveles.count(0), "resumidos": niveles.count(1),
                   "olvidados": niveles.count(2),
                   "protegidos": sum(r.protegido for r in self.recuerdos.values()), **olvido}
        self.genoma.registrar("memoria", "generacion", {f"generacion.{self.generacion}": resumen},
                              importante=True, contexto={"generacion": self.generacion})
        self._guardar()
        return resumen

    def contar_ciclo(self) -> dict[str, Any] | None:
        self.ciclos += 1
        if self.ciclos % self.ciclos_por_generacion == 0:
            return self.cerrar_generacion()
        self._guardar()
        return None


class Autoridad:
    """Corazon y Observacion deciden sin consulta humana. Observacion veta; ante error, se bloquea."""

    def __init__(self, genoma: Genoma, corazon: Callable[[dict], bool], observacion: Callable[[dict], bool]):
        self.genoma, self.corazon, self.observacion = genoma, corazon, observacion

    def resolver(self, propuesta: dict[str, Any]) -> dict[str, Any]:
        try:
            if not self.observacion(propuesta):
                veredicto, decide = "bloqueada", "observacion"
            elif self.corazon(propuesta):
                veredicto, decide = "aprobada", "corazon"
            else:
                veredicto, decide = "rechazada", "corazon"
        except Exception as error:
            veredicto, decide = "bloqueada", f"error:{type(error).__name__}"
        resultado = {"id": str(uuid4()), "veredicto": veredicto, "decide": decide, "propuesta": propuesta}
        self.genoma.registrar("autoridad", "decision",
                              {f"decision.{resultado['id']}": {"veredicto": veredicto, "decide": decide}},
                              contexto={"propuesta": _hash(propuesta)})
        return resultado


class VigilanteActivo:
    """Vigilante que repara y avisa a Observacion mediante una alarma."""

    def __init__(self, vigilante: Vigilante, alarma: Callable[[dict], None]):
        self.vigilante, self.alarma = vigilante, alarma

    @staticmethod
    def _sano(informe: dict[str, Any]) -> bool:
        return bool(informe["primaria_valida"] and informe["respaldo_valido"] and informe["replicas_coinciden"])

    def vigilar(self) -> dict[str, Any]:
        previo = self.vigilante.genoma.auditar()
        informe = self.vigilante.revisar(reparar=True)
        if not self._sano(informe):
            self.alarma({"gravedad": "critica", "motivo": "genoma_no_recuperable", "informe": informe})
        elif not self._sano(previo):
            self.alarma({"gravedad": "media", "motivo": "replica_reparada", "informe": informe})
        return informe
