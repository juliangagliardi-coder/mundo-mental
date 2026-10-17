import tempfile
import unittest
from pathlib import Path

from mundo_mental.autoridad import Autoridad
from mundo_mental.evolucion import Evolucion
from mundo_mental.observacion import Centinela, Guardian


BUENO = "def valor():\n    return 1\n"
ROTO = "def valor(:\n    return 1\n"
CON_DOBLE = BUENO + "\n\ndef doble(x):\n    return x * 2\n"
MEJORA_DOBLE = "from mundo_mental.modulo import doble\nassert doble(3) == 6\n"
TEST_MODULO = (
    "import unittest\n"
    "from mundo_mental.modulo import valor\n\n\n"
    "class TestModulo(unittest.TestCase):\n"
    "    def test_valor(self):\n"
    "        self.assertEqual(valor(), 1)\n"
)


class TestEvolucion(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)
        (self.raiz / "mundo_mental").mkdir()
        (self.raiz / "tests").mkdir()
        (self.raiz / "mundo_mental" / "modulo.py").write_text(BUENO, encoding="utf-8")
        (self.raiz / "mundo_mental" / "__init__.py").write_text("", encoding="utf-8")
        (self.raiz / "tests" / "test_modulo.py").write_text(TEST_MODULO, encoding="utf-8")

    def autoridad(self):
        guardian = Guardian(self.raiz / ".mente")
        return Autoridad(self.raiz / ".mente", Centinela(guardian.buzon), guardian)

    def motor(self, autoridad=None, **extra):
        return Evolucion(self.raiz, autoridad, tiempo_max=20, **extra)

    def modulo(self):
        return (self.raiz / "mundo_mental" / "modulo.py").read_text(encoding="utf-8")

    def test_promueve_cambio_que_conserva_suite(self):
        r = self.motor(self.autoridad()).proponer("mundo_mental/modulo.py", BUENO + "\n# candidato\n")
        self.assertEqual((r.estado, r.motivo), ("promovida", "suite_conservada"))
        self.assertIn("candidato", self.modulo())
        self.assertEqual(len(self.motor().historial()), 1)

    def test_sin_autoridad_solo_deja_lista(self):
        r = self.motor().proponer("mundo_mental/modulo.py", BUENO + "\n# x\n")
        self.assertEqual((r.estado, r.motivo), ("lista", "sin_autoridad"))
        self.assertEqual(self.modulo(), BUENO)

    def test_rechaza_sintaxis_y_no_toca_estable(self):
        r = self.motor().proponer("mundo_mental/modulo.py", ROTO)
        self.assertEqual((r.estado, r.motivo), ("rechazada", "sintaxis"))
        self.assertEqual(self.modulo(), BUENO)

    def test_rechaza_regresion_y_no_toca_estable(self):
        r = self.motor(self.autoridad()).proponer("mundo_mental/modulo.py", "def valor():\n    return 2\n")
        self.assertEqual((r.estado, r.motivo), ("rechazada", "regresion"))
        self.assertEqual(self.modulo(), BUENO)

    def test_rechaza_rutas_protegidas_y_fuera(self):
        for ruta in ("tests/test_modulo.py", "../fuera.py", "mundo_mental/guardian.py"):
            with self.subTest(ruta=ruta):
                r = self.motor().proponer(ruta, "x = 1\n")
                self.assertEqual((r.estado, r.motivo), ("rechazada", "ruta"))

    def test_limita_el_tamano(self):
        r = self.motor(max_bytes_parche=5).proponer("mundo_mental/modulo.py", BUENO)
        self.assertEqual((r.estado, r.motivo), ("rechazada", "tamano"))

    def test_promueve_con_mejora_demostrada(self):
        r = self.motor(self.autoridad()).proponer("mundo_mental/modulo.py", CON_DOBLE, mejora=MEJORA_DOBLE)
        self.assertEqual((r.estado, r.motivo), ("promovida", "mejora_demostrada"))
        self.assertIn("def doble", self.modulo())

    def test_rechaza_si_la_mejora_ya_pasaba(self):
        mejora = "from mundo_mental.modulo import valor\nassert valor() == 1\n"
        r = self.motor(self.autoridad()).proponer("mundo_mental/modulo.py", BUENO + "\n# x\n", mejora=mejora)
        self.assertEqual((r.estado, r.motivo), ("rechazada", "ya_cumple"))
        self.assertEqual(self.modulo(), BUENO)

    def test_rechaza_si_la_candidata_no_mejora(self):
        r = self.motor(self.autoridad()).proponer("mundo_mental/modulo.py", BUENO + "\n# x\n", mejora=MEJORA_DOBLE)
        self.assertEqual((r.estado, r.motivo), ("rechazada", "no_mejora"))
        self.assertEqual(self.modulo(), BUENO)

    def test_rechaza_mejora_con_sintaxis_rota(self):
        r = self.motor().proponer("mundo_mental/modulo.py", CON_DOBLE, mejora="assert (")
        self.assertEqual((r.estado, r.motivo), ("rechazada", "sintaxis_mejora"))


if __name__ == "__main__":
    unittest.main()
