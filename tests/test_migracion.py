import tempfile
import unittest
from pathlib import Path

from mundo_mental import Biblioteca, BibliotecaSQLite, migrar_biblioteca


class PruebasMigracion(unittest.TestCase):
    def preparar(self, raiz: Path) -> Biblioteca:
        biblioteca = Biblioteca(raiz)
        biblioteca.recordar([0, 1], "alternancia", "alternancia", True,
                            {"confianza": 0.9}, protegido=True)
        biblioteca.recordar([1, 0], "alternancia", "alternancia", True,
                            {"confianza": 0.8})
        biblioteca.recordar([0, 1], "fallo", "alternancia", False,
                            {"confianza": 0.7})
        biblioteca.consolidar()
        biblioteca.guardar_habilidad("patrones", {"version": 1, "reglas": ["alternancia"]})
        biblioteca.registrar_obra({"habilidad": "patrones", "tipo": "ampliacion", "aceptada": True})
        return biblioteca

    def test_migra_sin_modificar_origen_y_conserva_identidades(self):
        with tempfile.TemporaryDirectory() as carpeta:
            base = Path(carpeta)
            origen = base / "origen"
            destino = base / "destino"
            fuente = self.preparar(origen)
            antes = fuente.experiencias.read_bytes()
            ids_antes = {x["id"] for x in fuente._leer_jsonl(fuente.experiencias)}

            informe = migrar_biblioteca(origen, destino)
            nueva = BibliotecaSQLite(destino)

            self.assertTrue(informe.verificada)
            self.assertEqual(antes, fuente.experiencias.read_bytes())
            self.assertEqual(ids_antes, {x["id"] for x in nueva.exportar_episodios()})
            self.assertEqual(fuente.cargar_habilidad("patrones"), nueva.cargar_habilidad("patrones"))
            self.assertEqual(fuente.cargar_conceptos(), nueva.cargar_conceptos())
            self.assertEqual(len(fuente.historial_obras()), len(nueva.historial_obras()))

    def test_es_idempotente(self):
        with tempfile.TemporaryDirectory() as carpeta:
            base = Path(carpeta)
            self.preparar(base / "origen")
            primero = migrar_biblioteca(base / "origen", base / "destino")
            segundo = migrar_biblioteca(base / "origen", base / "destino")
            self.assertEqual(primero.huella_destino, segundo.huella_destino)
            self.assertEqual(segundo.episodios_destino, 3)

    def test_depuracion_equivalente(self):
        with tempfile.TemporaryDirectory() as carpeta:
            base = Path(carpeta)
            jsonl = self.preparar(base / "jsonl")
            migrar_biblioteca(base / "jsonl", base / "sqlite")
            sqlite = BibliotecaSQLite(base / "sqlite")
            resultado_jsonl = jsonl.depurar(max_recuerdos=2)
            resultado_sqlite = sqlite.depurar(max_recuerdos=2)
            self.assertEqual(resultado_jsonl, resultado_sqlite)
            self.assertEqual(jsonl.estado()["recuerdos_protegidos"], sqlite.estado()["recuerdos_protegidos"])


if __name__ == "__main__":
    unittest.main()
