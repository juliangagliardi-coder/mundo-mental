import json
import tempfile
import unittest

from mundo_mental import Genoma, Vigilante


class PruebasGenoma(unittest.TestCase):
    def test_deltas_compactos_reconstruyen_desde_ancla(self):
        with tempfile.TemporaryDirectory() as carpeta:
            genoma = Genoma(carpeta, intervalo_anclas=10)
            primero = genoma.registrar("corazon", "inicio", {"energia": 1, "modo": "sereno"})
            segundo = genoma.registrar("corazon", "latido", {"energia": 2})
            self.assertTrue(primero.ancla)
            self.assertFalse(segundo.ancla)
            self.assertEqual(genoma.reconstruir(genoma.hitos()), {"energia": 2, "modo": "sereno"})
            self.assertTrue(genoma.verificar(genoma.hitos()))

    def test_decision_importante_obliga_ancla_y_guarda_contexto(self):
        with tempfile.TemporaryDirectory() as carpeta:
            genoma = Genoma(carpeta)
            genoma.registrar("corazon", "inicio", {"estado": "estable"})
            hito = genoma.registrar(
                "corazon", "obra", {"estado": "reformado"}, importante=True,
                contexto={"alternativas": ["conservar"], "motivo": "mejora demostrada"},
            )
            self.assertTrue(hito.ancla)
            self.assertEqual(hito.contexto["motivo"], "mejora demostrada")

    def test_vigilante_repara_una_replicа_corrupta_desde_la_sana(self):
        with tempfile.TemporaryDirectory() as carpeta:
            genoma = Genoma(carpeta)
            genoma.registrar("biblioteca", "inicio", {"memorias": 1})
            genoma.rutas[0].write_text('{"dato":"corrupto"}\n', encoding="utf-8")
            informe = Vigilante(genoma).revisar()
            self.assertTrue(informe["reparado"])
            self.assertTrue(informe["primaria_valida"])
            self.assertTrue(informe["respaldo_valido"])
            self.assertTrue(informe["replicas_coinciden"])

    def test_toda_alteracion_historica_impide_reconstruir(self):
        with tempfile.TemporaryDirectory() as carpeta:
            genoma = Genoma(carpeta)
            genoma.registrar("tejido", "inicio", {"ciclo": 1})
            genoma.registrar("tejido", "avance", {"ciclo": 2})
            ruta = genoma.rutas[0]
            lineas = ruta.read_text(encoding="utf-8").splitlines()
            cambiado = json.loads(lineas[0])
            cambiado["cambio"]["ciclo"] = 99
            ruta.write_text(json.dumps(cambiado) + "\n" + lineas[1] + "\n", encoding="utf-8")
            self.assertFalse(genoma.verificar(genoma._leer_ruta(ruta)))
            self.assertEqual(genoma.reconstruir(genoma.hitos()), {"ciclo": 2})


if __name__ == "__main__":
    unittest.main()
