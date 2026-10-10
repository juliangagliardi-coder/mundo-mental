import tempfile
import unittest

from mundo_mental import BibliotecaSQLite, Corazon


class PruebasBibliotecaSQLite(unittest.TestCase):
    def test_recuerda_busca_consolida_y_versiona(self):
        with tempfile.TemporaryDirectory() as carpeta:
            biblioteca = BibliotecaSQLite(carpeta)
            biblioteca.recordar([0, 1], "alternancia", "alternancia", True)
            biblioteca.recordar([1, 0], "alternancia", "alternancia", True)
            encontrados = biblioteca.buscar_similares([0, 1])
            self.assertEqual(encontrados[0]["esperado"], "alternancia")
            self.assertIn("alternancia", biblioteca.consolidar())
            self.assertEqual(biblioteca.estado()["episodios"], 2)

    def test_funciona_con_el_corazon_existente(self):
        with tempfile.TemporaryDirectory() as carpeta:
            biblioteca = BibliotecaSQLite(carpeta)
            corazon = Corazon(biblioteca)
            ejemplos = [([0, 0], "igual"), ([1, 1], "igual")]
            self.assertTrue(corazon.latir("patrones", ejemplos, ejemplos)["aceptada"])
            self.assertEqual(biblioteca.estado()["obras"], 1)


if __name__ == "__main__":
    unittest.main()
