"""Primer cimiento ejecutable del Mundo Mental."""

from mundo_mental import Biblioteca, Corazon


def mostrar(resultado):
    estado = "ACEPTADA" if resultado["aceptada"] else "RECHAZADA"
    print(f"\nObra {estado}: {resultado['obra_id']}")
    print(f"Antes: {resultado['precision_antes']:.0%}")
    print(f"Candidata: {resultado['precision_candidata']:.0%}")
    print(f"Retención protegida: {resultado['retencion']:.0%}")
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

    conocimiento_protegido = fundamentos
    ampliacion = [
        ([0, 1, 1, 0], "simetria"),
        ([1, 0, 0, 1], "simetria"),
    ]
    mostrar(
        corazon.latir(
            "patrones",
            ampliacion,
            ampliacion,
            protegidos=conocimiento_protegido,
        )
    )

    recuerdo = biblioteca.buscar_similares([0, 1, 0, 1], limite=3)
    print("\nLa Biblioteca recuerda:")
    for item in recuerdo:
        print(f"- {item['entrada']} -> {item['esperado']} (similitud {item['similitud']:.0%})")

    print("\nPrimer latido completado. La historia quedó guardada en .mente/")


if __name__ == "__main__":
    main()
