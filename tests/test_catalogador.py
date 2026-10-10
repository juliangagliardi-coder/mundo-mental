import tempfile
import unittest

from mundo_mental import BibliotecaSQLite, Catalogador


class PruebasCatalogador(unittest.TestCase):
    def test_crea_libros_sellados_y_manifiestos(self):
        with tempfile.TemporaryDirectory() as carpeta:
            biblioteca = BibliotecaSQLite(carpeta, max_episodios_libro=2)
            for indice in range(5):
                biblioteca.recordar(
                    [indice % 2, (indice + 1) % 2], "alternancia", "alternancia", True,
                    {"origen": "curiosidad", "temas": ["patrones"]},
                )
            estado = biblioteca.estado()["catalogo"]
            self.assertEqual(estado["ubicaciones"], 5)
            self.assertEqual(estado["libros"], 3)
            self.assertEqual(estado["libros_sellados"], 2)
            self.assertTrue(biblioteca.verificar_catalogo()["valido"])

    def test_catalogador_no_es_un_aspecto(self):
        catalogador = Catalogador()
        self.assertFalse(hasattr(catalogador, "identidad"))
        self.assertFalse(hasattr(catalogador, "memoria_autobiografica"))

    def test_busqueda_catalogada_conserva_el_mejor_resultado(self):
        with tempfile.TemporaryDirectory() as carpeta:
            biblioteca = BibliotecaSQLite(carpeta, max_episodios_libro=8)
            for indice in range(160):
                entrada = [(indice >> bit) & 1 for bit in range(12)]
                biblioteca.recordar(entrada, f"r-{indice}", f"c-{indice % 7}", True)
            objetivo = [(73 >> bit) & 1 for bit in range(12)]
            catalogada = biblioteca.buscar_similares(objetivo, limite=5, estrategia="catalogo")
            exhaustiva = biblioteca.buscar_similares(objetivo, limite=5, estrategia="exhaustiva")
            self.assertEqual(catalogada[0]["id"], exhaustiva[0]["id"])

    def test_reconstruye_indices_desde_recuerdos_canonicos(self):
        with tempfile.TemporaryDirectory() as carpeta:
            biblioteca = BibliotecaSQLite(carpeta)
            for indice in range(6):
                biblioteca.recordar([indice, indice + 1], "r", "secuencia", True)
            with biblioteca._conexion() as conexion:
                conexion.execute("DELETE FROM catalogo_indice")
                conexion.execute("DELETE FROM catalogo_ubicaciones")
                conexion.execute("DELETE FROM catalogo_libros")
            self.assertFalse(biblioteca.verificar_catalogo()["valido"])
            estado = biblioteca.reconstruir_catalogo()
            self.assertEqual(estado["ubicaciones"], 6)
            self.assertTrue(biblioteca.verificar_catalogo()["valido"])


if __name__ == "__main__":
    unittest.main()
