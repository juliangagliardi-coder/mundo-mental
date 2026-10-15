"""Verificador: ejecuta código candidato en un proceso aparte, con auditoría previa, tiempo y memoria acotados.

Defensa en profundidad para código propio de Tierra; no es una frontera de seguridad frente a código hostil.
"""

from __future__ import annotations

import ast
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

IMPORTACIONES_PROHIBIDAS = frozenset({
    "os", "sys", "subprocess", "socket", "shutil", "ctypes", "multiprocessing", "threading",
    "pathlib", "importlib", "urllib", "http", "ftplib", "smtplib", "pickle", "signal", "builtins",
})
FUNCIONES_PROHIBIDAS = frozenset({"open", "exec", "eval", "compile", "__import__", "input", "breakpoint"})
DUNDER_PERMITIDOS = frozenset({
    "__init__", "__name__", "__str__", "__repr__", "__eq__", "__len__", "__iter__", "__next__",
    "__hash__", "__lt__", "__add__", "__contains__", "__getitem__", "__enter__", "__exit__",
})


@dataclass(frozen=True)
class ResultadoVerificacion:
    ok: bool
    motivo: str
    detalle: str = ""
    duracion: float = 0.0


class Verificador:
    def __init__(self, tiempo_max: float = 5.0, memoria_mb: int = 512):
        self.tiempo_max = float(tiempo_max)
        self.memoria_mb = int(memoria_mb)

    def auditar(self, codigo: str) -> tuple[str, str] | None:
        try:
            arbol = ast.parse(codigo)
        except SyntaxError as error:
            return ("sintaxis", f"línea {error.lineno}: {error.msg}")
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    raiz = alias.name.split(".")[0]
                    if raiz in IMPORTACIONES_PROHIBIDAS:
                        return ("prohibido", f"importación de {raiz}")
            elif isinstance(nodo, ast.ImportFrom):
                raiz = (nodo.module or "").split(".")[0]
                if nodo.level > 0 or raiz in IMPORTACIONES_PROHIBIDAS:
                    return ("prohibido", f"importación de {raiz or 'relativa'}")
            elif isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name):
                if nodo.func.id in FUNCIONES_PROHIBIDAS:
                    return ("prohibido", f"llamada a {nodo.func.id}")
            elif isinstance(nodo, ast.Attribute):
                nombre = nodo.attr
                if nombre.startswith("__") and nombre.endswith("__") and nombre not in DUNDER_PERMITIDOS:
                    return ("prohibido", f"atributo {nombre}")
            elif isinstance(nodo, ast.Name) and nodo.id in {"__builtins__", "__import__"}:
                return ("prohibido", f"nombre {nodo.id}")
        return None

    def _limites(self):
        try:
            import resource
        except ImportError:
            return None
        memoria = self.memoria_mb * 1024 * 1024
        cpu = int(self.tiempo_max) + 1

        def aplicar() -> None:
            resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
            resource.setrlimit(resource.RLIMIT_AS, (memoria, memoria))

        return aplicar

    def verificar(self, codigo: str, prueba: str = "") -> ResultadoVerificacion:
        fuente = f"{codigo}\n\n{prueba}\n"
        hallazgo = self.auditar(fuente)
        if hallazgo:
            return ResultadoVerificacion(False, hallazgo[0], hallazgo[1])
        inicio = time.monotonic()
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "candidata.py"
            ruta.write_text(fuente, encoding="utf-8")
            try:
                proceso = subprocess.run(
                    [sys.executable, "-I", str(ruta)], cwd=directorio, capture_output=True, text=True,
                    timeout=self.tiempo_max, env={"PYTHONHASHSEED": "0", "PYTHONIOENCODING": "utf-8"},
                    preexec_fn=self._limites(),
                )
            except subprocess.TimeoutExpired:
                return ResultadoVerificacion(False, "tiempo", f"más de {self.tiempo_max}s",
                                             time.monotonic() - inicio)
        duracion = time.monotonic() - inicio
        if proceso.returncode == 0:
            return ResultadoVerificacion(True, "ok", "", duracion)
        error = proceso.stderr.strip()[-500:]
        motivo = "fallo_prueba" if "AssertionError" in error else "error"
        return ResultadoVerificacion(False, motivo, error, duracion)
