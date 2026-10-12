"""Monitor gráfico del ciclo real de Mundo Mental.

Ejecutar desde la raíz del repositorio: python mundo.py
"""

from __future__ import annotations

import math
import queue
import tempfile
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from iniciar import ejecutar_ciclo
from mundo_mental.mundo_virtual import MundoVirtual


FONDO = "#101523"
PANEL = "#172238"
TEXTO = "#f5e6bd"
SUAVE = "#aebbd1"


class VentanaMundo:
    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        self.mundo = MundoVirtual()
        self.zoom = 0.72
        self.dx = 70
        self.dy = 70
        self.fase = 0
        self.arrastre: tuple[int, int] | None = None
        self.mensajes: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.detener = threading.Event()
        self.hilo: threading.Thread | None = None
        self.continuo = False

        raiz.title("Mundo Mental · Trabajo real visible")
        raiz.geometry("1240x780")
        raiz.minsize(980, 640)
        raiz.configure(bg=FONDO)
        raiz.protocol("WM_DELETE_WINDOW", self.cerrar)
        self._construir_interfaz()
        self.actualizar_panel()
        self.raiz.after(80, self.procesar_mensajes)
        self.raiz.after(170, self.animar)

    def _construir_interfaz(self) -> None:
        barra = tk.Frame(self.raiz, bg=FONDO)
        barra.pack(fill="x", padx=20, pady=(16, 8))
        tk.Label(
            barra, text="MUNDO MENTAL", font=("Georgia", 21, "bold"),
            fg=TEXTO, bg=FONDO,
        ).pack(side="left")
        tk.Label(
            barra, text="Monitor del ciclo integrado real", font=("Helvetica", 10),
            fg=SUAVE, bg=FONDO,
        ).pack(side="left", padx=14)
        ttk.Button(barra, text="Trabajar continuamente", command=self.iniciar).pack(side="right")
        ttk.Button(barra, text="Detener", command=self.pausar).pack(side="right", padx=6)
        ttk.Button(barra, text="Ejecutar un ciclo", command=self.un_ciclo).pack(side="right")

        cuerpo = tk.PanedWindow(
            self.raiz, orient="horizontal", sashwidth=6, bg=FONDO, bd=0,
        )
        cuerpo.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        mapa = tk.Frame(cuerpo, bg=PANEL)
        panel = tk.Frame(cuerpo, bg=PANEL, width=360)
        cuerpo.add(mapa, stretch="always")
        cuerpo.add(panel, minsize=310)

        self.canvas = tk.Canvas(mapa, bg=PANEL, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=8)
        self.canvas.bind("<ButtonPress-3>", self.iniciar_arrastre)
        self.canvas.bind("<B3-Motion>", self.arrastrar)
        self.canvas.bind("<MouseWheel>", self.zoom_raton)
        self.canvas.bind("<Button-4>", lambda _: self.cambiar_zoom(1.1))
        self.canvas.bind("<Button-5>", lambda _: self.cambiar_zoom(0.9))
        self.canvas.bind("<Configure>", lambda _: self.dibujar())

        tk.Label(
            panel, text="Ejecución real", font=("Georgia", 14, "bold"),
            fg=TEXTO, bg=PANEL,
        ).pack(anchor="w", padx=16, pady=(16, 4))
        self.estado = tk.Label(
            panel, text="DETENIDO", justify="left", anchor="w", wraplength=320,
            fg="#9edec5", bg=PANEL, font=("Helvetica", 10, "bold"),
        )
        self.estado.pack(fill="x", padx=16, pady=(0, 8))
        self.cronica = tk.Listbox(
            panel, bg="#101827", fg="#e7edf9", selectbackground="#405d8f",
            borderwidth=0, highlightthickness=0, font=("Helvetica", 9),
        )
        self.cronica.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self.cronica.bind("<<ListboxSelect>>", self.seleccionar_evento)
        self.ficha = tk.Label(
            panel,
            text="Pulsa «Ejecutar un ciclo» para ver trabajar al sistema real.",
            justify="left", anchor="nw", wraplength=315,
            fg=SUAVE, bg=PANEL, font=("Helvetica", 10),
        )
        self.ficha.pack(fill="x", padx=16, pady=(0, 16))

    def pantalla(self, x: float, y: float) -> tuple[float, float]:
        return x * self.zoom + self.dx, y * self.zoom + self.dy

    def iniciar_arrastre(self, evento: tk.Event) -> None:
        self.arrastre = (evento.x, evento.y)

    def arrastrar(self, evento: tk.Event) -> None:
        if self.arrastre is None:
            return
        self.dx += evento.x - self.arrastre[0]
        self.dy += evento.y - self.arrastre[1]
        self.arrastre = (evento.x, evento.y)
        self.dibujar()

    def zoom_raton(self, evento: tk.Event) -> None:
        self.cambiar_zoom(1.1 if evento.delta > 0 else 0.9)

    def cambiar_zoom(self, factor: float) -> None:
        self.zoom = max(0.38, min(1.45, self.zoom * factor))
        self.dibujar()

    @staticmethod
    def _plano(puntos: list[tuple[float, float]]) -> list[float]:
        return [valor for punto in puntos for valor in punto]

    def dibujar_terreno(self) -> None:
        c = self.canvas
        ancho = max(c.winfo_width(), 1)
        alto = max(c.winfo_height(), 1)
        c.create_rectangle(0, 0, ancho, alto, fill="#315a43", outline="")
        for x in range(-100, self.mundo.ANCHO + 120, 120):
            for y in range(20, self.mundo.ALTO, 100):
                sx, sy = self.pantalla(x + (y // 80 % 2) * 25, y)
                if -20 < sx < ancho + 20 and -20 < sy < alto + 20:
                    c.create_oval(
                        sx - 13, sy - 16, sx + 13, sy + 15,
                        fill="#1f4937", outline="#163a2d",
                    )
        rio = [
            self.pantalla(1210 + 50 * math.sin(y / 130), y)
            for y in range(0, self.mundo.ALTO + 50, 50)
        ]
        rio += [
            self.pantalla(1320 + 50 * math.sin(y / 130), y)
            for y in range(self.mundo.ALTO, -50, -50)
        ]
        c.create_polygon(
            *self._plano(rio), fill="#4b9dc4", outline="#83d0e9", width=2,
        )
        camino = [self.pantalla(x, y) for x, y in self.mundo.CAMINO]
        c.create_line(
            *self._plano(camino), fill="#342b27", width=33,
            capstyle="round", joinstyle="round",
        )
        c.create_line(
            *self._plano(camino), fill="#aa946e", width=26,
            capstyle="round", joinstyle="round",
        )

    def dibujar_casa(self, x: int, y: int, nombre: str, color: str) -> None:
        c = self.canvas
        sx, sy = self.pantalla(x, y)
        z = self.zoom
        c.create_rectangle(
            sx - 52 * z, sy - 25 * z, sx + 52 * z, sy + 45 * z,
            fill=color, outline="#392e2a", width=2,
        )
        c.create_polygon(
            sx - 63 * z, sy - 25 * z, sx, sy - 72 * z,
            sx + 63 * z, sy - 25 * z,
            fill="#704736", outline="#392e2a", width=2,
        )
        c.create_text(
            sx, sy + 59 * z, text=nombre, fill=TEXTO,
            font=("Georgia", max(8, int(10 * z)), "bold"),
        )

    def dibujar_puerta(self) -> None:
        c = self.canvas
        x, y = self.pantalla(1450, 650)
        z = self.zoom
        c.create_rectangle(
            x - 31 * z, y - 55 * z, x + 31 * z, y + 42 * z,
            fill="#593322", outline="#24130e", width=4,
        )
        c.create_rectangle(
            x - 25 * z, y - 50 * z, x + 25 * z, y + 38 * z,
            fill="#9b603b", outline="#c88954", width=2,
        )
        for alto in (-25, 0, 25):
            c.create_line(
                x - 23 * z, y + alto * z, x + 23 * z, y + alto * z,
                fill="#6f402b", width=2,
            )
        c.create_oval(
            x + 12 * z, y - 2 * z, x + 18 * z, y + 4 * z,
            fill="#e0bd59", outline="#806024",
        )

    def dibujar_biblioteca(self, x: float, y: float, tag: str) -> None:
        c, z = self.canvas, self.zoom
        c.create_oval(
            x - 13 * z, y - 35 * z, x + 13 * z, y - 9 * z,
            fill="#f2c9b5", outline="#17111c", width=2, tags=(tag,),
        )
        c.create_arc(
            x - 16 * z, y - 41 * z, x + 16 * z, y - 8 * z,
            start=180, extent=180, fill="#15121d", outline="#15121d", tags=(tag,),
        )
        c.create_oval(
            x - 7 * z, y - 24 * z, x - 3 * z, y - 20 * z,
            fill="#55d88d", outline="", tags=(tag,),
        )
        c.create_oval(
            x + 3 * z, y - 24 * z, x + 7 * z, y - 20 * z,
            fill="#55d88d", outline="", tags=(tag,),
        )
        c.create_polygon(
            x - 17 * z, y - 8 * z, x + 17 * z, y - 8 * z,
            x + 22 * z, y + 28 * z, x - 22 * z, y + 28 * z,
            fill="#b52245", outline="#71162e", width=2, tags=(tag,),
        )

    def dibujar_curiosidad(self, x: float, y: float, tag: str) -> None:
        c, z = self.canvas, self.zoom
        radio = (15 + 2 * math.sin(self.fase / 5)) * z
        c.create_oval(
            x - radio - 5 * z, y - radio - 5 * z,
            x + radio + 5 * z, y + radio + 5 * z,
            fill="#2b2460", outline="#7666d9", width=2, tags=(tag,),
        )
        c.create_oval(
            x - radio, y - radio, x + radio, y + radio,
            fill="#f8d75e", outline="#fff5b0", width=2, tags=(tag,),
        )
        c.create_oval(
            x - 5 * z, y - 5 * z, x + 5 * z, y + 5 * z,
            fill="#151533", outline="", tags=(tag,),
        )

    def dibujar_corazon(self, x: float, y: float, tag: str) -> None:
        c = self.canvas
        z = self.zoom * (1 + 0.08 * math.sin(self.fase / 4))
        radio = 33 * z
        c.create_oval(
            x - radio, y - radio, x, y,
            fill="#ec244d", outline="#8c1730", width=2, tags=(tag,),
        )
        c.create_oval(
            x, y - radio, x + radio, y,
            fill="#ec244d", outline="#8c1730", width=2, tags=(tag,),
        )
        c.create_polygon(
            x - radio, y - 8 * z, x + radio, y - 8 * z,
            x, y + radio + 18 * z,
            fill="#ec244d", outline="#8c1730", width=2, tags=(tag,),
        )

    def dibujar_caballero(
        self, x: float, y: float, tag: str, claro: bool, espada: bool,
    ) -> None:
        c, z = self.canvas, self.zoom
        metal = "#dcecff" if claro else "#53657d"
        sombra = "#8aa0bc" if claro else "#26384f"
        c.create_oval(
            x - 14 * z, y - 42 * z, x + 14 * z, y - 14 * z,
            fill=metal, outline=sombra, width=2, tags=(tag,),
        )
        c.create_rectangle(
            x - 20 * z, y - 14 * z, x + 20 * z, y + 31 * z,
            fill=metal, outline=sombra, width=2, tags=(tag,),
        )
        c.create_line(
            x - 10 * z, y - 29 * z, x + 10 * z, y - 29 * z,
            fill="#111827", width=max(2, int(5 * z)), tags=(tag,),
        )
        if espada:
            c.create_line(
                x + 22 * z, y - 5 * z, x + 48 * z, y - 56 * z,
                fill="#ecf4ff", width=max(2, int(4 * z)), tags=(tag,),
            )

    def dibujar_observador(self, x: float, y: float, tag: str) -> None:
        c, z = self.canvas, self.zoom
        c.create_oval(
            x - 64 * z, y - 18 * z, x + 64 * z, y + 22 * z,
            fill="#b8c9e5", outline="", tags=(tag,),
        )
        c.create_oval(
            x - 35 * z, y - 30 * z, x + 6 * z, y + 11 * z,
            fill="#f0e6e6", outline="#9d9ab0", tags=(tag,),
        )
        c.create_line(
            x + 2 * z, y - 4 * z, x + 45 * z, y + 4 * z,
            fill="#f0e6e6", width=max(2, int(16 * z)),
            capstyle="round", tags=(tag,),
        )
        c.create_arc(
            x - 77 * z, y - 4 * z, x - 8 * z, y + 30 * z,
            start=180, extent=180, fill="#d7e2f4", outline="", tags=(tag,),
        )
        c.create_arc(
            x + 3 * z, y - 5 * z, x + 77 * z, y + 31 * z,
            start=180, extent=180, fill="#d7e2f4", outline="", tags=(tag,),
        )

    def dibujar(self) -> None:
        c = self.canvas
        c.delete("all")
        self.dibujar_terreno()
        self.dibujar_casa(470, 505, "Biblioteca", "#4c78ae")
        self.dibujar_casa(300, 680, "Archivo", "#688c79")
        self.dibujar_casa(930, 505, "Santuario", "#9d4055")
        self.dibujar_puerta()

        for nombre, presencia in self.mundo.presencias.items():
            x, y = self.pantalla(presencia.x, presencia.y)
            tag = f"presencia:{nombre}"
            if presencia.estado == "trabajando":
                c.create_oval(
                    x - 42 * self.zoom, y - 52 * self.zoom,
                    x + 42 * self.zoom, y + 52 * self.zoom,
                    fill="#ffe17a", outline="#fff3ad", stipple="gray25",
                )
            if nombre == "Biblioteca":
                self.dibujar_biblioteca(x, y, tag)
            elif nombre == "Curiosidad":
                self.dibujar_curiosidad(x, y, tag)
            elif nombre == "Corazón":
                self.dibujar_corazon(x, y, tag)
            elif nombre == "Observador":
                self.dibujar_observador(x, y, tag)
            elif nombre == "Centinela":
                self.dibujar_caballero(x, y, tag, claro=True, espada=True)
            else:
                self.dibujar_caballero(x, y, tag, claro=False, espada=False)
            c.create_text(
                x, y + 58 * self.zoom, text=nombre, fill="#f6edcf",
                font=("Georgia", max(8, int(10 * self.zoom)), "bold"), tags=(tag,),
            )
            c.tag_bind(tag, "<Button-1>", lambda _, n=nombre: self.mostrar(n))

        c.create_text(
            16, 16, anchor="nw",
            text="Los destellos corresponden a llamadas reales del ciclo integrado",
            fill="#e9ddb6", font=("Helvetica", 9, "bold"),
        )

    def _observador_hilo(
        self, actor: str, accion: str, datos: dict[str, Any],
    ) -> None:
        self.mensajes.put(("evento", (actor, accion, datos)))
        time.sleep(0.65)

    def _ejecutar(self, continuo: bool) -> None:
        try:
            while not self.detener.is_set():
                with tempfile.TemporaryDirectory(prefix="mundo-mental-visual-") as carpeta:
                    resultado = ejecutar_ciclo(carpeta, observador=self._observador_hilo)
                resumen = {
                    "pregunta": resultado["pregunta"].texto,
                    "experimento": resultado["resultado"].estado,
                    "evidencia": resultado["dictamen"].motivo,
                    "reanudado": resultado["reanudado"],
                    "episodios": resultado["estado_biblioteca"]["episodios"],
                }
                self.mensajes.put(("completo", resumen))
                if not continuo or self.detener.wait(1.5):
                    break
        except Exception as error:
            self.mensajes.put(("error", repr(error)))
        finally:
            self.mensajes.put(("detenido", None))

    def _arrancar(self, continuo: bool) -> None:
        if self.hilo is not None and self.hilo.is_alive():
            return
        self.continuo = continuo
        self.detener.clear()
        self.mundo.comenzar()
        self.hilo = threading.Thread(
            target=self._ejecutar, args=(continuo,), daemon=True,
        )
        self.hilo.start()
        self.actualizar_panel()

    def iniciar(self) -> None:
        self._arrancar(continuo=True)

    def un_ciclo(self) -> None:
        self._arrancar(continuo=False)

    def pausar(self) -> None:
        self.detener.set()
        self.mundo.detener()
        self.actualizar_panel()

    def procesar_mensajes(self) -> None:
        try:
            while True:
                tipo, contenido = self.mensajes.get_nowait()
                if tipo == "evento":
                    actor, accion, datos = contenido
                    self.mundo.aplicar_evento(actor, accion, datos)
                elif tipo == "completo":
                    self.mundo.completar(contenido)
                elif tipo == "error":
                    self.mundo.detener()
                    messagebox.showerror("Error al ejecutar el ciclo", contenido)
                elif tipo == "detenido":
                    self.mundo.detener()
                self.actualizar_panel()
        except queue.Empty:
            pass
        self.raiz.after(80, self.procesar_mensajes)

    def actualizar_panel(self) -> None:
        self.cronica.delete(0, tk.END)
        for evento in reversed(self.mundo.eventos[-20:]):
            self.cronica.insert(
                tk.END, f"{evento.actor} · {evento.accion}: {evento.detalle}",
            )
        modo = "EJECUTANDO CÓDIGO REAL" if self.mundo.ejecutando else "DETENIDO"
        activo = self.mundo.activo or "ninguno"
        self.estado.configure(
            text=f"{modo}\nActivo: {activo}\nCiclos completos: {self.mundo.ciclos_terminados}",
        )
        self.dibujar()

    def animar(self) -> None:
        self.fase += 1
        self.dibujar()
        self.raiz.after(170, self.animar)

    def mostrar(self, nombre: str) -> None:
        presencia = self.mundo.presencias[nombre]
        self.ficha.configure(
            text=(
                f"{nombre}\n\nEstado visual: {presencia.estado}\n"
                f"Posición: {presencia.x}, {presencia.y}\n\n"
                f"{presencia.actividad}"
            )
        )

    def seleccionar_evento(self, _: object) -> None:
        seleccion = self.cronica.curselection()
        if not seleccion:
            return
        evento = list(reversed(self.mundo.eventos[-20:]))[seleccion[0]]
        self.ficha.configure(
            text=(
                f"{evento.actor} · {evento.accion}\n\n{evento.detalle}\n\n"
                f"{evento.momento}"
            )
        )

    def cerrar(self) -> None:
        self.detener.set()
        self.raiz.destroy()


def main() -> None:
    raiz = tk.Tk()
    VentanaMundo(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
