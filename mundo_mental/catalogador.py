"""Catalogador 0.1: índices mecánicos reconstruibles para la Biblioteca."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections import Counter
from datetime import datetime
from typing import Any, Iterable


def _canon(valor: Any) -> str:
    return json.dumps(valor, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _fecha(momento: str) -> str:
    try:
        return datetime.fromisoformat(momento.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return momento[:10] or "sin-fecha"


class Catalogador:
    """Auxiliar determinista sin identidad ni autoridad semántica."""

    VERSION = "0.1.0"

    def __init__(self, max_episodios_libro: int = 256):
        self.max_episodios_libro = max(1, int(max_episodios_libro))

    def crear_esquema(self, conexion: sqlite3.Connection) -> None:
        conexion.executescript("""
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

    @staticmethod
    def _terminos(episodio: dict[str, Any]) -> dict[str, float]:
        entrada = episodio.get("entrada", [])
        metadata = episodio.get("metadata", {}) or {}
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
        conexion.execute(
            "INSERT INTO catalogo_libros(id, fecha, secuencia, estado) VALUES (?, ?, ?, 'abierto')",
            (identidad, fecha, secuencia),
        )
        return conexion.execute("SELECT * FROM catalogo_libros WHERE id=?", (identidad,)).fetchone()

    def catalogar(self, conexion: sqlite3.Connection, episodio: dict[str, Any]) -> str:
        """Ubica un episodio canónico y actualiza mapas; no interpreta su significado."""
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
        self._actualizar_manifiesto(conexion, libro["id"])
        actualizado = conexion.execute("SELECT * FROM catalogo_libros WHERE id=?", (libro["id"],)).fetchone()
        if actualizado["cantidad"] >= self.max_episodios_libro:
            self._sellar(conexion, libro["id"])
        return libro["id"]

    def _actualizar_manifiesto(self, conexion: sqlite3.Connection, libro_id: str) -> None:
        filas = conexion.execute(
            "SELECT e.* FROM episodios e JOIN catalogo_ubicaciones u ON u.episodio_id=e.id "
            "WHERE u.libro_id=? ORDER BY u.posicion", (libro_id,),
        ).fetchall()
        episodios = [dict(fila) for fila in filas]
        temas: Counter[str] = Counter()
        origenes: Counter[str] = Counter()
        for episodio in episodios:
            temas[str(episodio.get("esperado", "sin-tema"))] += 1
            metadata = json.loads(episodio.get("metadata") or "{}")
            origen = metadata.get("origen") or metadata.get("aspecto")
            if origen:
                origenes[str(origen)] += 1
            extras = metadata.get("temas", [])
            if isinstance(extras, str):
                extras = [extras]
            temas.update(str(x) for x in extras)
        importancias = [float(x["importancia"]) for x in episodios]
        momentos = [str(x["momento"]) for x in episodios]
        manifiesto = {
            "version": 1,
            "libro": libro_id,
            "cantidad": len(episodios),
            "primer_momento": min(momentos) if momentos else None,
            "ultimo_momento": max(momentos) if momentos else None,
            "temas": dict(temas.most_common(32)),
            "origenes": dict(origenes.most_common(16)),
            "importancia": {
                "minima": min(importancias) if importancias else 0.0,
                "maxima": max(importancias) if importancias else 0.0,
            },
        }
        texto = _canon(manifiesto)
        huella = hashlib.sha256(texto.encode("utf-8")).hexdigest()
        conexion.execute(
            "UPDATE catalogo_libros SET cantidad=?, primer_momento=?, ultimo_momento=?, "
            "manifiesto=?, huella=? WHERE id=?",
            (len(episodios), manifiesto["primer_momento"], manifiesto["ultimo_momento"],
             texto, huella, libro_id),
        )

    def _sellar(self, conexion: sqlite3.Connection, libro_id: str) -> None:
        self._actualizar_manifiesto(conexion, libro_id)
        conexion.execute("UPDATE catalogo_libros SET estado='sellado' WHERE id=?", (libro_id,))

    def candidatos(self, conexion: sqlite3.Connection, entrada: Iterable[Any], limite: int = 128,
                   esperado: str | None = None) -> list[str]:
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
        return [fila["episodio_id"] for fila in filas]

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
        return {
            "valido": episodios == ubicados and huerfanos == 0,
            "episodios": episodios,
            "ubicados": ubicados,
            "huerfanos": huerfanos,
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
