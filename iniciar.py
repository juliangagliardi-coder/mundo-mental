"""Demostración ejecutable de un ciclo integrado de Mundo Mental."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Callable

from mundo_mental import Alarma, Biblioteca, Curiosidad, Guardian, ValidadorEvidencia

ObservadorCiclo = Callable[[str, str, dict[str, Any]], None]


def _avisar(
    observador: ObservadorCiclo | None,
    actor: str,
    accion: str,
    detalle: str,
    **datos: Any,
) -> None:
    """Emite telemetría opcional sin cambiar el resultado del ciclo."""
    if observador is None:
        return
    observador(actor, accion, {"detalle": detalle, **datos})


def ejecutar_ciclo(
    raiz: str | Path,
    observador: ObservadorCiclo | None = None,
) -> dict[str, object]:
    """Ejecuta el ciclo real y emite eventos para interfaces observadoras."""
    biblioteca = Biblioteca(raiz)
    guardian = Guardian(raiz)
    curiosidad = Curiosidad(raiz, guardian.buzon)

    _avisar(
        observador,
        "Curiosidad",
        "observar",
        "Examina los conceptos disponibles y busca vacíos de conocimiento.",
    )
    preguntas = curiosidad.observar_conceptos({
        "patrones": {"fiabilidad": 0.55, "ejemplos_unicos": 1}
    })
    pregunta = preguntas[0]
    _avisar(
        observador,
        "Curiosidad",
        "preguntar",
        pregunta.texto,
        pregunta_id=pregunta.id,
    )

    resultado = curiosidad.experimentar(
        pregunta,
        "doblar_valor",
        {"valor": 3},
        lambda datos: datos["valor"] * 2,
        supervisar=lambda *_: True,
    )
    _avisar(
        observador,
        "Curiosidad",
        "experimentar",
        f"Experimento {resultado.nombre}: {resultado.estado}; salida={resultado.salida}.",
        reproducible=resultado.reproducible,
    )

    validador = ValidadorEvidencia(biblioteca)
    dictamen = validador.evaluar(
        resultado,
        corroboracion="repeticion_independiente",
        entrada=[3],
        respuesta=str(resultado.salida),
        esperado="doble",
    )
    _avisar(
        observador,
        "Biblioteca",
        "validar_y_recordar",
        f"Dictamen real: {dictamen.motivo}; recuerdo={dictamen.recuerdo_id}.",
        aceptada=dictamen.aceptada,
    )

    guardian.buzon.enviar(
        Alarma("demostracion", "verificacion_de_recuperacion", "laboratorio", "alta")
    )
    _avisar(
        observador,
        "Observador",
        "recibir_alarma",
        "Recibe una alarma real de verificación en el laboratorio.",
    )
    incidente = guardian.despertar()[0]
    _avisar(
        observador,
        "Observador",
        "aislar",
        f"Aísla {incidente['zona']} para comprobar la recuperación.",
        alarma_id=incidente["alarma_id"],
    )
    reanudado = guardian.cerrar_y_reanudar(
        incidente["alarma_id"],
        "La demostración verificó una ejecución aislada y reproducible.",
        verificacion_aislada=True,
        verificacion_reproducible=resultado.reproducible,
    )
    _avisar(
        observador,
        "Observador",
        "reanudar",
        f"Cierra el incidente y reanuda la zona: {reanudado}.",
    )

    estado_biblioteca = biblioteca.estado()
    _avisar(
        observador,
        "Biblioteca",
        "estado",
        f"Biblioteca termina con {estado_biblioteca['episodios']} episodio validado.",
        estado=estado_biblioteca,
    )
    return {
        "pregunta": pregunta,
        "resultado": resultado,
        "dictamen": dictamen,
        "incidente": guardian.incidentes[0],
        "reanudado": reanudado,
        "estado_biblioteca": estado_biblioteca,
    }


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="mundo-mental-demo-") as carpeta:
        ciclo = ejecutar_ciclo(carpeta)
        pregunta = ciclo["pregunta"]
        resultado = ciclo["resultado"]
        dictamen = ciclo["dictamen"]
        incidente = ciclo["incidente"]

        print("Mundo Mental: ciclo integrado")
        print(f"\nPrimera pregunta de Curiosidad:\n- {pregunta.texto}")
        print(
            f"\nLaboratorio:\n- {resultado.nombre}: {resultado.estado}; "
            f"reproducible={resultado.reproducible}; salida={resultado.salida}"
        )
        print(f"\nEvidencia:\n- {dictamen.motivo}; recuerdo={dictamen.recuerdo_id}")
        print(
            f"\nObservación:\n- zona={incidente['zona']}; "
            f"estado={incidente['estado']}; reanudada={ciclo['reanudado']}"
        )
        print(
            f"\nBiblioteca:\n- episodios="
            f"{ciclo['estado_biblioteca']['episodios']}"
        )


if __name__ == "__main__":
    main()
