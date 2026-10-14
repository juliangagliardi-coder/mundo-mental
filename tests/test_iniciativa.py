import tempfile
import unittest
from pathlib import Path

from mundo_mental import Curiosidad, MotorDeCiclos, TejidoMental
from mundo_mental.iniciativa import Planificador, Receta

DEBIL = {"fiabilidad": 0.3, "ejemplos_unicos": 5}


def _receta():
    return Receta("doble", {"x": 2}, lambda entrada: entrada["x"] * 2)


class PruebasPlanificador(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)
        self.curiosidad = Curiosidad(self.raiz / "mente")
        self.motor = MotorDeCiclos(TejidoMental())

    def test_ejecuta_receta_autorizada_y_explica(self):
        self.curiosidad.observar_conceptos({"a": DEBIL})
        plan = Planificador(self.curiosidad, self.motor)
        plan.autorizar("baja_fiabilidad", _receta())
        resultados = plan.avanzar(1)
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0].salida, 4)
        self.assertEqual(plan.explicar()[0].estado, "completado")

    def test_sin_receta_no_ejecuta_y_conserva_la_pregunta(self):
        self.curiosidad.observar_conceptos({"a": DEBIL})
        plan = Planificador(self.curiosidad, self.motor)
        self.assertEqual(plan.avanzar(1), [])
        self.assertEqual(len(plan.sin_receta), 1)
        self.assertEqual(plan.explicar()[0].estado, "sin_receta")

    def test_supervision_detiene_el_experimento(self):
        self.curiosidad.observar_conceptos({"a": DEBIL})
        plan = Planificador(self.curiosidad, self.motor, supervisar=lambda p, n, e: False)
        plan.autorizar("baja_fiabilidad", _receta())
        resultados = plan.avanzar(1)
        self.assertEqual(resultados[0].estado, "detenido")
        self.assertIsNone(resultados[0].salida)

    def test_tope_total_pausa_el_motor(self):
        self.curiosidad.observar_conceptos({f"c{i}": DEBIL for i in range(5)})
        plan = Planificador(self.curiosidad, self.motor, max_total=2)
        plan.autorizar("baja_fiabilidad", _receta())
        plan.avanzar(10)
        self.assertEqual(plan.total, 2)
        self.assertEqual(self.motor.estado, "pausado")
        self.assertEqual(self.motor.motivo, "iniciativas_agotadas")

    def test_limite_total_acumulado_del_motor(self):
        motor = MotorDeCiclos(TejidoMental(), limite_total=3)
        motor.avanzar(2)
        motor.avanzar(5)
        self.assertEqual(motor.latidos_totales, 3)
        self.assertEqual(motor.motivo, "limite_total")

    def test_trescientos_ciclos_con_reinicio(self):
        self.curiosidad.observar_conceptos({f"c{i}": DEBIL for i in range(400)})
        ruta = self.raiz / "motor.json"
        motor = MotorDeCiclos(TejidoMental(), ruta)
        plan = Planificador(self.curiosidad, motor, max_total=1000)
        plan.autorizar("baja_fiabilidad", _receta())
        plan.avanzar(300)
        self.assertEqual(plan.total, 300)
        self.assertEqual(motor.latidos_totales, 300)
        reiniciado = MotorDeCiclos(TejidoMental(), ruta)
        self.assertEqual(reiniciado.tejido.ciclo, 300)
        self.assertEqual(reiniciado.estado, "despierto")

    def test_rechaza_limites_invalidos(self):
        with self.assertRaises(ValueError):
            Planificador(self.curiosidad, self.motor, max_total=0)
        with self.assertRaises(ValueError):
            MotorDeCiclos(TejidoMental(), limite_total=0)


if __name__ == "__main__":
    unittest.main()
