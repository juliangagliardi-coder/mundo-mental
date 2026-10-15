import unittest
from unittest.mock import patch

from mundo_mental.motor import MotorDeCiclos
from mundo_mental.tejido import TejidoMental


class MotorSesionTiempoTests(unittest.TestCase):
    @patch("mundo_mental.motor.time.monotonic", side_effect=[100.0, 100.0, 101.1])
    def test_tiempo_acumulado_entre_llamadas_pausa_el_motor(self, monotonic):
        motor = MotorDeCiclos(TejidoMental(), tiempo_max_segundos=1.0)
        primer = motor.avanzar(1)
        segundo = motor.avanzar(1)
        self.assertEqual(len(primer), 1)
        self.assertEqual(segundo, [])
        self.assertEqual(motor.estado, "pausado")
        self.assertEqual(motor.motivo, "tiempo_agotado")
        self.assertEqual(motor.tejido.ciclo, 1)
        self.assertEqual(monotonic.call_count, 3)

    @patch("mundo_mental.motor.time.monotonic", side_effect=[10.0, 15.0, 15.0])
    def test_despertar_inicia_una_sesion_nueva(self, monotonic):
        motor = MotorDeCiclos(TejidoMental(), tiempo_max_segundos=2.0)
        motor.pausar("manual")
        motor.despertar()
        hechos = motor.avanzar(1)
        self.assertEqual(len(hechos), 1)
        self.assertEqual(motor.estado, "despierto")
        self.assertEqual(motor.tejido.ciclo, 1)
        self.assertEqual(monotonic.call_count, 3)


if __name__ == "__main__":
    unittest.main()
