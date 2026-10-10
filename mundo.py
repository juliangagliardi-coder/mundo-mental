"""Visor gráfico local de la Ciudad Mental.

Ejecutar: python mundo.py
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from mundo_mental.ciudad import CiudadMental


COLORES = {
    "fondo": "#0b1020", "panel": "#131b33", "texto": "#e7edf9", "suave": "#9eb0d0",
    "biblioteca": "#4f8cff", "corazon": "#f06d8f", "observacion": "#b98cff",
    "calles": "#43d6b4", "portal": "#ffb45c", "ruta": "#3d507a", "alerta": "#ff6b6b",
}


class VentanaCiudad:
    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz
        self.ciudad = CiudadMental()
        raiz.title("Mundo Mental · Ciudad viva")
        raiz.geometry("1120x720")
        raiz.minsize(940, 600)
        raiz.configure(bg=COLORES["fondo"])
        self._construir()
        self.actualizar()

    def _construir(self) -> None:
        encabezado = tk.Frame(self.raiz, bg=COLORES["fondo"])
        encabezado.pack(fill="x", padx=22, pady=(18, 8))
        tk.Label(encabezado, text="MUNDO MENTAL", font=("Helvetica", 20, "bold"), fg=COLORES["texto"], bg=COLORES["fondo"]).pack(side="left")
        tk.Label(encabezado, text="Ciudad estable · Universos de Experimentación separados", font=("Helvetica", 10), fg=COLORES["suave"], bg=COLORES["fondo"]).pack(side="left", padx=14, pady=6)
        ttk.Button(encabezado, text="Simular pulso", command=self.pulso).pack(side="right")

        cuerpo = tk.PanedWindow(self.raiz, orient="horizontal", sashwidth=6, bg=COLORES["fondo"], bd=0)
        cuerpo.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        mapa = tk.Frame(cuerpo, bg=COLORES["panel"])
        lateral = tk.Frame(cuerpo, bg=COLORES["panel"], width=330)
        cuerpo.add(mapa, stretch="always")
        cuerpo.add(lateral, minsize=280)
        self.lienzo = tk.Canvas(mapa, bg=COLORES["panel"], highlightthickness=0)
        self.lienzo.pack(fill="both", expand=True, padx=8, pady=8)
        self.lienzo.bind("<Configure>", lambda _: self.dibujar())

        tk.Label(lateral, text="Actividad en tiempo real", font=("Helvetica", 13, "bold"), fg=COLORES["texto"], bg=COLORES["panel"]).pack(anchor="w", padx=16, pady=(16, 8))
        self.actividad = tk.Listbox(lateral, bg="#0e1529", fg=COLORES["texto"], selectbackground="#2f477b", borderwidth=0, highlightthickness=0, font=("Helvetica", 9))
        self.actividad.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self.actividad.bind("<<ListboxSelect>>", self.seleccionar_evento)
        self.inspector = tk.Label(lateral, text="Selecciona un habitante o evento.", justify="left", anchor="nw", wraplength=290, fg=COLORES["suave"], bg=COLORES["panel"], font=("Helvetica", 10))
        self.inspector.pack(fill="x", padx=16, pady=(0, 16))

    def escala(self) -> tuple[float, float]:
        return max(self.lienzo.winfo_width() / 760, 0.65), max(self.lienzo.winfo_height() / 510, 0.65)

    def punto(self, lugar: str) -> tuple[float, float]:
        sx, sy = self.escala()
        x, y = self.ciudad.LUGARES[lugar]
        return x * sx, y * sy

    def dibujar(self) -> None:
        c = self.lienzo
        c.delete("all")
        c.create_text(20, 20, anchor="w", text="CIUDAD ESTABLE", fill=COLORES["suave"], font=("Helvetica", 10, "bold"))
        for origen, destino, etiqueta in self.ciudad.rutas:
            x1, y1 = self.punto(origen); x2, y2 = self.punto(destino)
            c.create_line(x1, y1, x2, y2, fill=COLORES["ruta"], width=3, dash=(5, 4))
            c.create_text((x1 + x2) / 2, (y1 + y2) / 2 - 10, text=etiqueta, fill=COLORES["suave"], font=("Helvetica", 8))
        etiquetas = {"biblioteca": "Biblioteca", "corazon": "Corazón", "observacion": "Observación", "calles": "Calles", "portal": "Portal\nUniversos"}
        for lugar, texto in etiquetas.items():
            x, y = self.punto(lugar)
            color = COLORES[lugar]
            ancho, alto = (115, 66) if lugar != "portal" else (105, 58)
            c.create_rectangle(x - ancho / 2, y - alto / 2, x + ancho / 2, y + alto / 2, fill=color, outline="", tags=(f"lugar:{lugar}",))
            c.create_text(x, y, text=texto, fill="#07111d", font=("Helvetica", 10, "bold"), tags=(f"lugar:{lugar}",))
        for nombre, habitante in self.ciudad.habitantes.items():
            x, y = self.punto(habitante.lugar)
            desplazamiento = {"Biblioteca": (-30, 42), "Curiosidad": (28, 42), "Corazón": (0, 42), "Observación": (0, 42), "Calles": (0, 42)}[nombre]
            px, py = x + desplazamiento[0], y + desplazamiento[1]
            color = COLORES["alerta"] if habitante.estado == "alerta" else "#f8fbff"
            c.create_oval(px - 11, py - 11, px + 11, py + 11, fill=color, outline="#07111d", width=2, tags=(f"actor:{nombre}",))
            c.create_text(px, py + 20, text=nombre, fill=COLORES["texto"], font=("Helvetica", 8, "bold"), tags=(f"actor:{nombre}",))
            c.tag_bind(f"actor:{nombre}", "<Button-1>", lambda _, n=nombre: self.mostrar_habitante(n))

    def pulso(self) -> None:
        self.ciudad.pulso_demo()
        self.actualizar()

    def actualizar(self) -> None:
        self.actividad.delete(0, tk.END)
        for evento in reversed(self.ciudad.eventos[-14:]):
            self.actividad.insert(tk.END, f"{evento.actor}: {evento.detalle}")
        self.dibujar()

    def mostrar_habitante(self, nombre: str) -> None:
        ficha = self.ciudad.ficha(nombre)
        self.inspector.configure(text=f"{ficha['nombre']}\n\nLugar: {ficha['lugar']}\nEstado: {ficha['estado']}\n\n{ficha['actividad']}")

    def seleccionar_evento(self, _: object) -> None:
        seleccion = self.actividad.curselection()
        if not seleccion:
            return
        evento = list(reversed(self.ciudad.eventos[-14:]))[seleccion[0]]
        self.inspector.configure(text=f"{evento.tipo.upper()}\n\n{evento.actor}\n{evento.detalle}\n\n{evento.momento}")


def main() -> None:
    raiz = tk.Tk()
    VentanaCiudad(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
