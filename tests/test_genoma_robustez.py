import tempfile
import unittest

from mundo_mental import Genoma, Vigilante


class PruebasRobustezGenoma(unittest.TestCase):
    def test_replica_malformada_no_rompe_la_auditoria_y_se_repara(self):
        with tempfile.TemporaryDirectory() as carpeta:
            genoma = Genoma(carpeta)
            genoma.registrar("biblioteca", "inicio", {"memorias": 1})
            genoma.rutas[0].write_text('{"dato":"corrupto"}\n', encoding="utf-8")
            informe = Vigilante(genoma).revisar()
            self.assertTrue(informe["reparado"])
            self.assertTrue(informe["primaria_valida"])
            self.assertTrue(informe["respaldo_valido"])
            self.assertTrue(informe["replicas_coinciden"])
            self.assertEqual(len(genoma.hitos()), 1)

    def test_replica_ausente_no_borra_la_replica_sana(self):
        with tempfile.TemporaryDirectory() as carpeta:
            genoma = Genoma(carpeta)
            genoma.registrar("biblioteca", "inicio", {"memorias": 1})
            genoma.rutas[0].unlink()
            informe = Vigilante(genoma).revisar()
            self.assertTrue(informe["reparado"])
            self.assertTrue(genoma.rutas[0].exists())
            self.assertEqual(len(genoma._leer_ruta(genoma.rutas[0])), 1)
            self.assertEqual(len(genoma._leer_ruta(genoma.rutas[1])), 1)

    def test_ambas_ilegibles_no_se_reparan_y_el_registro_falla_cerrado(self):
        with tempfile.TemporaryDirectory() as carpeta:
            genoma = Genoma(carpeta)
            genoma.registrar("biblioteca", "inicio", {"memorias": 1})
            for ruta in genoma.rutas:
                ruta.write_text("basura\n", encoding="utf-8")
            informe = Vigilante(genoma).revisar()
            self.assertFalse(informe["reparado"])
            self.assertFalse(informe["primaria_valida"])
            with self.assertRaises(ValueError):
                genoma.registrar("biblioteca", "nuevo", {"memorias": 2})


if __name__ == "__main__":
    unittest.main()
