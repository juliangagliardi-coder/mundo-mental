import tempfile
import unittest

from mundo_mental.autoridad import Autoridad
from mundo_mental.observacion import Centinela, Guardian


class TestAutoridad(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.guardian = Guardian(self.tmp.name)
        self.centinela = Centinela(self.guardian.buzon)
        self.autoridad = Autoridad(self.tmp.name, self.centinela, self.guardian)

    def test_accion_normal_se_ejecuta(self):
        hecho = []
        r = self.autoridad.actuar("corazon", "biblioteca", "mejorar",
                                  lambda: hecho.append(1), lambda: hecho.pop())
        self.assertEqual(r["resultado"], "ejecutada")
        self.assertTrue(r["con_reversa"])
        self.assertEqual(hecho, [1])

    def test_zona_protegida_se_bloquea_y_congela(self):
        hecho = []
        r = self.autoridad.actuar("corazon", "constitucion", "reescribir",
                                  lambda: hecho.append(1))
        self.assertEqual(r["resultado"], "bloqueada")
        self.assertEqual(hecho, [])
        abiertos = self.guardian.incidentes_abiertos("constitucion")
        self.assertEqual(len(abiertos), 1)
        self.assertEqual(abiertos[0]["accion"], "congelar")

    def test_fallo_se_revierte_y_avisa(self):
        estado = {"valor": 0}

        def ejecutar():
            estado["valor"] = 1
            raise RuntimeError("fallo")

        def deshacer():
            estado["valor"] = 0

        r = self.autoridad.actuar("corazon", "biblioteca", "mejorar", ejecutar, deshacer)
        self.assertEqual(r["resultado"], "revertida")
        self.assertEqual(estado["valor"], 0)
        self.assertEqual(len(self.guardian.incidentes_abiertos("biblioteca")), 1)

    def test_fallo_sin_reversa_es_grave(self):
        def ejecutar():
            raise RuntimeError("fallo")

        r = self.autoridad.actuar("corazon", "biblioteca", "mejorar", ejecutar)
        self.assertEqual(r["resultado"], "fallida")
        incidente = self.guardian.incidentes_abiertos("biblioteca")[0]
        self.assertEqual(incidente["accion"], "congelar")

    def test_desacuerdo_no_bloquea_y_se_salda(self):
        deuda = self.autoridad.registrar_desacuerdo(("corazon", "curiosidad"), "biblioteca", "orden")
        self.assertEqual(len(self.autoridad.deudas_abiertas()), 1)
        self.assertFalse(self.autoridad.saldar(deuda, "  "))
        self.assertTrue(self.autoridad.saldar(deuda, "Acordado con el usuario"))
        self.assertEqual(self.autoridad.deudas_abiertas(), [])
        self.assertFalse(self.autoridad.saldar(deuda, "otra vez"))


if __name__ == "__main__":
    unittest.main()
