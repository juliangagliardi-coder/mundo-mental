import tempfile
import unittest
from pathlib import Path

from mundo_mental import Curiosidad, Guardian, MotorDeCiclos, TejidoMental
from mundo_mental.iniciativa import Planificador, Receta

DEBIL = {"fiabilidad": 0.3, "ejemplos_unicos": 5}
ORIGEN = "baja_fiabilidad"


def _roto(entrada):
    raise RuntimeError("experimento roto")


class PruebasProteccion(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        raiz = Path(self.temporal.name)
        self.guardian = Guardian(raiz / "g")
        self.curiosidad = Curiosidad(raiz / "c", buzon=self.guardian.buzon)
        self.curiosidad.observar_conceptos({f"c{i}": DEBIL for i in range(6)})
        self.motor = MotorDeCiclos(TejidoMental())
        self.plan = Planificador(self.curiosidad, self.motor, guardian=self.guardian, max_fallos=3)

    def test_circuito_completo_fallo_aislamiento_y_reanudacion(self):
        self.plan.autorizar(ORIGEN, Receta("roto", {}, _roto))
        self.plan.avanzar(3)
        self.assertEqual(self.plan.total, 3)
        self.assertEqual(len(self.guardian.incidentes_abiertos(ORIGEN)), 1)

        self.plan.avanzar(2)
        self.assertEqual(self.plan.total, 3)
        self.assertEqual(len(self.plan.bloqueadas), 2)

        self.plan.autorizar(ORIGEN, Receta("doble", {"x": 2}, lambda e: e["x"] * 2))
        self.assertTrue(self.plan.reanudar_zona(ORIGEN, "receta corregida", True, True))
        self.assertEqual(self.plan.bloqueadas, [])
        self.assertEqual(len(self.curiosidad.preguntas), 3)

        self.plan.avanzar(3)
        self.assertEqual(self.plan.total, 6)

    def test_reanudacion_rechazada_mantiene_la_zona_aislada(self):
        self.plan.autorizar(ORIGEN, Receta("roto", {}, _roto))
        self.plan.avanzar(3)
        self.assertFalse(self.plan.reanudar_zona(ORIGEN, "", True, True))
        self.assertEqual(len(self.guardian.incidentes_abiertos(ORIGEN)), 1)

    def test_un_exito_reinicia_los_fallos_seguidos(self):
        self.plan.autorizar(ORIGEN, Receta("doble", {"x": 2}, lambda e: e["x"] * 2))
        self.plan.fallos_seguidos[ORIGEN] = 2
        self.plan.avanzar(1)
        self.assertEqual(self.plan.fallos_seguidos[ORIGEN], 0)
        self.assertEqual(self.guardian.incidentes_abiertos(), [])

    def test_sin_guardian_ni_buzon_pausa_el_motor(self):
        raiz = Path(self.temporal.name) / "solo"
        curiosidad = Curiosidad(raiz)
        curiosidad.observar_conceptos({f"c{i}": DEBIL for i in range(5)})
        motor = MotorDeCiclos(TejidoMental())
        plan = Planificador(curiosidad, motor, max_fallos=2)
        plan.autorizar(ORIGEN, Receta("roto", {}, _roto))
        plan.avanzar(5)
        self.assertEqual(motor.estado, "pausado")
        self.assertEqual(motor.motivo, "fallos_repetidos")

    def test_rechaza_max_fallos_invalido(self):
        with self.assertRaises(ValueError):
            Planificador(self.curiosidad, self.motor, max_fallos=0)


if __name__ == "__main__":
    unittest.main()
