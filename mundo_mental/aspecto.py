"""Identidad ejecutable, vida interior y evolución reversible de los Aspectos."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any
from uuid import uuid4


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _limitar(valor: float) -> float:
    return max(0.0, min(1.0, float(valor)))


def _normalizar(valor: Any) -> Any:
    """Devuelve la forma que tendría un valor tras guardarse y leerse como JSON."""
    return json.loads(json.dumps(valor, ensure_ascii=False))


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
    sensibilidades: dict[str, float] = field(default_factory=dict)

    def validar(self) -> None:
        campos = (self.nombre, self.esencia, self.proposito, self.perspectiva, self.voz)
        if any(not valor.strip() for valor in campos):
            raise ValueError("La identidad no puede contener dimensiones esenciales vacías")
        if not self.principios:
            raise ValueError("Todo Aspecto necesita al menos un principio")
        if set(self.autoridad) & set(self.limites):
            raise ValueError("Una capacidad no puede ser autoridad y límite a la vez")
        if any(not 0.0 <= float(valor) <= 1.0 for valor in self.sensibilidades.values()):
            raise ValueError("Las sensibilidades deben estar entre 0 y 1")

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
    cerrado: str | None = None


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
    resultado: str | None = None


@dataclass(frozen=True)
class ValoracionAtencion:
    interes: float
    umbral: float
    atendido: bool
    razones: tuple[str, ...]


class MemoriaAutobiografica:
    def __init__(self, ruta: str | Path):
        self.ruta = Path(ruta)
        self._cerrojo = RLock()

    def recordar(self, aspecto: str, tipo: str, relato: str, datos: dict[str, Any] | None = None) -> str:
        identidad = str(uuid4())
        registro = {
            "id": identidad, "momento": _ahora(), "aspecto": aspecto,
            "tipo": tipo, "relato": relato, "datos": datos or {},
        }
        with self._cerrojo:
            self.ruta.parent.mkdir(parents=True, exist_ok=True)
            with self.ruta.open("a", encoding="utf-8") as archivo:
                archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
        return identidad

    def historia(self, limite: int | None = None) -> list[dict[str, Any]]:
        with self._cerrojo:
            if not self.ruta.exists():
                return []
            with self.ruta.open(encoding="utf-8") as archivo:
                recuerdos = [json.loads(linea) for linea in archivo if linea.strip()]
        return recuerdos[-limite:] if limite is not None else recuerdos


class Aspecto:
    """Ser funcional con núcleo estable y personalidad persistente que puede madurar."""

    DIMENSIONES_NUCLEARES = {"nombre", "esencia", "proposito", "perspectiva", "principios", "limites"}

    def __init__(self, identidad: IdentidadAspecto, raiz: str | Path = ".mente"):
        identidad.validar()
        self.identidad = identidad
        self.raiz = Path(raiz)
        nombre_archivo = identidad.nombre.lower().replace(" ", "_")
        self.memoria_de_si = MemoriaAutobiografica(
            self.raiz / "autobiografias" / f"{nombre_archivo}.jsonl"
        )
        self._estado = self.raiz / "identidades" / f"{nombre_archivo}.json"
        self._cerrojo = RLock()
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
        self._restaurar_estado()

    @property
    def nombre(self) -> str:
        return self.identidad.nombre

    def narrar(self, tipo: str, relato: str, **datos: Any) -> str:
        return self.memoria_de_si.recordar(self.nombre, tipo, relato, datos)

    def cambiar_estado(self, nuevo: str, motivo: str) -> None:
        if not nuevo.strip():
            raise ValueError("El estado no puede estar vacío")
        anterior = self.estado_interno
        if anterior == nuevo:
            return
        self.estado_interno = nuevo
        self.narrar("cambio_de_estado", f"Pasé de {anterior} a {nuevo}: {motivo}", anterior=anterior, nuevo=nuevo)
        self._persistir_estado()

    def sentir(self, necesidad: str, intensidad: float, motivo: str) -> None:
        anterior = self.necesidades.get(necesidad, 0.0)
        valor = _limitar(intensidad)
        self.necesidades[necesidad] = valor
        if abs(valor - anterior) >= 0.2:
            self.narrar("necesidad", f"{necesidad} cambió por {motivo}", anterior=anterior, nuevo=valor)
        self._persistir_estado()

    def comprometerse(self, descripcion: str, razon: str, fuerza: float = 0.5) -> Compromiso:
        if not descripcion.strip() or not razon.strip():
            raise ValueError("Un compromiso necesita descripción y razón")
        compromiso = Compromiso(descripcion, razon, _limitar(fuerza))
        self.compromisos.append(compromiso)
        self.narrar("compromiso", descripcion, razon=razon, fuerza=compromiso.fuerza, id=compromiso.id)
        self._persistir_estado()
        return compromiso

    def liberar_compromiso(self, compromiso_id: str, motivo: str) -> None:
        compromiso = next((x for x in self.compromisos if x.id == compromiso_id), None)
        if compromiso is None:
            raise KeyError(compromiso_id)
        if not compromiso.activo:
            return
        compromiso.activo = False
        compromiso.cerrado = _ahora()
        self.narrar("compromiso_cerrado", compromiso.descripcion, motivo=motivo, id=compromiso.id)
        self._persistir_estado()

    def proponer_evolucion(
        self, dimension: str, valor_candidato: Any, motivo: str,
        evidencia: tuple[str, ...] = (), reversible: bool = True,
    ) -> PropuestaEvolucion:
        if dimension in self.DIMENSIONES_NUCLEARES:
            raise ValueError("El núcleo identitario no se altera mediante evolución ordinaria")
        if not reversible:
            raise ValueError("La evolución ordinaria debe ser reversible")
        if dimension not in self.disposiciones and dimension != "estado_interno":
            raise KeyError(f"Dimensión evolutiva desconocida: {dimension}")
        actual = self.estado_interno if dimension == "estado_interno" else self.disposiciones[dimension]
        propuesta = PropuestaEvolucion(
            self.nombre, dimension, actual, valor_candidato, motivo, tuple(evidencia), True
        )
        self.evoluciones.append(propuesta)
        self.narrar("propuesta_evolutiva", f"Considero cambiar {dimension}", propuesta=asdict(propuesta))
        self._persistir_estado()
        return propuesta

    def ensayar_evolucion(self, propuesta_id: str) -> dict[str, Any]:
        propuesta = self._evolucion(propuesta_id)
        if propuesta.estado != "propuesta":
            raise RuntimeError("Solo una propuesta pendiente puede entrar en ensayo")
        propuesta.estado = "en_ensayo"
        self.narrar("ensayo_evolutivo", f"Ensayo {propuesta.dimension}", propuesta=propuesta.id)
        self._persistir_estado()
        return {"dimension": propuesta.dimension, "antes": propuesta.valor_actual,
                "candidato": propuesta.valor_candidato, "reversible": propuesta.reversible}

    def consolidar_evolucion(self, propuesta_id: str, evidencia_resultado: str) -> None:
        propuesta = self._evolucion(propuesta_id)
        if propuesta.estado != "en_ensayo":
            raise RuntimeError("Una evolución debe ensayarse antes de consolidarse")
        if not evidencia_resultado.strip():
            raise ValueError("La consolidación necesita evidencia del resultado")
        if propuesta.dimension == "estado_interno":
            self.estado_interno = str(propuesta.valor_candidato)
        else:
            self.disposiciones[propuesta.dimension] = _limitar(float(propuesta.valor_candidato))
        propuesta.estado = "consolidada"
        propuesta.resultado = evidencia_resultado
        self.narrar("evolucion", f"Maduré en {propuesta.dimension}", evidencia=evidencia_resultado,
                    antes=propuesta.valor_actual, despues=propuesta.valor_candidato,
                    propuesta=propuesta.id)
        self._persistir_estado()

    def revertir_evolucion(self, propuesta_id: str, motivo: str) -> None:
        propuesta = self._evolucion(propuesta_id)
        if not propuesta.reversible:
            raise RuntimeError("La evolución fue declarada irreversible")
        if propuesta.estado == "revertida":
            return
        if propuesta.estado == "consolidada":
            if propuesta.dimension == "estado_interno":
                self.estado_interno = str(propuesta.valor_actual)
            else:
                self.disposiciones[propuesta.dimension] = _limitar(float(propuesta.valor_actual))
        propuesta.estado = "revertida"
        propuesta.resultado = motivo
        self.narrar("reversion_evolutiva", f"Revertí {propuesta.dimension}: {motivo}", propuesta=propuesta.id)
        self._persistir_estado()

    def _evolucion(self, propuesta_id: str) -> PropuestaEvolucion:
        for propuesta in self.evoluciones:
            if propuesta.id == propuesta_id:
                return propuesta
        raise KeyError(propuesta_id)

    def evaluar_impulso(self, impulso: Any) -> ValoracionAtencion:
        tipo = str(getattr(impulso, "tipo", "")).lower()
        temas = {str(x).lower() for x in getattr(impulso, "temas", ())}
        claves = {tipo, *temas}
        sensibilidad = max((float(self.identidad.sensibilidades.get(x, 0.0)) for x in claves), default=0.0)
        palabras = " ".join((self.identidad.esencia, self.identidad.proposito,
                              self.identidad.perspectiva, *self.identidad.principios)).lower()
        coincidencias = sum(1 for clave in claves if clave and clave.replace("_", " ") in palabras)
        importancia = _limitar(getattr(impulso, "importancia", 0.0))
        dirigido = getattr(impulso, "destino", None) == self.nombre
        interes = min(1.0, 0.08 + 0.34 * sensibilidad + 0.22 * importancia
                      + 0.16 * self.disposiciones["apertura"]
                      + 0.08 * (1.0 - self.disposiciones["cautela"])
                      + min(0.08, coincidencias * 0.04) + (0.18 if dirigido else 0.0))
        umbral = _limitar(0.50 + 0.16 * self.disposiciones["cautela"]
                          - 0.16 * self.disposiciones["apertura"])
        razones = [f"importancia={importancia:.2f}", f"sensibilidad={sensibilidad:.2f}"]
        if coincidencias:
            razones.append(f"afinidad_identitaria={coincidencias}")
        if dirigido:
            razones.append("destino_explicito")
        return ValoracionAtencion(round(interes, 6), round(umbral, 6), interes >= umbral, tuple(razones))

    def valorar_impulso(self, impulso: Any) -> float:
        return self.evaluar_impulso(impulso).interes

    def recibir_impulso(self, impulso: Any) -> dict[str, Any]:
        valoracion = self.evaluar_impulso(impulso)
        if valoracion.atendido:
            self.atendidos += 1
            if getattr(impulso, "importancia", 0.0) >= 0.8:
                self.narrar("impulso_significativo", f"Atendí {getattr(impulso, 'tipo', 'impulso')}",
                            impulso=getattr(impulso, "id", None), interes=valoracion.interes,
                            razones=valoracion.razones)
        else:
            self.ignorados += 1
        self._persistir_estado()
        return {"aspecto": self.nombre, "atendido": valoracion.atendido,
                "interes": valoracion.interes,
                "detalle": ";".join(valoracion.razones)}

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

    def _persistir_estado(self) -> None:
        contenido = {
            "version": 1,
            "nucleo": _normalizar(self.identidad.huella()),
            "estado_interno": self.estado_interno,
            "necesidades": self.necesidades,
            "disposiciones": self.disposiciones,
            "compromisos": [asdict(x) for x in self.compromisos],
            "evoluciones": [asdict(x) for x in self.evoluciones],
            "atendidos": self.atendidos,
            "ignorados": self.ignorados,
        }
        with self._cerrojo:
            self._estado.parent.mkdir(parents=True, exist_ok=True)
            temporal = self._estado.with_suffix(".tmp")
            temporal.write_text(json.dumps(contenido, ensure_ascii=False, indent=2), encoding="utf-8")
            temporal.replace(self._estado)

    def _restaurar_estado(self) -> None:
        if not self._estado.exists():
            return
        contenido = json.loads(self._estado.read_text(encoding="utf-8"))
        nucleo_guardado = contenido.get("nucleo", {})
        if nucleo_guardado and nucleo_guardado != _normalizar(self.identidad.huella()):
            raise RuntimeError(f"La identidad persistida de {self.nombre} no coincide con su núcleo actual")
        self.estado_interno = str(contenido.get("estado_interno", self.estado_interno))
        self.necesidades.update({k: _limitar(v) for k, v in contenido.get("necesidades", {}).items()})
        self.disposiciones.update({k: _limitar(v) for k, v in contenido.get("disposiciones", {}).items()})
        self.compromisos = [Compromiso(**x) for x in contenido.get("compromisos", [])]
        self.evoluciones = [PropuestaEvolucion(**{**x, "evidencia": tuple(x.get("evidencia", ()))})
                            for x in contenido.get("evoluciones", [])]
        self.atendidos = int(contenido.get("atendidos", 0))
        self.ignorados = int(contenido.get("ignorados", 0))
