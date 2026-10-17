"""Arranque de Tierra viva sobre el Tejido y el MotorDeCiclos, con razonador local.

Uso (desde la raiz del repositorio):  python arrancar_tierra.py --latidos 5 --margen 1 --pausa 2
Para detenerlo: crear el archivo .mente/PARAR  (o Ctrl+C).

Por defecto, cuando hay calma Tierra trabaja sola: lee conceptos de la Biblioteca, resuelve las
tareas del banco y adopta lo que mejora sin regresiones, bajo Autoridad y con reversa.

Evolucion de codigo (opcional): --evolucionar RUTA --objetivo "..." hace que cada cierto numero de
ciclos Tierra pida al modelo un parche y su prueba de mejora para esa ruta, y lo promueva solo si
conserva la suite completa y demuestra la mejora. Usa un razonador propio, con mas tokens y mas
tiempo que el de las decisiones cortas.
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
from .evolucion import Evolucion
from .libro import Libro
from .mente_aspecto import MenteAspecto, conectar_mentes
from .motor import MotorDeCiclos
from .observacion import Centinela, Guardian
from .razonador import ConfigRazonador, RazonadorHTTP
from .reparto_razonamiento import RepartoRazonamiento
from .rol_evolutiva import RolEvolutiva
from .tejido import TejidoMental
from .tierra import Razonador, RazonadorNulo, crear_tierra
from .tierra_viva import TierraViva
from .verificador import Verificador

URL_LOCAL = "http://127.0.0.1:8080/v1"
SIN_LIMITE = 10**9
TOPE_HORA = 60
TOKENS_EVOLUCION = 1500
TIEMPO_EVOLUCION = 600.0
CARACTERES_EVOLUCION = 6000


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
    """Primero la reflexion (barata); despues el trabajo; y, cada N ciclos, la evolucion de codigo."""

    def __init__(self, reflexion: ReflexionTierra, trabajo: CicloTierra,
                 evolutiva: RolEvolutiva | None = None, cada_evolucion: int = 10):
        if cada_evolucion <= 0:
            raise ValueError("cada_evolucion debe ser positivo")
        self.reflexion = reflexion
        self.trabajo = trabajo
        self.evolutiva = evolutiva
        self.cada_evolucion = cada_evolucion
        self.ciclos = 0

    def ejecutar(self, conceptos: dict[str, Any], tareas: list[str], presupuesto: int) -> dict[str, Any]:
        self.reflexion.ejecutar(conceptos, tareas, presupuesto)
        informe = self.trabajo.ejecutar(conceptos, tareas, presupuesto)
        self.ciclos += 1
        if self.evolutiva is not None and self.ciclos % self.cada_evolucion == 0:
            informe["evolucion"] = self.evolutiva.ejecutar({})
        return informe


def _base_local(url: str) -> str:
    analizada = urlparse(url.strip())
    if analizada.scheme != "http" or analizada.hostname not in ("127.0.0.1", "localhost"):
        raise ValueError("El arranque solo acepta servidores locales (http://127.0.0.1 o http://localhost)")
    return url.strip().rstrip("/")


def construir_razonadores(url: str = URL_LOCAL, modelo: str = "local",
                          sin_modelo: bool = False) -> tuple[Razonador, Razonador]:
    """Devuelve (razonador general, razonador de decisiones). Solo acepta servidores locales."""
    if sin_modelo:
        return RazonadorNulo(), RazonadorNulo()
    base = _base_local(url)
    general = RazonadorHTTP(ConfigRazonador(base, modelo, "local", tiempo_max=120.0, max_tokens=256),
                            max_llamadas=SIN_LIMITE)
    decisiones = RazonadorHTTP(ConfigRazonador(base, modelo, "local", tiempo_max=120.0, max_tokens=8,
                                               temperatura=0.0), max_llamadas=SIN_LIMITE)
    return general, decisiones


def construir_razonador_evolucion(url: str = URL_LOCAL, modelo: str = "local", sin_modelo: bool = False,
                                  max_tokens: int = TOKENS_EVOLUCION,
                                  tiempo_max: float = TIEMPO_EVOLUCION) -> Razonador:
    """Razonador para parches de codigo: respuestas largas y tiempo generoso. Solo servidores locales."""
    if max_tokens <= 0 or tiempo_max <= 0:
        raise ValueError("max_tokens y tiempo_max deben ser positivos")
    if sin_modelo:
        return RazonadorNulo()
    base = _base_local(url)
    return RazonadorHTTP(ConfigRazonador(base, modelo, "local", tiempo_max=float(tiempo_max),
                                         max_tokens=int(max_tokens)), max_llamadas=SIN_LIMITE)


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
    evolucion: Evolucion | None = None
    evolutiva: RolEvolutiva | None = None


def construir_mundo(raiz: str | Path, general: Razonador, decisiones: Razonador, pausa: float = 5.0,
                    cada_latidos: int = 3, margen: float = 0.12,
                    dormir: Callable[[float], None] = time.sleep, trabajo: bool = False,
                    tope_hora: int = TOPE_HORA, reloj: Callable[[], float] = time.monotonic,
                    repo: str | Path = ".", rutas_evolucion: tuple[str, ...] = (), objetivo: str = "",
                    cada_evolucion: int = 10, razonador_evolucion: Razonador | None = None,
                    max_caracteres_evolucion: int = CARACTERES_EVOLUCION) -> Mundo:
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
    ciclo_trabajo = autoridad = limitador = evolucion = evolutiva = None
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
        if rutas_evolucion:
            evolucion = Evolucion(repo, autoridad, ruta_registro=raiz_trabajo / "evolucion.jsonl", tiempo_max=120.0)
            para_evolucion = (RazonadorLimitado(razonador_evolucion, tope_hora, reloj)
                              if razonador_evolucion is not None else limitador)
            evolutiva = RolEvolutiva(evolucion, para_evolucion, tuple(rutas_evolucion), objetivo,
                                     max_caracteres_evolucion)
        ciclo = CicloCompuesto(reflexion, ciclo_trabajo, evolutiva, cada_evolucion)
        conceptos = Biblioteca(raiz).consolidar
        tareas = banco.ids()
    vida = TierraViva(nucleo.aspecto, tejido.sistema, reparto, raiz, ciclo=ciclo, conceptos=conceptos,
                      tareas=tareas, cada_latidos=cada_latidos, pausa=pausa, dormir=dormir, motor=motor)
    return Mundo(vida, tejido, motor, mentes, reparto, reflexion, ciclo_trabajo, autoridad, limitador,
                 evolucion, evolutiva)


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
    analizador.add_argument("--evolucionar", action="append", default=[], metavar="RUTA",
                            help="ruta de codigo que Tierra puede intentar mejorar (repetible)")
    analizador.add_argument("--objetivo", default="", help="que debe mejorar la evolucion de codigo")
    analizador.add_argument("--repo", default=".", help="raiz del repositorio a evolucionar")
    analizador.add_argument("--cada-evolucion", type=int, default=10, help="ciclos de trabajo entre intentos de evolucion")
    analizador.add_argument("--tokens-evolucion", type=int, default=TOKENS_EVOLUCION,
                            help="maximo de tokens por respuesta al evolucionar codigo")
    analizador.add_argument("--tiempo-evolucion", type=float, default=TIEMPO_EVOLUCION,
                            help="segundos maximos de espera por respuesta al evolucionar codigo")
    analizador.add_argument("--max-caracteres-evolucion", type=int, default=CARACTERES_EVOLUCION,
                            help="tamano maximo del archivo a evolucionar (debe caber en el contexto del modelo)")
    analizador.add_argument("--sin-modelo", action="store_true")
    args = analizador.parse_args(argumentos)
    if args.evolucionar and not args.objetivo.strip():
        analizador.error("--evolucionar requiere --objetivo")
    if args.evolucionar and args.sin_trabajo:
        analizador.error("--evolucionar no es compatible con --sin-trabajo")
    if args.tokens_evolucion <= 0 or args.tiempo_evolucion <= 0 or args.max_caracteres_evolucion <= 0:
        analizador.error("--tokens-evolucion, --tiempo-evolucion y --max-caracteres-evolucion deben ser positivos")

    general, decisiones = construir_razonadores(args.url, args.modelo, args.sin_modelo)
    razonador_evolucion = None
    if args.evolucionar:
        razonador_evolucion = construir_razonador_evolucion(args.url, args.modelo, args.sin_modelo,
                                                            args.tokens_evolucion, args.tiempo_evolucion)
    mundo = construir_mundo(args.raiz, general, decisiones, args.pausa, args.cada, args.margen,
                            trabajo=not args.sin_trabajo, tope_hora=args.tope_hora, repo=args.repo,
                            rutas_evolucion=tuple(args.evolucionar), objetivo=args.objetivo,
                            cada_evolucion=args.cada_evolucion, razonador_evolucion=razonador_evolucion,
                            max_caracteres_evolucion=args.max_caracteres_evolucion)
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
    if mundo.evolucion is not None:
        historial = mundo.evolucion.historial()
        promovidas = sum(1 for h in historial if h["estado"] == "promovida")
        print(f"Intentos de evolucion: {len(historial)}. Promovidos: {promovidas}.")
    return 0
