import tempfile
import unittest
from pathlib import Path

from mundo_mental import Biblioteca


class PruebasBiblioteca(unittest.TestCase):
    def test_recuerda_encuentra_y_explica(self):
        with tempfile.TemporaryDirectory() as carpeta:
            biblioteca = Biblioteca(carpeta)
            biblioteca.recordar([0, 1, 0, 1], "alternancia", "alternancia", True)
            biblioteca.recordar([1, 1, 1, 1], "igual", "igual", True)
            recuerdos = biblioteca.buscar_similares([0, 1, 0, 1])
            self.assertEqual(recuerdos[0]["esperado"], "alternancia")
            self.assertEqual(recuerdos[0]["similitud"], 1.0)
            self.assertIn("Coinciden 4 de 4", recuerdos[0]["explicacion"])
            self.assertEqual(recuerdos[0]["accesos"], 0)
            guardados = Biblioteca._leer_jsonl(biblioteca.experiencias)
            self.assertEqual(next(x for x in guardados if x["id"] == recuerdos[0]["id"])["accesos"], 1)

    def test_consolida_conceptos(self):
        with tempfile.TemporaryDirectory() as carpeta:
            biblioteca = Biblioteca(carpeta)
            biblioteca.recordar([0, 1, 0, 1], "alternancia", "alternancia", True)
            biblioteca.recordar([1, 0, 1, 0], "alternancia", "alternancia", True)
            conceptos = biblioteca.consolidar(minimo_ejemplos=2)
            self.assertIn("alternancia", conceptos)
            self.assertEqual(conceptos["alternancia"]["ejemplos_unicos"], 2)

    def test_depura_duplicados_y_protege(self):
        with tempfile.TemporaryDirectory() as carpeta:
            biblioteca = Biblioteca(carpeta)
            biblioteca.recordar([0, 0], "igual", "igual", True, protegido=True)
            biblioteca.recordar([0, 0], "igual", "igual", True)
            biblioteca.recordar([0, 1], "alternancia", "alternancia", True)
            resultado = biblioteca.depurar(max_recuerdos=1)
            self.assertEqual(resultado["antes"], 3)
            recuerdos = Biblioteca._leer_jsonl(biblioteca.experiencias)
            self.assertEqual(len(recuerdos), 1)
            self.assertTrue(recuerdos[0]["protegido"])
            self.assertEqual(recuerdos[0]["repeticiones"], 2)

    def test_habilidad_se_versiona(self):
        with tempfile.TemporaryDirectory() as carpeta:
            biblioteca = Biblioteca(carpeta)
            uno = {"tipo": "casa_patrones", "version": 1, "ejemplos": {}}
            dos = {"tipo": "casa_patrones", "version": 1, "ejemplos": {"igual": [[0, 0]]}}
            biblioteca.guardar_habilidad("patrones", uno)
            biblioteca.guardar_habilidad("patrones", dos)
            self.assertEqual(biblioteca.cargar_habilidad("patrones"), dos)
            self.assertEqual(len(list((Path(carpeta) / "habilidades/versiones").glob("*.json"))), 1)

    def test_estado_informa_salas(self):
        with tempfile.TemporaryDirectory() as carpeta:
            biblioteca = Biblioteca(carpeta)
            self.assertEqual(biblioteca.estado()["version"], "0.2.0")


if __name__ == "__main__":
    unittest.main()
