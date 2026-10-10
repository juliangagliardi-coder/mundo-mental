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

    def test_movimiento_del_jugador_respeta_fronteras(self):
        mundo = MundoVirtual()
        self.assertFalse(mundo.mover_jugador(-500, 0))
        self.assertEqual((mundo.jugador.x, mundo.jugador.y), (175, 600))
        self.assertTrue(mundo.mover_jugador(25, 0))

    def test_recoger_y_entregar_brasas_completa_aventura(self):
        mundo = MundoVirtual()
        for x, y in mundo.BRASAS:
            mundo.jugador.x, mundo.jugador.y = x, y
            mundo._recoger_brasas()
        self.assertEqual(mundo.jugador.brasas, 3)
        mundo.jugador.x, mundo.jugador.y = mundo.DESTINO_RITUAL
        evento = mundo.interactuar()
        self.assertTrue(mundo.mision_completada)
        self.assertEqual(evento.tipo, "ritual")

    def test_interactuar_con_habitante_deja_dialogo(self):
        mundo = MundoVirtual()
        mundo.jugador.x, mundo.jugador.y = mundo.seres["Biblioteca"].x, mundo.seres["Biblioteca"].y
        self.assertEqual(mundo.interactuar().tipo, "dialogo")

    def test_pulso_cuenta_una_historia_en_el_terreno(self):
        mundo = MundoVirtual()
        eventos = mundo.pulso_demo()
        self.assertEqual([evento.tipo for evento in eventos], ["pregunta", "movimiento", "registro", "vigilancia"])
        self.assertEqual(mundo.seres["Curiosidad"].x, 1450)


if __name__ == "__main__":
    unittest.main()
