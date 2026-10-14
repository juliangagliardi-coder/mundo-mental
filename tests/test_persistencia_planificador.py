import tempfile
import unittest
from pathlib import Path

from mundo_mental import Curiosidad, Guardian, MotorDeCiclos, TejidoMental
from mundo_mental.iniciativa import Planificador, Receta

DEBIL = {"fiabilidad": 0.3, "ejemplos_unicos": 5}
ORIGEN = "baja_fiabilidad"


def _roto(entrada):
    raise RuntimeError("experimento roto")


def _doble(entrada):
    return entrada["x"] * 2


class PruebasPersistenciaPlanificador(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)

    def test_restaura_fallos_total_y_bloqueadas_tras_reinicio(self):
        guardian = Guardian(self.raiz / "g")
        curiosidad = Curiosidad(self.raiz / "c", buzon=guardian.buzon)
        curiosidad.observar_conceptos({f"c{i}": DEBIL for i in range(6)})
        ruta = self.raiz / "plan.json"
        plan = Planificador(curiosidad, MotorDeCiclos(TejidoMental()), guardian=guardian,
                            ruta_estado=ruta)
        plan.autorizar(ORIGEN, Receta("roto", {}, _roto))
        plan.avanzar(5)
        textos = sorted(p.texto for p in plan.bloqueadas)

        nuevo = Planificador(curiosidad, MotorDeCiclos(TejidoMental()), guardian=guardian,
                             ruta_estado=ruta)
        self.assertEqual(nuevo.total, 3)
        self.assertEqual(nuevo.fallos_seguidos[ORIGEN], 3)
        self.assertEqual(sorted(p.texto for p in nuevo.bloqueadas), textos)
        self.assertEqual(len(nuevo.bloqueadas), 2)

    def test_estado_corrupto_pausa_el_motor(self):
        ruta = self.raiz / "plan.json"
        ruta.write_text("{no es json", encoding="utf-8")
        motor = MotorDeCiclos(TejidoMental())
        Planificador(Curiosidad(self.raiz / "c"), motor, ruta_estado=ruta)
        self.assertEqual(motor.estado, "pausado")
        self.assertTrue(motor.motivo.startswith("estado_planificador_corrupto"))

    def test_estado_con_campos_ausentes_pausa_el_motor(self):
        ruta = self.raiz / "plan.json"
        ruta.write_text('{"total": 1}', encoding="utf-8")
        motor = MotorDeCiclos(TejidoMental())
        Planificador(Curiosidad(self.raiz / "c"), motor, ruta_estado=ruta)
        self.assertEqual(motor.estado, "pausado")

    def test_mil_ciclos_con_cuatro_reinicios(self):
        curiosidad = Curiosidad(self.raiz / "c")
        curiosidad.observar_conceptos({f"c{i}": DEBIL for i in range(1100)})
        ruta_motor, ruta_plan = self.raiz / "motor.json", self.raiz / "plan.json"
        for _ in range(4):
            motor = MotorDeCiclos(TejidoMental(), ruta_motor)
            plan = Planificador(curiosidad, motor, max_total=5000, ruta_estado=ruta_plan)
            plan.autorizar(ORIGEN, Receta("doble", {"x": 2}, _doble))
            plan.avanzar(250)
        final = MotorDeCiclos(TejidoMental(), ruta_motor)
        self.assertEqual(final.latidos_totales, 1000)
        self.assertEqual(final.tejido.ciclo, 1000)
        self.assertEqual(final.estado, "despierto")
        self.assertEqual(Planificador(curiosidad, final, ruta_estado=ruta_plan).total, 1000)


if __name__ == "__main__":
    unittest.main()
