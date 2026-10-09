"""
Pantalla temporal para las pestañas que todavía no están implementadas.
Cuando un módulo esté listo, su pestaña deja de usar esto.
"""
from tkinter import ttk


def mostrar_pendiente(frame: ttk.Frame, titulo: str, version: str,
                      archivo: str, requisitos: list[str]) -> None:
    contenedor = ttk.Frame(frame, padding=30)
    contenedor.pack(fill="both", expand=True)

    ttk.Label(contenedor, text=titulo, style="Titulo.TLabel").pack(anchor="w")
    ttk.Label(contenedor, text=f"Módulo en desarrollo — planificado para {version}",
              style="Suave.TLabel").pack(anchor="w", pady=(2, 18))

    caja = ttk.LabelFrame(contenedor, text="  Requisitos de este módulo  ", padding=16)
    caja.pack(fill="x")
    for req in requisitos:
        ttk.Label(caja, text=f"•  {req}", style="Panel.TLabel").pack(anchor="w", pady=2)

    ttk.Label(contenedor, text=f"Archivo a editar: {archivo}",
              style="Suave.TLabel").pack(anchor="w", pady=(18, 0))
