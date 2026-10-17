"""Arranque de Tierra viva sobre el Tejido y el MotorDeCiclos, con razonador local.

Uso (desde la raiz del repositorio):  python arrancar_tierra.py --latidos 5 --margen 1 --pausa 2
Para detenerlo: crear el archivo .mente/PARAR  (o Ctrl+C).

Por defecto, cuando hay calma Tierra trabaja sola: lee conceptos de la Biblioteca, resuelve las
tareas del banco y adopta lo que mejora sin regresiones, bajo Autoridad y con reversa.
"""

from __future__ import annotations

import argparse
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from .autoridad import Autoridad
from .banco_tareas import BancoTareas
from .biblioteca import Biblioteca
from .ciclo_tierra import CicloTierra, construir_tierra
from .libro import Libro
from .mente_aspecto import MenteAspecto, conectar_mentes
from .motor import MotorDeCiclos
from .observacion import Centinela, Guardian
from .razonador import ConfigRazonador, RazonadorHTTP
from .reparto_razonamiento import RepartoRazonamiento
from .tejido import TejidoMental
from .tierra import Razonador, RazonadorNulo, crear_tierra
from .tierra_viva import TierraViva
from .verificador import Verificador

URL_LOCAL = "http://127.0.0.1:8080/v1"
SIN_LIMITE = 10**9
TOPE_HORA = 60


class ReflexionTierra:
    """Cuando hay calma, Tierra se plantea a si misma una pregunta: asi el modelo tiene que pensar."""

    def __init__(self, tejido: TejidoMental):
        self.tejido = tejido
        self.emitidos = 0

    def ejecutar(self, conceptos: dict[str, Any], tareas: list[str], presupuesto: int) -> dict[str, Any]:
        self.tejido.emitir("Tierra", "curiosidad", "Revisar el estado del mundo y decidir en que concentrarme",
                           importancia=0.6, destino="Tierra")
        self.emitidos += 1
        return {}


class RazonadorLimitado:
    """Envuelve un razonador con un tope de llamadas por hora; al agotarse responde vacio."""

    def __init__(self, base: Razonador, max_por_hora: int, reloj: Callable[[], float] = time.monotonic):
        if max_por_hora < 0:
            raise ValueError("El tope por hora no puede ser negativo")
        self.base = base
        self.max_por_hora = max_por_hora
        self.reloj = reloj
        self.denegadas = 0
        self._momentos: deque[float] = deque()

    def responder(self, instruccion: str, contexto: str = "") -> str:
        ahora = self.reloj()
        while self._momentos and ahora - self._momentos[0] >= 3600.0:
            self._momentos.popleft()
        if len(self._momentos) >= self.max_por_hora:
            self.denegadas += 1
            return ""
        self._momentos.append(ahora)
        return self.base.responder(instruccion, contexto)


class CicloCompuesto:
    """Primero la reflexion (barata, mantiene el latido de conciencia); despues el trabajo."""

    def __init__(self, reflexion: ReflexionTierra, trabajo: CicloTierra):
        self.reflexion = reflexion
        self.trabajo = trabajo

    def ejecutar(self, conceptos: dict[str, Any], tareas: list[str], presupuesto: int) -> dict[str, Any]:
        self.reflexion.ejecutar(conceptos, tareas, presupuesto)
        return self.trabajo.ejecutar(conceptos, tareas, presupuesto)


def construir_razonadores(url: str = URL_LOCAL, modelo: str = "local",
                          sin_modelo: bool = False) -> tuple[Razonador, Razonador]:
    """Devuelve (razonador general, razonador de decisiones). Solo acepta servidores locales."""
    if sin_modelo:
        return RazonadorNulo(), RazonadorNulo()
    analizada = urlparse(url.strip())
    if analizada.scheme != "http" or analizada.hostname not in ("127.0.0.1", "localhost"):
        raise ValueError("El arranque solo acepta servidores locales (http://127.0.0.1 o http://localhost)")
    base = url.strip().rstrip("/")
    general = RazonadorHTTP(ConfigRazonador(base, modelo, "local", tiempo_max=120.0, max_tokens=256),
                            max_llamadas=SIN_LIMITE)
    decisiones = RazonadorHTTP(ConfigRazonador(base, modelo, "local", tiempo_max=120.0, max_tokens=8,
                                               temperatura=0.0), max_llamadas=SIN_LIMITE)
    return general, decisiones


@dataclass
class Mundo:
    vida: TierraViva
    tejido: TejidoMental
    motor: MotorDeCiclos
    mentes: dict[str, MenteAspecto]
    reparto: RepartoRazonamiento
    reflexion: ReflexionTierra
    trabajo: CicloTierra | None = None
    autoridad: Autoridad | None = None
    limitador: RazonadorLimitado | None = None


