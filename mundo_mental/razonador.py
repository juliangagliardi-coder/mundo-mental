"""Razonador real para Tierra: cliente HTTP compatible con la API de chat tipo OpenAI.

La clave solo se lee del entorno; nunca se escribe en archivos, registros ni mensajes de error.
Si falla, devuelve texto vacío y deja el motivo en `ultimo_error`, igual que el razonador nulo.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable, Mapping

from .tierra import RazonadorNulo

URL_POR_DEFECTO = "https://api.openai.com/v1"
SISTEMA = "Eres el razonador de Tierra. Responde solo con lo que se pide, sin explicaciones adicionales."
ANFITRIONES_LOCALES = ("http://localhost", "http://127.0.0.1")


@dataclass(frozen=True)
class ConfigRazonador:
    url_base: str
    modelo: str
    clave: str
    tiempo_max: float = 60.0
    max_tokens: int = 1024
    temperatura: float = 0.2

    def __repr__(self) -> str:
        return f"ConfigRazonador(url_base={self.url_base!r}, modelo={self.modelo!r}, clave='***')"

    @classmethod
    def desde_entorno(cls, entorno: Mapping[str, str] | None = None) -> "ConfigRazonador | None":
        datos = os.environ if entorno is None else entorno
        clave = datos.get("MUNDO_MENTAL_API_KEY", "").strip()
        modelo = datos.get("MUNDO_MENTAL_MODELO", "").strip()
        url = datos.get("MUNDO_MENTAL_API_URL", URL_POR_DEFECTO).strip().rstrip("/")
        if not clave or not modelo:
            return None
        if not (url.startswith("https://") or url.startswith(ANFITRIONES_LOCALES)):
            raise ValueError("La URL del razonador debe usar https (o localhost)")
        return cls(url_base=url, modelo=modelo, clave=clave)


def _enviar_urllib(url: str, cabeceras: dict[str, str], cuerpo: bytes, tiempo_max: float) -> bytes:
    peticion = urllib.request.Request(url, data=cuerpo, headers=cabeceras, method="POST")
    with urllib.request.urlopen(peticion, timeout=tiempo_max) as respuesta:
        return respuesta.read()


class RazonadorHTTP:
    def __init__(self, config: ConfigRazonador,
                 enviar: Callable[[str, dict[str, str], bytes, float], bytes] | None = None,
                 max_llamadas: int = 50):
        self.config = config
        self._enviar = enviar or _enviar_urllib
        self.max_llamadas = int(max_llamadas)
        self.llamadas = 0
        self.ultimo_error = ""

    def responder(self, instruccion: str, contexto: str = "") -> str:
        self.ultimo_error = ""
        if self.llamadas >= self.max_llamadas:
            self.ultimo_error = "presupuesto_agotado"
            return ""
        self.llamadas += 1
        mensajes = [{"role": "system", "content": SISTEMA}]
        if contexto:
            mensajes.append({"role": "user", "content": f"Contexto:\n{contexto}"})
        mensajes.append({"role": "user", "content": instruccion})
        cuerpo = json.dumps({
            "model": self.config.modelo, "messages": mensajes,
            "max_tokens": self.config.max_tokens, "temperature": self.config.temperatura,
        }).encode("utf-8")
        cabeceras = {"Content-Type": "application/json", "Authorization": f"Bearer {self.config.clave}"}
        try:
            crudo = self._enviar(self.config.url_base + "/chat/completions", cabeceras, cuerpo,
                                 self.config.tiempo_max)
            texto = json.loads(crudo.decode("utf-8"))["choices"][0]["message"]["content"]
            if not isinstance(texto, str):
                raise ValueError("contenido no textual")
        except urllib.error.HTTPError as error:
            self.ultimo_error = f"http_{error.code}"
            return ""
        except (urllib.error.URLError, TimeoutError, OSError):
            self.ultimo_error = "red"
            return ""
        except (KeyError, IndexError, TypeError, ValueError):
            self.ultimo_error = "respuesta_invalida"
            return ""
        return texto


def crear_razonador(entorno: Mapping[str, str] | None = None, enviar=None, max_llamadas: int = 50):
    config = ConfigRazonador.desde_entorno(entorno)
    if config is None:
        return RazonadorNulo()
    return RazonadorHTTP(config, enviar, max_llamadas)
