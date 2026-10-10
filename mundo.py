"""Mundo Mental: representación gráfica de trabajo observable.

Abrir con: python mundo.py
"""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk

from mundo_mental.mundo_virtual import MundoVirtual


class VentanaMundo:
    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz; self.mundo = MundoVirtual(); self.zoom = .72; self.dx = 70; self.dy = 70; self.fase = 0; self.arrastre = None
        raiz.title("Mundo Mental · Trabajo visible"); raiz.geometry("1240x780"); raiz.minsize(980,640); raiz.configure(bg="#101523")
        self._interfaz(); self.actualizar(); self.animar()

    def _interfaz(self)->None:
        barra=tk.Frame(self.raiz,bg="#101523"); barra.pack(fill="x",padx=20,pady=(16,8))
        tk.Label(barra,text="MUNDO MENTAL",font=("Georgia",21,"bold"),fg="#f5e6bd",bg="#101523").pack(side="left")
        tk.Label(barra,text="Reino medieval fantástico · Trabajo observable",font=("Helvetica",10),fg="#aebbd1",bg="#101523").pack(side="left",padx=14)
        ttk.Button(barra,text="Iniciar trabajo",command=self.iniciar).pack(side="right")
        ttk.Button(barra,text="Pausar",command=self.pausar).pack(side="right",padx=6)
        ttk.Button(barra,text="Un paso",command=self.paso).pack(side="right")
        cuerpo=tk.PanedWindow(self.raiz,orient="horizontal",sashwidth=6,bg="#101523",bd=0); cuerpo.pack(fill="both",expand=True,padx=18,pady=(0,18))
        mapa=tk.Frame(cuerpo,bg="#172238"); panel=tk.Frame(cuerpo,bg="#172238",width=350); cuerpo.add(mapa,stretch="always"); cuerpo.add(panel,minsize=300)
        self.canvas=tk.Canvas(mapa,bg="#172238",highlightthickness=0); self.canvas.pack(fill="both",expand=True,padx=8,pady=8)
        self.canvas.bind("<ButtonPress-3>",self.iniciar_arrastre); self.canvas.bind("<B3-Motion>",self.arrastrar); self.canvas.bind("<MouseWheel>",self.zoom_raton); self.canvas.bind("<Button-4>",lambda e:self.cambiar_zoom(1.1)); self.canvas.bind("<Button-5>",lambda e:self.cambiar_zoom(.9)); self.canvas.bind("<Configure>",lambda e:self.dibujar())
        tk.Label(panel,text="Trabajo en tiempo real",font=("Georgia",14,"bold"),fg="#f5e6bd",bg="#172238").pack(anchor="w",padx=16,pady=(16,4))
        self.estado=tk.Label(panel,text="En pausa · Próximo: Curiosidad",justify="left",anchor="w",wraplength=300,fg="#9edec5",bg="#172238",font=("Helvetica",10,"bold")); self.estado.pack(fill="x",padx=16,pady=(0,8))
        self.cronica=tk.Listbox(panel,bg="#101827",fg="#e7edf9",selectbackground="#405d8f",borderwidth=0,highlightthickness=0,font=("Helvetica",9)); self.cronica.pack(fill="both",expand=True,padx=16,pady=(0,12)); self.cronica.bind("<<ListboxSelect>>",self.seleccionar)
        self.ficha=tk.Label(panel,text="Selecciona un habitante para ver qué está haciendo.",justify="left",anchor="nw",wraplength=290,fg="#afbed7",bg="#172238",font=("Helvetica",10)); self.ficha.pack(fill="x",padx=16,pady=(0,16))

    def pantalla(self,x:float,y:float)->tuple[float,float]: return x*self.zoom+self.dx,y*self.zoom+self.dy
    def iniciar_arrastre(self,e:tk.Event)->None: self.arrastre=(e.x,e.y)
    def arrastrar(self,e:tk.Event)->None:
        if self.arrastre: self.dx+=e.x-self.arrastre[0]; self.dy+=e.y-self.arrastre[1]; self.arrastre=(e.x,e.y); self.dibujar()
    def zoom_raton(self,e:tk.Event)->None: self.cambiar_zoom(1.1 if e.delta>0 else .9)
    def cambiar_zoom(self,factor:float)->None: self.zoom=max(.38,min(1.45,self.zoom*factor)); self.dibujar()
    def poligono(self,puntos:list[tuple[float,float]])->list[float]: return [v for punto in puntos for v in punto]

    def terreno(self,c:tk.Canvas)->None:
        w,h=max(c.winfo_width(),1),max(c.winfo_height(),1); c.create_rectangle(0,0,w,h,fill="#315a43",outline="")
        for x in range(-100,self.mundo.ANCHO+120,120):
            for y in range(20,self.mundo.ALTO,100):
                sx,sy=self.pantalla(x+(y//80%2)*25,y)
                if -20<sx<w+20 and -20<sy<h+20: c.create_oval(sx-13,sy-16,sx+13,sy+15,fill="#1f4937",outline="#163a2d")
        rio=[]
        for y in range(0,self.mundo.ALTO+50,50): rio.append(self.pantalla(1210+50*math.sin(y/130),y))
        for y in range(self.mundo.ALTO,-50,-50): rio.append(self.pantalla(1320+50*math.sin(y/130),y))
        c.create_polygon(*self.poligono(rio),fill="#4b9dc4",outline="#83d0e9",width=2)
    def camino(self,c:tk.Canvas)->None:
        puntos=[self.pantalla(x,y) for x,y in self.mundo.CAMINO]; c.create_line(*self.poligono(puntos),fill="#342b27",width=33,capstyle="round",joinstyle="round"); c.create_line(*self.poligono(puntos),fill="#aa946e",width=26,capstyle="round",joinstyle="round")
    def casa(self,c:tk.Canvas,x:int,y:int,nombre:str,color:str)->None:
        sx,sy=self.pantalla(x,y); z=self.zoom; c.create_rectangle(sx-52*z,sy-25*z,sx+52*z,sy+45*z,fill=color,outline="#392e2a",width=2); c.create_polygon(sx-63*z,sy-25*z,sx,sy-72*z,sx+63*z,sy-25*z,fill="#704736",outline="#392e2a",width=2); c.create_rectangle(sx-10*z,sy+5*z,sx+10*z,sy+45*z,fill="#4b2d22",outline="#2d1a15"); c.create_text(sx,sy+59*z,text=nombre,fill="#f5e6bd",font=("Georgia",max(8,int(10*z)),"bold"))
    def puerta(self,c:tk.Canvas)->None:
        x,y=self.pantalla(1450,650); z=self.zoom; c.create_rectangle(x-31*z,y-55*z,x+31*z,y+42*z,fill="#593322",outline="#24130e",width=4); c.create_rectangle(x-25*z,y-50*z,x+25*z,y+38*z,fill="#9b603b",outline="#c88954",width=2)
        for alto in (-25,0,25): c.create_line(x-23*z,y+alto*z,x+23*z,y+alto*z,fill="#6f402b",width=2)
        c.create_oval(x+12*z,y-2*z,x+18*z,y+4*z,fill="#e0bd59",outline="#806024"); c.create_text(x,y+60*z,text="Puerta a Universos",fill="#f5e6bd",font=("Georgia",max(8,int(10*z)),"bold"))
    def bibliotecaria(self,c:tk.Canvas,x:float,y:float,tag:str)->None:
        z=self.zoom; c.create_oval(x-13*z,y-35*z,x+13*z,y-9*z,fill="#f2c9b5",outline="#17111c",width=2,tags=(tag,)); c.create_arc(x-16*z,y-41*z,x+16*z,y-8*z,start=180,extent=180,fill="#15121d",outline="#15121d",tags=(tag,)); c.create_oval(x-7*z,y-24*z,x-3*z,y-20*z,fill="#55d88d",outline="",tags=(tag,)); c.create_oval(x+3*z,y-24*z,x+7*z,y-20*z,fill="#55d88d",outline="",tags=(tag,)); c.create_polygon(x-17*z,y-8*z,x+17*z,y-8*z,x+22*z,y+28*z,x-22*z,y+28*z,fill="#b52245",outline="#71162e",width=2,tags=(tag,))
    def curiosidad(self,c:tk.Canvas,x:float,y:float,tag:str)->None:
        z=self.zoom; r=(15+2*math.sin(self.fase/5))*z; c.create_oval(x-r-5*z,y-r-5*z,x+r+5*z,y+r+5*z,fill="#2b2460",outline="#7666d9",width=2,tags=(tag,)); c.create_oval(x-r,y-r,x+r,y+r,fill="#f8d75e",outline="#fff5b0",width=2,tags=(tag,)); c.create_oval(x-5*z,y-5*z,x+5*z,y+5*z,fill="#151533",outline="",tags=(tag,)); a=self.fase/6; c.create_text(x+math.cos(a)*31*z,y+math.sin(a)*23*z,text="?",fill="#b7a6ff",font=("Helvetica",max(10,int(16*z)),"bold"),tags=(tag,))
    def corazon(self,c:tk.Canvas,x:float,y:float,tag:str)->None:
        z=self.zoom*(1+.08*math.sin(self.fase/4)); r=33*z; c.create_oval(x-r,y-r,x,y,fill="#ec244d",outline="#8c1730",width=2,tags=(tag,)); c.create_oval(x,y-r,x+r,y,fill="#ec244d",outline="#8c1730",width=2,tags=(tag,)); c.create_polygon(x-r,y-8*z,x+r,y-8*z,x,y+r+18*z,fill="#ec244d",outline="#8c1730",width=2,tags=(tag,))
    def caballero(self,c:tk.Canvas,x:float,y:float,tag:str,claro:bool=False,espada:bool=False)->None:
        z=self.zoom; metal="#dcecff" if claro else "#53657d"; sombra="#8aa0bc" if claro else "#26384f"; c.create_oval(x-14*z,y-42*z,x+14*z,y-14*z,fill=metal,outline=sombra,width=2,tags=(tag,)); c.create_rectangle(x-20*z,y-14*z,x+20*z,y+31*z,fill=metal,outline=sombra,width=2,tags=(tag,)); c.create_line(x-20*z,y+31*z,x-15*z,y+50*z,fill=sombra,width=max(2,int(7*z)),tags=(tag,)); c.create_line(x+20*z,y+31*z,x+15*z,y+50*z,fill=sombra,width=max(2,int(7*z)),tags=(tag,)); c.create_line(x-10*z,y-29*z,x+10*z,y-29*z,fill="#111827",width=max(2,int(5*z)),tags=(tag,))
        if espada: c.create_line(x+22*z,y-5*z,x+48*z,y-56*z,fill="#ecf4ff",width=max(2,int(4*z)),tags=(tag,)); c.create_line(x+14*z,y-15*z,x+32*z,y-6*z,fill="#d6b35f",width=max(2,int(5*z)),tags=(tag,))
    def observador(self,c:tk.Canvas,x:float,y:float,tag:str)->None:
        z=self.zoom; c.create_oval(x-64*z,y-18*z,x+64*z,y+22*z,fill="#b8c9e5",outline="",tags=(tag,)); c.create_oval(x-35*z,y-30*z,x+6*z,y+11*z,fill="#f0e6e6",outline="#9d9ab0",tags=(tag,)); c.create_arc(x-40*z,y-22*z,x-18*z,y-7*z,start=200,extent=130,style="arc",outline="#5d5c78",width=2,tags=(tag,)); c.create_line(x+2*z,y-4*z,x+45*z,y+4*z,fill="#f0e6e6",width=max(2,int(16*z)),capstyle="round",tags=(tag,)); c.create_arc(x-77*z,y-4*z,x-8*z,y+30*z,start=180,extent=180,fill="#d7e2f4",outline="",tags=(tag,)); c.create_arc(x+3*z,y-5*z,x+77*z,y+31*z,start=180,extent=180,fill="#d7e2f4",outline="",tags=(tag,))

    def dibujar(self)->None:
        c=self.canvas; c.delete("all"); self.terreno(c); self.camino(c); self.casa(c,470,505,"Biblioteca","#4c78ae"); self.casa(c,300,680,"Archivo","#688c79"); self.casa(c,930,505,"Santuario","#9d4055"); self.puerta(c)
        for nombre,ser in self.mundo.seres.items():
            x,y=self.pantalla(ser.x,ser.y); tag=f"ser:{nombre}"; brillo="#ffe17a" if ser.estado=="trabajando" else ""
            if brillo: c.create_oval(x-38*self.zoom,y-48*self.zoom,x+38*self.zoom,y+48*self.zoom,fill=brillo,outline="",stipple="gray25")
            if nombre=="Biblioteca": self.bibliotecaria(c,x,y,tag)
            elif nombre=="Curiosidad": self.curiosidad(c,x,y,tag)
            elif nombre=="Corazón": self.corazon(c,x,y,tag)
            elif nombre=="Observador": self.observador(c,x,y,tag)
            elif nombre=="Centinela": self.caballero(c,x,y,tag,claro=True,espada=True)
            else: self.caballero(c,x,y,tag)
            c.create_text(x,y+55*self.zoom,text=nombre,fill="#f6edcf",font=("Georgia",max(8,int(10*self.zoom)),"bold"),tags=(tag,)); c.tag_bind(tag,"<Button-1>",lambda e,n=nombre:self.mostrar(n))
        c.create_text(16,16,anchor="nw",text="Arrastra con botón derecho · Rueda para acercar · El mundo solo visualiza trabajo",fill="#e9ddb6",font=("Helvetica",9,"bold"))

    def iniciar(self)->None: self.mundo.iniciar(); self.actualizar()
    def pausar(self)->None: self.mundo.pausar(); self.actualizar()
    def paso(self)->None: self.mundo.avanzar(); self.actualizar()
    def actualizar(self)->None:
        self.cronica.delete(0,tk.END)
        for evento in reversed(self.mundo.eventos[-18:]): self.cronica.insert(tk.END,f"{evento.actor}: {evento.detalle}")
        modo="TRABAJANDO" if self.mundo.ciclo_activo else "EN PAUSA"; self.estado.configure(text=f"{modo} · Próximo: {self.mundo.paso_siguiente()} · Ciclos: {self.mundo.ciclos_terminados}")
        self.dibujar()
    def animar(self)->None:
        self.fase+=1
        if self.mundo.ciclo_activo and self.fase%12==0: self.mundo.avanzar(); self.actualizar()
        else: self.dibujar()
        self.raiz.after(170,self.animar)
    def mostrar(self,nombre:str)->None:
        ser=self.mundo.seres[nombre]; self.ficha.configure(text=f"{nombre}\n\nEstado: {ser.estado}\nPosición: {ser.x}, {ser.y}\n\n{ser.actividad}")
    def seleccionar(self,_:object)->None:
        elegido=self.cronica.curselection()
        if not elegido:return
        evento=list(reversed(self.mundo.eventos[-18:]))[elegido[0]]; self.ficha.configure(text=f"{evento.tipo.upper()}\n\n{evento.actor}\n{evento.detalle}\n\n{evento.momento}")


def main()->None:
    raiz=tk.Tk(); VentanaMundo(raiz); raiz.mainloop()

if __name__=="__main__":main()
