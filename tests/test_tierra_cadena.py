import json
import tempfile
import unittest
from pathlib import Path

from mundo_mental.banco_tareas import BancoTareas, TAREAS_BASE
from mundo_mental.ciclo_tierra import CicloTierra, construir_tierra
from mundo_mental.libro import Ficha, Libro, tokenizar
from mundo_mental.rol_internalizadora import RolInternalizadora
from mundo_mental.rol_lectora import RolLectora
from mundo_mental.rol_programadora import RolProgramadora, extraer_codigo
from mundo_mental.verificador import Verificador

REF = {t.id: t.referencia for t in TAREAS_BASE}


def bloque(codigo):
    return "```python\n" + codigo + "\n```"


class Guion:
    def __init__(self, *respuestas):
        self.respuestas = list(respuestas)
        self.prompts = []

    def responder(self, instruccion, contexto=""):
        self.prompts.append(instruccion)
        return self.respuestas.pop(0) if self.respuestas else ""


class Base(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.raiz = Path(self._dir.name)


class TestLibro(Base):
    def ficha(self, titulo="Palíndromo", estado="imaginado", **extra):
        datos = dict(titulo=titulo, tema="cadenas", texto="Detectar palíndromos en cadenas",
                     ejemplo="def f(): return 1", prueba="assert f() == 1", procedencia="manual",
                     licencia="CC0", estado=estado)
        datos.update(extra)
        return Ficha(**datos)

    def test_exige_procedencia_y_licencia(self):
        libro = Libro(self.raiz / "l.jsonl")
        with self.assertRaises(ValueError):
            libro.anadir(self.ficha(procedencia=""))
        with self.assertRaises(ValueError):
            libro.anadir(self.ficha(licencia=" "))

    def test_verificada_exige_ejemplo_y_prueba(self):
        with self.assertRaises(ValueError):
            Libro(self.raiz / "l.jsonl").anadir(self.ficha(estado="verificado", prueba=""))

    def test_libro_con_verificador_rechaza_verificada_falsa(self):
        libro = Libro(self.raiz / "l.jsonl", Verificador())
        with self.assertRaises(ValueError):
            libro.anadir(self.ficha(estado="verificado", prueba="assert f() == 2"))
        libro.anadir(self.ficha(estado="verificado"))
        self.assertEqual(len(libro.fichas("verificado")), 1)

    def test_busqueda_ordena_y_ignora_tildes(self):
        libro = Libro(self.raiz / "l.jsonl")
        libro.anadir(self.ficha("Palíndromo"))
        libro.anadir(self.ficha("Fibonacci", tema="numeros", texto="Sucesión numérica", ejemplo="def g(): pass", prueba=""))
        encontrados = libro.buscar("palindromo cadenas")
        self.assertEqual(encontrados[0][0].titulo, "Palíndromo")
        self.assertEqual(libro.buscar("zzz"), [])
        self.assertIn("palindromo", tokenizar("Palíndromo"))

    def test_persistencia_duplicados_y_fracasos(self):
        ruta = self.raiz / "l.jsonl"
        libro = Libro(ruta)
        primera = libro.anadir(self.ficha())
        self.assertEqual(libro.anadir(self.ficha()).id, primera.id)
        mejorada = libro.anadir(self.ficha(estado="verificado"))
        self.assertEqual(mejorada.id, primera.id)
        libro.registrar_fracaso("ctx", "motivo")
        otro = Libro(ruta)
        self.assertEqual(otro.obtener(primera.id).estado, "verificado")
        self.assertEqual(len(otro.fichas()), 1)
        self.assertEqual(otro.fracasos()[0]["motivo"], "motivo")

    def test_solo_verificadas(self):
        libro = Libro(self.raiz / "l.jsonl")
        libro.anadir(self.ficha())
        self.assertEqual(libro.buscar("palindromos", solo_verificadas=True), [])


class TestVerificador(unittest.TestCase):
    def setUp(self):
        self.v = Verificador(tiempo_max=1.0)

    def test_resultados(self):
        self.assertTrue(self.v.verificar("def f(): return 1", "assert f() == 1").ok)
        r = self.v.verificar("def f(): return 1", "assert f() == 2")
        self.assertEqual((r.ok, r.motivo), (False, "fallo_prueba"))
        self.assertEqual(self.v.verificar("raise ValueError('x')").motivo, "error")
        self.assertEqual(self.v.verificar("while True:\n    pass").motivo, "tiempo")
        self.assertEqual(self.v.verificar("def f(:").motivo, "sintaxis")

    def test_auditoria(self):
        for codigo in ("import os", "from subprocess import run", "x = open('a')", "eval('1')",
                       "().__class__.__bases__", "from . import x", "__import__('os')"):
            with self.subTest(codigo=codigo):
                self.assertEqual(self.v.verificar(codigo).motivo, "prohibido")
        self.assertTrue(self.v.verificar("import unicodedata\nclass A:\n    def __init__(self):\n        super().__init__()\nA()").ok)


class TestBanco(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.banco = BancoTareas()

    def test_las_referencias_superan_todo(self):
        self.assertTrue(all(self.banco.autoverificar().values()))

    def test_las_ocultas_detectan_trampas(self):
        r = self.banco.evaluar({"suma_pares": "def suma_pares(numeros):\n    return 6"})
        d = r["detalle"]["suma_pares"]
        self.assertEqual((d["visibles"], d["ocultas"], d["superada"]), (True, False, False))

    def test_comparar_detecta_regresiones(self):
        buena = self.banco.evaluar({"suma_pares": REF["suma_pares"], "fibonacci": REF["fibonacci"]})
        mala = self.banco.evaluar({"suma_pares": "def suma_pares(n): return 0", "fibonacci": REF["fibonacci"],
                                   "es_palindromo": REF["es_palindromo"]})
        c = self.banco.comparar(buena, mala)
        self.assertEqual(c["regresiones"], ["suma_pares"])
        self.assertFalse(c["aceptable"])
        mejor = self.banco.evaluar({"suma_pares": REF["suma_pares"], "fibonacci": REF["fibonacci"],
                                    "es_palindromo": REF["es_palindromo"]})
        c2 = self.banco.comparar(buena, mejor)
        self.assertTrue(c2["aceptable"])
        self.assertGreater(c2["diferencia"], 0)


FUENTE = """Introducción sin código pero con prosa.

# Doble
Duplica un número.
```python
def doble(x):
    return x * 2
```
```python
assert doble(2) == 4
```

# SinPrueba
Un ejemplo sin prueba.
```python
def triple(x):
    return x * 3
```

# Rota
Prueba incorrecta.
```python
def cuadrado(x):
    return x * x
```
```python
assert cuadrado(3) == 10
```
"""


class TestInternalizadoraYLectora(Base):
    def test_internaliza_y_busca(self):
        libro = Libro(self.raiz / "l.jsonl")
        rol = RolInternalizadora(libro)
        r = rol.ejecutar({"fuente": {"titulo": "Manual", "texto": FUENTE, "procedencia": "propio", "licencia": "CC0"}})
        self.assertEqual((r["verificadas"], r["rechazadas"]), (1, 1))
        self.assertEqual(r["imaginadas"], 3)
        self.assertEqual(len(libro.fracasos()), 1)
        lectura = RolLectora(libro).ejecutar({"consulta": "duplica numero", "solo_verificadas": True})
        self.assertEqual(len(lectura["resultados"]), 1)
        self.assertEqual(lectura["resultados"][0]["estado"], "verificado")
        self.assertEqual(RolLectora(libro).ejecutar({"consulta": " "})["resultados"], [])

    def test_exige_procedencia(self):
        with self.assertRaises(ValueError):
            RolInternalizadora(Libro(self.raiz / "l.jsonl")).ejecutar(
                {"fuente": {"titulo": "X", "texto": "a", "licencia": "MIT"}})


class TestProgramadora(Base):
    def setUp(self):
        super().setUp()
        self.libro = Libro(self.raiz / "l.jsonl")
        self.banco = BancoTareas()

    def rol(self, razonador=None):
        return RolProgramadora(self.libro, self.banco, razonador)

    def test_extraer_codigo(self):
        self.assertEqual(extraer_codigo(bloque("def a(): pass")), "def a(): pass")
        self.assertEqual(extraer_codigo("hola"), "")

    def test_sin_modelo_ni_libro_falla_y_deja_rastro(self):
        r = self.rol().ejecutar({"tarea_id": "fibonacci"})
        self.assertEqual((r["estado"], r["origen"]), ("fallida", None))
        self.assertEqual(self.libro.fracasos()[-1]["motivo"], "sin_solucion")

    def test_reutiliza_el_libro(self):
        self.libro.anadir(Ficha("Palíndromo", "cadenas", "Indica si un texto es palíndromo", REF["es_palindromo"],
                                "assert es_palindromo('aba')", "propio", "CC0", "verificado"))
        r = self.rol().ejecutar({"tarea_id": "es_palindromo"})
        self.assertEqual((r["estado"], r["origen"], r["candidata_lista"]), ("resuelta", "libro", True))
        self.assertEqual(r["adopcion"], "requiere_aprobacion_humana")

    def test_reintenta_con_el_error(self):
        guion = Guion(bloque("def es_palindromo(t):\n    return False"), bloque(REF["es_palindromo"]))
        r = self.rol(guion).ejecutar({"tarea_id": "es_palindromo", "intentos": 3})
        self.assertEqual((r["estado"], r["origen"], len(r["intentos"])), ("resuelta", "modelo", 2))
        self.assertIn("fallo_prueba", guion.prompts[1])
        self.assertNotIn("Panama", "".join(guion.prompts))

    def test_solucion_que_no_generaliza_es_parcial(self):
        r = self.rol(Guion(bloque("def suma_pares(numeros):\n    return 6"))).ejecutar({"tarea_id": "suma_pares"})
        self.assertEqual((r["estado"], r["candidata_lista"]), ("parcial", False))
        self.assertEqual(self.libro.fracasos()[-1]["motivo"], "no_generaliza")

    def test_tarea_desconocida(self):
        with self.assertRaises(KeyError):
            self.rol().ejecutar({"tarea_id": "no_existe"})


class TestCiclo(Base):
    def test_ciclo_completo(self):
        libro = Libro(self.raiz / "libro.jsonl")
        banco = BancoTareas()
        guion = Guion("resumen del analista", bloque(REF["es_palindromo"]), bloque(REF["suma_pares"]))
        nucleo, _ = construir_tierra(self.raiz / "mente", libro, banco, guion)
        self.assertEqual(nucleo.roles(), ("analista", "controladora", "internalizadora", "lectora", "programadora"))
        registro = self.raiz / "registro.jsonl"
        ciclo = CicloTierra(nucleo, banco, registro)
        conceptos = {"a": {"fiabilidad": 0.2, "ejemplos_unicos": 5}, "c": {"fiabilidad": 0.9, "ejemplos_unicos": 1}}
        informe = ciclo.ejecutar(conceptos, ["es_palindromo", "suma_pares"], 100)
        self.assertEqual(informe["resumen"], {"resuelta": 2, "parcial": 0, "fallida": 0})
        self.assertEqual(sum(informe["curiosidad"]["reparto"].values()), 100)
        self.assertEqual(informe["analisis"]["debiles"], ["a"])
        lineas = registro.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lineas), 1)
        self.assertEqual(json.loads(lineas[0])["resumen"]["resuelta"], 2)
        tipos = [r["tipo"] for r in nucleo.aspecto.memoria_de_si.historia()]
        self.assertIn("ciclo", tipos)

    def test_ciclo_sin_modelo_registra_fallos(self):
        libro = Libro(self.raiz / "libro.jsonl")
        banco = BancoTareas()
        nucleo, _ = construir_tierra(self.raiz / "mente", libro, banco)
        informe = CicloTierra(nucleo, banco, self.raiz / "r.jsonl").ejecutar({}, ["fibonacci"], 40)
        self.assertEqual(informe["resumen"]["fallida"], 1)
        self.assertIsNone(informe["curiosidad"]["siguiente"])
        with self.assertRaises(ValueError):
            CicloTierra(nucleo, banco, self.raiz / "r.jsonl").ejecutar({}, [], -1)

    def test_registro_en_ruta_protegida(self):
        libro = Libro(self.raiz / "libro.jsonl")
        banco = BancoTareas()
        nucleo, _ = construir_tierra(self.raiz / "mente", libro, banco)
        with self.assertRaises(ValueError):
            CicloTierra(nucleo, banco, "tests/registro.jsonl")


if __name__ == "__main__":
    unittest.main()
