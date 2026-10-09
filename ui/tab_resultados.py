"""
Pestaña 6 — Resultados y estadísticas.

Muestra un resumen de los procesos y los datos que cada módulo publica
con `sistema.registrar_resultado(modulo, {...})`. No hay que tocar este
archivo para que aparezcan los resultados de un módulo nuevo.
"""
import tkinter as tk
from tkinter import ttk

from core.proceso import Estado
from core.sistema import Sistema
from ui import tema

MODULOS = [
    ("planificacion", "Planificación"),
    ("concurrencia", "Concurrencia"),
    ("interbloqueo", "Interbloqueos"),
    ("memoria", "Memoria"),
]


class TabResultados(ttk.Frame):
    def __init__(self, parent, sistema: Sistema):
        super().__init__(parent, padding=16)
        self.sistema = sistema

        ttk.Label(self, text="Resultados y estadísticas", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(self, text="Se actualiza automáticamente cuando se ejecuta una simulación.",
                  style="Suave.TLabel").pack(anchor="w", pady=(2, 14))

        self.fila_tarjetas = ttk.Frame(self)
        self.fila_tarjetas.pack(fill="x")

        self.rejilla = ttk.Frame(self)
        self.rejilla.pack(fill="both", expand=True, pady=(16, 0))
        for i in range(2):
            self.rejilla.columnconfigure(i, weight=1, uniform="col")

        sistema.suscribir(self.refrescar)
        self.refrescar()

    def _tarjeta(self, padre, titulo: str, valor: str):
        caja = tk.Frame(padre, bg=tema.PANEL, highlightthickness=1,
                        highlightbackground=tema.BORDE, padx=18, pady=12)
        tk.Label(caja, text=valor, bg=tema.PANEL, fg=tema.TEXTO,
                 font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(caja, text=titulo, bg=tema.PANEL, fg=tema.TEXTO_SUAVE,
                 font=tema.FUENTE).pack(anchor="w")
        return caja

    def refrescar(self):
        for w in self.fila_tarjetas.winfo_children() + self.rejilla.winfo_children():
            w.destroy()

        procesos = self.sistema.procesos
        terminados = sum(1 for p in procesos if p.estado == Estado.TERMINADO)
        memoria = sum(p.memoria for p in procesos)
        tarjetas = [
            ("Procesos registrados", str(len(procesos))),
            ("Procesos terminados", str(terminados)),
            ("Memoria solicitada", f"{memoria} KB"),
            ("Módulos con resultados", f"{len(self.sistema.resultados)} / {len(MODULOS)}"),
        ]
        for titulo, valor in tarjetas:
            self._tarjeta(self.fila_tarjetas, titulo, valor).pack(
                side="left", fill="x", expand=True, padx=(0, 10))

        for i, (clave, nombre) in enumerate(MODULOS):
            caja = ttk.LabelFrame(self.rejilla, text=f"  {nombre}  ", padding=12)
            caja.grid(row=i // 2, column=i % 2, sticky="nsew", padx=(0, 10), pady=(0, 10))
            datos = self.sistema.resultados.get(clave)
            if not datos:
                ttk.Label(caja, text="Sin simulaciones todavía.",
                          style="PanelSuave.TLabel").pack(anchor="w")
                continue
            for etiqueta, valor in datos.items():
                fila = ttk.Frame(caja, style="Panel.TFrame")
                fila.pack(fill="x", pady=1)
                ttk.Label(fila, text=etiqueta, style="PanelSuave.TLabel").pack(side="left")
                ttk.Label(fila, text=str(valor), style="Panel.TLabel").pack(side="right")
