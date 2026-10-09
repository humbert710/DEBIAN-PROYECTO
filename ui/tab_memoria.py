"""
Pestaña — Gestión de memoria.  (PENDIENTE — v0.3)

Responsable: ______________________

Reemplazar el contenido de __init__ por la interfaz real del módulo.
`self.sistema` da acceso a los procesos y al registro de resultados
(ver core/sistema.py).
"""
from tkinter import ttk

from core.sistema import Sistema
from ui.pendiente import mostrar_pendiente


class TabMemoria(ttk.Frame):
    def __init__(self, parent, sistema: Sistema):
        super().__init__(parent)
        self.sistema = sistema
        mostrar_pendiente(
            self,
            titulo="Gestión de memoria",
            version="v0.3",
            archivo="ui/tab_memoria.py  +  core/memoria.py",
            requisitos=[
            'Barra visual de la RAM (sistema.memoria_total KB) con bloques por proceso',
            'Estrategias First Fit, Best Fit y Worst Fit (mínimo 2)',
            'Asignar memoria a los procesos de sistema.procesos y liberar bloques',
            'Mostrar espacio ocupado, libre y fragmentación externa',
            "Publicar resultados con sistema.registrar_resultado('memoria', {...})",
            'Lógica en core/memoria.py, interfaz en este archivo',
            ],
        )
