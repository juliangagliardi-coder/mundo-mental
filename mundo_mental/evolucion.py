"""Evolución de código en copia: medir, probar y promover cambios reversibles.

No es un ejecutor de código hostil. Los parches proceden de Tierra, se limitan a una ruta
permitida y se prueban en una copia temporal del repositorio antes de tocar el árbol estable.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .autoridad import Autoridad
from .tierra import ruta_protegida


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ResultadoSuite:
    ok: bool
    retorno: int
    salida: str
    duracion: float
    motivo: str = "ok"


@dataclass(frozen=True)
class ResultadoEvolucion:
    id: str
    ruta: str
    estado: str
    motivo: str
    baseline: ResultadoSuite
    candidata: ResultadoSuite | None = None
    detalle: str = ""

    def como_dict(self) -> dict[str, Any]:
        return asdict(self)


class Evolucion:
    """Promueve cambios de un archivo solo si la suite completa no empeora."""

    ZONA = "evolucion"

    def __init__(self, raiz_repositorio: str | Path, autoridad: Autoridad | None = None,
                 ruta_registro: str | Path | None = None, tiempo_max: float = 60.0,
                 max_bytes_parche: int = 200_000):
        if tiempo_max <= 0:
            raise ValueError("El tiempo máximo debe ser positivo")
        if max_bytes_parche <= 0:
            raise ValueError("El tamaño máximo del parche debe ser positivo")
        self.raiz = Path(raiz_repositorio).resolve()
        self.autoridad = autoridad
        self.tiempo_max = float(tiempo_max)
        self.max_bytes_parche = int(max_bytes_parche)
        self.ruta_registro = Path(ruta_registro) if ruta_registro else self.raiz / ".mente" / "evolucion.jsonl"

    def _ruta(self, ruta: str) -> Path:
        limpia = str(ruta).replace("\\", "/")
        if ruta_protegida(limpia):
            raise PermissionError(f"Ruta protegida: {ruta}")
        destino = (self.raiz / limpia).resolve()
        try:
            destino.relative_to(self.raiz)
        except ValueError as error:
            raise PermissionError(f"Ruta fuera del repositorio: {ruta}") from error
        if not destino.is_file():
            raise FileNotFoundError(destino)
        return destino

    def _ejecutar_suite(self, raiz: Path) -> ResultadoSuite:
        inicio = time.monotonic()
        try:
            proceso = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=raiz,
                capture_output=True, text=True, timeout=self.tiempo_max,
                env={"PYTHONHASHSEED": "0", "PYTHONIOENCODING": "utf-8"},
            )
        except subprocess.TimeoutExpired:
            return ResultadoSuite(False, -1, "", time.monotonic() - inicio, "tiempo")
        salida = ((proceso.stdout or "") + "\n" + (proceso.stderr or "")).strip()[-4000:]
        return ResultadoSuite(proceso.returncode == 0, proceso.returncode, salida,
                              time.monotonic() - inicio, "ok" if proceso.returncode == 0 else "pruebas")

    def _registrar(self, resultado: ResultadoEvolucion) -> None:
        self.ruta_registro.parent.mkdir(parents=True, exist_ok=True)
        with self.ruta_registro.open("a", encoding="utf-8") as archivo:
            archivo.write(json.dumps(resultado.como_dict(), ensure_ascii=False) + "\n")

    def historial(self) -> list[dict[str, Any]]:
        if not self.ruta_registro.exists():
            return []
        with self.ruta_registro.open(encoding="utf-8") as archivo:
            return [json.loads(linea) for linea in archivo if linea.strip()]

    def proponer(self, ruta: str, contenido: str, actor: str = "Tierra") -> ResultadoEvolucion:
        identificador = str(uuid4())
        vacio = ResultadoSuite(False, -1, "", 0.0, "no_ejecutada")
        try:
            destino = self._ruta(ruta)
        except (PermissionError, FileNotFoundError) as error:
            resultado = ResultadoEvolucion(identificador, ruta, "rechazada", "ruta", vacio, detalle=str(error))
            self._registrar(resultado)
            return resultado
        if len(contenido.encode("utf-8")) > self.max_bytes_parche:
            resultado = ResultadoEvolucion(identificador, ruta, "rechazada", "tamano", vacio,
                                            detalle=f"más de {self.max_bytes_parche} bytes")
            self._registrar(resultado)
            return resultado
        try:
            compile(contenido, ruta, "exec")
        except SyntaxError as error:
            resultado = ResultadoEvolucion(identificador, ruta, "rechazada", "sintaxis", vacio,
                                            detalle=f"línea {error.lineno}: {error.msg}")
            self._registrar(resultado)
            return resultado

        baseline = self._ejecutar_suite(self.raiz)
        if not baseline.ok:
            resultado = ResultadoEvolucion(identificador, ruta, "rechazada", "baseline", baseline,
                                            detalle="La suite estable falla; no hay referencia fiable")
            self._registrar(resultado)
            return resultado
        with tempfile.TemporaryDirectory(prefix="mundo_mental_candidata_") as temporal:
            copia = Path(temporal) / "repositorio"
            shutil.copytree(self.raiz, copia, ignore=shutil.ignore_patterns(".git", ".mente", "__pycache__", "*.pyc"))
            destino_copia = copia / destino.relative_to(self.raiz)
            destino_copia.write_text(contenido, encoding="utf-8")
            candidata = self._ejecutar_suite(copia)
        if not candidata.ok:
            resultado = ResultadoEvolucion(identificador, ruta, "rechazada", "regresion", baseline, candidata,
                                            "La candidata no conserva la suite completa")
            self._registrar(resultado)
            return resultado

        original = destino.read_text(encoding="utf-8")

        def ejecutar() -> None:
            destino.write_text(contenido, encoding="utf-8")

        def deshacer() -> None:
            destino.write_text(original, encoding="utf-8")

        if self.autoridad is None:
            estado, motivo = "lista", "sin_autoridad"
        else:
            decision = self.autoridad.actuar(actor, self.ZONA, f"promover:{ruta}", ejecutar, deshacer)
            estado = "promovida" if decision["resultado"] == "ejecutada" else decision["resultado"]
            motivo = "suite_conservada" if estado == "promovida" else decision["resultado"]
        resultado = ResultadoEvolucion(identificador, ruta, estado, motivo, baseline, candidata)
        self._registrar(resultado)
        return resultado
