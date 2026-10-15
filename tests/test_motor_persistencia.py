import tempfile
import unittest
from pathlib import Path

from mundo_mental.motor import MotorDeCiclos
from mundo_mental.tejido import TejidoMental


class MotorPersistenciaTests(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(self.carpeta.cleanup)
        self.ruta = Path(self.carpeta.name) / "motor.json"

    def test_historial_sobrevive_al_reinicio(self):
        motor = MotorDeCiclos(TejidoMental(), self.ruta)
        motor.avanzar(5)
        nuevo = MotorDeCiclos(TejidoMental(), self.ruta)
        self.assertEqual(nuevo.latidos_totales, 5)
        self.assertEqual(nuevo.tejido.ciclo, 5)
        self.assertEqual([r.ciclo for r in nuevo.historial], [1, 2, 3, 4, 5])

    def test_historial_respeta_el_maximo_al_cargar(self):
        motor = MotorDeCiclos(TejidoMental(), self.ruta, max_historial=10)
        motor.avanzar(10)
        nuevo = MotorDeCiclos(TejidoMental(), self.ruta, max_historial=3)
        self.assertEqual([r.ciclo for r in nuevo.historial], [8, 9, 10])

    def test_estado_version_1_sigue_cargando(self):
        self.ruta.write_text('{"version": 1, "estado": "durmiendo", "motivo": "descanso", '
                             '"ciclo": 7, "latidos_totales": 7}', encoding="utf-8")
        motor = MotorDeCiclos(TejidoMental(), self.ruta)
        self.assertEqual(motor.estado, "durmiendo")
        self.assertEqual(motor.tejido.ciclo, 7)
        self.assertEqual(motor.historial, [])

    def test_historial_corrupto_deja_el_motor_pausado(self):
        self.ruta.write_text('{"version": 2, "estado": "despierto", "motivo": "", '
                             '"ciclo": 1, "latidos_totales": 1, "historial": [{"ciclo": 1}]}',
                             encoding="utf-8")
        motor = MotorDeCiclos(TejidoMental(), self.ruta)
        self.assertEqual(motor.estado, "pausado")
        self.assertTrue(motor.motivo.startswith("estado_corrupto"))

    def test_presupuesto_de_tiempo_pausa_el_motor(self):
        motor = MotorDeCiclos(TejidoMental(), self.ruta, tiempo_max_segundos=1e-9)
        hechos = motor.avanzar(1000)
        self.assertLess(len(hechos), 1000)
        self.assertEqual(motor.estado, "pausado")
        self.assertEqual(motor.motivo, "tiempo_agotado")

    def test_tiempo_invalido_se_rechaza(self):
        with self.assertRaises(ValueError):
            MotorDeCiclos(TejidoMental(), tiempo_max_segundos=0)

    def test_un_motor_pausado_no_avanza(self):
        motor = MotorDeCiclos(TejidoMental(), self.ruta, limite_total=2)
        motor.avanzar(5)
        self.assertEqual(motor.motivo, "limite_total")
        with self.assertRaises(RuntimeError):
            motor.avanzar(1)


if __name__ == "__main__":
    unittest.main()
