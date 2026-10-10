import tempfile
import unittest

from mundo_mental import Aspecto, IdentidadAspecto


class PruebasIdentidad(unittest.TestCase):
    def identidad(self):
        return IdentidadAspecto(
            nombre="Prueba", esencia="Explorar", proposito="Comprobar continuidad",
            perspectiva="Busca diferencias", principios=("honestidad",),
            voz="Clara", autoridad=("observar",), limites=("borrar",),
        )

    def test_identidad_valida_y_recuerda_su_historia(self):
        with tempfile.TemporaryDirectory() as carpeta:
            aspecto = Aspecto(self.identidad(), carpeta)
            aspecto.narrar("nacimiento", "Reconocí mi propósito")
            aspecto.cambiar_estado("atento", "Apareció una diferencia")
            self.assertEqual(aspecto.ficha()["recuerdos_autobiograficos"], 2)
            self.assertEqual(aspecto.estado_interno, "atento")

    def test_rechaza_identidad_contradictoria(self):
        identidad = IdentidadAspecto(
            nombre="X", esencia="X", proposito="X", perspectiva="X",
            principios=("X",), voz="X", autoridad=("borrar",), limites=("borrar",),
        )
        with self.assertRaises(ValueError):
            identidad.validar()

    def test_necesidades_y_compromisos_forman_vida_interior(self):
        with tempfile.TemporaryDirectory() as carpeta:
            aspecto = Aspecto(self.identidad(), carpeta)
            aspecto.sentir("conexion", 0.9, "necesita colaborar")
            compromiso = aspecto.comprometerse("Escuchar antes de concluir", "evitar prejuicios", 0.8)
            ficha = aspecto.ficha()
            self.assertEqual(ficha["necesidades"]["conexion"], 0.9)
            self.assertEqual(ficha["compromisos_activos"], 1)
            self.assertTrue(compromiso.activo)

    def test_evolucion_se_ensaya_consolida_y_revierte_sin_tocar_nucleo(self):
        with tempfile.TemporaryDirectory() as carpeta:
            aspecto = Aspecto(self.identidad(), carpeta)
            propuesta = aspecto.proponer_evolucion(
                "apertura", 0.8, "la colaboración fue útil", ("experimento-1",)
            )
            ensayo = aspecto.ensayar_evolucion(propuesta.id)
            self.assertEqual(ensayo["antes"], 0.5)
            self.assertEqual(aspecto.disposiciones["apertura"], 0.5)
            aspecto.consolidar_evolucion(propuesta.id, "mejoró la cooperación")
            self.assertEqual(aspecto.disposiciones["apertura"], 0.8)
            aspecto.revertir_evolucion(propuesta.id, "apareció un efecto adverso")
            self.assertEqual(aspecto.disposiciones["apertura"], 0.5)
            self.assertEqual(aspecto.identidad.esencia, "Explorar")

    def test_nucleo_no_cambia_por_evolucion_ordinaria(self):
        with tempfile.TemporaryDirectory() as carpeta:
            aspecto = Aspecto(self.identidad(), carpeta)
            with self.assertRaises(ValueError):
                aspecto.proponer_evolucion("principios", (), "sería más rápido")


if __name__ == "__main__":
    unittest.main()
