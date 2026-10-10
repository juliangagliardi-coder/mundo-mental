import tempfile
import unittest

from mundo_mental import BuzonAlarmas, Curiosidad, Guardian


class PruebasCuriosidad(unittest.TestCase):
    def test_formula_pregunta_propia_desde_un_vacio(self):
        with tempfile.TemporaryDirectory() as carpeta:
            curiosidad = Curiosidad(carpeta)
            preguntas = curiosidad.observar_conceptos({
                "simetria": {"fiabilidad": 0.6, "ejemplos_unicos": 4}
            })
            self.assertEqual(len(preguntas), 1)
            self.assertIn("simetria", preguntas[0].texto)
            self.assertEqual(curiosidad.siguiente_pregunta(), preguntas[0])

    def test_puede_pedir_ayuda_al_guardian(self):
        with tempfile.TemporaryDirectory() as carpeta:
            guardian = Guardian(carpeta)
            curiosidad = Curiosidad(carpeta, guardian.buzon)
            curiosidad.pedir_ayuda("resultado_imposible", "laboratorio", "alta")
            self.assertEqual(guardian.despertar()[0]["actor"], "curiosidad")


if __name__ == "__main__":
    unittest.main()
