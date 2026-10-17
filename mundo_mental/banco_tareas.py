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

TAREAS_DIFICILES = (
    Tarea(
        "parentesis_balanceados",
        "Indica si los paréntesis (), corchetes [] y llaves {} de un texto están balanceados y bien anidados; ignora los demás caracteres.",
        "parentesis_balanceados(texto)",
        "assert parentesis_balanceados('([]{})')\nassert not parentesis_balanceados('(]')",
        "assert parentesis_balanceados('')\nassert parentesis_balanceados('a(b[c]d)e')\nassert not parentesis_balanceados('((')\n"
        "assert not parentesis_balanceados('())')\nassert not parentesis_balanceados(')(')\nassert not parentesis_balanceados('{[}]')",
        "def parentesis_balanceados(texto):\n    pares = {')': '(', ']': '[', '}': '{'}\n    pila = []\n    for c in texto:\n"
        "        if c in '([{':\n            pila.append(c)\n        elif c in pares:\n"
        "            if not pila or pila.pop() != pares[c]:\n                return False\n    return not pila",
    ),
    Tarea(
        "romano_a_entero",
        "Convierte un número romano válido en mayúsculas (I, V, X, L, C, D, M) a entero.",
        "romano_a_entero(texto)",
        "assert romano_a_entero('XIV') == 14",
        "assert romano_a_entero('III') == 3\nassert romano_a_entero('IV') == 4\nassert romano_a_entero('IX') == 9\n"
        "assert romano_a_entero('MCMXCIV') == 1994\nassert romano_a_entero('MMXXVI') == 2026\nassert romano_a_entero('CDXLIV') == 444",
        "def romano_a_entero(texto):\n    valores = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}\n    total = 0\n"
        "    for i, c in enumerate(texto):\n        v = valores[c]\n        if i + 1 < len(texto) and v < valores[texto[i + 1]]:\n"
        "            total -= v\n        else:\n            total += v\n    return total",
    ),
    Tarea(
        "agrupar_anagramas",
        "Agrupa palabras que son anagramas entre sí, ignorando mayúsculas. Devuelve una lista de grupos; cada grupo conserva el orden de aparición y los grupos van por orden de primera aparición.",
        "agrupar_anagramas(palabras)",
        "assert agrupar_anagramas(['roma', 'amor', 'casa']) == [['roma', 'amor'], ['casa']]",
        "assert agrupar_anagramas([]) == []\nassert agrupar_anagramas(['a']) == [['a']]\n"
        "assert agrupar_anagramas(['Roma', 'amor', 'mora', 'casa', 'saca']) == [['Roma', 'amor', 'mora'], ['casa', 'saca']]",
        "def agrupar_anagramas(palabras):\n    grupos = {}\n    for p in palabras:\n"
        "        grupos.setdefault(''.join(sorted(p.lower())), []).append(p)\n    return list(grupos.values())",
    ),
    Tarea(
        "aplanar",
        "Aplana una lista con listas anidadas a cualquier profundidad en una lista simple, conservando el orden. Las cadenas no se separan.",
        "aplanar(lista)",
        "assert aplanar([1, [2, [3]]]) == [1, 2, 3]",
        "assert aplanar([]) == []\nassert aplanar([[[]]]) == []\nassert aplanar(['ab', ['cd']]) == ['ab', 'cd']\n"
        "assert aplanar([1, [2, [3, [4, [5]]]], 6]) == [1, 2, 3, 4, 5, 6]",
        "def aplanar(lista):\n    resultado = []\n    for x in lista:\n        if isinstance(x, list):\n"
        "            resultado.extend(aplanar(x))\n        else:\n            resultado.append(x)\n    return resultado",
    ),
    Tarea(
        "palabras_frecuentes",
        "Devuelve las n palabras más frecuentes de un texto, en minúscula e ignorando signos de puntuación; en caso de empate, por orden alfabético.",
        "palabras_frecuentes(texto, n)",
        "assert palabras_frecuentes('a b a c b a', 2) == ['a', 'b']",
        "assert palabras_frecuentes('', 3) == []\nassert palabras_frecuentes('Hola, hola! mundo', 1) == ['hola']\n"
        "assert palabras_frecuentes('b a c', 2) == ['a', 'b']\nassert palabras_frecuentes('a b', 5) == ['a', 'b']\n"
        "assert palabras_frecuentes('x x y y z', 2) == ['x', 'y']",
        "import re\nfrom collections import Counter\n\n\ndef palabras_frecuentes(texto, n):\n"
        "    cuenta = Counter(re.findall(r'\\w+', texto.lower()))\n"
        "    return [p for p, _ in sorted(cuenta.items(), key=lambda kv: (-kv[1], kv[0]))[:n]]",
    ),
    Tarea(
        "fusionar_intervalos",
        "Fusiona intervalos [inicio, fin] que se solapan o se tocan y devuelve la lista ordenada de intervalos resultantes como listas. No debe modificar la entrada.",
        "fusionar_intervalos(intervalos)",
        "assert fusionar_intervalos([[1, 3], [2, 6], [8, 10]]) == [[1, 6], [8, 10]]",
        "assert fusionar_intervalos([]) == []\nassert fusionar_intervalos([[1, 4], [4, 5]]) == [[1, 5]]\n"
        "assert fusionar_intervalos([[5, 6], [1, 2]]) == [[1, 2], [5, 6]]\nassert fusionar_intervalos([[1, 10], [2, 3]]) == [[1, 10]]\n"
        "assert fusionar_intervalos([[1, 2], [3, 4]]) == [[1, 2], [3, 4]]\nx = [[3, 4], [1, 2]]\nfusionar_intervalos(x)\nassert x == [[3, 4], [1, 2]]",
        "def fusionar_intervalos(intervalos):\n    resultado = []\n    for ini, fin in sorted(intervalos):\n"
        "        if resultado and ini <= resultado[-1][1]:\n            resultado[-1][1] = max(resultado[-1][1], fin)\n"
        "        else:\n            resultado.append([ini, fin])\n    return resultado",
    ),
    Tarea(
        "cesar",
        "Cifra un texto con César desplazando k letras del alfabeto inglés (k puede ser negativo o mayor que 26); conserva las mayúsculas y deja intactos los demás caracteres.",
        "cesar(texto, k)",
        "assert cesar('abc', 1) == 'bcd'",
        "assert cesar('xyz', 3) == 'abc'\nassert cesar('Hola, Mundo!', 3) == 'Krod, Pxqgr!'\nassert cesar('abc', -1) == 'zab'\n"
        "assert cesar('abc', 27) == 'bcd'\nassert cesar('ñandú', 1) == 'ñboeú'",
        "def cesar(texto, k):\n    salida = []\n    for c in texto:\n        if 'a' <= c <= 'z':\n"
        "            salida.append(chr((ord(c) - 97 + k) % 26 + 97))\n        elif 'A' <= c <= 'Z':\n"
        "            salida.append(chr((ord(c) - 65 + k) % 26 + 65))\n        else:\n            salida.append(c)\n    return ''.join(salida)",
    ),
    Tarea(
        "maximo_subarreglo",
        "Devuelve la mayor suma de un tramo contiguo no vacío de una lista de enteros; devuelve 0 si la lista está vacía.",
        "maximo_subarreglo(numeros)",
        "assert maximo_subarreglo([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6",
        "assert maximo_subarreglo([]) == 0\nassert maximo_subarreglo([-3, -1, -2]) == -1\nassert maximo_subarreglo([5]) == 5\n"
        "assert maximo_subarreglo([1, 2, 3]) == 6\nassert maximo_subarreglo([2, -1, 2]) == 3",
        "def maximo_subarreglo(numeros):\n    if not numeros:\n        return 0\n    mejor = actual = numeros[0]\n"
        "    for x in numeros[1:]:\n        actual = max(x, actual + x)\n        mejor = max(mejor, actual)\n    return mejor",
    ),
)

