"""
Pestaña — Concurrencia y sincronización.  (PENDIENTE — v0.3)

Responsable: ______________________

Reemplazar el contenido de __init__ por la interfaz real del módulo.
`self.sistema` da acceso a los procesos y al registro de resultados
(ver core/sistema.py).
"""
from tkinter import ttk

from core.sistema import Sistema
from ui.pendiente import mostrar_pendiente


class TabConcurrencia(ttk.Frame):
    def __init__(self, parent, sistema: Sistema):
        super().__init__(parent)
        self.sistema = sistema
        mostrar_pendiente(
            self,
            titulo="Concurrencia y sincronización",
            version="v0.3",
            archivo="ui/tab_concurrencia.py  +  core/concurrencia.py",
            requisitos=[
            'Escenario de cuenta bancaria compartida con varios hilos (threading.Thread)',
            "Panel 'Sin sincronización': evidenciar condición de carrera (saldo incorrecto)",
            "Panel 'Con Lock': proteger la sección crítica con threading.Lock",
            'Mostrar valor esperado vs. obtenido de ambos escenarios lado a lado',
            'Actualizar la interfaz desde el hilo principal (root.after), nunca desde los hilos',
            "Publicar resultados con sistema.registrar_resultado('concurrencia', {...})",
            'Lógica en core/concurrencia.py, interfaz en este archivo',
            ],
        )
