import tempfile
import unittest

from mundo_mental import Aspecto, IdentidadAspecto


class PruebasIdentidad(unittest.TestCase):
    def test_identidad_valida_y_recuerda_su_historia(self):
        with tempfile.TemporaryDirectory() as carpeta:
            identidad = IdentidadAspecto(
                nombre="Prueba", esencia="Explorar", proposito="Comprobar continuidad",
                perspectiva="Busca diferencias", principios=("honestidad",),
                voz="Clara", autoridad=("observar",), limites=("borrar",),
            )
            aspecto = Aspecto(identidad, carpeta)
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


if __name__ == "__main__":
    unittest.main()
