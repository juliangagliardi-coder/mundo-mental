import tempfile
import unittest
from pathlib import Path

from mundo_mental.calles import Calle, Calles, Mensaje, Router


class PruebasCalles(unittest.TestCase):
    def test_router_transporta_solo_por_contrato_explicito(self):
        router = Router()
        calle = Calle("consulta", "Curiosidad", "Biblioteca", "pregunta")
        router.registrar_calle(calle)
        router.registrar_destino("Biblioteca", lambda mensaje: mensaje.contenido)

        resultado = router.enviar(
            "consulta", Mensaje("pregunta", "¿Qué falta?", "Curiosidad")
        )

        self.assertEqual(resultado, "¿Qué falta?")
        self.assertEqual(calle.transportados, 1)
        with self.assertRaises(ValueError):
            router.enviar("consulta", Mensaje("orden", "Borrar", "Curiosidad"))
        self.assertEqual(calle.rechazados, 1)

    def test_calle_cerrada_y_destino_ausente_fallan_sin_ocultar_causa(self):
        router = Router()
        calle = Calle("ruta", "A", "B", "dato", activa=False)
        router.registrar_calle(calle)
        with self.assertRaisesRegex(RuntimeError, "cerrada"):
            router.enviar("ruta", Mensaje("dato", 1, "A"))

        calle.activa = True
        with self.assertRaisesRegex(KeyError, "destino B"):
            router.enviar("ruta", Mensaje("dato", 1, "A"))

    def test_aspecto_calles_recuerda_apertura_y_fallo(self):
        with tempfile.TemporaryDirectory() as temporal:
            calles = Calles(Path(temporal))
            calles.registrar_calle(Calle("ruta", "A", "B", "dato"))
            with self.assertRaises(KeyError):
                calles.enviar("ruta", Mensaje("dato", 1, "A"))

            tipos = [recuerdo["tipo"] for recuerdo in calles.memoria_de_si.historia()]
            self.assertIn("calle_abierta", tipos)
            self.assertIn("fallo_transporte", tipos)


if __name__ == "__main__":
    unittest.main()
