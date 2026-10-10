import tempfile
import unittest

from mundo_mental import Alarma, BuzonAlarmas, Centinela, Guardian


class PruebasObservacion(unittest.TestCase):
    def test_aspecto_despierta_guardian(self):
        with tempfile.TemporaryDirectory() as carpeta:
            guardian = Guardian(carpeta)
            guardian.buzon.enviar(Alarma("curiosidad", "incoherencia", "laboratorio", "alta"))
            decisiones = guardian.despertar()
            self.assertFalse(guardian.dormido)
            self.assertEqual(decisiones[0]["accion"], "congelar")
            self.assertEqual(guardian.despertar(), [])

    def test_centinela_detecta_silencio_y_zona_protegida(self):
        with tempfile.TemporaryDirectory() as carpeta:
            buzon = BuzonAlarmas(f"{carpeta}/alarmas.jsonl")
            centinela = Centinela(buzon, max_silencio_ciclos=1)
            centinela.latir("biblioteca")
            centinela.avanzar()
            centinela.avanzar()
            self.assertEqual(len(centinela.comprobar()), 1)
            self.assertFalse(centinela.comprobar_acceso("curiosidad", "constitucion"))
            self.assertEqual(len(buzon.leer()), 2)


if __name__ == "__main__":
    unittest.main()
