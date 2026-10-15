import tempfile
import unittest

from mundo_mental.tierra import (
    REGLAS_MAXIMAS, ROLES_PREVISTOS, Razonador, RazonadorNulo, crear_tierra,
    identidad_tierra, ruta_protegida,
)


class RolDePrueba:
    def __init__(self, nombre, resultado=None):
        self.nombre = nombre
        self.necesita_modelo = False
        self._resultado = {"ok": True} if resultado is None else resultado

    def ejecutar(self, entrada):
        return self._resultado


class TestIdentidadTierra(unittest.TestCase):
    def test_identidad_valida_y_con_tres_reglas(self):
        identidad = identidad_tierra()
        identidad.validar()
        self.assertEqual(identidad.principios, REGLAS_MAXIMAS)
        self.assertEqual(len(REGLAS_MAXIMAS), 3)

    def test_no_puede_aprobar_sus_propuestas(self):
        self.assertIn("aprobar_sus_propias_propuestas", identidad_tierra().limites)


class TestRutasProtegidas(unittest.TestCase):
    def test_rutas_protegidas(self):
        for ruta in ("CONSTITUCION.md", "tests/test_x.py", "mundo_mental/autoridad.py",
                     "./tests/../CONSTITUCION.md", "mundo_mental/guardian.py",
                     "mundo_mental/Centinela.py", "../fuera.txt", "tests\\a.py"):
            with self.subTest(ruta=ruta):
                self.assertTrue(ruta_protegida(ruta))

    def test_rutas_permitidas(self):
        for ruta in ("docs/nota.md", "mundo_mental/tierra.py", "libro/ficha.json"):
            with self.subTest(ruta=ruta):
                self.assertFalse(ruta_protegida(ruta))


class TestNucleoTierra(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.nucleo = crear_tierra(self._dir.name)

    def tipos(self):
        return [r["tipo"] for r in self.nucleo.aspecto.memoria_de_si.historia()]

    def test_rol_desconocido_se_rechaza(self):
        with self.assertRaises(ValueError):
            self.nucleo.registrar_rol(RolDePrueba("inventado"))

    def test_rol_duplicado_se_rechaza(self):
        self.nucleo.registrar_rol(RolDePrueba("analista"))
        with self.assertRaises(ValueError):
            self.nucleo.registrar_rol(RolDePrueba("analista"))

    def test_ejecutar_rol_registra_en_la_memoria(self):
        self.nucleo.registrar_rol(RolDePrueba("analista"))
        self.assertEqual(self.nucleo.ejecutar_rol("analista"), {"ok": True})
        self.assertIn("rol_ejecutado", self.tipos())
        self.assertEqual(self.nucleo.roles(), ("analista",))

    def test_rol_sin_registrar_falla(self):
        with self.assertRaises(KeyError):
            self.nucleo.ejecutar_rol("lectora")

    def test_rol_que_no_devuelve_diccionario_falla(self):
        self.nucleo.registrar_rol(RolDePrueba("lectora", resultado=[1]))
        with self.assertRaises(TypeError):
            self.nucleo.ejecutar_rol("lectora")

    def test_escritura_denegada_deja_rastro(self):
        self.assertFalse(self.nucleo.autorizar_escritura("CONSTITUCION.md"))
        self.assertIn("escritura_denegada", self.tipos())
        self.assertTrue(self.nucleo.autorizar_escritura("docs/nota.md"))

    def test_razonador_nulo_cumple_el_contrato(self):
        self.assertIsInstance(RazonadorNulo(), Razonador)
        self.assertEqual(RazonadorNulo().responder("hola"), "")

    def test_roles_previstos(self):
        self.assertEqual(len(ROLES_PREVISTOS), 5)


if __name__ == "__main__":
    unittest.main()
