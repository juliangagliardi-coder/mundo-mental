"""El Libro: conocimiento de programación con procedencia, licencia y estado (reglas 6 y 22)."""

from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any
from uuid import uuid4

ESTADOS = ("imaginado", "verificado")
K1 = 1.5
B = 0.75


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


def tokenizar(texto: str) -> list[str]:
    plano = unicodedata.normalize("NFKD", texto.lower())
    plano = "".join(c for c in plano if not unicodedata.combining(c))
    return [t for t in re.findall(r"[a-z0-9_]+", plano) if len(t) > 1]


@dataclass(frozen=True)
class Ficha:
    titulo: str
    tema: str
    texto: str
    ejemplo: str
    prueba: str
    procedencia: str
    licencia: str
    estado: str = "imaginado"
    id: str = field(default_factory=lambda: str(uuid4()))
    creada: str = field(default_factory=_ahora)

    def huella(self) -> str:
        bruto = "\x1f".join((self.titulo, self.texto, self.ejemplo, self.prueba))
        return hashlib.sha256(bruto.encode("utf-8")).hexdigest()

    def validar(self) -> None:
        if not self.titulo.strip():
            raise ValueError("La ficha necesita título")
        if not self.procedencia.strip() or not self.licencia.strip():
            raise ValueError("Toda ficha necesita procedencia y licencia")
        if self.estado not in ESTADOS:
            raise ValueError(f"Estado desconocido: {self.estado}")
        if not (self.texto.strip() or self.ejemplo.strip()):
            raise ValueError("La ficha no puede estar vacía")
        if self.estado == "verificado" and not (self.ejemplo.strip() and self.prueba.strip()):
            raise ValueError("Una ficha verificada necesita ejemplo y prueba")


class Libro:
    def __init__(self, ruta: str | Path, verificador: Any = None):
        self.ruta = Path(ruta)
        self._verificador = verificador
        self._cerrojo = RLock()
        self._fichas: dict[str, Ficha] = {}
        self._fracasos: list[dict[str, Any]] = []
        self._cargar()

    def _cargar(self) -> None:
        if not self.ruta.exists():
            return
        with self.ruta.open(encoding="utf-8") as archivo:
            for linea in archivo:
                if not linea.strip():
                    continue
                registro = json.loads(linea)
                if registro["tipo"] == "ficha":
                    ficha = Ficha(**registro["datos"])
                    self._fichas[ficha.id] = ficha
                elif registro["tipo"] == "fracaso":
                    self._fracasos.append(registro["datos"])

    def _anexar(self, tipo: str, datos: dict[str, Any]) -> None:
        with self._cerrojo:
            self.ruta.parent.mkdir(parents=True, exist_ok=True)
            with self.ruta.open("a", encoding="utf-8") as archivo:
                archivo.write(json.dumps({"tipo": tipo, "datos": datos}, ensure_ascii=False) + "\n")

    def _guardar(self, ficha: Ficha) -> None:
        self._fichas[ficha.id] = ficha
        self._anexar("ficha", asdict(ficha))

    def anadir(self, ficha: Ficha) -> Ficha:
        ficha.validar()
        if ficha.estado == "verificado" and self._verificador is not None:
            resultado = self._verificador.verificar(ficha.ejemplo, ficha.prueba)
            if not resultado.ok:
                raise ValueError(f"La verificación falló: {resultado.motivo}")
        with self._cerrojo:
            huella = ficha.huella()
            for existente in self._fichas.values():
                if existente.huella() == huella:
                    if ficha.estado == "verificado" and existente.estado != "verificado":
                        mejorada = replace(ficha, id=existente.id, creada=existente.creada)
                        self._guardar(mejorada)
                        return mejorada
                    return existente
            self._guardar(ficha)
            return ficha

    def obtener(self, ficha_id: str) -> Ficha:
        return self._fichas[ficha_id]

    def fichas(self, estado: str | None = None) -> list[Ficha]:
        return [f for f in self._fichas.values() if estado is None or f.estado == estado]

    def registrar_fracaso(self, contexto: str, motivo: str, datos: dict[str, Any] | None = None) -> None:
        registro = {"momento": _ahora(), "contexto": contexto, "motivo": motivo, "datos": datos or {}}
        with self._cerrojo:
            self._fracasos.append(registro)
            self._anexar("fracaso", registro)

    def fracasos(self) -> list[dict[str, Any]]:
        return list(self._fracasos)

    def buscar(self, consulta: str, limite: int = 5, solo_verificadas: bool = False) -> list[tuple[Ficha, float]]:
        terminos = set(tokenizar(consulta))
        fichas = [f for f in self._fichas.values() if not solo_verificadas or f.estado == "verificado"]
        if not terminos or not fichas:
            return []
        docs = {f.id: Counter(tokenizar(f"{f.titulo} {f.titulo} {f.tema} {f.texto} {f.ejemplo}")) for f in fichas}
        longitudes = {i: sum(c.values()) for i, c in docs.items()}
        media = (sum(longitudes.values()) / len(fichas)) or 1.0
        n = len(fichas)
        df = {t: sum(1 for c in docs.values() if t in c) for t in terminos}
        resultados = []
        for ficha in fichas:
            conteo = docs[ficha.id]
            puntos = 0.0
            for termino in terminos:
                if termino not in conteo:
                    continue
                idf = math.log(1 + (n - df[termino] + 0.5) / (df[termino] + 0.5))
                tf = conteo[termino]
                puntos += idf * tf * (K1 + 1) / (tf + K1 * (1 - B + B * longitudes[ficha.id] / media))
            if puntos > 0:
                resultados.append((ficha, puntos))
        resultados.sort(key=lambda x: (-x[1], x[0].titulo))
        return resultados[:max(0, int(limite))]
