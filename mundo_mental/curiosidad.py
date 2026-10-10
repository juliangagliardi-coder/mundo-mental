"""Curiosidad 0.2: preguntas, laboratorio aislado y supervisión cooperativa."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from .aspecto import Aspecto, IdentidadAspecto
from .observacion import Alarma, BuzonAlarmas


@dataclass(frozen=True)
class Pregunta:
    texto: str
    origen: str
    prioridad: float
    evidencias: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class ResultadoExperimento:
    pregunta_id: str
    nombre: str
    entrada: dict[str, Any]
    salida: Any
    reproducible: bool
    estado: str
    motivo: str = ""


class Curiosidad(Aspecto):
    IDENTIDAD = IdentidadAspecto(
        nombre="Curiosidad",
        esencia="Libertad investigadora dentro de la Biblioteca",
        proposito="Convertir vacíos reducibles de conocimiento en preguntas y experimentos",
        perspectiva="Busca incertidumbre fértil, contradicciones y conexiones ausentes",
        principios=("preguntar_antes_de_afirmar", "aprender_del_fracaso", "distinguir_imaginado"),
        voz="Inquisitiva, provisional y honesta sobre la incertidumbre",
        autoridad=("formular_preguntas", "priorizar_investigaciones", "experimentar_en_laboratorio"),
        limites=("promoverse_a_si_misma", "alterar_observacion", "confundir_sueno_con_evidencia"),
        tensiones=("libertad_y_disciplina", "novedad_y_progreso"),
        relaciones={"biblioteca": "lee sus vacíos", "observacion": "puede pedir protección"},
    )

    def __init__(self, raiz: str | Path = ".mente", buzon: BuzonAlarmas | None = None):
        super().__init__(self.IDENTIDAD, raiz)
        self.preguntas: list[Pregunta] = []
        self.buzon = buzon
        self.laboratorio: list[ResultadoExperimento] = []

    def observar_conceptos(self, conceptos: dict[str, dict[str, Any]]) -> list[Pregunta]:
        nuevas = []
        for nombre, concepto in conceptos.items():
            fiabilidad = float(concepto.get("fiabilidad", 0.0))
            ejemplos = int(concepto.get("ejemplos_unicos", 0))
            if fiabilidad < 0.8:
                pregunta = Pregunta(
                    f"¿Qué casos contradicen o debilitan el concepto {nombre}?",
                    "baja_fiabilidad",
                    min(1.0, 1.0 - fiabilidad + 0.2),
                    (nombre,),
                )
            elif ejemplos < 3:
                pregunta = Pregunta(
                    f"¿Qué ejemplo nuevo distinguiría mejor el concepto {nombre}?",
                    "pocos_ejemplos",
                    0.6,
                    (nombre,),
                )
            else:
                continue
            if all(x.texto != pregunta.texto for x in self.preguntas):
                self.preguntas.append(pregunta)
                nuevas.append(pregunta)
                self.narrar("pregunta", pregunta.texto, origen=pregunta.origen, prioridad=pregunta.prioridad)
        self.preguntas.sort(key=lambda x: x.prioridad, reverse=True)
        return nuevas

    def siguiente_pregunta(self) -> Pregunta | None:
        return self.preguntas.pop(0) if self.preguntas else None

    def experimentar(
        self,
        pregunta: Pregunta,
        nombre: str,
        entrada: dict[str, Any],
        experimento: Callable[[dict[str, Any]], Any],
        supervisar: Callable[[Pregunta, str, dict[str, Any]], bool] | None = None,
    ) -> ResultadoExperimento:
        """Ejecuta una hipótesis en el laboratorio, nunca en la memoria estable.

        El supervisor recibe la pregunta y la entrada antes de la ejecución. Si la
        rechaza, se deja un registro detenido; la función del experimento no corre.
        """
        if supervisar is not None and not supervisar(pregunta, nombre, dict(entrada)):
            resultado = ResultadoExperimento(
                pregunta.id, nombre, dict(entrada), None, False, "detenido", "supervision"
            )
            self.laboratorio.append(resultado)
            self.narrar("experimento_detenido", nombre, pregunta_id=pregunta.id)
            return resultado

        copia_entrada = dict(entrada)
        try:
            salida = experimento(copia_entrada)
            reproducible = salida == experimento(dict(entrada))
            resultado = ResultadoExperimento(
                pregunta.id, nombre, dict(entrada), salida, reproducible, "completado"
            )
        except Exception as error:
            resultado = ResultadoExperimento(
                pregunta.id, nombre, dict(entrada), None, False, "fallido", type(error).__name__
            )
        self.laboratorio.append(resultado)
        self.narrar(
            "experimento", nombre, pregunta_id=pregunta.id,
            estado=resultado.estado, reproducible=resultado.reproducible,
        )
        return resultado

    def resultados_laboratorio(self) -> tuple[ResultadoExperimento, ...]:
        return tuple(self.laboratorio)

    def pedir_ayuda(self, motivo: str, zona: str, gravedad: str = "media") -> str:
        if self.buzon is None:
            raise RuntimeError("Curiosidad no tiene una Calle de alarma conectada")
        self.cambiar_estado("cauta", motivo)
        return self.buzon.enviar(Alarma(self.nombre.lower(), motivo, zona, gravedad))
