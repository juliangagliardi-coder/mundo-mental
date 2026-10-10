import unittest

from benchmarks.viabilidad_01 import ejecutar


class PruebasViabilidad(unittest.TestCase):
    def test_instrumento_produce_linea_base_sin_cambiar_el_palacio(self):
        informe = ejecutar([4], semilla=7)
        self.assertEqual(informe["instrumento"], "viabilidad-0.1")
        self.assertEqual(informe["tamanos"], [4])
        resultado = informe["resultados"][0]
        self.assertEqual(resultado["episodios"], 4)
        self.assertGreaterEqual(resultado["persistencia_bytes"], 1)
        self.assertGreaterEqual(resultado["incorporar_segundos"], 0)

    def test_rechaza_tamanos_invalidos(self):
        with self.assertRaises(ValueError):
            ejecutar([0])


if __name__ == "__main__":
    unittest.main()
