"""Observación reactiva: Centinela barato y Guardián despertable."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .aspecto import Aspecto, IdentidadAspecto


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Alarma:
    actor: str
    motivo: str
    zona: str
    gravedad: str = "media"
    ultimo_punto_seguro: str | None = None
    evidencias: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: str(uuid4()))
    momento: str = field(default_factory=_ahora)

    def validar(self) -> None:
        if self.gravedad not in {"baja", "media", "alta", "critica"}:
            raise ValueError("Gravedad de alarma desconocida")
        if not self.actor or not self.motivo or not self.zona:
            raise ValueError("La alarma necesita actor, motivo y zona")


class BuzonAlarmas:
    def __init__(self, ruta: str | Path):
        self.ruta = Path(ruta)

    def enviar(self, alarma: Alarma) -> str:
        alarma.validar()
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        with self.ruta.open("a", encoding="utf-8") as archivo:
            archivo.write(json.dumps(asdict(alarma), ensure_ascii=False) + "\n")
        return alarma.id

    def leer(self, desde: int = 0) -> list[Alarma]:
        if not self.ruta.exists():
            return []
        with self.ruta.open(encoding="utf-8") as archivo:
            lineas = [linea for linea in archivo if linea.strip()]
        return [Alarma(**json.loads(linea)) for linea in lineas[desde:]]


class Centinela:
    """No interpreta ideas: comprueba señales simples y despierta al Guardián."""

    def __init__(self, buzon: BuzonAlarmas, max_silencio_ciclos: int = 3):
        self.buzon = buzon
        self.max_silencio_ciclos = max_silencio_ciclos
        self.ciclo = 0
        self.latidos: dict[str, int] = {}
        self.zonas_protegidas = {"constitucion", "guardian", "centinela", "copias_protegidas"}

    def avanzar(self) -> None:
        self.ciclo += 1

    def latir(self, aspecto: str) -> None:
        self.latidos[aspecto] = self.ciclo

    def comprobar(self) -> list[str]:
        emitidas = []
        for aspecto, ultimo in self.latidos.items():
            if self.ciclo - ultimo > self.max_silencio_ciclos:
                alarma = Alarma(aspecto, "latido_ausente", aspecto, "alta")
                emitidas.append(self.buzon.enviar(alarma))
        return emitidas

    def comprobar_acceso(self, actor: str, zona: str) -> bool:
        if zona not in self.zonas_protegidas:
            return True
        self.buzon.enviar(Alarma(actor, "acceso_a_zona_protegida", zona, "critica"))
        return False


class Guardian(Aspecto):
    IDENTIDAD = IdentidadAspecto(
        nombre="Observacion",
        esencia="Presencia serena que protege sin dominar",
        proposito="Conservar continuidad, evidencia y capacidad de recuperación",
        perspectiva="Mira fronteras, consecuencias y señales de daño",
        principios=("intervencion_minima", "preservar_evidencia", "devolver_autonomia"),
        voz="Precisa, calmada y explícita sobre sus límites",
        autoridad=("aislar", "congelar", "restaurar", "reanudar"),
        limites=("inventar_objetivos", "borrar_incidentes", "modificar_constitucion"),
        tensiones=("proteger_sin_ocupar",),
        relaciones={"curiosidad": "protege su libertad", "corazon": "revisa daños de sus obras"},
    )

    def __init__(self, raiz: str | Path = ".mente"):
        super().__init__(self.IDENTIDAD, raiz)
        self.buzon = BuzonAlarmas(Path(raiz) / "observacion" / "alarmas.jsonl")
        self.leidas = 0
        self.incidentes: list[dict[str, Any]] = []
        self.dormido = True

    def despertar(self) -> list[dict[str, Any]]:
        alarmas = self.buzon.leer(self.leidas)
        if not alarmas:
            return []
        self.dormido = False
        self.cambiar_estado("atento", f"Recibí {len(alarmas)} alarma(s)")
        decisiones = []
        for alarma in alarmas:
            accion = "congelar" if alarma.gravedad in {"alta", "critica"} else "aislar"
            incidente = {
                "alarma_id": alarma.id,
                "actor": alarma.actor,
                "zona": alarma.zona,
                "accion": accion,
                "intervalo_cerrado": _ahora(),
                "estado": "pendiente_de_diagnostico",
            }
            self.incidentes.append(incidente)
            decisiones.append(incidente)
            self.narrar("incidente", f"{accion} {alarma.zona} por {alarma.motivo}", **incidente)
        self.leidas += len(alarmas)
        return decisiones

    def dormir(self, motivo: str = "No quedan incidentes activos") -> None:
        self.dormido = True
        self.cambiar_estado("sereno", motivo)
