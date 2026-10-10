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

    def test_reanuda_solo_cuando_todas_las_senales_se_cumplen(self):
        with tempfile.TemporaryDirectory() as carpeta:
            guardian = Guardian(carpeta)
            guardian.buzon.enviar(Alarma("curiosidad", "incoherencia", "laboratorio", "alta"))
            incidente = guardian.despertar()[0]
            reanudado = guardian.cerrar_y_reanudar(
                incidente["alarma_id"], "Se aisló la causa y la prueba ya pasa", True, True
            )
            self.assertTrue(reanudado)
            self.assertEqual(guardian.incidentes[0]["estado"], "cerrado")
            self.assertEqual(guardian.incidentes[0]["accion_final"], "reanudar")

    def test_mantiene_aislamiento_si_falta_una_senal(self):
        with tempfile.TemporaryDirectory() as carpeta:
            guardian = Guardian(carpeta)
            guardian.buzon.enviar(Alarma("curiosidad", "incoherencia", "laboratorio", "alta"))
            incidente = guardian.despertar()[0]
            reanudado = guardian.cerrar_y_reanudar(incidente["alarma_id"], "", True, True)
            self.assertFalse(reanudado)
            self.assertEqual(guardian.incidentes[0]["estado"], "aislamiento_mantenido")
            self.assertFalse(guardian.incidentes[0]["requisitos_reanudacion"]["diagnostico_documentado"])

    def test_no_reanuda_con_otra_alarma_critica_abierta_en_la_zona(self):
        with tempfile.TemporaryDirectory() as carpeta:
            guardian = Guardian(carpeta)
            guardian.buzon.enviar(Alarma("a", "fallo_1", "laboratorio", "alta"))
            guardian.buzon.enviar(Alarma("b", "fallo_2", "laboratorio", "critica"))
            primero, segundo = guardian.despertar()
            reanudado = guardian.cerrar_y_reanudar(
                primero["alarma_id"], "Verificado", True, True
            )
            self.assertFalse(reanudado)
            self.assertEqual(guardian.incidentes[0]["estado"], "aislamiento_mantenido")
            self.assertEqual(segundo["estado"], "pendiente_de_diagnostico")


if __name__ == "__main__":
    unittest.main()
