import unittest

from mundo_mental.mundo_virtual import MundoVirtual


class PruebasMundoVirtual(unittest.TestCase):
    def test_mundo_tiene_seres_con_coordenadas_fisicas(self):
        mundo = MundoVirtual()
        self.assertGreater(mundo.ANCHO, 1000)
        for nombre in ("Biblioteca", "Curiosidad", "Corazón", "Observador", "Centinela", "Catalogador"):
            ser = mundo.seres[nombre]
            self.assertTrue(0 <= ser.x <= mundo.ANCHO)
            self.assertTrue(0 <= ser.y <= mundo.ALTO)

    def test_movimiento_actualiza_posicion_y_deja_traza(self):
        mundo = MundoVirtual()
        evento = mundo.mover("Curiosidad", 1400, 650, "Camina hacia la puerta")
        self.assertEqual((mundo.seres["Curiosidad"].x, mundo.seres["Curiosidad"].y), (1400, 650))
        self.assertEqual(evento.tipo, "movimiento")

    def test_no_se_puede_salir_del_mundo(self):
        mundo = MundoVirtual()
        with self.assertRaises(ValueError):
            mundo.mover("Curiosidad", mundo.ANCHO + 1, 100, "Cruza el límite")

    def test_pulso_cuenta_una_historia_en_el_terreno(self):
        mundo = MundoVirtual()
        eventos = mundo.pulso_demo()
        self.assertEqual([evento.tipo for evento in eventos], ["pregunta", "movimiento", "registro", "vigilancia"])
        self.assertEqual(mundo.seres["Curiosidad"].x, 1450)


if __name__ == "__main__":
    unittest.main()
