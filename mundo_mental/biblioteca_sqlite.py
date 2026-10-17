"""Biblioteca experimental adaptable con memoria activa en SQLite/WAL."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from .biblioteca import _limitar, _normalizar, _similitud
from .catalogador import Catalogador
from .contratos_biblioteca import DiagnosticoBusqueda, PuertoCatalogo


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


class BibliotecaSQLite:
    """La Biblioteca interpreta; sus órganos reemplazables almacenan y localizan."""

    VERSION = "0.5.0-experimental"

    def __init__(self, raiz: str | Path = ".mente", ventana_novedad: int = 512,
                 max_episodios_libro: int = 256,
                 catalogador: PuertoCatalogo | None = None):
        self.raiz = Path(raiz)
        self.raiz.mkdir(parents=True, exist_ok=True)
        self.db = self.raiz / "biblioteca.sqlite3"
        self.habilidades = self.raiz / "habilidades"
        self.archivo_habilidades = self.habilidades / "versiones"
        self.planos = self.raiz / "planos"
        self.ventana_novedad = max(1, ventana_novedad)
        self.catalogador: PuertoCatalogo = catalogador or Catalogador(max_episodios_libro)
        self._ultimo_diagnostico: DiagnosticoBusqueda | None = None
        for sala in (self.habilidades, self.archivo_habilidades, self.planos):
            sala.mkdir(parents=True, exist_ok=True)
        self._crear_esquema()
        self._sincronizar_catalogo()

    @contextmanager
    def _conexion(self) -> Iterator[sqlite3.Connection]:
        conexion = sqlite3.connect(self.db, timeout=30)
        try:
            conexion.row_factory = sqlite3.Row
            conexion.execute("PRAGMA journal_mode=WAL")
            conexion.execute("PRAGMA foreign_keys=ON")
            with conexion:
                yield conexion
        finally:
            conexion.close()

    def _crear_esquema(self) -> None:
        with self._conexion() as conexion:
            conexion.executescript("""
                CREATE TABLE IF NOT EXISTS episodios (
                    id TEXT PRIMARY KEY, momento TEXT NOT NULL, entrada TEXT NOT NULL,
                    respuesta TEXT NOT NULL, esperado TEXT NOT NULL, correcto INTEGER NOT NULL,
                    importancia REAL NOT NULL, novedad REAL NOT NULL, protegido INTEGER NOT NULL,
                    accesos INTEGER NOT NULL DEFAULT 0, repeticiones INTEGER NOT NULL DEFAULT 1,
                    ultimo_acceso TEXT, metadata TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_episodios_esperado ON episodios(esperado);
                CREATE INDEX IF NOT EXISTS idx_episodios_momento ON episodios(momento DESC);
                CREATE TABLE IF NOT EXISTS conceptos (nombre TEXT PRIMARY KEY, contenido TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS obras (
                    id TEXT PRIMARY KEY, momento TEXT NOT NULL, habilidad TEXT, tipo TEXT,
                    aceptada INTEGER, precision_candidata REAL, contenido TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_obras_consulta ON obras(habilidad, tipo, aceptada);
            """)
            self.catalogador.crear_esquema(conexion)

    def _sincronizar_catalogo(self) -> None:
        with self._conexion() as conexion:
            episodios = conexion.execute("SELECT COUNT(*) FROM episodios").fetchone()[0]
            estado = self.catalogador.estado(conexion)
            if episodios != estado["ubicaciones"]:
                self.catalogador.reconstruir(conexion)

    @staticmethod
    def _episodio(fila: sqlite3.Row) -> dict[str, Any]:
        salida = dict(fila)
        salida["entrada"] = json.loads(salida["entrada"])
        salida["metadata"] = json.loads(salida["metadata"])
        salida["correcto"] = bool(salida["correcto"])
        salida["protegido"] = bool(salida["protegido"])
        return salida

    def exportar_episodios(self) -> list[dict[str, Any]]:
        with self._conexion() as conexion:
            return [self._episodio(fila) for fila in conexion.execute(
                "SELECT * FROM episodios ORDER BY momento, id"
            )]

    def importar_episodios(self, episodios: Iterable[dict[str, Any]]) -> dict[str, int]:
        recibidos = 0
        insertados = 0
        with self._conexion() as conexion:
            for episodio in episodios:
                recibidos += 1
                cursor = conexion.execute(
                    "INSERT OR IGNORE INTO episodios VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (episodio["id"], episodio["momento"],
                     json.dumps(episodio["entrada"], ensure_ascii=False),
                     episodio["respuesta"], episodio["esperado"], int(episodio["correcto"]),
                     float(episodio["importancia"]), float(episodio["novedad"]),
                     int(episodio.get("protegido", False)), episodio.get("accesos", 0),
                     episodio.get("repeticiones", 1), episodio.get("ultimo_acceso"),
                     json.dumps(episodio.get("metadata", {}), ensure_ascii=False)),
                )
                if cursor.rowcount:
                    insertados += 1
                    self.catalogador.catalogar(conexion, episodio)
        return {"recibidos": recibidos, "insertados": insertados,
                "omitidos": recibidos - insertados}

    def importar_conceptos(self, conceptos: dict[str, dict[str, Any]]) -> int:
        with self._conexion() as conexion:
            conexion.executemany(
                "INSERT INTO conceptos VALUES (?, ?) ON CONFLICT(nombre) DO UPDATE SET contenido=excluded.contenido",
                [(nombre, json.dumps(concepto, ensure_ascii=False)) for nombre, concepto in conceptos.items()],
            )
        return len(conceptos)

    def importar_obras(self, obras: Iterable[dict[str, Any]]) -> dict[str, int]:
        recibidas = 0
        insertadas = 0
        with self._conexion() as conexion:
            for obra in obras:
                recibidas += 1
                cursor = conexion.execute(
                    "INSERT OR IGNORE INTO obras VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (obra["id"], obra["momento"], obra.get("habilidad"), obra.get("tipo"),
                     int(obra.get("aceptada", False)), obra.get("precision_candidata"),
                     json.dumps(obra, ensure_ascii=False)),
                )
                insertadas += int(bool(cursor.rowcount))
        return {"recibidas": recibidas, "insertadas": insertadas,
                "omitidas": recibidas - insertadas}

    def recordar(self, entrada: Iterable[Any], respuesta: str, esperado: str, correcto: bool,
                 metadata: dict[str, Any] | None = None, importancia: float | None = None,
                 protegido: bool = False) -> str:
        patron = _normalizar(entrada)
        metadata = metadata or {}
        with self._conexion() as conexion:
            filas = conexion.execute(
                "SELECT entrada FROM episodios ORDER BY momento DESC LIMIT ?", (self.ventana_novedad,)
            ).fetchall()
            parecido = max((_similitud(patron, json.loads(x["entrada"])) for x in filas), default=0.0)
            novedad = 1.0 - parecido
            confianza = float(metadata.get("confianza", 0.5))
            sorpresa = 1.0 - confianza if correcto else confianza
            if importancia is None:
                importancia = (0.55 if not correcto else 0.20) + 0.30 * novedad + 0.15 * sorpresa
            episodio = {
                "id": str(uuid4()), "momento": _ahora(), "entrada": patron,
                "respuesta": respuesta, "esperado": esperado, "correcto": bool(correcto),
                "importancia": _limitar(importancia), "novedad": _limitar(novedad),
                "protegido": bool(protegido), "accesos": 0, "repeticiones": 1,
                "ultimo_acceso": None, "metadata": metadata,
            }
            conexion.execute(
                "INSERT INTO episodios VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 1, NULL, ?)",
                (episodio["id"], episodio["momento"], json.dumps(patron, ensure_ascii=False),
                 respuesta, esperado, int(correcto), episodio["importancia"], episodio["novedad"],
                 int(protegido), json.dumps(metadata, ensure_ascii=False)),
            )
            self.catalogador.catalogar(conexion, episodio)
        return episodio["id"]

    def _filas_exhaustivas(self, conexion: sqlite3.Connection,
                           esperado: str | None) -> list[sqlite3.Row]:
        if esperado is None:
            return conexion.execute("SELECT * FROM episodios").fetchall()
        return conexion.execute("SELECT * FROM episodios WHERE esperado=?", (esperado,)).fetchall()

    def _seleccionar_filas(self, conexion: sqlite3.Connection, objetivo: list[Any], limite: int,
                           esperado: str | None, estrategia: str) -> tuple[list[sqlite3.Row], DiagnosticoBusqueda]:
        total = conexion.execute(
            "SELECT COUNT(*) FROM episodios WHERE (? IS NULL OR esperado=?)", (esperado, esperado)
        ).fetchone()[0]
        presupuesto = max(64, max(1, limite) * 16)
        if estrategia == "exhaustiva" or total <= presupuesto:
            filas = self._filas_exhaustivas(conexion, esperado)
            return filas, DiagnosticoBusqueda(
                estrategia, "exhaustiva", total, presupuesto, len(filas), len(filas)
            )
        try:
            localizacion = self.catalogador.localizar(conexion, objetivo, presupuesto, esperado)
            if not localizacion.ids and total:
                filas = self._filas_exhaustivas(conexion, esperado)
                return filas, DiagnosticoBusqueda(
                    estrategia, "exhaustiva_degradada", total, presupuesto, 0, len(filas), True,
                    "El catálogo no señaló candidatos; la Biblioteca protegió la recuperación exhaustiva.",
                )
            marcas = ",".join("?" for _ in localizacion.ids)
            filas = conexion.execute(
                f"SELECT * FROM episodios WHERE id IN ({marcas})", localizacion.ids
            ).fetchall()
            return filas, DiagnosticoBusqueda(
                estrategia, "catalogo", total, presupuesto,
                localizacion.coincidencias, len(filas)
            )
        except (sqlite3.DatabaseError, ValueError, KeyError, json.JSONDecodeError) as error:
            filas = self._filas_exhaustivas(conexion, esperado)
            return filas, DiagnosticoBusqueda(
                estrategia, "exhaustiva_degradada", total, presupuesto, 0, len(filas), True,
                f"El catálogo falló de forma recuperable: {type(error).__name__}.",
            )

    def buscar_similares(self, entrada: Iterable[Any], limite: int = 5,
                         esperado: str | None = None, explicar: bool = True,
                         estrategia: str = "catalogo") -> list[dict[str, Any]]:
        if estrategia not in {"catalogo", "exhaustiva"}:
            raise ValueError("estrategia debe ser 'catalogo' o 'exhaustiva'")
        objetivo = _normalizar(entrada)
        with self._conexion() as conexion:
            filas, diagnostico = self._seleccionar_filas(
                conexion, objetivo, limite, esperado, estrategia
            )
            candidatos = [self._episodio(fila) for fila in filas]
            for recuerdo in candidatos:
                similitud = _similitud(objetivo, recuerdo["entrada"])
                recuerdo["similitud"] = _limitar(similitud)
                recuerdo["puntuacion_recuperacion"] = _limitar(
                    0.70 * similitud + 0.20 * recuerdo["importancia"] + 0.10 * int(recuerdo["correcto"])
                )
                if explicar:
                    coincidencias = sum(a == b for a, b in zip(objetivo, recuerdo["entrada"]))
                    recuerdo["explicacion"] = (
                        f"Coinciden {coincidencias} de {max(len(objetivo), len(recuerdo['entrada']))} "
                        f"posiciones; importancia {recuerdo['importancia']:.0%}."
                    )
            candidatos.sort(key=lambda x: (x["puntuacion_recuperacion"], x["momento"]), reverse=True)
            elegidos = candidatos[:max(0, limite)]
            momento = _ahora()
            conexion.executemany(
                "UPDATE episodios SET accesos=accesos+1, ultimo_acceso=? WHERE id=?",
                [(momento, x["id"]) for x in elegidos],
            )
            self._ultimo_diagnostico = DiagnosticoBusqueda(
                diagnostico.estrategia_solicitada,
                diagnostico.estrategia_usada,
                diagnostico.total_episodios,
                diagnostico.presupuesto_candidatos,
                diagnostico.candidatos_localizados,
                len(candidatos),
                diagnostico.degradada,
                diagnostico.motivo,
            )
            return elegidos

    def diagnostico_ultima_busqueda(self) -> dict[str, Any] | None:
        return self._ultimo_diagnostico.exportar() if self._ultimo_diagnostico else None

    def consolidar(self, minimo_ejemplos: int = 2) -> dict[str, dict[str, Any]]:
        grupos: dict[str, list[dict[str, Any]]] = {}
        for episodio in self.exportar_episodios():
            grupos.setdefault(episodio["esperado"], []).append(episodio)
        conceptos = {}
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
                "nombre": nombre, "episodios": len(episodios), "ejemplos_unicos": len(unicos),
                "fiabilidad": _limitar(sum(x["correcto"] for x in episodios) / len(episodios)),
                "rasgos_comunes": rasgos, "actualizado": _ahora(),
            }
        self.importar_conceptos(conceptos)
        return conceptos

    def cargar_conceptos(self) -> dict[str, dict[str, Any]]:
        with self._conexion() as conexion:
            return {fila["nombre"]: json.loads(fila["contenido"])
                    for fila in conexion.execute("SELECT * FROM conceptos")}

    def depurar(self, max_recuerdos: int | None = None) -> dict[str, int]:
        recuerdos = self.exportar_episodios()
        fusionados: dict[tuple[str, str], dict[str, Any]] = {}
        for recuerdo in recuerdos:
            clave = (json.dumps(recuerdo["entrada"], ensure_ascii=False), recuerdo["esperado"])
            if clave not in fusionados:
                fusionados[clave] = recuerdo
                continue
            actual = fusionados[clave]
            repeticiones = actual.get("repeticiones", 1) + recuerdo.get("repeticiones", 1)
            accesos = actual.get("accesos", 0) + recuerdo.get("accesos", 0)
            protegido = actual.get("protegido", False) or recuerdo.get("protegido", False)
            if recuerdo.get("importancia", 0) > actual.get("importancia", 0):
                actual = recuerdo
                fusionados[clave] = actual
            actual["repeticiones"], actual["accesos"], actual["protegido"] = repeticiones, accesos, protegido
        salida = list(fusionados.values())
        if max_recuerdos is not None and len(salida) > max_recuerdos:
            protegidos = [x for x in salida if x.get("protegido")]
            libres = [x for x in salida if not x.get("protegido")]
            libres.sort(key=lambda x: (not x["correcto"], x.get("importancia", 0), x.get("accesos", 0)), reverse=True)
            salida = protegidos + libres[:max(0, max_recuerdos - len(protegidos))]
        with self._conexion() as conexion:
            conexion.execute("DELETE FROM catalogo_indice")
            conexion.execute("DELETE FROM catalogo_ubicaciones")
            conexion.execute("DELETE FROM catalogo_libros")
            conexion.execute("DELETE FROM episodios")
        self.importar_episodios(sorted(salida, key=lambda x: x["momento"]))
        return {"antes": len(recuerdos), "despues": len(salida), "fusionados": len(recuerdos) - len(salida)}

    def guardar_habilidad(self, nombre: str, estado: dict[str, Any]) -> Path:
        ruta = self.habilidades / f"{nombre}.json"
        if ruta.exists():
            version = len(list(self.archivo_habilidades.glob(f"{nombre}-*.json"))) + 1
            (self.archivo_habilidades / f"{nombre}-{version:04d}.json").write_text(
                ruta.read_text(encoding="utf-8"), encoding="utf-8")
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
        self.importar_obras([registro])
        return registro["id"]

    def historial_obras(self) -> list[dict[str, Any]]:
        with self._conexion() as conexion:
            return [json.loads(x["contenido"]) for x in conexion.execute(
                "SELECT contenido FROM obras ORDER BY momento, id")]

    def consultar_obras(self, habilidad: str | None = None, tipo: str | None = None,
                         limite: int = 5) -> list[dict[str, Any]]:
        consulta = "SELECT contenido FROM obras WHERE (? IS NULL OR habilidad=?) AND (? IS NULL OR tipo=?) ORDER BY aceptada DESC, precision_candidata DESC, momento DESC LIMIT ?"
        with self._conexion() as conexion:
            return [json.loads(x["contenido"]) for x in conexion.execute(
                consulta, (habilidad, habilidad, tipo, tipo, max(0, limite)))]

    def verificar_catalogo(self) -> dict[str, Any]:
        with self._conexion() as conexion:
            return self.catalogador.verificar(conexion)

    def reconstruir_catalogo(self) -> dict[str, int]:
        with self._conexion() as conexion:
            return self.catalogador.reconstruir(conexion)

    def estado(self) -> dict[str, Any]:
        with self._conexion() as conexion:
            episodios = conexion.execute("SELECT COUNT(*) FROM episodios").fetchone()[0]
            protegidos = conexion.execute("SELECT COUNT(*) FROM episodios WHERE protegido=1").fetchone()[0]
            obras = conexion.execute("SELECT COUNT(*) FROM obras").fetchone()[0]
            catalogo = self.catalogador.estado(conexion)
        return {
            "version": self.VERSION, "episodios": episodios,
            "conceptos": len(self.cargar_conceptos()),
            "habilidades": len(list(self.habilidades.glob("*.json"))),
            "versiones_archivadas": len(list(self.archivo_habilidades.glob("*.json"))),
            "obras": obras, "recuerdos_protegidos": protegidos, "catalogo": catalogo,
        }
