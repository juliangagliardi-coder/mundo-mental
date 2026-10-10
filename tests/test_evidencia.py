import tempfile
import unittest

from mundo_mental import Biblioteca, ResultadoExperimento, ValidadorEvidencia


class PruebasEvidenciaValidada(unittest.TestCase):
    def resultado(self, reproducible=True, estado="completado"):
        return ResultadoExperimento("pregunta-1", "prueba", {"x": 2}, 4, reproducible, estado)

    def test_solo_promueve_evidencia_reproducible_y_corrobora(self):
        with tempfile.TemporaryDirectory() as carpeta:
            biblioteca = Biblioteca(carpeta)
            validador = ValidadorEvidencia(biblioteca)
            dictamen = validador.evaluar(
                self.resultado(), "repeticion_externa", [2], "4", "doble"
            )
            self.assertTrue(dictamen.aceptada)
            self.assertIsNotNone(dictamen.recuerdo_id)
            recuerdos = biblioteca.buscar_similares([2])
            self.assertEqual(len(recuerdos), 1)
            self.assertEqual(recuerdos[0]["metadata"]["origen"], "laboratorio_validado")
            self.assertEqual(recuerdos[0]["metadata"]["corroboracion"], "repeticion_externa")

    def test_rechaza_sin_modificar_biblioteca_si_falta_corrobacion(self):
        with tempfile.TemporaryDirectory() as carpeta:
            biblioteca = Biblioteca(carpeta)
            validador = ValidadorEvidencia(biblioteca)
            dictamen = validador.evaluar(self.resultado(), None, [2], "4", "doble")
            self.assertFalse(dictamen.aceptada)
            self.assertEqual(dictamen.motivo, "sin_corrobacion_independiente")
            self.assertEqual(biblioteca.estado()["episodios"], 0)

    def test_rechaza_resultados_no_reproducibles_o_incompletos(self):
        with tempfile.TemporaryDirectory() as carpeta:
            biblioteca = Biblioteca(carpeta)
            validador = ValidadorEvidencia(biblioteca)
            no_repetible = validador.evaluar(self.resultado(False), "externa", [2], "4", "doble")
            detenido = validador.evaluar(self.resultado(True, "detenido"), "externa", [2], "4", "doble")
            self.assertEqual(no_repetible.motivo, "experimento_no_reproducible")
            self.assertEqual(detenido.motivo, "experimento_no_completado")
            self.assertEqual(biblioteca.estado()["episodios"], 0)


if __name__ == "__main__":
    unittest.main()
