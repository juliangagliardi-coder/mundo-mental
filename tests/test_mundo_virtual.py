import unittest

from mundo_mental.mundo_virtual import MundoVirtual


class PruebasMundoVirtual(unittest.TestCase):
    def test_mundo_tiene_seres_y_flujo_observable(self):
        mundo = MundoVirtual()
        self.assertEqual(mundo.paso_siguiente(), "Curiosidad")
        self.assertIn("Biblioteca", mundo.seres)
        self.assertIn("Centinela", mundo.seres)

    def test_ciclo_avanza_por_las_cinco_etapas(self):
        mundo = MundoVirtual()
        eventos = [mundo.avanzar() for _ in range(5)]
        self.assertEqual([evento.actor for evento in eventos], ["Curiosidad", "Catalogador", "Biblioteca", "Corazón", "Centinela"])
        self.assertEqual(mundo.ciclos_terminados, 1)
        self.assertEqual(mundo.paso_siguiente(), "Curiosidad")

    def test_inicio_y_pausa_son_explicitos(self):
        mundo = MundoVirtual()
        mundo.iniciar()
        self.assertTrue(mundo.ciclo_activo)
        mundo.pausar()
        self.assertFalse(mundo.ciclo_activo)

    def test_ciclo_no_pretende_escribir_memoria_persistente(self):
        mundo = MundoVirtual()
        for _ in range(5):
            mundo.avanzar()
        self.assertIn("no se escribe memoria persistente", mundo.eventos[-1].detalle)


if __name__ == "__main__":
    unittest.main()
