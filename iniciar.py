"""Demostración ejecutable de un ciclo integrado de Mundo Mental."""

from __future__ import annotations

import tempfile
from pathlib import Path

from mundo_mental import Alarma, Biblioteca, Curiosidad, Guardian, ValidadorEvidencia
from mundo_mental.autoridad import Autoridad
from mundo_mental.observacion import Centinela


def ejecutar_ciclo(raiz: str | Path) -> dict[str, object]:
    """Ejecuta un ciclo completo sin promover evidencia ni reanudar sin verificaciones."""
    biblioteca = Biblioteca(raiz)
    guardian = Guardian(raiz)
    curiosidad = Curiosidad(raiz, guardian.buzon)
    autoridad = Autoridad(raiz, Centinela(guardian.buzon), guardian)

    preguntas = curiosidad.observar_conceptos({
        "patrones": {"fiabilidad": 0.55, "ejemplos_unicos": 1}
    })
    pregunta = preguntas[0]
    resultado = curiosidad.experimentar(
        pregunta,
        "doblar_valor",
        {"valor": 3},
        lambda datos: datos["valor"] * 2,
        supervisar=lambda *_: True,
    )
    validador = ValidadorEvidencia(biblioteca)
    experiencias = biblioteca.experiencias
    previo = experiencias.read_text(encoding="utf-8") if experiencias.exists() else None
    dictamenes: list[object] = []

    def validar() -> None:
        dictamenes.append(validador.evaluar(
            resultado,
            corroboracion="repeticion_independiente",
            entrada=[3],
            respuesta=str(resultado.salida),
            esperado="doble",
        ))

    def deshacer() -> None:
        if previo is None:
            experiencias.unlink(missing_ok=True)
        else:
            experiencias.write_text(previo, encoding="utf-8")

    decision = autoridad.actuar("curiosidad", "biblioteca", "validar_evidencia", validar, deshacer)
    dictamen = dictamenes[0] if dictamenes else None

    guardian.buzon.enviar(Alarma("demostracion", "verificacion_de_recuperacion", "laboratorio", "alta"))
    incidente = guardian.despertar()[0]
    reanudado = guardian.cerrar_y_reanudar(
        incidente["alarma_id"],
        "La demostración verificó una ejecución aislada y reproducible.",
        verificacion_aislada=True,
        verificacion_reproducible=resultado.reproducible,
    )
    return {
        "pregunta": pregunta,
        "resultado": resultado,
        "dictamen": dictamen,
        "decision": decision,
        "incidente": guardian.incidentes[0],
        "reanudado": reanudado,
        "estado_biblioteca": biblioteca.estado(),
    }


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="mundo-mental-demo-") as carpeta:
        ciclo = ejecutar_ciclo(carpeta)
        pregunta = ciclo["pregunta"]
        resultado = ciclo["resultado"]
        dictamen = ciclo["dictamen"]
        decision = ciclo["decision"]
        incidente = ciclo["incidente"]

        print("Mundo Mental: ciclo integrado")
        print(f"\nPrimera pregunta de Curiosidad:\n- {pregunta.texto}")
        print(f"\nLaboratorio:\n- {resultado.nombre}: {resultado.estado}; reproducible={resultado.reproducible}; salida={resultado.salida}")
        if dictamen is None:
            print(f"\nEvidencia:\n- no validada; autoridad={decision['resultado']}")
        else:
            print(f"\nEvidencia:\n- {dictamen.motivo}; recuerdo={dictamen.recuerdo_id}; autoridad={decision['resultado']}")
        print(f"\nObservación:\n- zona={incidente['zona']}; estado={incidente['estado']}; reanudada={ciclo['reanudado']}")
        print(f"\nBiblioteca:\n- episodios={ciclo['estado_biblioteca']['episodios']}")


if __name__ == "__main__":
    main()
