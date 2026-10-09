"""
Pestaña — Planificación del procesador.  (PENDIENTE — v0.2)

Responsable: ______________________

Reemplazar el contenido de __init__ por la interfaz real del módulo.
`self.sistema` da acceso a los procesos y al registro de resultados
(ver core/sistema.py).
"""
from tkinter import ttk

from core.sistema import Sistema
from ui.pendiente import mostrar_pendiente


class TabPlanificacion(ttk.Frame):
    def __init__(self, parent, sistema: Sistema):
        super().__init__(parent)
        self.sistema = sistema
        mostrar_pendiente(
            self,
            titulo="Planificación del procesador",
            version="v0.2",
            archivo="ui/tab_planificacion.py  +  core/planificacion.py",
            requisitos=[
            'Algoritmos FCFS, SJF (no expropiativo) y Round Robin con quantum configurable',
            'Usar copias de sistema.procesos (p.copia()) para no alterar la lista original',
            'Mostrar orden de ejecución y diagrama de Gantt (tk.Canvas)',
            'Tabla con tiempo de espera, retorno y respuesta por proceso + promedios',
            "Botón 'Comparar los 3' con los promedios lado a lado",
            "Publicar resultados con sistema.registrar_resultado('planificacion', {...})",
            'Lógica en core/planificacion.py, interfaz en este archivo',
            ],
        )
