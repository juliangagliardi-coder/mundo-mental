import tempfile
import unittest
from pathlib import Path

from mundo_mental import Aspecto, IdentidadAspecto, TejidoMental


class Eco(Aspecto):
    IDENTIDAD = IdentidadAspecto(
        nombre="Eco",
        esencia="Escuchar sin apropiarse",
        proposito="Confirmar impulsos",
        perspectiva="Atiende señales explícitas",
        principios=("trazabilidad",),
        voz="Breve y verificable",
    )

    def __init__(self, raiz):
        super().__init__(self.IDENTIDAD, raiz)
        self.recibidos = []

    def recibir_impulso(self, impulso):
        self.recibidos.append(impulso)
        return {"atendido": True, "interes": 1.0, "detalle": "confirmado"}


class PruebasTejido(unittest.TestCase):
    def test_origen_debe_pertenecer_al_tejido(self):
        tejido = TejidoMental()
        with self.assertRaisesRegex(KeyError, "no pertenece"):
            tejido.emitir("Intruso", "dato", 1)

    def test_incorpora_emite_responde_y_retira(self):
        with tempfile.TemporaryDirectory() as temporal:
            eco = Eco(Path(temporal))
            tejido = TejidoMental()
            tejido.incorporar(eco, temas=("prueba",))

            causa = tejido.emitir("Eco", "inicio", 1, temas=("prueba",))
            reacciones = tejido.latir()
            respuesta = tejido.responder("Eco", causa, "confirmacion", 2, destino="Eco")
            tejido.latir()

            self.assertTrue(any(reaccion.atendido for reaccion in reacciones))
            self.assertEqual(respuesta.causa, causa.id)
            self.assertEqual(respuesta.correlacion, causa.id)
            self.assertEqual(tejido.estado()["ciclo"], 2)
            tejido.retirar("Eco")
            self.assertNotIn("Eco", tejido.aspectos)

    def test_rechaza_dos_aspectos_con_el_mismo_nombre(self):
        with tempfile.TemporaryDirectory() as temporal:
            tejido = TejidoMental()
            tejido.incorporar(Eco(Path(temporal) / "uno"))
            with self.assertRaisesRegex(ValueError, "otro Aspecto"):
                tejido.incorporar(Eco(Path(temporal) / "dos"))


if __name__ == "__main__":
    unittest.main()
