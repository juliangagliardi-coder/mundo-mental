import unittest

from mundo_mental.ciudad import CiudadMental


class PruebasCiudadMental(unittest.TestCase):
    def test_ciudad_registra_eventos_y_limita_historial(self):
        ciudad = CiudadMental()
        ciudad.registrar("prueba", "Biblioteca", "Registro verificable")
        self.assertEqual(ciudad.eventos[-1].actor, "Biblioteca")
        for numero in range(100):
            ciudad.registrar("pulso", "Calles", str(numero))
        self.assertEqual(len(ciudad.eventos), 80)

    def test_habitantes_protegidos_tienen_lugar_y_estado(self):
        ciudad = CiudadMental()
        for nombre in ("Biblioteca", "Observador", "Centinela", "Catalogador", "Corazón"):
            self.assertIn(nombre, ciudad.habitantes)
            self.assertIn(ciudad.habitantes[nombre].lugar, ciudad.LUGARES)
        self.assertEqual(ciudad.habitantes["Observador"].estado, "durmiente")
        self.assertEqual(ciudad.habitantes["Centinela"].estado, "en_guardia")

    def test_viaje_actualiza_lugar_y_deja_traza(self):
        ciudad = CiudadMental()
        evento = ciudad.viajar("Curiosidad", "portal", "Solicita universo")
        self.assertEqual(ciudad.habitantes["Curiosidad"].lugar, "portal")
        self.assertEqual(evento.tipo, "viaje")

    def test_pulso_cuenta_una_historia_observable(self):
        ciudad = CiudadMental()
        eventos = ciudad.pulso_demo()
        self.assertEqual([evento.tipo for evento in eventos], ["pregunta", "viaje", "evidencia", "vigilancia"])
        self.assertEqual(eventos[-1].actor, "Centinela")


if __name__ == "__main__":
    unittest.main()
