"""Pruebas del razonador HTTP sin usar red: se inyecta una función de envío falsa."""

import json
import unittest
import urllib.error

from mundo_mental.razonador import ConfigRazonador, RazonadorHTTP, crear_razonador
from mundo_mental.tierra import RazonadorNulo

ENTORNO = {
    "MUNDO_MENTAL_API_URL": "http://127.0.0.1:8080/v1",
    "MUNDO_MENTAL_MODELO": "modelo-local",
    "MUNDO_MENTAL_API_KEY": "local",
}


def _respuesta(texto):
    return json.dumps({"choices": [{"message": {"content": texto}}]}).encode("utf-8")


class PruebasRazonadorLocal(unittest.TestCase):
    def test_sin_entorno_devuelve_razonador_nulo(self):
        self.assertIsInstance(crear_razonador({}), RazonadorNulo)

    def test_acepta_localhost_sin_https(self):
        config = ConfigRazonador.desde_entorno(ENTORNO)
        self.assertIsNotNone(config)
        self.assertNotIn("local", repr(config).replace("modelo-local", "").replace("127.0.0.1", ""))

    def test_rechaza_http_remoto(self):
        entorno = dict(ENTORNO, MUNDO_MENTAL_API_URL="http://ejemplo.com/v1")
        with self.assertRaises(ValueError):
            ConfigRazonador.desde_entorno(entorno)

    def test_responde_con_texto(self):
        razonador = crear_razonador(ENTORNO, enviar=lambda *a: _respuesta("hola"))
        self.assertEqual(razonador.responder("di hola"), "hola")
        self.assertEqual(razonador.ultimo_error, "")

    def test_error_de_red(self):
        def falla(*_):
            raise urllib.error.URLError("sin conexión")
        razonador = crear_razonador(ENTORNO, enviar=falla)
        self.assertEqual(razonador.responder("x"), "")
        self.assertEqual(razonador.ultimo_error, "red")

    def test_error_http(self):
        def falla(url, *_):
            raise urllib.error.HTTPError(url, 500, "error", {}, None)
        razonador = crear_razonador(ENTORNO, enviar=falla)
        self.assertEqual(razonador.responder("x"), "")
        self.assertEqual(razonador.ultimo_error, "http_500")

    def test_respuesta_invalida(self):
        razonador = crear_razonador(ENTORNO, enviar=lambda *a: b"{}")
        self.assertEqual(razonador.responder("x"), "")
        self.assertEqual(razonador.ultimo_error, "respuesta_invalida")

    def test_presupuesto_agotado(self):
        razonador = crear_razonador(ENTORNO, enviar=lambda *a: _respuesta("ok"), max_llamadas=1)
        self.assertEqual(razonador.responder("1"), "ok")
        self.assertEqual(razonador.responder("2"), "")
        self.assertEqual(razonador.ultimo_error, "presupuesto_agotado")

    def test_clase_correcta(self):
        razonador = crear_razonador(ENTORNO, enviar=lambda *a: _respuesta("ok"))
        self.assertIsInstance(razonador, RazonadorHTTP)


if __name__ == "__main__":
    unittest.main()
