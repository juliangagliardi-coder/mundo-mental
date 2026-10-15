import tempfile
import unittest

from mundo_mental.curiosidad import Curiosidad
from mundo_mental.roles_tierra import RolAnalista, RolControladora
from mundo_mental.tierra import crear_tierra, ruta_protegida

CONCEPTOS = {
    "a": {"fiabilidad": 0.2, "ejemplos_unicos": 5},
    "b": {"fiabilidad": 0.7, "ejemplos_unicos": 5},
    "c": {"fiabilidad": 0.9, "ejemplos_unicos": 1},
    "d": {"fiabilidad": 0.95, "ejemplos_unicos": 9},
}


class Redactor:
    def responder(self, instruccion, contexto=""):
        return "texto redactado"


class TestRolAnalista(unittest.TestCase):
    def test_clasifica_conceptos_con_reglas(self):
        r = RolAnalista().ejecutar({"conceptos": CONCEPTOS})
        self.assertEqual((r["total"], r["debiles"], r["pocos_ejemplos"], r["solidos"]),
                         (4, ["a", "b"], ["c"], ["d"]))
        self.assertNotIn("redaccion", r)

    def test_el_razonador_solo_redacta(self):
        r = RolAnalista(Redactor()).ejecutar({"conceptos": CONCEPTOS})
        self.assertEqual(r["redaccion"], "texto redactado")
        self.assertEqual(r["debiles"], ["a", "b"])

    def test_sin_conceptos(self):
        self.assertEqual(RolAnalista().ejecutar({})["total"], 0)


class TestRolControladora(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.curiosidad = Curiosidad(self._dir.name)
        self.rol = RolControladora(self.curiosidad)

    def test_elige_la_pregunta_mas_prioritaria(self):
        r = self.rol.ejecutar({"conceptos": CONCEPTOS})
        self.assertEqual(len(r["preguntas_nuevas"]), 3)
        self.assertIn("concepto a", r["siguiente"])
        self.assertEqual(r["pendientes"], 2)

    def test_el_reparto_suma_el_presupuesto(self):
        r = self.rol.ejecutar({"conceptos": CONCEPTOS, "presupuesto": 100})
        self.assertEqual(sum(r["reparto"].values()), 100)
        self.assertEqual(len(r["reparto"]), 3)
        self.assertEqual(max(r["reparto"], key=r["reparto"].get), r["siguiente"])

    def test_sin_preguntas(self):
        r = self.rol.ejecutar({})
        self.assertIsNone(r["siguiente"])
        self.assertEqual((r["reparto"], r["pendientes"]), ({}, 0))

    def test_presupuesto_negativo_falla(self):
        with self.assertRaises(ValueError):
            self.rol.ejecutar({"conceptos": CONCEPTOS, "presupuesto": -1})

    def test_integracion_con_nucleo_tierra(self):
        nucleo = crear_tierra(self._dir.name + "/tierra")
        nucleo.registrar_rol(RolAnalista())
        nucleo.registrar_rol(RolControladora(self.curiosidad))
        self.assertEqual(nucleo.roles(), ("analista", "controladora"))
        self.assertEqual(nucleo.ejecutar_rol("analista", {"conceptos": CONCEPTOS})["total"], 4)
        self.assertIsNotNone(nucleo.ejecutar_rol("controladora", {"conceptos": CONCEPTOS})["siguiente"])
        self.assertTrue(ruta_protegida("CONSTITUCION.md"))


if __name__ == "__main__":
    unittest.main()
