"""Visor gráfico local de la Ciudad Mental.

Ejecutar: python mundo.py
"""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk

from mundo_mental.ciudad import CiudadMental


COLORES = {
    "fondo": "#0b1020", "panel": "#131b33", "texto": "#e7edf9", "suave": "#9eb0d0",
    "biblioteca": "#4f8cff", "corazon": "#f06d8f", "observacion": "#b98cff", "archivo": "#8eb6a5",
    "guardia": "#d7e8ff", "calles": "#7a879b", "portal": "#9c633f", "ruta": "#465775", "alerta": "#ff6b6b",
}


class VentanaCiudad:
    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz; self.ciudad = CiudadMental(); self.fase = 0
        raiz.title("Mundo Mental · Ciudad viva"); raiz.geometry("1120x720"); raiz.minsize(940, 600); raiz.configure(bg=COLORES["fondo"])
        self._construir(); self.actualizar(); self.animar()

    def _construir(self) -> None:
        encabezado = tk.Frame(self.raiz, bg=COLORES["fondo"]); encabezado.pack(fill="x", padx=22, pady=(18, 8))
        tk.Label(encabezado, text="MUNDO MENTAL", font=("Helvetica", 20, "bold"), fg=COLORES["texto"], bg=COLORES["fondo"]).pack(side="left")
        tk.Label(encabezado, text="Ciudad estable · Universos de Experimentación separados", font=("Helvetica", 10), fg=COLORES["suave"], bg=COLORES["fondo"]).pack(side="left", padx=14, pady=6)
        ttk.Button(encabezado, text="Simular pulso", command=self.pulso).pack(side="right")
        cuerpo = tk.PanedWindow(self.raiz, orient="horizontal", sashwidth=6, bg=COLORES["fondo"], bd=0); cuerpo.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        mapa = tk.Frame(cuerpo, bg=COLORES["panel"]); lateral = tk.Frame(cuerpo, bg=COLORES["panel"], width=330); cuerpo.add(mapa, stretch="always"); cuerpo.add(lateral, minsize=280)
        self.lienzo = tk.Canvas(mapa, bg=COLORES["panel"], highlightthickness=0); self.lienzo.pack(fill="both", expand=True, padx=8, pady=8); self.lienzo.bind("<Configure>", lambda _: self.dibujar())
        tk.Label(lateral, text="Actividad en tiempo real", font=("Helvetica", 13, "bold"), fg=COLORES["texto"], bg=COLORES["panel"]).pack(anchor="w", padx=16, pady=(16, 8))
        self.actividad = tk.Listbox(lateral, bg="#0e1529", fg=COLORES["texto"], selectbackground="#2f477b", borderwidth=0, highlightthickness=0, font=("Helvetica", 9)); self.actividad.pack(fill="both", expand=True, padx=16, pady=(0, 12)); self.actividad.bind("<<ListboxSelect>>", self.seleccionar_evento)
        self.inspector = tk.Label(lateral, text="Selecciona un habitante o evento.", justify="left", anchor="nw", wraplength=290, fg=COLORES["suave"], bg=COLORES["panel"], font=("Helvetica", 10)); self.inspector.pack(fill="x", padx=16, pady=(0, 16))

    def escala(self) -> tuple[float, float]: return max(self.lienzo.winfo_width()/760, .65), max(self.lienzo.winfo_height()/510, .65)
    def punto(self, lugar: str) -> tuple[float, float]:
        sx, sy = self.escala(); x, y = self.ciudad.LUGARES[lugar]; return x*sx, y*sy
    def _etiqueta(self, c: tk.Canvas, x: float, y: float, texto: str, color: str, etiqueta: str) -> None: c.create_text(x, y, text=texto, fill=color, font=("Helvetica", 8, "bold"), tags=(etiqueta,))

    def _calle(self, c: tk.Canvas, x1: float, y1: float, x2: float, y2: float, etiqueta: str) -> None:
        c.create_line(x1, y1, x2, y2, fill="#252f45", width=15, capstyle="round", tags=(etiqueta,)); c.create_line(x1, y1, x2, y2, fill=COLORES["calles"], width=10, capstyle="round", tags=(etiqueta,))
        distancia = max(1, int(math.hypot(x2-x1, y2-y1)/15))
        for indice in range(1, distancia):
            proporcion = indice / distancia; x, y = x1+(x2-x1)*proporcion, y1+(y2-y1)*proporcion
            c.create_line(x-3, y-3, x+3, y+3, fill="#aeb7c7", width=1, tags=(etiqueta,))

    def _puerta(self, c: tk.Canvas, x: float, y: float, etiqueta: str) -> None:
        c.create_rectangle(x-29, y-47, x+29, y+42, fill="#5a3425", outline="#2c1813", width=4, tags=(etiqueta,)); c.create_rectangle(x-23, y-42, x+23, y+38, fill="#9c633f", outline="#bd8051", width=2, tags=(etiqueta,))
        for altura in (-22, 2, 26): c.create_line(x-21, y+altura, x+21, y+altura, fill="#70432d", width=2, tags=(etiqueta,))
        c.create_oval(x+12, y, x+17, y+5, fill="#e4bd58", outline="#7e5c20", tags=(etiqueta,))

    def _bibliotecaria(self, c: tk.Canvas, x: float, y: float, etiqueta: str) -> None:
        c.create_oval(x-14, y-34, x+14, y-6, fill="#f2c9b5", outline="#07111d", width=2, tags=(etiqueta,)); c.create_arc(x-17, y-40, x+17, y-5, start=180, extent=180, fill="#161420", outline="#161420", tags=(etiqueta,)); c.create_oval(x-7, y-23, x-3, y-19, fill="#54d68d", outline="", tags=(etiqueta,)); c.create_oval(x+3, y-23, x+7, y-19, fill="#54d68d", outline="", tags=(etiqueta,)); c.create_polygon(x-17, y-5, x+17, y-5, x+22, y+27, x-22, y+27, fill="#bd2448", outline="#7c1733", width=2, tags=(etiqueta,))

    def _curiosidad(self, c: tk.Canvas, x: float, y: float, etiqueta: str) -> None:
        latido = math.sin(self.fase/5); radio = 14+2*latido; c.create_oval(x-radio-5, y-radio-5, x+radio+5, y+radio+5, fill="#2b2460", outline="#7666d9", width=2, tags=(etiqueta,)); c.create_oval(x-radio, y-radio, x+radio, y+radio, fill="#f8d75e", outline="#fff5b0", width=2, tags=(etiqueta,)); c.create_oval(x-5, y-5, x+5, y+5, fill="#151533", outline="", tags=(etiqueta,)); angulo = self.fase/6; qx, qy = x+math.cos(angulo)*29, y+math.sin(angulo)*20; c.create_text(qx, qy, text="?", fill="#b7a6ff", font=("Helvetica", 16, "bold"), tags=(etiqueta,))
        for desfase, color in ((0,"#5ae0ff"),(2.1,"#f48cce"),(4.2,"#b7f56b")):
            ax, ay = x+math.cos(angulo+desfase)*36, y+math.sin(angulo+desfase)*25; c.create_oval(ax-3, ay-3, ax+3, ay+3, fill=color, outline="", tags=(etiqueta,))

    def _corazon(self, c: tk.Canvas, x: float, y: float, etiqueta: str) -> None:
        pulso = 1+.08*math.sin(self.fase/4); r = 31*pulso; c.create_oval(x-r,y-r,x,y,fill="#ec244d",outline="#8c1730",width=2,tags=(etiqueta,)); c.create_oval(x,y-r,x+r,y,fill="#ec244d",outline="#8c1730",width=2,tags=(etiqueta,)); c.create_polygon(x-r,y-8,x+r,y-8,x,y+r+16,fill="#ec244d",outline="#8c1730",width=2,tags=(etiqueta,))
    def _observador(self, c: tk.Canvas, x: float, y: float, etiqueta: str) -> None:
        c.create_oval(x-64,y-18,x+64,y+22,fill="#b8c9e5",outline="",tags=(etiqueta,)); c.create_oval(x-35,y-30,x+6,y+11,fill="#f0e6e6",outline="#9d9ab0",tags=(etiqueta,)); c.create_arc(x-40,y-22,x-18,y-7,start=200,extent=130,style="arc",outline="#5d5c78",width=2,tags=(etiqueta,)); c.create_line(x+2,y-4,x+45,y+4,fill="#f0e6e6",width=16,capstyle="round",tags=(etiqueta,)); c.create_arc(x-77,y-4,x-8,y+30,start=180,extent=180,fill="#d7e2f4",outline="",tags=(etiqueta,)); c.create_arc(x+3,y-5,x+77,y+31,start=180,extent=180,fill="#d7e2f4",outline="",tags=(etiqueta,))
    def _caballero(self, c: tk.Canvas, x: float, y: float, etiqueta: str, claro: bool=False, espada: bool=False) -> None:
        metal="#dcecff" if claro else "#53657d"; sombra="#8aa0bc" if claro else "#26384f"; c.create_oval(x-14,y-42,x+14,y-14,fill=metal,outline=sombra,width=2,tags=(etiqueta,)); c.create_rectangle(x-20,y-14,x+20,y+31,fill=metal,outline=sombra,width=2,tags=(etiqueta,)); c.create_line(x-20,y+31,x-15,y+50,fill=sombra,width=7,tags=(etiqueta,)); c.create_line(x+20,y+31,x+15,y+50,fill=sombra,width=7,tags=(etiqueta,)); c.create_line(x-10,y-29,x+10,y-29,fill="#111827",width=5,tags=(etiqueta,))
        if espada: c.create_line(x+22,y-5,x+48,y-56,fill="#ecf4ff",width=4,tags=(etiqueta,)); c.create_line(x+14,y-15,x+32,y-6,fill="#d6b35f",width=5,tags=(etiqueta,))

    def dibujar(self) -> None:
        c=self.lienzo; c.delete("all"); c.create_rectangle(0,0,max(c.winfo_width(),1),max(c.winfo_height(),1),fill=COLORES["panel"],outline=""); c.create_text(20,20,anchor="w",text="CIUDAD ESTABLE",fill=COLORES["suave"],font=("Helvetica",10,"bold"))
        for origen,destino,etiqueta in self.ciudad.rutas:
            x1,y1=self.punto(origen); x2,y2=self.punto(destino); self._calle(c,x1,y1,x2,y2,f"ruta:{etiqueta}"); self._etiqueta(c,(x1+x2)/2,(y1+y2)/2-12,etiqueta,COLORES["suave"],f"ruta:{etiqueta}")
        edificios={"biblioteca":"Biblioteca","archivo":"Archivo","corazon":"Corazón"}
        for lugar,texto in edificios.items():
            x,y=self.punto(lugar); color=COLORES[lugar]; c.create_rectangle(x-57,y-32,x+57,y+32,fill=color,outline="",tags=(f"lugar:{lugar}",)); c.create_text(x,y,text=texto,fill="#07111d",font=("Helvetica",10,"bold"),tags=(f"lugar:{lugar}",))
        x,y=self.punto("portal"); self._puerta(c,x,y,"lugar:portal"); self._etiqueta(c,x,y+59,"Puerta a Universos",COLORES["texto"],"lugar:portal")
        x,y=self.punto("observacion"); self._observador(c,x,y,"actor:Observador"); self._etiqueta(c,x,y+38,"Observador",COLORES["texto"],"actor:Observador")
        x,y=self.punto("guardia"); self._caballero(c,x,y,"actor:Centinela",claro=True,espada=True); self._etiqueta(c,x,y+60,"Centinela",COLORES["texto"],"actor:Centinela")
        x,y=self.punto("corazon"); self._corazon(c,x,y,"actor:Corazón"); self._etiqueta(c,x,y+56,"Corazón",COLORES["texto"],"actor:Corazón")
        x,y=self.punto(self.ciudad.habitantes["Biblioteca"].lugar); self._bibliotecaria(c,x-27,y+51,"actor:Biblioteca"); self._etiqueta(c,x-27,y+88,"Biblioteca",COLORES["texto"],"actor:Biblioteca")
        x,y=self.punto("archivo"); self._caballero(c,x,y+26,"actor:Catalogador"); self._etiqueta(c,x,y+88,"Catalogador",COLORES["texto"],"actor:Catalogador")
        x,y=self.punto(self.ciudad.habitantes["Curiosidad"].lugar); self._curiosidad(c,x+31,y+51,"actor:Curiosidad"); self._etiqueta(c,x+31,y+88,"Curiosidad",COLORES["texto"],"actor:Curiosidad")
        for nombre in self.ciudad.habitantes: c.tag_bind(f"actor:{nombre}","<Button-1>",lambda _,n=nombre:self.mostrar_habitante(n))
        c.tag_bind("lugar:portal","<Button-1>",lambda _:self.inspector.configure(text="PUERTA A UNIVERSOS\n\nUna puerta de madera simple. Conduce únicamente a Universos de Experimentación autorizados por Curiosidad."))

    def pulso(self) -> None: self.ciudad.pulso_demo(); self.actualizar()
    def actualizar(self) -> None:
        self.actividad.delete(0,tk.END)
        for evento in reversed(self.ciudad.eventos[-14:]): self.actividad.insert(tk.END,f"{evento.actor}: {evento.detalle}")
        self.dibujar()
    def animar(self) -> None: self.fase+=1; self.dibujar(); self.raiz.after(180,self.animar)
    def mostrar_habitante(self,nombre:str)->None:
        ficha=self.ciudad.ficha(nombre); self.inspector.configure(text=f"{ficha['nombre']}\n\nLugar: {ficha['lugar']}\nEstado: {ficha['estado']}\n\n{ficha['actividad']}")
    def seleccionar_evento(self,_:object)->None:
        seleccion=self.actividad.curselection()
        if not seleccion:return
        evento=list(reversed(self.ciudad.eventos[-14:]))[seleccion[0]]; self.inspector.configure(text=f"{evento.tipo.upper()}\n\n{evento.actor}\n{evento.detalle}\n\n{evento.momento}")

def main()->None:
    raiz=tk.Tk(); VentanaCiudad(raiz); raiz.mainloop()
if __name__=="__main__":main()
