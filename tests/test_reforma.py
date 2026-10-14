import tempfile
import unittest

from mundo_mental.autoridad import Autoridad
from mundo_mental.biblioteca import Biblioteca
from mundo_mental.observacion import Centinela, Guardian
from mundo_mental.reforma import reformar


class FalsoCorazon:
    def __init__(self, biblioteca, fallar=False):
        self.biblioteca = biblioteca
        self.fallar = fallar
        self.llamadas = 0

    def latir(self, habilidad, entrenamiento, pruebas, protegidos=()):
        self.llamadas += 1
        self.biblioteca.guardar_habilidad(habilidad, {"v": 2})
        if self.fallar:
            raise RuntimeError("fallo")
        return {"aceptada": True}


class TestReforma(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.biblioteca = Biblioteca(self.tmp.name)
        self.biblioteca.guardar_habilidad("x", {"v": 1})
        self.guardian = Guardian(self.tmp.name)
        self.autoridad = Autoridad(self.tmp.name, Centinela(self.guardian.buzon), self.guardian)

    def test_reforma_exitosa_se_registra(self):
        corazon = FalsoCorazon(self.biblioteca)
        r = reformar(corazon, self.autoridad, "x", [], [])
        self.assertEqual(r["resultado"], "ejecutada")
        self.assertEqual(r["latido"], {"aceptada": True})
        self.assertEqual(self.biblioteca.cargar_habilidad("x"), {"v": 2})

    def test_reforma_fallida_restaura_la_habilidad(self):
        corazon = FalsoCorazon(self.biblioteca, fallar=True)
        r = reformar(corazon, self.autoridad, "x", [], [])
        self.assertEqual(r["resultado"], "revertida")
        self.assertEqual(self.biblioteca.cargar_habilidad("x"), {"v": 1})
        self.assertIsNone(r["latido"])

    def test_zona_protegida_no_llega_a_latir(self):
        corazon = FalsoCorazon(self.biblioteca)
        r = reformar(corazon, self.autoridad, "x", [], [], zona="constitucion")
        self.assertEqual(r["resultado"], "bloqueada")
        self.assertEqual(corazon.llamadas, 0)
        self.assertEqual(self.biblioteca.cargar_habilidad("x"), {"v": 1})


if __name__ == "__main__":
    unittest.main()
