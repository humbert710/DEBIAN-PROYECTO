"""
Estado compartido de la aplicación.

Hay UNA sola instancia de Sistema y todas las pestañas la reciben.
Así los procesos que se crean en la pestaña Procesos están disponibles
en Planificación y Memoria, y cada módulo puede publicar sus resultados
para que la pestaña Resultados los muestre.

Cómo usarlo desde un módulo:
    sistema.procesos                         -> lista de Proceso
    sistema.suscribir(funcion)               -> llamar a 'funcion' cuando cambien los procesos
    sistema.registrar_resultado("memoria", {"Fragmentación": "12 %"})
"""
from typing import Callable

from core.proceso import Proceso

MEMORIA_TOTAL_KB = 1024  # Tamaño de la "RAM" simulada


class Sistema:
    def __init__(self):
        self.procesos: list[Proceso] = []
        self.memoria_total = MEMORIA_TOTAL_KB
        # Cada módulo guarda aquí un diccionario {nombre_dato: valor}
        self.resultados: dict[str, dict[str, str]] = {}
        self._suscriptores: list[Callable[[], None]] = []

    # ---------- Suscripción a cambios ----------
    def suscribir(self, funcion: Callable[[], None]) -> None:
        self._suscriptores.append(funcion)

    def notificar(self) -> None:
        for funcion in self._suscriptores:
            funcion()

    # ---------- Procesos ----------
    def existe_pid(self, pid: str) -> bool:
        return any(p.pid.lower() == pid.lower() for p in self.procesos)

    def siguiente_pid(self) -> str:
        n = 1
        while self.existe_pid(f"P{n}"):
            n += 1
        return f"P{n}"

    def agregar_proceso(self, proceso: Proceso) -> None:
        if self.existe_pid(proceso.pid):
            raise ValueError(f"Ya existe un proceso con el ID {proceso.pid}.")
        self.procesos.append(proceso)
        self.notificar()

    def eliminar_proceso(self, pid: str) -> None:
        self.procesos = [p for p in self.procesos if p.pid != pid]
        self.notificar()

    def limpiar_procesos(self) -> None:
        self.procesos.clear()
        self.notificar()

    def cargar_ejemplo(self) -> None:
        """Datos de ejemplo para demostraciones y la defensa."""
        self.procesos = [
            Proceso("P1", llegada=0, rafaga=8, prioridad=3, memoria=200),
            Proceso("P2", llegada=1, rafaga=4, prioridad=1, memoria=120),
            Proceso("P3", llegada=2, rafaga=9, prioridad=4, memoria=300),
            Proceso("P4", llegada=3, rafaga=5, prioridad=2, memoria=90),
            Proceso("P5", llegada=4, rafaga=2, prioridad=5, memoria=150),
        ]
        self.notificar()

    # ---------- Resultados ----------
    def registrar_resultado(self, modulo: str, datos: dict[str, str]) -> None:
        self.resultados[modulo] = datos
        self.notificar()
