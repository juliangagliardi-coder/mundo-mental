import tempfile
import unittest

from mundo_mental import Biblioteca


class PruebasBiblioteca(unittest.TestCase):
    def test_recuerda_y_encuentra_lo_parecido(self):
        with tempfile.TemporaryDirectory() as carpeta:
            biblioteca = Biblioteca(carpeta)
            biblioteca.recordar([0, 1, 0, 1], "alternancia", "alternancia", True)
            biblioteca.recordar([1, 1, 1, 1], "igual", "igual", True)
            recuerdos = biblioteca.buscar_similares([0, 1, 0, 1])
            self.assertEqual(recuerdos[0]["esperado"], "alternancia")
            self.assertEqual(recuerdos[0]["similitud"], 1.0)

    def test_habilidad_se_guarda_y_restaura(self):
        with tempfile.TemporaryDirectory() as carpeta:
            biblioteca = Biblioteca(carpeta)
            estado = {"tipo": "casa_patrones", "version": 1, "ejemplos": {"igual": [[0, 0]]}}
            biblioteca.guardar_habilidad("patrones", estado)
            self.assertEqual(biblioteca.cargar_habilidad("patrones"), estado)


if __name__ == "__main__":
    unittest.main()
