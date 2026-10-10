import tempfile
import unittest

from mundo_mental import Aspecto, IdentidadAspecto, Impulso, SistemaNervioso


def crear_aspecto(nombre, raiz, perspectiva="Busca conocimiento"):
    return Aspecto(IdentidadAspecto(
        nombre=nombre, esencia="Comprender", proposito="Aprender y colaborar",
        perspectiva=perspectiva, principios=("honestidad",), voz="Clara",
        autoridad=("atender",), limites=("dominar",),
    ), raiz)


class PruebasSistemaNervioso(unittest.TestCase):
    def test_difunde_sin_procesar_hasta_el_latido(self):
        with tempfile.TemporaryDirectory() as carpeta:
            sistema = SistemaNervioso()
            uno = crear_aspecto("Uno", carpeta)
            dos = crear_aspecto("Dos", carpeta)
            sistema.conectar(uno)
            sistema.conectar(dos)
            resultado = sistema.publicar(Impulso("hallazgo", {"x": 1}, "prueba", importancia=0.9))
            self.assertEqual(resultado["encolados"], 2)
            self.assertEqual(uno.atendidos + uno.ignorados, 0)
            reacciones = sistema.latir()
            self.assertEqual(len(reacciones), 2)
            self.assertEqual(sistema.estadisticas.entregados, 2)

    def test_deduplica_y_respeta_destino(self):
        with tempfile.TemporaryDirectory() as carpeta:
            sistema = SistemaNervioso()
            uno = crear_aspecto("Uno", carpeta)
            dos = crear_aspecto("Dos", carpeta)
            sistema.conectar(uno)
            sistema.conectar(dos)
            impulso = Impulso("mensaje", "hola", "prueba", destino="Uno")
            self.assertEqual(sistema.publicar(impulso)["encolados"], 1)
            self.assertEqual(sistema.publicar(impulso)["encolados"], 0)
            self.assertEqual(sistema.estadisticas.duplicados, 1)

    def test_saturacion_conserva_lo_urgente(self):
        with tempfile.TemporaryDirectory() as carpeta:
            sistema = SistemaNervioso(capacidad_por_aspecto=2)
            aspecto = crear_aspecto("Uno", carpeta)
            sistema.conectar(aspecto)
            sistema.publicar(Impulso("ruido", 1, "prueba", urgencia=0))
            sistema.publicar(Impulso("rutina", 2, "prueba", urgencia=1))
            critico = Impulso("cambio", 3, "prueba", urgencia=3, importancia=1.0)
            sistema.publicar(critico)
            reacciones = sistema.latir()
            self.assertEqual(len(reacciones), 2)
            self.assertEqual(reacciones[0].impulso_id, critico.id)
            self.assertEqual(sistema.estadisticas.descartados_saturacion, 1)

    def test_reflejo_no_espera_al_pensamiento(self):
        sistema = SistemaNervioso()
        vistos = []
        sistema.registrar_reflejo("dolor", lambda impulso: vistos.append(impulso.id))
        impulso = Impulso("dolor", "detener zona", "centinela", urgencia=3)
        resultado = sistema.publicar(impulso)
        self.assertEqual(resultado["reflejos"], 1)
        self.assertEqual(vistos, [impulso.id])


if __name__ == "__main__":
    unittest.main()
