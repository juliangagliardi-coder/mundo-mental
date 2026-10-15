import json
import unittest
import urllib.error

from mundo_mental.razonador import ConfigRazonador, RazonadorHTTP, crear_razonador
from mundo_mental.tierra import RazonadorNulo

CLAVE = "clave-secreta-de-prueba"
ENTORNO = {"MUNDO_MENTAL_API_KEY": CLAVE, "MUNDO_MENTAL_MODELO": "modelo-x"}


def respuesta(texto):
    return json.dumps({"choices": [{"message": {"content": texto}}]}).encode("utf-8")


class Registro:
    def __init__(self, resultado):
        self.resultado = resultado
        self.peticiones = []

    def __call__(self, url, cabeceras, cuerpo, tiempo_max):
        self.peticiones.append((url, cabeceras, json.loads(cuerpo.decode("utf-8")), tiempo_max))
        if isinstance(self.resultado, Exception):
            raise self.resultado
        return self.resultado


class TestConfig(unittest.TestCase):
    def test_sin_clave_o_modelo_no_hay_config(self):
        self.assertIsNone(ConfigRazonador.desde_entorno({}))
        self.assertIsNone(ConfigRazonador.desde_entorno({"MUNDO_MENTAL_API_KEY": CLAVE}))
        self.assertIsNone(ConfigRazonador.desde_entorno({"MUNDO_MENTAL_MODELO": "m"}))

    def test_url_por_defecto_y_normalizada(self):
        config = ConfigRazonador.desde_entorno({**ENTORNO, "MUNDO_MENTAL_API_URL": "https://api.ejemplo.com/v1/"})
        self.assertEqual(config.url_base, "https://api.ejemplo.com/v1")
        self.assertEqual(ConfigRazonador.desde_entorno(ENTORNO).url_base, "https://api.openai.com/v1")

    def test_rechaza_http_remoto_pero_admite_local(self):
        with self.assertRaises(ValueError):
            ConfigRazonador.desde_entorno({**ENTORNO, "MUNDO_MENTAL_API_URL": "http://api.ejemplo.com"})
        self.assertIsNotNone(ConfigRazonador.desde_entorno({**ENTORNO, "MUNDO_MENTAL_API_URL": "http://localhost:11434/v1"}))

    def test_la_clave_no_aparece_en_repr(self):
        self.assertNotIn(CLAVE, repr(ConfigRazonador.desde_entorno(ENTORNO)))


class TestRazonador(unittest.TestCase):
    def razonador(self, resultado, max_llamadas=50):
        registro = Registro(resultado)
        return RazonadorHTTP(ConfigRazonador.desde_entorno(ENTORNO), registro, max_llamadas), registro

    def test_peticion_y_respuesta(self):
        razonador, registro = self.razonador(respuesta("hola"))
        self.assertEqual(razonador.responder("saluda", "ctx"), "hola")
        url, cabeceras, cuerpo, _ = registro.peticiones[0]
        self.assertEqual(url, "https://api.openai.com/v1/chat/completions")
        self.assertEqual(cabeceras["Authorization"], f"Bearer {CLAVE}")
        self.assertEqual(cuerpo["model"], "modelo-x")
        self.assertEqual(cuerpo["messages"][-1]["content"], "saluda")
        self.assertEqual(len(cuerpo["messages"]), 3)
        self.assertEqual(razonador.ultimo_error, "")

    def test_errores_devuelven_vacio_sin_filtrar_la_clave(self):
        casos = (
            (urllib.error.HTTPError("u", 401, "no", {}, None), "http_401"),
            (urllib.error.URLError("sin red"), "red"),
            (TimeoutError(), "red"),
            (b"no es json", "respuesta_invalida"),
            (json.dumps({"choices": []}).encode(), "respuesta_invalida"),
            (json.dumps({"choices": [{"message": {"content": 5}}]}).encode(), "respuesta_invalida"),
        )
        for resultado, esperado in casos:
            with self.subTest(esperado=esperado):
                razonador, _ = self.razonador(resultado)
                self.assertEqual(razonador.responder("x"), "")
                self.assertEqual(razonador.ultimo_error, esperado)
                self.assertNotIn(CLAVE, razonador.ultimo_error)

    def test_presupuesto_de_llamadas(self):
        razonador, registro = self.razonador(respuesta("ok"), max_llamadas=2)
        self.assertEqual([razonador.responder("a"), razonador.responder("b"), razonador.responder("c")], ["ok", "ok", ""])
        self.assertEqual(razonador.ultimo_error, "presupuesto_agotado")
        self.assertEqual(len(registro.peticiones), 2)

    def test_fabrica(self):
        self.assertIsInstance(crear_razonador({}), RazonadorNulo)
        self.assertIsInstance(crear_razonador(ENTORNO), RazonadorHTTP)


if __name__ == "__main__":
    unittest.main()
