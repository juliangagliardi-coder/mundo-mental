import tempfile
import unittest
from pathlib import Path

from mundo_mental.autoridad import Autoridad
from mundo_mental.evolucion import Evolucion
from mundo_mental.observacion import Centinela, Guardian
from mundo_mental.rol_evolutiva import RolEvolutiva, extraer_bloques

BUENO = "def valor():\n    return 1\n"
CON_DOBLE = BUENO + "\n\ndef doble(x):\n    return x * 2\n"
MEJORA_DOBLE = "from mundo_mental.modulo import doble\nassert doble(3) == 6\n"
TEST_MODULO = (
    "import unittest\n"
    "from mundo_mental.modulo import valor\n\n\n"
    "class TestModulo(unittest.TestCase):\n"
    "    def test_valor(self):\n"
    "        self.assertEqual(valor(), 1)\n"
)


def bloque(codigo):
    return "```python\n" + codigo + "\n```"


class Guion:
    def __init__(self, *respuestas):
        self.respuestas = list(respuestas)
        self.prompts = []

    def responder(self, instruccion, contexto=""):
        self.prompts.append(instruccion)
        return self.respuestas.pop(0) if self.respuestas else ""


class TestRolEvolutiva(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)
        (self.raiz / "mundo_mental").mkdir()
        (self.raiz / "tests").mkdir()
        (self.raiz / "mundo_mental" / "modulo.py").write_text(BUENO, encoding="utf-8")
        (self.raiz / "mundo_mental" / "__init__.py").write_text("", encoding="utf-8")
        (self.raiz / "tests" / "test_modulo.py").write_text(TEST_MODULO, encoding="utf-8")
        guardian = Guardian(self.raiz / ".mente")
        autoridad = Autoridad(self.raiz / ".mente", Centinela(guardian.buzon), guardian)
        self.evolucion = Evolucion(self.raiz, autoridad, tiempo_max=20)

    def rol(self, guion, **extra):
        datos = dict(rutas=("mundo_mental/modulo.py",), objetivo="añadir doble")
        datos.update(extra)
        return RolEvolutiva(self.evolucion, guion, **datos)

    def test_extraer_bloques(self):
        self.assertEqual(extraer_bloques(bloque("a = 1") + "\n" + bloque("b = 2")), ["a = 1", "b = 2"])
        self.assertEqual(extraer_bloques("sin código"), [])

    def test_promueve_parche_con_su_prueba_de_mejora(self):
        guion = Guion(bloque(CON_DOBLE) + "\n" + bloque(MEJORA_DOBLE))
        r = self.rol(guion).ejecutar({})
        self.assertEqual((r["estado"], r["motivo"]), ("promovida", "mejora_demostrada"))
        self.assertIn("def doble", (self.raiz / "mundo_mental" / "modulo.py").read_text(encoding="utf-8"))
        self.assertIn("def valor", guion.prompts[0])

    def test_sin_dos_bloques_no_propone(self):
        r = self.rol(Guion(bloque(CON_DOBLE))).ejecutar({})
        self.assertEqual((r["estado"], r["motivo"]), ("omitida", "sin_propuesta"))
        self.assertEqual(self.evolucion.historial(), [])

    def test_archivo_demasiado_grande_se_omite(self):
        r = self.rol(Guion(), max_caracteres=5).ejecutar({})
        self.assertEqual((r["estado"], r["motivo"]), ("omitida", "demasiado_grande"))

    def test_exige_rutas_permitidas_y_objetivo(self):
        with self.assertRaises(ValueError):
            self.rol(Guion(), rutas=("tests/test_modulo.py",))
        with self.assertRaises(ValueError):
            self.rol(Guion(), rutas=())
        with self.assertRaises(ValueError):
            self.rol(Guion(), objetivo=" ")


if __name__ == "__main__":
    unittest.main()
