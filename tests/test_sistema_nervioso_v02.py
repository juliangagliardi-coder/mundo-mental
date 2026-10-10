import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from mundo_mental import Aspecto, IdentidadAspecto, Impulso, SistemaNervioso, TejidoMental


def identidad(nombre, sensibilidad=None):
    return IdentidadAspecto(
        nombre=nombre, esencia="Comprender señales", proposito="Colaborar sin perder identidad",
        perspectiva="Distingue importancia y afinidad", principios=("honestidad",),
        voz="Clara", autoridad=("atender",), limites=("dominar",),
        sensibilidades=sensibilidad or {},
    )


class PruebasSistemaNervioso02(unittest.TestCase):
    def test_pausa_conserva_bandeja_y_reanuda(self):
        with tempfile.TemporaryDirectory() as carpeta:
            aspecto = Aspecto(identidad("Uno", {"hallazgo": 1.0}), carpeta)
            sistema = SistemaNervioso()
            sistema.conectar(aspecto)
            sistema.pausar("Uno")
            sistema.publicar(Impulso("hallazgo", 1, "otro", importancia=1.0))
            self.assertEqual(sistema.latir(), [])
            self.assertEqual(sistema.pendientes("Uno"), 1)
            sistema.reanudar("Uno")
            self.assertEqual(len(sistema.latir()), 1)

    def test_reintenta_en_otro_latido_y_luego_atiende(self):
        intentos = []

        def receptor(impulso):
            intentos.append(impulso.id)
            if len(intentos) == 1:
                raise RuntimeError("transitorio")
            return {"atendido": True, "interes": 0.9}

        sistema = SistemaNervioso(max_reintentos=2)
        sistema.conectar_receptor("inestable", receptor)
        sistema.publicar(Impulso("evento", {}, "prueba"))
        primera = sistema.latir()
        self.assertIn("reintento:1", primera[0].detalle)
        self.assertEqual(sistema.pendientes("inestable"), 1)
        segunda = sistema.latir()
        self.assertTrue(segunda[0].atendido)
        self.assertEqual(sistema.estadisticas.reintentados, 1)

    def test_aisla_tras_agotar_reintentos(self):
        sistema = SistemaNervioso(max_reintentos=1)
        sistema.conectar_receptor("roto", lambda _: (_ for _ in ()).throw(ValueError("fallo")))
        sistema.publicar(Impulso("evento", {}, "prueba"))
        sistema.latir()
        sistema.latir()
        self.assertEqual(sistema.estadisticas.aislados, 1)
        self.assertEqual(len(sistema.cuarentena), 1)

    def test_caducidad_y_traza_causal(self):
        sistema = SistemaNervioso()
        pasado = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        resultado = sistema.publicar(Impulso("viejo", None, "prueba", caduca=pasado))
        self.assertEqual(resultado["encolados"], 0)
        raiz = Impulso("pregunta", "por qué", "Uno")
        hija = raiz.derivar("respuesta", "porque", "Dos")
        sistema.publicar(raiz)
        sistema.publicar(hija)
        self.assertEqual([x.id for x in sistema.trazar(raiz.id)], [raiz.id, hija.id])

    def test_tejido_exige_origen_real_y_conserva_causa(self):
        with tempfile.TemporaryDirectory() as carpeta:
            uno = Aspecto(identidad("Uno", {"respuesta": 1.0}), carpeta)
            dos = Aspecto(identidad("Dos", {"pregunta": 1.0}), carpeta)
            tejido = TejidoMental()
            tejido.incorporar(uno)
            tejido.incorporar(dos)
            pregunta = tejido.emitir("Uno", "pregunta", "¿qué ves?", importancia=0.8)
            tejido.latir()
            respuesta = tejido.responder("Dos", pregunta, "respuesta", "una relación")
            self.assertEqual(respuesta.causa, pregunta.id)
            self.assertEqual(respuesta.correlacion, pregunta.id)
            with self.assertRaises(KeyError):
                tejido.emitir("Fantasma", "evento", None)


if __name__ == "__main__":
    unittest.main()
