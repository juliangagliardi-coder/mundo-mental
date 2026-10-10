"""Demostración de Biblioteca 0.2 y del primer Corazón."""

from mundo_mental import Biblioteca, Corazon


def mostrar(resultado):
    estado = "ACEPTADA" if resultado["aceptada"] else "RECHAZADA"
    print(f"\nObra {estado}: {resultado['obra_id']}")
    print(f"Antes: {resultado['precision_antes']:.0%}")
    print(f"Candidata: {resultado['precision_candidata']:.0%}")
    print(f"Retención protegida: {resultado['retencion']:.0%}")
    print(f"Obras anteriores consultadas: {resultado['antecedentes_consultados']}")
    print(f"Motivo: {resultado['motivo']}")


def main():
    biblioteca = Biblioteca(".mente")
    corazon = Corazon(biblioteca)

    fundamentos = [
        ([0, 0, 0, 0], "igual"),
        ([1, 1, 1, 1], "igual"),
        ([0, 1, 0, 1], "alternancia"),
        ([1, 0, 1, 0], "alternancia"),
    ]
    mostrar(corazon.latir("patrones", fundamentos, fundamentos))

    ampliacion = [
        ([0, 1, 1, 0], "simetria"),
        ([1, 0, 0, 1], "simetria"),
    ]
    mostrar(corazon.latir("patrones", ampliacion, ampliacion, protegidos=fundamentos))

    recuerdos = biblioteca.buscar_similares([0, 1, 0, 1], limite=3)
    print("\nLa Biblioteca recuerda y explica:")
    for recuerdo in recuerdos:
        print(f"- {recuerdo['entrada']} -> {recuerdo['esperado']}: {recuerdo['explicacion']}")

    print("\nConceptos consolidados:")
    for nombre, concepto in biblioteca.consolidar().items():
        print(f"- {nombre}: {concepto['ejemplos_unicos']} ejemplos, fiabilidad {concepto['fiabilidad']:.0%}")

    print("\nEstado de la Biblioteca:")
    for clave, valor in biblioteca.estado().items():
        print(f"- {clave}: {valor}")

    print("\nBiblioteca 0.2 completó su primer ciclo. La memoria vive en .mente/")


if __name__ == "__main__":
    main()
