"""
Pestaña — Interbloqueos.  (PENDIENTE — v0.4)

Responsable: ______________________

Reemplazar el contenido de __init__ por la interfaz real del módulo.
`self.sistema` da acceso a los procesos y al registro de resultados
(ver core/sistema.py).
"""
from tkinter import ttk

from core.sistema import Sistema
from ui.pendiente import mostrar_pendiente


class TabInterbloqueo(ttk.Frame):
    def __init__(self, parent, sistema: Sistema):
        super().__init__(parent)
        self.sistema = sistema
        mostrar_pendiente(
            self,
            titulo="Interbloqueos",
            version="v0.4",
            archivo="ui/tab_interbloqueo.py  +  core/interbloqueo.py",
            requisitos=[
            'Grafo de asignación de recursos: procesos (círculos) y recursos (cuadros)',
            'Flechas de asignación y de solicitud',
            "Botón 'Provocar deadlock' y detección del ciclo (resaltarlo en rojo)",
            'Relacionar con las 4 condiciones de Coffman',
            'Estrategia: detección y recuperación (terminar un proceso) y/o algoritmo del banquero',
            "Publicar resultados con sistema.registrar_resultado('interbloqueo', {...})",
            'Lógica en core/interbloqueo.py, interfaz en este archivo',
            ],
        )
