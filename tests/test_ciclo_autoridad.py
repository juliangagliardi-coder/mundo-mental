import tempfile
import unittest
from pathlib import Path

from iniciar import ejecutar_ciclo


class TestCicloConAutoridad(unittest.TestCase):
    def test_validacion_pasa_por_la_autoridad(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ciclo = ejecutar_ciclo(carpeta)
            decision = ciclo["decision"]
            self.assertEqual(decision["resultado"], "ejecutada")
            self.assertTrue(decision["con_reversa"])
            self.assertIsNotNone(ciclo["dictamen"])
            self.assertTrue(ciclo["reanudado"])
            self.assertTrue((Path(carpeta) / "autoridad" / "registro.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
