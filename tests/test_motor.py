import json
import tempfile
import unittest
from pathlib import Path

from mundo_mental import TejidoMental
from mundo_mental.motor import MotorDeCiclos


class PruebasMotor(unittest.TestCase):
    def test_avanza_y_cuenta_ciclos(self):
        motor = MotorDeCiclos(TejidoMental())
        resumenes = motor.avanzar(3)
        self.assertEqual([r.ciclo for r in resumenes], [1, 2, 3])
        self.assertEqual(motor.diagnostico()["latidos_totales"], 3)

    def test_presupuesto_pausa_el_motor(self):
        motor = MotorDeCiclos(TejidoMental(), presupuesto=2)
        self.assertEqual(len(motor.avanzar(5)), 2)
        self.assertEqual(motor.estado, "pausado")
        self.assertEqual(motor.motivo, "presupuesto_agotado")
        with self.assertRaisesRegex(RuntimeError, "pausado"):
            motor.avanzar()

    def test_dormir_y_despertar(self):
        motor = MotorDeCiclos(TejidoMental())
        motor.dormir()
        with self.assertRaises(RuntimeError):
            motor.avanzar()
        motor.despertar()
        self.assertEqual(len(motor.avanzar()), 1)

    def test_recupera_estado_tras_reinicio(self):
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "motor.json"
            primero = MotorDeCiclos(TejidoMental(), ruta)
            primero.avanzar(4)
            primero.pausar("mantenimiento")
            segundo = MotorDeCiclos(TejidoMental(), ruta)
            self.assertEqual(segundo.estado, "pausado")
            self.assertEqual(segundo.tejido.ciclo, 4)
            self.assertEqual(segundo.diagnostico()["latidos_totales"], 4)
            segundo.despertar()
            self.assertEqual(segundo.avanzar()[0].ciclo, 5)

    def test_estado_corrupto_arranca_pausado(self):
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "motor.json"
            ruta.write_text("{no es json", encoding="utf-8")
            motor = MotorDeCiclos(TejidoMental(), ruta)
            self.assertEqual(motor.estado, "pausado")
            self.assertTrue(motor.motivo.startswith("estado_corrupto"))

    def test_estado_con_valor_invalido_arranca_pausado(self):
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "motor.json"
            ruta.write_text(json.dumps({"estado": "volando", "ciclo": 1, "latidos_totales": 1}))
            self.assertEqual(MotorDeCiclos(TejidoMental(), ruta).estado, "pausado")

    def test_rechaza_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            MotorDeCiclos(TejidoMental(), presupuesto=0)
        with self.assertRaises(ValueError):
            MotorDeCiclos(TejidoMental()).avanzar(0)


if __name__ == "__main__":
    unittest.main()
