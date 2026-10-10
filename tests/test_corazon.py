import tempfile
import unittest

from mundo_mental import Biblioteca, Corazon


class PruebasCorazon(unittest.TestCase):
    def test_acepta_una_mejora_real(self):
        with tempfile.TemporaryDirectory() as carpeta:
            corazon = Corazon(Biblioteca(carpeta))
            ejemplos = [([0, 0, 0, 0], "igual"), ([1, 1, 1, 1], "igual")]
            resultado = corazon.latir("patrones", ejemplos, ejemplos)
            self.assertTrue(resultado["aceptada"])
            self.assertEqual(resultado["precision_candidata"], 1.0)
            self.assertEqual(resultado["antecedentes_consultados"], 0)

    def test_rechaza_una_obra_sin_mejora_y_consulta_historia(self):
        with tempfile.TemporaryDirectory() as carpeta:
            biblioteca = Biblioteca(carpeta)
            corazon = Corazon(biblioteca)
            ejemplos = [([0, 1, 0, 1], "alternancia")]
            self.assertTrue(corazon.latir("patrones", ejemplos, ejemplos)["aceptada"])
            segunda = corazon.latir("patrones", ejemplos, ejemplos, protegidos=ejemplos)
            self.assertFalse(segunda["aceptada"])
            self.assertEqual(segunda["antecedentes_consultados"], 1)
            self.assertEqual(len(biblioteca.historial_obras()), 2)

    def test_conserva_conocimiento_protegido(self):
        with tempfile.TemporaryDirectory() as carpeta:
            corazon = Corazon(Biblioteca(carpeta))
            antiguo = [([0, 1, 0, 1], "alternancia")]
            nuevo = [([0, 1, 1, 0], "simetria")]
            corazon.latir("patrones", antiguo, antiguo)
            resultado = corazon.latir("patrones", nuevo, nuevo, protegidos=antiguo)
            self.assertTrue(resultado["aceptada"])
            self.assertEqual(resultado["retencion"], 1.0)


if __name__ == "__main__":
    unittest.main()