TAREAS_LOTE2 = (
    Tarea("suma_digitos", "Suma los dígitos de un entero; los negativos se tratan por su valor absoluto.", "suma_digitos(n)",
        "assert suma_digitos(123) == 6",
        """assert suma_digitos(0) == 0
assert suma_digitos(-45) == 9
assert suma_digitos(1000) == 1
assert suma_digitos(99999) == 45""",
        """def suma_digitos(n):
    return sum(int(c) for c in str(abs(n)))"""),
    Tarea("es_anagrama", "Indica si dos textos son anagramas ignorando mayúsculas y espacios.", "es_anagrama(a, b)",
        "assert es_anagrama('Roma', 'amor')",
        """assert es_anagrama('a gentleman', 'elegant man')
assert not es_anagrama('ab', 'abc')
assert es_anagrama('', '')
assert not es_anagrama('aab', 'abb')""",
        """def es_anagrama(a, b):
    def limpio(t):
        return sorted(c for c in t.lower() if not c.isspace())
    return limpio(a) == limpio(b)"""),
    Tarea("mcd", "Devuelve el máximo común divisor de dos enteros no negativos; mcd(0, 0) = 0.", "mcd(a, b)",
        "assert mcd(12, 18) == 6",
        """assert mcd(0, 5) == 5
assert mcd(7, 13) == 1
assert mcd(0, 0) == 0
assert mcd(100, 75) == 25""",
        """def mcd(a, b):
    while b:
        a, b = b, a % b
    return a"""),
    Tarea("mcm", "Devuelve el mínimo común múltiplo de dos enteros positivos.", "mcm(a, b)",
        "assert mcm(4, 6) == 12",
        """assert mcm(1, 5) == 5
assert mcm(7, 13) == 91
assert mcm(12, 18) == 36
assert mcm(5, 5) == 5""",
        """def mcm(a, b):
    x, y = a, b
    while y:
        x, y = y, x % y
    return a * b // x"""),
    Tarea("entero_a_binario", "Devuelve la representación binaria de un entero n >= 0 como texto, sin prefijo.", "entero_a_binario(n)",
        "assert entero_a_binario(5) == '101'",
        """assert entero_a_binario(0) == '0'
assert entero_a_binario(1) == '1'
assert entero_a_binario(255) == '11111111'
assert entero_a_binario(1024) == '10000000000'""",
        """def entero_a_binario(n):
    return bin(n)[2:]"""),
    Tarea("comprimir_texto", "Comprime un texto por repeticiones consecutivas: 'aaabcc' pasa a 'a3b1c2'.", "comprimir_texto(texto)",
        "assert comprimir_texto('aaabcc') == 'a3b1c2'",
        """assert comprimir_texto('') == ''
assert comprimir_texto('a') == 'a1'
assert comprimir_texto('aabbaa') == 'a2b2a2'
assert comprimir_texto('zzzzzzzzzzzz') == 'z12'""",
        """def comprimir_texto(texto):
    salida = []
    i = 0
    while i < len(texto):
        j = i
        while j < len(texto) and texto[j] == texto[i]:
            j += 1
        salida.append(texto[i] + str(j - i))
        i = j
    return ''.join(salida)"""),
    Tarea("interseccion_ordenada", "Devuelve los elementos comunes de dos listas, sin repetir y en orden ascendente.", "interseccion_ordenada(a, b)",
        "assert interseccion_ordenada([1, 2, 2, 3], [2, 3, 4]) == [2, 3]",
        """assert interseccion_ordenada([], [1]) == []
assert interseccion_ordenada([1, 1], [1, 1]) == [1]
assert interseccion_ordenada([5, 3, 1], [1, 3, 5]) == [1, 3, 5]
assert interseccion_ordenada([1, 2], [3, 4]) == []""",
        """def interseccion_ordenada(a, b):
    return sorted(set(a) & set(b))"""),
    Tarea("segundo_mayor", "Devuelve el segundo valor distinto más grande de una lista, o None si no existe.", "segundo_mayor(numeros)",
        "assert segundo_mayor([3, 1, 4, 1, 5]) == 4",
        """assert segundo_mayor([]) is None
assert segundo_mayor([2, 2]) is None
assert segundo_mayor([1, 2]) == 1
assert segundo_mayor([5, 5, 4]) == 4
assert segundo_mayor([-1, -2, -3]) == -2""",
        """def segundo_mayor(numeros):
    distintos = sorted(set(numeros), reverse=True)
    return distintos[1] if len(distintos) > 1 else None"""),
    Tarea("paginar", "Divide una lista en páginas de tamaño tam; si tam <= 0 lanza ValueError.", "paginar(lista, tam)",
        "assert paginar([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]",
        """assert paginar([], 3) == []
assert paginar([1, 2], 5) == [[1, 2]]
try:
    paginar([1], 0)
    raise AssertionError('debe fallar')
except ValueError:
    pass""",
        """def paginar(lista, tam):
    if tam <= 0:
        raise ValueError('tam debe ser positivo')
    return [lista[i:i + tam] for i in range(0, len(lista), tam)]"""),
    Tarea("contar_letras", "Devuelve un diccionario con la frecuencia de cada letra en minúscula; ignora lo que no sea letra.", "contar_letras(texto)",
        "assert contar_letras('Hola') == {'h': 1, 'o': 1, 'l': 1, 'a': 1}",
        """assert contar_letras('') == {}
assert contar_letras('a1 A!') == {'a': 2}
assert contar_letras('ñu') == {'ñ': 1, 'u': 1}""",
        """def contar_letras(texto):
    cuenta = {}
    for c in texto.lower():
        if c.isalpha():
            cuenta[c] = cuenta.get(c, 0) + 1
    return cuenta"""),
    Tarea("transponer", "Devuelve la transpuesta de una matriz rectangular (lista de listas); la matriz vacía da []. No modifica la entrada.", "transponer(matriz)",
        "assert transponer([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]",
        """assert transponer([]) == []
assert transponer([[1]]) == [[1]]
assert transponer([[1], [2], [3]]) == [[1, 2, 3]]
m = [[1, 2], [3, 4]]
transponer(m)
assert m == [[1, 2], [3, 4]]""",
        """def transponer(matriz):
    return [list(fila) for fila in zip(*matriz)]"""),
    Tarea("busqueda_binaria", "Devuelve el índice de x en una lista ordenada ascendente, o -1 si no está.", "busqueda_binaria(lista, x)",
        "assert busqueda_binaria([1, 3, 5, 7], 5) == 2",
        """assert busqueda_binaria([], 1) == -1
assert busqueda_binaria([1], 1) == 0
assert busqueda_binaria([1, 3, 5, 7], 8) == -1
assert busqueda_binaria([1, 3, 5, 7], 1) == 0
assert busqueda_binaria([1, 3, 5, 7], 7) == 3
assert busqueda_binaria(list(range(0, 10000, 2)), 4998) == 2499""",
        """def busqueda_binaria(lista, x):
    lo, hi = 0, len(lista) - 1
    while lo <= hi:
        medio = (lo + hi) // 2
        if lista[medio] == x:
            return medio
        if lista[medio] < x:
            lo = medio + 1
        else:
            hi = medio - 1
    return -1"""),
    Tarea("fizzbuzz", "Devuelve una lista de n textos del 1 al n: 'Fizz' si es múltiplo de 3, 'Buzz' de 5, 'FizzBuzz' de ambos.", "fizzbuzz(n)",
        "assert fizzbuzz(5) == ['1', '2', 'Fizz', '4', 'Buzz']",
        """assert fizzbuzz(0) == []
assert fizzbuzz(15)[-1] == 'FizzBuzz'
assert fizzbuzz(15)[2] == 'Fizz'
assert fizzbuzz(10)[9] == 'Buzz'""",
        """def fizzbuzz(n):
    salida = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            salida.append('FizzBuzz')
        elif i % 3 == 0:
            salida.append('Fizz')
        elif i % 5 == 0:
            salida.append('Buzz')
        else:
            salida.append(str(i))
    return salida"""),
    Tarea("camel_a_snake", "Convierte un identificador camelCase a snake_case: cada mayúscula (salvo al inicio) pasa a '_' más su minúscula.", "camel_a_snake(texto)",
        "assert camel_a_snake('miVariableLarga') == 'mi_variable_larga'",
        """assert camel_a_snake('') == ''
assert camel_a_snake('a') == 'a'
assert camel_a_snake('unaDosTres') == 'una_dos_tres'
assert camel_a_snake('Casa') == 'casa'
assert camel_a_snake('aB') == 'a_b'""",
        """def camel_a_snake(texto):
    salida = []
    for i, c in enumerate(texto):
        if c.isupper():
            if i > 0:
                salida.append('_')
            salida.append(c.lower())
        else:
            salida.append(c)
    return ''.join(salida)"""),
    Tarea("numero_a_romano", "Convierte un entero entre 1 y 3999 a número romano en mayúsculas.", "numero_a_romano(n)",
        "assert numero_a_romano(14) == 'XIV'",
        """assert numero_a_romano(4) == 'IV'
assert numero_a_romano(9) == 'IX'
assert numero_a_romano(1994) == 'MCMXCIV'
assert numero_a_romano(2026) == 'MMXXVI'
assert numero_a_romano(3999) == 'MMMCMXCIX'
assert numero_a_romano(444) == 'CDXLIV'""",
        """def numero_a_romano(n):
    tabla = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'),
             (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
    salida = []
    for valor, simbolo in tabla:
        while n >= valor:
            salida.append(simbolo)
            n -= valor
    return ''.join(salida)"""),
    Tarea("es_bisiesto", "Indica si un año del calendario gregoriano es bisiesto.", "es_bisiesto(anio)",
        "assert es_bisiesto(2024)\nassert not es_bisiesto(1900)",
        """assert es_bisiesto(2000)
assert not es_bisiesto(2100)
assert not es_bisiesto(2023)
assert es_bisiesto(1600)""",
        """def es_bisiesto(anio):
    return anio % 4 == 0 and (anio % 100 != 0 or anio % 400 == 0)"""),
    Tarea("hay_par_con_suma", "Indica si existen dos elementos en posiciones distintas de la lista cuya suma sea el objetivo.", "hay_par_con_suma(numeros, objetivo)",
        "assert hay_par_con_suma([2, 7, 11, 15], 9)",
        """assert not hay_par_con_suma([], 1)
assert not hay_par_con_suma([5], 10)
assert hay_par_con_suma([5, 5], 10)
assert not hay_par_con_suma([1, 2, 3], 7)
assert hay_par_con_suma([-1, 1], 0)""",
        """def hay_par_con_suma(numeros, objetivo):
    vistos = set()
    for x in numeros:
        if objetivo - x in vistos:
            return True
        vistos.add(x)
    return False"""),
    Tarea("moda", "Devuelve el valor más frecuente de una lista; en empate el menor; None si está vacía.", "moda(numeros)",
        "assert moda([1, 2, 2, 3]) == 2",
        """assert moda([]) is None
assert moda([1, 1, 2, 2]) == 1
assert moda([5]) == 5
assert moda([3, 3, 1, 1, 2]) == 1
assert moda([-1, -1, 0]) == -1""",
        """def moda(numeros):
    if not numeros:
        return None
    cuenta = {}
    for x in numeros:
        cuenta[x] = cuenta.get(x, 0) + 1
    return min(cuenta, key=lambda v: (-cuenta[v], v))"""),
    Tarea("prefijo_comun", "Devuelve el prefijo común más largo de una lista de palabras, o '' si no hay.", "prefijo_comun(palabras)",
        "assert prefijo_comun(['flor', 'flores', 'flota']) == 'flo'",
        """assert prefijo_comun([]) == ''
assert prefijo_comun(['a']) == 'a'
assert prefijo_comun(['abc', 'xyz']) == ''
assert prefijo_comun(['igual', 'igual']) == 'igual'
assert prefijo_comun(['', 'a']) == ''""",
        """def prefijo_comun(palabras):
    if not palabras:
        return ''
    prefijo = palabras[0]
    for p in palabras[1:]:
        while not p.startswith(prefijo):
            prefijo = prefijo[:-1]
    return prefijo"""),
    Tarea("fusionar_ordenadas", "Fusiona dos listas ordenadas ascendentes en una sola lista ordenada. No modifica las entradas.", "fusionar_ordenadas(a, b)",
        "assert fusionar_ordenadas([1, 3, 5], [2, 4]) == [1, 2, 3, 4, 5]",
        """assert fusionar_ordenadas([], []) == []
assert fusionar_ordenadas([], [1]) == [1]
assert fusionar_ordenadas([1, 1], [1]) == [1, 1, 1]
assert fusionar_ordenadas([1, 2], [3, 4]) == [1, 2, 3, 4]
x = [1, 3]
y = [2]
fusionar_ordenadas(x, y)
assert x == [1, 3] and y == [2]""",
        """def fusionar_ordenadas(a, b):
    i = j = 0
    salida = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            salida.append(a[i])
            i += 1
        else:
            salida.append(b[j])
            j += 1
    salida.extend(a[i:])
    salida.extend(b[j:])
    return salida"""),
)


class BancoTareas:
    def __init__(self, tareas: tuple[Tarea, ...] | None = None, verificador: Verificador | None = None):
        tareas = TAREAS_BASE + TAREAS_EXTRA + TAREAS_DIFICILES + TAREAS_LOTE2 if tareas is None else tareas
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
