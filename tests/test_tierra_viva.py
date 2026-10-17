import tempfile
import unittest
from pathlib import Path

from mundo_mental.aspecto import Aspecto, IdentidadAspecto
from mundo_mental.mente_aspecto import MenteAspecto, conectar_mentes, interpretar_decision
from mundo_mental.reparto_razonamiento import RepartoRazonamiento
from mundo_mental.sistema_nervioso import Impulso, SistemaNervioso
from mundo_mental.tierra_viva import TierraViva


class Falso:
    def __init__(self, respuesta=""):
        self.respuesta = respuesta
        self.llamadas = 0

    def responder(self, instruccion, contexto=""):
        self.llamadas += 1
        if isinstance(self.respuesta, Exception):
            raise self.respuesta
        return self.respuesta


def identidad(nombre="Prueba"):
    return IdentidadAspecto(nombre=nombre, esencia="e", proposito="p", perspectiva="v",
                            principios=("x",), voz="v")


def impulso_dudoso(**cambios):
    datos = dict(tipo="curiosidad", contenido="x", origen="otro")
    datos.update(cambios)
    return Impulso(**datos)


class TestDecision(unittest.TestCase):
    def test_interpretar(self):
        self.assertIs(interpretar_decision("SI"), True)
        self.assertIs(interpretar_decision("S\u00ed, claro"), True)
        self.assertIs(interpretar_decision(" no."), False)
        self.assertIsNone(interpretar_decision("quiz\u00e1s"))
        self.assertIsNone(interpretar_decision(""))


class TestMente(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.aspecto = Aspecto(identidad(), self.tmp.name)

    def test_el_modelo_puede_atender_lo_que_la_formula_ignora(self):
        mente = MenteAspecto(self.aspecto, Falso("SI"), margen=1.0)
        r = mente.recibir_impulso(impulso_dudoso())
        self.assertTrue(r["atendido"])
        self.assertEqual((self.aspecto.atendidos, self.aspecto.ignorados), (1, 0))
        self.assertEqual(mente.cambios, 1)

    def test_el_modelo_puede_ignorar_lo_que_la_formula_atiende(self):
        mente = MenteAspecto(self.aspecto, Falso("NO"), margen=1.0)
        r = mente.recibir_impulso(impulso_dudoso(importancia=1.0, destino="Prueba"))
        self.assertFalse(r["atendido"])
        self.assertEqual((self.aspecto.atendidos, self.aspecto.ignorados), (0, 1))

    def test_respuesta_confusa_o_error_usa_la_formula(self):
        for respuesta in ("quiz\u00e1s", "", RuntimeError("fallo")):
            tmp = tempfile.TemporaryDirectory()
            self.addCleanup(tmp.cleanup)
            aspecto = Aspecto(identidad(), tmp.name)
            mente = MenteAspecto(aspecto, Falso(respuesta), margen=1.0)
            r = mente.recibir_impulso(impulso_dudoso())
            self.assertFalse(r["atendido"])
            self.assertEqual(mente.respaldos, 1)

    def test_alarmas_y_urgencias_no_consultan_al_modelo(self):
        falso = Falso("NO")
        mente = MenteAspecto(self.aspecto, falso, margen=1.0)
        mente.recibir_impulso(impulso_dudoso(canal="alarma"))
        mente.recibir_impulso(impulso_dudoso(urgencia=3))
        self.assertEqual(falso.llamadas, 0)

    def test_sin_presupuesto_usa_la_formula(self):
        falso = Falso("SI")
        reparto = RepartoRazonamiento(por_latido=0)
        mente = MenteAspecto(self.aspecto, falso, reparto, margen=1.0)
        r = mente.recibir_impulso(impulso_dudoso())
        self.assertFalse(r["atendido"])
        self.assertEqual(falso.llamadas, 0)

    def test_el_modelo_no_cambia_la_identidad(self):
        antes = self.aspecto.identidad.huella()
        MenteAspecto(self.aspecto, Falso("SI"), margen=1.0).recibir_impulso(impulso_dudoso())
        self.assertEqual(self.aspecto.identidad.huella(), antes)

    def test_conectar_mentes_en_el_sistema_nervioso(self):
        sistema = SistemaNervioso()
        mentes = conectar_mentes(sistema, [self.aspecto], Falso("SI"), margen=1.0)
        sistema.publicar(impulso_dudoso())
        reacciones = sistema.latir()
        self.assertEqual(len(reacciones), 1)
        self.assertTrue(reacciones[0].atendido)
        self.assertIn("Prueba", mentes)


class TestReparto(unittest.TestCase):
    def test_limites_por_latido_y_por_aspecto(self):
        reparto = RepartoRazonamiento(por_latido=2, por_aspecto=1)
        self.assertTrue(reparto.pedir("A"))
        self.assertFalse(reparto.pedir("A"))
        self.assertTrue(reparto.pedir("B"))
        self.assertFalse(reparto.pedir("C"))
        reparto.nuevo_latido()
        self.assertTrue(reparto.pedir("A"))

    def test_limite_por_hora(self):
        reloj = [0.0]
        reparto = RepartoRazonamiento(por_latido=10, por_aspecto=10, por_hora=2, reloj=lambda: reloj[0])
        self.assertTrue(reparto.pedir("A"))
        self.assertTrue(reparto.pedir("A"))
        self.assertFalse(reparto.pedir("A"))
        reloj[0] = 3601.0
        self.assertTrue(reparto.pedir("A"))


class CicloFalso:
    def __init__(self, fallar=False):
        self.fallar = fallar
        self.llamadas = 0

    def ejecutar(self, conceptos, tareas, presupuesto):
        self.llamadas += 1
        if self.fallar:
            raise RuntimeError("ciclo roto")
        return {}


class TestTierraViva(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.aspecto = Aspecto(identidad("Tierra"), self.tmp.name)

    def crear(self, ciclo=None, cada=1):
        return TierraViva(self.aspecto, SistemaNervioso(), RepartoRazonamiento(), self.tmp.name,
                          ciclo=ciclo, cada_latidos=cada, pausa=0, dormir=lambda s: None)

    def test_vive_el_numero_de_latidos_pedido(self):
        self.assertEqual(self.crear().vivir(max_latidos=3), 3)

    def test_se_detiene_con_el_archivo_parar(self):
        (Path(self.tmp.name) / "PARAR").write_text("", encoding="utf-8")
        self.assertEqual(self.crear().vivir(max_latidos=50), 0)

    def test_ejecuta_ciclos_cuando_esta_tranquila(self):
        ciclo = CicloFalso()
        vida = self.crear(ciclo, cada=2)
        vida.vivir(max_latidos=4)
        self.assertEqual((ciclo.llamadas, vida.ciclos), (2, 2))

    def test_un_ciclo_roto_no_mata_el_bucle(self):
        vida = self.crear(CicloFalso(fallar=True))
        self.assertEqual(vida.vivir(max_latidos=2), 2)
        self.assertEqual(vida.fallos_ciclo, 2)


if __name__ == "__main__":
    unittest.main()
