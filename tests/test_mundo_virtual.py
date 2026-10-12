import tempfile
import unittest

from iniciar import ejecutar_ciclo
from mundo_mental.mundo_virtual import MundoVirtual


class PruebasMundoVirtual(unittest.TestCase):
    def test_el_monitor_no_inventa_eventos_por_si_solo(self):
        mundo = MundoVirtual()
        mundo.comenzar()
        self.assertEqual(mundo.eventos, [])
        self.assertIsNone(mundo.activo)

    def test_aplica_telemetria_del_ciclo_real(self):
        mundo = MundoVirtual()
        evento = mundo.aplicar_evento(
            "Curiosidad",
            "preguntar",
            {"detalle": "Formula una pregunta real", "pregunta_id": "p-1"},
        )
        self.assertEqual(evento.actor, "Curiosidad")
        self.assertEqual(mundo.activo, "Curiosidad")
        self.assertEqual(mundo.presencias["Curiosidad"].estado, "trabajando")

    def test_ciclo_integrado_emite_eventos_observables_reales(self):
        recibidos = []
        with tempfile.TemporaryDirectory() as carpeta:
            resultado = ejecutar_ciclo(
                carpeta,
                observador=lambda actor, accion, datos: recibidos.append(
                    (actor, accion, datos)
                ),
            )
        actores = {actor for actor, _, _ in recibidos}
        self.assertIn("Curiosidad", actores)
        self.assertIn("Biblioteca", actores)
        self.assertIn("Observador", actores)
        self.assertTrue(resultado["dictamen"].aceptada)
        self.assertTrue(resultado["reanudado"])

    def test_catalogador_y_corazon_quedan_honestamente_en_espera(self):
        mundo = MundoVirtual()
        mundo.aplicar_evento("Curiosidad", "observar", {"detalle": "Trabaja"})
        self.assertEqual(mundo.presencias["Catalogador"].estado, "en_espera")
        self.assertEqual(mundo.presencias["Corazón"].estado, "latiente")


if __name__ == "__main__":
    unittest.main()
