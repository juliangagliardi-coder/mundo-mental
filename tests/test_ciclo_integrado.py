import tempfile
import unittest

from iniciar import ejecutar_ciclo


class PruebasCicloIntegrado(unittest.TestCase):
    def test_ciclo_completo_formula_experimenta_valida_y_reanuda(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ciclo = ejecutar_ciclo(carpeta)
            self.assertIn("patrones", ciclo["pregunta"].texto)
            self.assertEqual(ciclo["resultado"].estado, "completado")
            self.assertTrue(ciclo["resultado"].reproducible)
            self.assertTrue(ciclo["dictamen"].aceptada)
            self.assertTrue(ciclo["reanudado"])
            self.assertEqual(ciclo["incidente"]["estado"], "cerrado")
            self.assertEqual(ciclo["estado_biblioteca"]["episodios"], 1)


if __name__ == "__main__":
    unittest.main()
