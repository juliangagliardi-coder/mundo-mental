import json
import tempfile
import unittest
from pathlib import Path

from mundo_mental.genoma import Genoma, Vigilante
from mundo_mental.genoma_vivo import Autoridad, MemoriaViva, VigilanteActivo


def _corromper(ruta: Path) -> None:
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    primero = json.loads(lineas[0])
    primero["zona"] = "falsificada"
    lineas[0] = json.dumps(primero)
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")


class TestGenomaVivo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.genoma = Genoma(self.tmp.name)
        self.memoria = MemoriaViva(self.tmp.name, self.genoma, ciclos_por_generacion=10)

    def _generaciones(self, n):
        for _ in range(n):
            self.memoria.cerrar_generacion()

    def test_olvido_gradual_y_proteccion_fundacional(self):
        origen = self.memoria.recordar("origen", {"nace": "mundo"})
        decision = self.memoria.recordar("decision", {"eligio": "A"})
        biblio = self.memoria.recordar("biblioteca", {"saber": "x"})
        detalle = self.memoria.recordar("detalle", {"a": 1, "b": 2, "c": 3, "d": 4})
        self._generaciones(3)
        self.assertEqual(self.memoria.recuerdos[detalle.id].nivel, 1)
        self.assertTrue(self.memoria.recuerdos[detalle.id].contenido["_resumido"])
        self.assertNotIn("d", self.memoria.recuerdos[detalle.id].contenido)
        self._generaciones(5)
        olvidado = self.memoria.recuerdos[detalle.id]
        self.assertEqual((olvidado.nivel, olvidado.contenido), (2, {}))
        self.assertEqual(olvidado.huella, detalle.huella)
        for r in (origen, decision, biblio):
            self.assertEqual(self.memoria.recuerdos[r.id].nivel, 0)
            self.assertEqual(self.memoria.recuerdos[r.id].contenido, r.contenido)

    def test_el_uso_protege_del_olvido(self):
        util = self.memoria.recordar("detalle", {"clave": "util"})
        for _ in range(3):
            self.memoria.usar(util.id)
        inutil = self.memoria.recordar("detalle", {"clave": "inutil"})
        self._generaciones(20)
        self.assertEqual(self.memoria.recuerdos[util.id].nivel, 0)
        self.assertEqual(self.memoria.recuerdos[inutil.id].nivel, 2)

    def test_corroborar_protege_y_decae_lo_no_usado(self):
        contexto = self.memoria.recordar("contexto", {"v": 1})
        self.memoria.corroborar(contexto.id)
        self.memoria.corroborar(contexto.id)
        self.assertTrue(self.memoria.recuerdos[contexto.id].protegido)
        suelto = self.memoria.recordar("detalle", {"v": 2})
        self._generaciones(2)
        self.assertLess(self.memoria.recuerdos[suelto.id].relevancia, 0.2)

    def test_generaciones_por_ciclos_y_persistencia(self):
        r = self.memoria.recordar("incidente_grave", {"fallo": "critico"})
        cierres = [self.memoria.contar_ciclo() for _ in range(25)]
        self.assertEqual(self.memoria.generacion, 2)
        self.assertEqual(len([c for c in cierres if c]), 2)
        reabierta = MemoriaViva(self.tmp.name, self.genoma, ciclos_por_generacion=10)
        self.assertEqual((reabierta.generacion, reabierta.ciclos), (2, 25))
        self.assertEqual(reabierta.recuerdos[r.id].contenido, {"fallo": "critico"})

    def test_genoma_sigue_verificable_y_guarda_lo_fundamental(self):
        r = self.memoria.recordar("hito", {"nace": "ciclo-1"})
        self._generaciones(4)
        self.assertTrue(Genoma.verificar(self.genoma.hitos()))
        estado = Genoma.reconstruir(self.genoma.hitos())
        self.assertEqual(estado[f"recuerdo.{r.id}"], r.huella)
        self.assertIn("generacion.4", estado)

    def test_categoria_invalida(self):
        with self.assertRaises(ValueError):
            self.memoria.recordar("inventada", {})
        with self.assertRaises(ValueError):
            MemoriaViva(self.tmp.name, generaciones_detalle=5, generaciones_olvido=2)

    def test_autoridad_observacion_veta_y_falla_cerrado(self):
        si = lambda p: True
        no = lambda p: False

        def roto(p):
            raise RuntimeError("x")

        self.assertEqual(Autoridad(self.genoma, si, si).resolver({"a": 1})["veredicto"], "aprobada")
        veto = Autoridad(self.genoma, si, no).resolver({"a": 2})
        self.assertEqual((veto["veredicto"], veto["decide"]), ("bloqueada", "observacion"))
        self.assertEqual(Autoridad(self.genoma, no, si).resolver({"a": 3})["veredicto"], "rechazada")
        fallo = Autoridad(self.genoma, roto, si).resolver({"a": 4})
        self.assertEqual(fallo["veredicto"], "bloqueada")
        self.assertTrue(fallo["decide"].startswith("error:"))
        estado = Genoma.reconstruir(self.genoma.hitos())
        self.assertEqual(len([k for k in estado if k.startswith("decision.")]), 4)

    def test_vigilante_activo_repara_y_alarma_media(self):
        self.memoria.recordar("origen", {"x": 1})
        self.memoria.recordar("decision", {"y": 2})
        alarmas = []
        _corromper(self.genoma.rutas[1])
        informe = VigilanteActivo(Vigilante(self.genoma), alarmas.append).vigilar()
        self.assertTrue(informe["reparado"])
        self.assertEqual([a["gravedad"] for a in alarmas], ["media"])
        VigilanteActivo(Vigilante(self.genoma), alarmas.append).vigilar()
        self.assertEqual(len(alarmas), 1)

    def test_vigilante_activo_alarma_critica_con_doble_corrupcion(self):
        self.memoria.recordar("origen", {"x": 1})
        alarmas = []
        for ruta in self.genoma.rutas:
            _corromper(ruta)
        VigilanteActivo(Vigilante(self.genoma), alarmas.append).vigilar()
        self.assertEqual([a["gravedad"] for a in alarmas], ["critica"])
        with self.assertRaises(ValueError):
            Genoma.reconstruir(self.genoma.hitos())


if __name__ == "__main__":
    unittest.main()
