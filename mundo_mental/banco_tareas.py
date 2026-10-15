"""Banco de tareas con pruebas visibles y ocultas: mide si una versión mejora a la anterior (reglas 3, 11)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .verificador import Verificador


@dataclass(frozen=True)
class Tarea:
    id: str
    enunciado: str
    funcion: str
    visibles: str
    ocultas: str
    referencia: str = field(default="", repr=False)


TAREAS_BASE = (
    Tarea(
        "suma_pares", "Suma los números pares de una lista de enteros.", "suma_pares(numeros)",
        "assert suma_pares([1, 2, 3, 4]) == 6",
        "assert suma_pares([]) == 0\nassert suma_pares([-2, -3, 8]) == 6\nassert suma_pares([1, 3]) == 0",
        "def suma_pares(numeros):\n    return sum(n for n in numeros if n % 2 == 0)",
    ),
    Tarea(
        "es_palindromo", "Indica si un texto es palíndromo ignorando mayúsculas y signos.", "es_palindromo(texto)",
        "assert es_palindromo('Reconocer')\nassert not es_palindromo('hola')",
        "assert es_palindromo('A man, a plan, a canal: Panama')\nassert es_palindromo('')\nassert not es_palindromo('ab')",
        "def es_palindromo(texto):\n    c = [x.lower() for x in texto if x.isalnum()]\n    return c == c[::-1]",
    ),
    Tarea(
        "invertir_palabras", "Invierte el orden de las palabras de un texto separadas por espacios.",
        "invertir_palabras(texto)",
        "assert invertir_palabras('uno dos tres') == 'tres dos uno'",
        "assert invertir_palabras('') == ''\nassert invertir_palabras('  a   b ') == 'b a'",
        "def invertir_palabras(texto):\n    return ' '.join(reversed(texto.split()))",
    ),
    Tarea(
        "fibonacci", "Devuelve el n-ésimo número de Fibonacci con fibonacci(0)=0 y fibonacci(1)=1.",
        "fibonacci(n)",
        "assert fibonacci(10) == 55",
        "assert fibonacci(0) == 0\nassert fibonacci(1) == 1\nassert fibonacci(30) == 832040",
        "def fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a",
    ),
    Tarea(
        "contar_vocales", "Cuenta las vocales de un texto, con o sin tilde, sin distinguir mayúsculas.",
        "contar_vocales(texto)",
        "assert contar_vocales('Murcielago') == 5",
        "assert contar_vocales('') == 0\nassert contar_vocales('xyz') == 0\nassert contar_vocales('canción') == 3\nassert contar_vocales('ÁÉÍÓÚ') == 5",
        "import unicodedata\n\n\ndef contar_vocales(texto):\n    base = unicodedata.normalize('NFD', texto)\n    return sum(1 for c in base.lower() if c in 'aeiou')",
    ),
)


class BancoTareas:
    def __init__(self, tareas: tuple[Tarea, ...] = TAREAS_BASE, verificador: Verificador | None = None):
        self._tareas = {t.id: t for t in tareas}
        self._verificador = verificador or Verificador()

    def ids(self) -> tuple[str, ...]:
        return tuple(self._tareas)

    def obtener(self, tarea_id: str) -> Tarea:
        return self._tareas[tarea_id]

    def autoverificar(self) -> dict[str, bool]:
        resultado = {}
        for tarea in self._tareas.values():
            v = self._verificador.verificar(tarea.referencia, tarea.visibles)
            o = self._verificador.verificar(tarea.referencia, tarea.ocultas)
            resultado[tarea.id] = v.ok and o.ok
        return resultado

    def evaluar(self, soluciones: dict[str, str]) -> dict[str, Any]:
        detalle = {}
        for tarea in self._tareas.values():
            codigo = soluciones.get(tarea.id, "")
            v = self._verificador.verificar(codigo, tarea.visibles) if codigo.strip() else None
            o = self._verificador.verificar(codigo, tarea.ocultas) if codigo.strip() else None
            visibles = bool(v and v.ok)
            ocultas = bool(o and o.ok)
            detalle[tarea.id] = {"visibles": visibles, "ocultas": ocultas, "superada": visibles and ocultas}
        superadas = sum(1 for d in detalle.values() if d["superada"])
        return {"detalle": detalle, "superadas": superadas, "total": len(detalle),
                "puntuacion": superadas / len(detalle) if detalle else 0.0}

    @staticmethod
    def comparar(anterior: dict[str, Any], candidata: dict[str, Any]) -> dict[str, Any]:
        regresiones = sorted(
            t for t, d in anterior["detalle"].items()
            if d["superada"] and not candidata["detalle"].get(t, {}).get("superada", False)
        )
        mejora = candidata["puntuacion"] > anterior["puntuacion"]
        return {"mejora": mejora, "regresiones": regresiones,
                "aceptable": mejora and not regresiones,
                "diferencia": candidata["puntuacion"] - anterior["puntuacion"]}
