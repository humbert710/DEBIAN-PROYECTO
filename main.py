"""
DebianSim — Simulador visual de administración de recursos de un SO.
Proyecto final · Sistemas Operativos I (029) · UMG · Equipo Debian

Ejecutar:  python main.py
"""
import tkinter as tk
from tkinter import ttk

from core.sistema import Sistema
from ui import tema
from ui.tab_procesos import TabProcesos
from ui.tab_planificacion import TabPlanificacion
from ui.tab_concurrencia import TabConcurrencia
from ui.tab_interbloqueo import TabInterbloqueo
from ui.tab_memoria import TabMemoria
from ui.tab_resultados import TabResultados

VERSION = "0.3.0"

PESTANAS = [
    ("1 · Procesos", TabProcesos),
    ("2 · Planificación", TabPlanificacion),
    ("3 · Concurrencia", TabConcurrencia),
    ("4 · Interbloqueo", TabInterbloqueo),
    ("5 · Memoria", TabMemoria),
    ("6 · Resultados", TabResultados),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"DebianSim v{VERSION} — Simulador de Recursos del SO")
        self.geometry("1100x700")
        self.minsize(950, 600)
        tema.aplicar_tema(self)

        self.sistema = Sistema()

        encabezado = tk.Frame(self, bg=tema.FONDO, padx=18, pady=12)
        encabezado.pack(fill="x")
        tk.Label(encabezado, text="◉", fg=tema.ACENTO, bg=tema.FONDO,
                 font=("Segoe UI", 20, "bold")).pack(side="left")
        tk.Label(encabezado, text=" DebianSim", fg=tema.TEXTO, bg=tema.FONDO,
                 font=("Segoe UI", 17, "bold")).pack(side="left")
        tk.Label(encabezado, text="   Simulador visual de administración de recursos",
                 fg=tema.TEXTO_SUAVE, bg=tema.FONDO, font=tema.FUENTE).pack(side="left", pady=(5, 0))
        tk.Label(encabezado, text=f"v{VERSION}  ·  Sistemas Operativos I  ·  UMG",
                 fg=tema.TEXTO_SUAVE, bg=tema.FONDO, font=tema.FUENTE).pack(side="right")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        for titulo, clase in PESTANAS:
            notebook.add(clase(notebook, self.sistema), text=titulo)


if __name__ == "__main__":
    App().mainloop()
