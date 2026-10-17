import tempfile
import unittest
from pathlib import Path

from mundo_mental.autoridad import Autoridad
from mundo_mental.evolucion import Evolucion
from mundo_mental.observacion import BuzonAlarmas, Centinela, Guardian


BUENO = "def valor():\n    return 1\n"
ROTO = "def valor(:\n    return 1\n"


class TestEvolucion(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)
        (self.raiz / "mundo_mental").mkdir()
        (self.raiz / "tests").mkdir()
        (self.raiz / "mundo_mental" / "modulo.py").write_text(BUENO, encoding="utf-8")
        (self.raiz / "mundo_mental" / "__init__.py").write_text("", encoding="utf-8")
        (self.raiz / "tests" / "test_modulo.py").write_text(
            "from mundo_mental.modulo import valor\n\nclass T:\n    def test_valor(self):\n        assert valor() == 1\n", encoding="utf-8")

    def autoridad(self):
        guardian = Guardian(self.raiz / ".mente")
        return Autoridad(self.raiz / ".mente", Centinela(guardian.buzon), guardian)

    def motor(self, autoridad=None, **extra):
        return Evolucion(self.raiz, autoridad, tiempo_max=10, **extra)

    def test_promueve_cambio_que_conserva_suite(self):
        r = self.motor(self.autoridad()).proponer("mundo_mental/modulo.py", BUENO + "\n# candidato\n")
        self.assertEqual((r.estado, r.motivo), ("promovida", "suite_conservada"))
        self.assertIn("candidato", (self.raiz / "mundo_mental" / "modulo.py").read_text(encoding="utf-8"))
        self.assertEqual(len(self.motor().historial()), 1)

    def test_sin_autoridad_solo_deja_lista(self):
        r = self.motor().proponer("mundo_mental/modulo.py", BUENO)
        self.assertEqual((r.estado, r.motivo), ("lista", "sin_autoridad"))
        self.assertEqual((self.raiz / "mundo_mental" / "modulo.py").read_text(encoding="utf-8"), BUENO)

    def test_rechaza_sintaxis_y_no_toca_estable(self):
        r = self.motor().proponer("mundo_mental/modulo.py", ROTO)
        self.assertEqual((r.estado, r.motivo), ("rechazada", "sintaxis"))
        self.assertEqual((self.raiz / "mundo_mental" / "modulo.py").read_text(encoding="utf-8"), BUENO)

    def test_rechaza_regresion_y_no_toca_estable(self):
        r = self.motor().proponer("mundo_mental/modulo.py", "def valor():\n    return 2\n")
        self.assertEqual((r.estado, r.motivo), ("rechazada", "regresion"))
        self.assertEqual((self.raiz / "mundo_mental" / "modulo.py").read_text(encoding="utf-8"), BUENO)

    def test_rechaza_rutas_protegidas_y_fuera(self):
        (self.raiz / "CONSTITUCION.md").write_text("x", encoding="utf-8")
        for ruta in ("CONSTITUCION.md", "tests/test_modulo.py", "../fuera.py"):
            with self.subTest(ruta=ruta):
                r = self.motor().proponer(ruta, "x = 1\n")
                self.assertEqual((r.estado, r.motivo), ("rechazada", "ruta"))

    def test_limita_el_tamano(self):
        r = self.motor(max_bytes_parche=5).proponer("mundo_mental/modulo.py", BUENO)
        self.assertEqual((r.estado, r.motivo), ("rechazada", "tamano"))


if __name__ == "__main__":
    unittest.main()
