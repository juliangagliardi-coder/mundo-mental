"""Catalogador 0.2: mapas mecánicos, incrementales y reconstruibles."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections import Counter
from datetime import datetime
from typing import Any, Iterable

from .contratos_biblioteca import LocalizacionCatalogo


def _canon(valor: Any) -> str:
    return json.dumps(valor, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _fecha(momento: str) -> str:
    try:
        return datetime.fromisoformat(momento.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return momento[:10] or "sin-fecha"


class Catalogador:
    """Órgano determinista: localiza, pero no interpreta ni decide qué significa."""

    VERSION = "0.2.0"

    def __init__(self, max_episodios_libro: int = 256):
        self.max_episodios_libro = max(1, int(max_episodios_libro))

    def crear_esquema(self, conexion: sqlite3.Connection) -> None:
        conexion.executescript("""
            CREATE TABLE IF NOT EXISTS catalogo_meta (
                clave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS catalogo_libros (
                id TEXT PRIMARY KEY,
                fecha TEXT NOT NULL,
                secuencia INTEGER NOT NULL,
                estado TEXT NOT NULL,
                cantidad INTEGER NOT NULL DEFAULT 0,
                primer_momento TEXT,
                ultimo_momento TEXT,
                manifiesto TEXT NOT NULL DEFAULT '{}',
                huella TEXT NOT NULL DEFAULT '',
                UNIQUE(fecha, secuencia)
            );
            CREATE INDEX IF NOT EXISTS idx_catalogo_libros_fecha
                ON catalogo_libros(fecha, secuencia);
            CREATE TABLE IF NOT EXISTS catalogo_ubicaciones (
                episodio_id TEXT PRIMARY KEY,
                libro_id TEXT NOT NULL,
                posicion INTEGER NOT NULL,
                FOREIGN KEY(episodio_id) REFERENCES episodios(id) ON DELETE CASCADE,
                FOREIGN KEY(libro_id) REFERENCES catalogo_libros(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_catalogo_ubicaciones_libro
                ON catalogo_ubicaciones(libro_id, posicion);
            CREATE TABLE IF NOT EXISTS catalogo_indice (
                termino TEXT NOT NULL,
                episodio_id TEXT NOT NULL,
                libro_id TEXT NOT NULL,
                peso REAL NOT NULL,
                PRIMARY KEY(termino, episodio_id),
                FOREIGN KEY(episodio_id) REFERENCES episodios(id) ON DELETE CASCADE,
                FOREIGN KEY(libro_id) REFERENCES catalogo_libros(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_catalogo_indice_termino
                ON catalogo_indice(termino, peso DESC);
        """)
        conexion.execute(
            "INSERT INTO catalogo_meta(clave, valor) VALUES ('version', ?) "
            "ON CONFLICT(clave) DO UPDATE SET valor=excluded.valor",
            (self.VERSION,),
        )

    @staticmethod
    def _terminos(episodio: dict[str, Any]) -> dict[str, float]:
        entrada = episodio.get("entrada", [])
        metadata = episodio.get("metadata", {}) or {}
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        terminos: dict[str, float] = {f"longitud:{len(entrada)}": 0.25}
        for posicion, valor in enumerate(entrada):
            terminos[f"posicion:{posicion}:{_canon(valor)}"] = 1.0
        esperado = episodio.get("esperado")
        if esperado is not None:
            terminos[f"esperado:{_canon(esperado)}"] = 0.5
        origen = metadata.get("origen") or metadata.get("aspecto")
        if origen:
            terminos[f"origen:{_canon(origen)}"] = 0.4
        temas = metadata.get("temas", [])
        if isinstance(temas, str):
            temas = [temas]
        for tema in temas:
            terminos[f"tema:{_canon(tema)}"] = 0.4
        return terminos

    @staticmethod
    def _manifiesto_vacio(libro_id: str) -> dict[str, Any]:
        return {
            "version": 2,
            "libro": libro_id,
            "cantidad": 0,
            "primer_momento": None,
            "ultimo_momento": None,
            "temas": {},
            "origenes": {},
            "importancia": {"minima": 0.0, "maxima": 0.0},
        }

    def _libro_abierto(self, conexion: sqlite3.Connection, fecha: str) -> sqlite3.Row | None:
        return conexion.execute(
            "SELECT * FROM catalogo_libros WHERE fecha=? AND estado='abierto' "
            "ORDER BY secuencia DESC LIMIT 1", (fecha,),
        ).fetchone()

    def _crear_libro(self, conexion: sqlite3.Connection, fecha: str) -> sqlite3.Row:
        secuencia = conexion.execute(
            "SELECT COALESCE(MAX(secuencia), 0) + 1 FROM catalogo_libros WHERE fecha=?", (fecha,)
        ).fetchone()[0]
        identidad = f"{fecha}-{secuencia:06d}"
        manifiesto = self._manifiesto_vacio(identidad)
        texto = _canon(manifiesto)
        conexion.execute(
            "INSERT INTO catalogo_libros(id, fecha, secuencia, estado, manifiesto, huella) "
            "VALUES (?, ?, ?, 'abierto', ?, ?)",
            (identidad, fecha, secuencia, texto, hashlib.sha256(texto.encode("utf-8")).hexdigest()),
        )
        return conexion.execute("SELECT * FROM catalogo_libros WHERE id=?", (identidad,)).fetchone()

    def catalogar(self, conexion: sqlite3.Connection, episodio: dict[str, Any]) -> str:
        """Ubica un episodio canónico y actualiza mapas sin releer el Libro entero."""
        existente = conexion.execute(
            "SELECT libro_id FROM catalogo_ubicaciones WHERE episodio_id=?", (episodio["id"],)
        ).fetchone()
        if existente:
            return existente["libro_id"]
        fecha = _fecha(episodio["momento"])
        libro = self._libro_abierto(conexion, fecha)
        if libro is None or libro["cantidad"] >= self.max_episodios_libro:
            if libro is not None:
                self._sellar(conexion, libro["id"])
            libro = self._crear_libro(conexion, fecha)
        posicion = int(libro["cantidad"])
        conexion.execute(
            "INSERT INTO catalogo_ubicaciones VALUES (?, ?, ?)",
            (episodio["id"], libro["id"], posicion),
        )
        terminos = self._terminos(episodio)
        conexion.executemany(
            "INSERT OR REPLACE INTO catalogo_indice VALUES (?, ?, ?, ?)",
            [(termino, episodio["id"], libro["id"], peso) for termino, peso in terminos.items()],
        )
        self._actualizar_manifiesto_incremental(conexion, libro["id"], episodio)
        actualizado = conexion.execute("SELECT * FROM catalogo_libros WHERE id=?", (libro["id"],)).fetchone()
        if actualizado["cantidad"] >= self.max_episodios_libro:
            self._sellar(conexion, libro["id"])
        return libro["id"]

    def _actualizar_manifiesto_incremental(
        self, conexion: sqlite3.Connection, libro_id: str, episodio: dict[str, Any]
    ) -> None:
        fila = conexion.execute(
            "SELECT manifiesto FROM catalogo_libros WHERE id=?", (libro_id,)
        ).fetchone()
        manifiesto = json.loads(fila["manifiesto"]) if fila and fila["manifiesto"] else self._manifiesto_vacio(libro_id)
        cantidad_anterior = int(manifiesto.get("cantidad", 0))
        momento = str(episodio["momento"])
        importancia = float(episodio.get("importancia", 0.0))
        temas = Counter(manifiesto.get("temas", {}))
        origenes = Counter(manifiesto.get("origenes", {}))
        temas[str(episodio.get("esperado", "sin-tema"))] += 1
        metadata = episodio.get("metadata", {}) or {}
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        origen = metadata.get("origen") or metadata.get("aspecto")
        if origen:
            origenes[str(origen)] += 1
        extras = metadata.get("temas", [])
        if isinstance(extras, str):
            extras = [extras]
        temas.update(str(x) for x in extras)
        rango = manifiesto.get("importancia", {})
        manifiesto.update({
            "version": 2,
            "cantidad": cantidad_anterior + 1,
            "primer_momento": min(filter(None, [manifiesto.get("primer_momento"), momento])),
            "ultimo_momento": max(filter(None, [manifiesto.get("ultimo_momento"), momento])),
            "temas": dict(temas.most_common(32)),
            "origenes": dict(origenes.most_common(16)),
            "importancia": {
                "minima": importancia if cantidad_anterior == 0 else min(float(rango.get("minima", importancia)), importancia),
                "maxima": importancia if cantidad_anterior == 0 else max(float(rango.get("maxima", importancia)), importancia),
            },
        })
        texto = _canon(manifiesto)
        huella = hashlib.sha256(texto.encode("utf-8")).hexdigest()
        conexion.execute(
            "UPDATE catalogo_libros SET cantidad=?, primer_momento=?, ultimo_momento=?, "
            "manifiesto=?, huella=? WHERE id=?",
            (manifiesto["cantidad"], manifiesto["primer_momento"], manifiesto["ultimo_momento"],
             texto, huella, libro_id),
        )

    def _sellar(self, conexion: sqlite3.Connection, libro_id: str) -> None:
        conexion.execute("UPDATE catalogo_libros SET estado='sellado' WHERE id=?", (libro_id,))

    def localizar(self, conexion: sqlite3.Connection, entrada: Iterable[Any], limite: int = 128,
                  esperado: str | None = None) -> LocalizacionCatalogo:
        patron = list(entrada)
        terminos = [f"longitud:{len(patron)}"] + [
            f"posicion:{posicion}:{_canon(valor)}" for posicion, valor in enumerate(patron)
        ]
        if esperado is not None:
            terminos.append(f"esperado:{_canon(esperado)}")
        marcas = ",".join("?" for _ in terminos)
        filtro = "AND e.esperado=?" if esperado is not None else ""
        parametros: list[Any] = list(terminos)
        if esperado is not None:
            parametros.append(esperado)
        parametros.append(max(1, int(limite)))
        filas = conexion.execute(
            f"SELECT i.episodio_id, SUM(i.peso) AS puntuacion "
            f"FROM catalogo_indice i JOIN episodios e ON e.id=i.episodio_id "
            f"WHERE i.termino IN ({marcas}) {filtro} "
            f"GROUP BY i.episodio_id "
            f"ORDER BY puntuacion DESC, e.importancia DESC, e.momento DESC LIMIT ?",
            parametros,
        ).fetchall()
        ids = tuple(fila["episodio_id"] for fila in filas)
        return LocalizacionCatalogo(
            ids=ids,
            terminos_consultados=len(terminos),
            coincidencias=len(ids),
            version_catalogo=self.VERSION,
        )

    def candidatos(self, conexion: sqlite3.Connection, entrada: Iterable[Any], limite: int = 128,
                   esperado: str | None = None) -> list[str]:
        """Compatibilidad con Catalogador 0.1."""
        return list(self.localizar(conexion, entrada, limite, esperado).ids)

    def reconstruir(self, conexion: sqlite3.Connection) -> dict[str, int]:
        """Regenera todos los mapas desde la memoria canónica."""
        conexion.execute("DELETE FROM catalogo_indice")
        conexion.execute("DELETE FROM catalogo_ubicaciones")
        conexion.execute("DELETE FROM catalogo_libros")
        filas = conexion.execute("SELECT * FROM episodios ORDER BY momento, id").fetchall()
        for fila in filas:
            episodio = dict(fila)
            episodio["entrada"] = json.loads(episodio["entrada"])
            episodio["metadata"] = json.loads(episodio["metadata"])
            self.catalogar(conexion, episodio)
        return self.estado(conexion)

    def verificar(self, conexion: sqlite3.Connection) -> dict[str, Any]:
        episodios = conexion.execute("SELECT COUNT(*) FROM episodios").fetchone()[0]
        ubicados = conexion.execute("SELECT COUNT(*) FROM catalogo_ubicaciones").fetchone()[0]
        huerfanos = conexion.execute(
            "SELECT COUNT(*) FROM catalogo_ubicaciones u LEFT JOIN episodios e "
            "ON e.id=u.episodio_id WHERE e.id IS NULL"
        ).fetchone()[0]
        referencias_huerfanas = conexion.execute(
            "SELECT COUNT(*) FROM catalogo_indice i LEFT JOIN episodios e "
            "ON e.id=i.episodio_id WHERE e.id IS NULL"
        ).fetchone()[0]
        manifiestos_incoherentes = 0
        for fila in conexion.execute("SELECT id, cantidad, manifiesto, huella FROM catalogo_libros"):
            texto = fila["manifiesto"]
            manifiesto = json.loads(texto)
            reales = conexion.execute(
                "SELECT COUNT(*) FROM catalogo_ubicaciones WHERE libro_id=?", (fila["id"],)
            ).fetchone()[0]
            huella = hashlib.sha256(texto.encode("utf-8")).hexdigest()
            if reales != fila["cantidad"] or manifiesto.get("cantidad") != reales or huella != fila["huella"]:
                manifiestos_incoherentes += 1
        valido = episodios == ubicados and huerfanos == 0 and referencias_huerfanas == 0 and manifiestos_incoherentes == 0
        return {
            "valido": valido,
            "episodios": episodios,
            "ubicados": ubicados,
            "huerfanos": huerfanos,
            "referencias_huerfanas": referencias_huerfanas,
            "manifiestos_incoherentes": manifiestos_incoherentes,
        }

    def estado(self, conexion: sqlite3.Connection) -> dict[str, int]:
        libros = conexion.execute("SELECT COUNT(*) FROM catalogo_libros").fetchone()[0]
        sellados = conexion.execute(
            "SELECT COUNT(*) FROM catalogo_libros WHERE estado='sellado'"
        ).fetchone()[0]
        ubicaciones = conexion.execute("SELECT COUNT(*) FROM catalogo_ubicaciones").fetchone()[0]
        terminos = conexion.execute("SELECT COUNT(*) FROM catalogo_indice").fetchone()[0]
        return {"libros": libros, "libros_sellados": sellados,
                "ubicaciones": ubicaciones, "terminos": terminos}
