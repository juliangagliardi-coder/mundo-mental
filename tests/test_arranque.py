import tempfile
import unittest
from pathlib import Path

from mundo_mental.aspecto import Aspecto, IdentidadAspecto
from mundo_mental.arranque import (RazonadorLimitado, ReflexionTierra, construir_mundo,
                                   construir_razonadores)
from mundo_mental.banco_tareas import BancoTareas, TAREAS_BASE
from mundo_mental.mente_aspecto import conectar_mentes
from mundo_mental.sistema_nervioso import Impulso, SistemaNervioso
from mundo_mental.tejido import TejidoMental
from mundo_mental.tierra import RazonadorNulo

REF = {t.id: t.referencia for t in TAREAS_BASE}


class Falso:
    def __init__(self, respuesta="SI"):
        self.respuesta = respuesta
        self.llamadas = 0

    def responder(self, instruccion, contexto=""):
        self.llamadas += 1
        return self.respuesta


class Programador:
    """Razonador de prueba: devuelve la referencia de la tarea cuando el contexto es un id del banco."""

    def responder(self, instruccion, contexto=""):
        if contexto in REF:
            return "```python\n" + REF[contexto] + "\n```"
        return "resumen"


def identidad(nombre):
    return IdentidadAspecto(nombre=nombre, esencia="e", proposito="p", perspectiva="v",
                            principios=("x",), voz="v")


class TestRazonadores(unittest.TestCase):
    def test_sin_modelo_devuelve_nulos(self):
        general, decisiones = construir_razonadores(sin_modelo=True)
        self.assertIsInstance(general, RazonadorNulo)
        self.assertIsInstance(decisiones, RazonadorNulo)

    def test_rechaza_servidores_no_locales(self):
        for url in ("https://api.openai.com/v1", "http://127.0.0.1.ejemplo.com/v1", "http://10.0.0.5:8080/v1"):
            with self.assertRaises(ValueError):
                construir_razonadores(url)

    def test_acepta_local_y_limita_tokens_de_decision(self):
        general, decisiones = construir_razonadores("http://127.0.0.1:8080/v1")
        self.assertEqual(decisiones.config.max_tokens, 8)
        self.assertGreater(general.config.max_tokens, decisiones.config.max_tokens)
        self.assertGreater(decisiones.max_llamadas, 1000)


class TestTope(unittest.TestCase):
    def test_limita_llamadas_por_hora(self):
        t = [0.0]
        r = RazonadorLimitado(Falso("ok"), 2, reloj=lambda: t[0])
        self.assertEqual([r.responder("x"), r.responder("x"), r.responder("x")], ["ok", "ok", ""])
        self.assertEqual(r.denegadas, 1)
        t[0] = 3601.0
        self.assertEqual(r.responder("x"), "ok")

    def test_rechaza_tope_negativo(self):
        with self.assertRaises(ValueError):
            RazonadorLimitado(Falso(), -1)


class TestMundo(unittest.TestCase):
    def crear(self, decisiones=None, **extra):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        mundo = construir_mundo(tmp.name, RazonadorNulo(), decisiones or RazonadorNulo(), pausa=0,
                                dormir=lambda s: None, **extra)
        return mundo, tmp.name

    def test_late_y_avanza_el_tejido(self):
        mundo, _ = self.crear()
        self.assertEqual(mundo.vida.vivir(max_latidos=6), 6)
        self.assertEqual(mundo.tejido.ciclo, 6)
        self.assertIn("Tierra", mundo.mentes)

    def test_la_reflexion_llega_a_tierra(self):
        mundo, _ = self.crear(cada_latidos=1)
        mundo.vida.vivir(max_latidos=6)
        self.assertGreaterEqual(mundo.reflexion.emitidos, 1)
        self.assertGreaterEqual(mundo.tejido.sistema.estadisticas.publicados, 1)

    def test_con_margen_total_el_modelo_es_consultado(self):
        falso = Falso("SI")
        mundo, _ = self.crear(decisiones=falso, cada_latidos=1, margen=1.0)
        mundo.vida.vivir(max_latidos=6)
        self.assertGreaterEqual(falso.llamadas, 1)
        self.assertGreaterEqual(mundo.mentes["Tierra"].consultas, 1)

    def test_parar_detiene_el_arranque(self):
        mundo, raiz = self.crear()
        (Path(raiz) / "PARAR").write_text("", encoding="utf-8")
        self.assertEqual(mundo.vida.vivir(max_latidos=50), 0)

    def test_motor_pausado_detiene_la_vida(self):
        mundo, _ = self.crear()
        mundo.motor.pausar("prueba")
        self.assertEqual(mundo.vida.vivir(max_latidos=10), 0)

    def test_sin_trabajo_por_defecto(self):
        mundo, _ = self.crear()
        self.assertIsNone(mundo.trabajo)
        self.assertIsNone(mundo.autoridad)


class TestMundoConTrabajo(unittest.TestCase):
    def test_el_mundo_adopta_solo_lo_que_mejora(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        mundo = construir_mundo(tmp.name, Programador(), RazonadorNulo(), pausa=0, dormir=lambda s: None,
                                cada_latidos=1, trabajo=True)
        mundo.vida.vivir(max_latidos=12)
        self.assertGreaterEqual(mundo.vida.ciclos, 1)
        self.assertEqual(mundo.vida.fallos_ciclo, 0)
        self.assertGreaterEqual(mundo.reflexion.emitidos, 1)
        self.assertEqual(set(mundo.trabajo._cargar_adoptadas()), set(BancoTareas().ids()))

    def test_el_tope_horario_frena_al_modelo(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        mundo = construir_mundo(tmp.name, Programador(), RazonadorNulo(), pausa=0, dormir=lambda s: None,
                                cada_latidos=1, trabajo=True, tope_hora=0, reloj=lambda: 0.0)
        mundo.vida.vivir(max_latidos=12)
        self.assertGreaterEqual(mundo.limitador.denegadas, 1)
        self.assertEqual(mundo.trabajo._cargar_adoptadas(), {})


class TestSuscripciones(unittest.TestCase):
    def test_conectar_mentes_conserva_temas_e_importancia_minima(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tejido = TejidoMental()
        aspecto = Aspecto(identidad("Atenta"), tmp.name)
        tejido.incorporar(aspecto, temas=("curiosidad",), importancia_minima=0.4)
        conectar_mentes(tejido.sistema, [aspecto], Falso("SI"))
        self.assertEqual(tejido.sistema.suscripciones["Atenta"], {"curiosidad"})
        self.assertEqual(tejido.sistema.importancia_minima["Atenta"], 0.4)
        r = tejido.sistema.publicar(Impulso(tipo="otro", contenido="x", origen="Z", importancia=0.9))
        self.assertEqual(r["encolados"], 0)


if __name__ == "__main__":
    unittest.main()
