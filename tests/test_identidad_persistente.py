import tempfile
import unittest

from mundo_mental import Aspecto, IdentidadAspecto, Impulso


class PruebasIdentidadPersistente(unittest.TestCase):
    def identidad(self, nombre="Persistente"):
        return IdentidadAspecto(
            nombre=nombre, esencia="Cuidar continuidad", proposito="Madurar sin disolverse",
            perspectiva="Recuerda cambios", principios=("reversibilidad",), voz="Serena",
            autoridad=("aprender",), limites=("borrar_historia",),
            sensibilidades={"continuidad": 1.0},
        )

    def test_reinicio_conserva_vida_interior_y_evolucion(self):
        with tempfile.TemporaryDirectory() as carpeta:
            primero = Aspecto(self.identidad(), carpeta)
            primero.sentir("conexion", 0.9, "cooperación útil")
            compromiso = primero.comprometerse("Escuchar", "comprender antes de actuar", 0.8)
            propuesta = primero.proponer_evolucion("apertura", 0.75, "funcionó", ("ensayo-1",))
            primero.ensayar_evolucion(propuesta.id)
            primero.consolidar_evolucion(propuesta.id, "mejoró la colaboración")

            segundo = Aspecto(self.identidad(), carpeta)
            self.assertEqual(segundo.necesidades["conexion"], 0.9)
            self.assertEqual(segundo.disposiciones["apertura"], 0.75)
            self.assertEqual(segundo.compromisos[0].id, compromiso.id)
            self.assertEqual(segundo.evoluciones[0].estado, "consolidada")

    def test_atencion_es_explicable_y_depende_de_identidad(self):
        with tempfile.TemporaryDirectory() as carpeta:
            atento = Aspecto(self.identidad("Atento"), carpeta)
            neutro = Aspecto(IdentidadAspecto(
                nombre="Neutro", esencia="Ordenar", proposito="Mantener forma",
                perspectiva="Observa estructura", principios=("claridad",), voz="Breve",
            ), carpeta)
            impulso = Impulso("continuidad", {}, "prueba", importancia=0.6)
            valor_atento = atento.evaluar_impulso(impulso)
            valor_neutro = neutro.evaluar_impulso(impulso)
            self.assertGreater(valor_atento.interes, valor_neutro.interes)
            self.assertIn("sensibilidad=1.00", valor_atento.razones)

    def test_nucleo_e_irreversibilidad_quedan_fuera_de_evolucion_ordinaria(self):
        with tempfile.TemporaryDirectory() as carpeta:
            aspecto = Aspecto(self.identidad(), carpeta)
            with self.assertRaises(ValueError):
                aspecto.proponer_evolucion("perspectiva", "otra", "optimización")
            with self.assertRaises(ValueError):
                aspecto.proponer_evolucion("apertura", 1.0, "salto", reversible=False)


if __name__ == "__main__":
    unittest.main()
