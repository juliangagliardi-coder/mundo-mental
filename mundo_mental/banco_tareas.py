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

TAREAS_EXTRA = (
    Tarea(
        "maximo_lista", "Devuelve el mayor número de una lista de enteros, o None si la lista está vacía.",
        "maximo_lista(numeros)",
        "assert maximo_lista([3, 9, 2]) == 9",
        "assert maximo_lista([]) is None\nassert maximo_lista([-5, -2, -9]) == -2\nassert maximo_lista([7]) == 7",
        "def maximo_lista(numeros):\n    return max(numeros) if numeros else None",
    ),
    Tarea(
        "contar_palabras", "Cuenta las palabras de un texto separadas por uno o más espacios.",
        "contar_palabras(texto)",
        "assert contar_palabras('uno dos tres') == 3",
        "assert contar_palabras('') == 0\nassert contar_palabras('  a   b ') == 2\nassert contar_palabras('   ') == 0",
        "def contar_palabras(texto):\n    return len(texto.split())",
    ),
    Tarea(
        "es_primo", "Indica si un entero es primo. Los menores que 2 no lo son.", "es_primo(n)",
        "assert es_primo(7)\nassert not es_primo(8)",
        "assert not es_primo(0)\nassert not es_primo(1)\nassert not es_primo(-3)\nassert es_primo(2)\n"
        "assert es_primo(97)\nassert not es_primo(91)",
        "def es_primo(n):\n    if n < 2:\n        return False\n    i = 2\n    while i * i <= n:\n        if n % i == 0:\n            return False\n        i += 1\n    return True",
    ),
    Tarea(
        "quitar_duplicados",
        "Devuelve una lista sin elementos repetidos, conservando el orden de la primera aparición.",
        "quitar_duplicados(lista)",
        "assert quitar_duplicados([1, 2, 1, 3, 2]) == [1, 2, 3]",
        "assert quitar_duplicados([]) == []\nassert quitar_duplicados(['a', 'b', 'a']) == ['a', 'b']\n"
        "assert quitar_duplicados([3, 3, 3]) == [3]",
        "def quitar_duplicados(lista):\n    vistos = set()\n    resultado = []\n    for x in lista:\n        if x not in vistos:\n            vistos.add(x)\n            resultado.append(x)\n    return resultado",
    ),
    Tarea(
        "factorial", "Devuelve el factorial de un entero n >= 0, con factorial(0) = 1.", "factorial(n)",
        "assert factorial(5) == 120",
        "assert factorial(0) == 1\nassert factorial(1) == 1\nassert factorial(10) == 3628800",
        "def factorial(n):\n    resultado = 1\n    for i in range(2, n + 1):\n        resultado *= i\n    return resultado",
    ),
    Tarea(
        "mayusculas_iniciales",
        "Pone en mayúscula la primera letra de cada palabra y en minúscula el resto, separando por un espacio.",
        "mayusculas_iniciales(texto)",
        "assert mayusculas_iniciales('hola mundo') == 'Hola Mundo'",
        "assert mayusculas_iniciales('') == ''\nassert mayusculas_iniciales('hOLA   mUNDO') == 'Hola Mundo'\n"
        "assert mayusculas_iniciales('ñandú rojo') == 'Ñandú Rojo'",
        "def mayusculas_iniciales(texto):\n    return ' '.join(p.capitalize() for p in texto.split())",
    ),
    Tarea(
        "rotar_lista",
        "Rota una lista k posiciones hacia la derecha; k puede ser mayor que la longitud o negativo.",
        "rotar_lista(lista, k)",
        "assert rotar_lista([1, 2, 3, 4], 1) == [4, 1, 2, 3]",
        "assert rotar_lista([], 3) == []\nassert rotar_lista([1, 2, 3], 4) == [3, 1, 2]\n"
        "assert rotar_lista([1, 2, 3], -1) == [2, 3, 1]\nassert rotar_lista([1, 2, 3], 0) == [1, 2, 3]",
        "def rotar_lista(lista, k):\n    if not lista:\n        return []\n    k %= len(lista)\n    if k == 0:\n        return list(lista)\n    return lista[-k:] + lista[:-k]",
    ),
)


class BancoTareas:
    def __init__(self, tareas: tuple[Tarea, ...] | None = None, verificador: Verificador | None = None):
        tareas = TAREAS_BASE + TAREAS_EXTRA if tareas is None else tareas
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