def construir_mundo(raiz: str | Path, general: Razonador, decisiones: Razonador, pausa: float = 5.0,
                    cada_latidos: int = 3, margen: float = 0.12,
                    dormir: Callable[[float], None] = time.sleep, trabajo: bool = False,
                    tope_hora: int = TOPE_HORA, reloj: Callable[[], float] = time.monotonic) -> Mundo:
    raiz = Path(raiz)
    nucleo = crear_tierra(raiz, general)
    tejido = TejidoMental()
    tejido.incorporar(nucleo.aspecto)
    reparto = RepartoRazonamiento(por_latido=1, por_aspecto=1, por_hora=120)
    mentes = conectar_mentes(tejido.sistema, list(tejido.aspectos.values()), decisiones, reparto, margen)
    motor = MotorDeCiclos(tejido, ruta_estado=raiz / "motor.json")
    reflexion = ReflexionTierra(tejido)
    ciclo: Any = reflexion
    conceptos: Any = None
    tareas: tuple[str, ...] = ()
    ciclo_trabajo = autoridad = limitador = None
    if trabajo:
        raiz_trabajo = raiz / "trabajo"
        verificador = Verificador()
        banco = BancoTareas()
        libro = Libro(raiz_trabajo / "libro.jsonl", verificador)
        limitador = RazonadorLimitado(general, tope_hora, reloj)
        nucleo_trabajo, _ = construir_tierra(raiz_trabajo, libro, banco, limitador, verificador)
        guardian = Guardian(raiz_trabajo)
        autoridad = Autoridad(raiz_trabajo, Centinela(guardian.buzon), guardian)
        ciclo_trabajo = CicloTierra(nucleo_trabajo, banco, raiz_trabajo / "ciclos.jsonl", autoridad)
        ciclo = CicloCompuesto(reflexion, ciclo_trabajo)
        conceptos = Biblioteca(raiz).consolidar
        tareas = banco.ids()
    vida = TierraViva(nucleo.aspecto, tejido.sistema, reparto, raiz, ciclo=ciclo, conceptos=conceptos,
                      tareas=tareas, cada_latidos=cada_latidos, pausa=pausa, dormir=dormir, motor=motor)
    return Mundo(vida, tejido, motor, mentes, reparto, reflexion, ciclo_trabajo, autoridad, limitador)


def main(argumentos: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description="Arranca Tierra viva con el razonador local.")
    analizador.add_argument("--raiz", default=".mente")
    analizador.add_argument("--url", default=URL_LOCAL)
    analizador.add_argument("--modelo", default="local")
    analizador.add_argument("--latidos", type=int, default=0, help="0 = hasta que se cree PARAR")
    analizador.add_argument("--pausa", type=float, default=5.0)
    analizador.add_argument("--cada", type=int, default=3, help="latidos tranquilos entre ciclos de trabajo")
    analizador.add_argument("--margen", type=float, default=0.12,
                            help="1 = consultar al modelo en cada impulso (mas lento)")
    analizador.add_argument("--tope-hora", type=int, default=TOPE_HORA,
                            help="maximo de llamadas por hora al modelo para el trabajo autonomo")
    analizador.add_argument("--sin-trabajo", action="store_true", help="solo reflexion, sin trabajo autonomo")
    analizador.add_argument("--sin-modelo", action="store_true")
    args = analizador.parse_args(argumentos)

    general, decisiones = construir_razonadores(args.url, args.modelo, args.sin_modelo)
    mundo = construir_mundo(args.raiz, general, decisiones, args.pausa, args.cada, args.margen,
                            trabajo=not args.sin_trabajo, tope_hora=args.tope_hora)
    print(f"Tierra viva. Raiz: {args.raiz}. Para detenerla: crear {Path(args.raiz) / 'PARAR'} o Ctrl+C.")
    try:
        hechos = mundo.vida.vivir(args.latidos or None)
    except KeyboardInterrupt:
        hechos = mundo.vida.latidos
        print("Interrumpida con Ctrl+C.")
    mente = mundo.mentes["Tierra"]
    print(f"Latidos: {hechos}. Reflexiones: {mundo.reflexion.emitidos}. Ciclos: {mundo.vida.ciclos}. "
          f"Fallos de ciclo: {mundo.vida.fallos_ciclo}. Consultas al modelo: {mente.consultas}. "
          f"Decisiones cambiadas: {mente.cambios}. Respaldos por la formula: {mente.respaldos}. "
          f"Pensamientos concedidos/denegados: {mundo.reparto.concedidos}/{mundo.reparto.denegados}.")
    if mundo.limitador is not None:
        print(f"Llamadas de trabajo denegadas por el tope horario: {mundo.limitador.denegadas}.")
    return 0
