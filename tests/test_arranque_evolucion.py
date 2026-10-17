import tempfile
import unittest
from pathlib import Path

from mundo_mental.arranque import (
    RazonadorLimitado, construir_mundo, construir_razonador_evolucion, main,
)
from mundo_mental.razonador import RazonadorHTTP
from mundo_mental.tierra import RazonadorNulo


class Guion:
    def responder(self, instruccion, contexto=""):
        return ""


class TestArranqueEvolucion(unittest.TestCase):
    def test_razonador_de_evolucion_usa_mas_tokens_y_tiempo(self):
        r = construir_razonador_evolucion("http://127.0.0.1:8080/v1", "local", False, 1500, 600.0)
        self.assertIsInstance(r, RazonadorHTTP)
        self.assertEqual((r.config.max_tokens, r.config.tiempo_max), (1500, 600.0))

    def test_sin_modelo_devuelve_nulo(self):
        self.assertIsInstance(construir_razonador_evolucion(sin_modelo=True), RazonadorNulo)

    def test_solo_servidores_locales_y_valores_positivos(self):
        with self.assertRaises(ValueError):
            construir_razonador_evolucion("http://example.com/v1")
        with self.assertRaises(ValueError):
            construir_razonador_evolucion(max_tokens=0)
        with self.assertRaises(ValueError):
            construir_razonador_evolucion(tiempo_max=-1)

    def test_el_mundo_usa_el_razonador_propio_de_evolucion(self):
        with tempfile.TemporaryDirectory() as tmp:
            propio = Guion()
            mundo = construir_mundo(Path(tmp) / "mente", RazonadorNulo(), RazonadorNulo(), trabajo=True,
                                    repo=tmp, rutas_evolucion=("mundo_mental/modulo.py",),
                                    objetivo="mejorar", razonador_evolucion=propio)
            self.assertIsNotNone(mundo.evolutiva)
            self.assertIsInstance(mundo.evolutiva.razonador, RazonadorLimitado)
            self.assertIs(mundo.evolutiva.razonador.base, propio)

    def test_evolucionar_exige_objetivo_y_trabajo(self):
        with self.assertRaises(SystemExit):
            main(["--evolucionar", "mundo_mental/modulo.py", "--sin-modelo"])
        with self.assertRaises(SystemExit):
            main(["--evolucionar", "mundo_mental/modulo.py", "--objetivo", "x", "--sin-trabajo", "--sin-modelo"])


if __name__ == "__main__":
    unittest.main()
