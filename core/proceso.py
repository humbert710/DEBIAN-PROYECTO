"""
Modelo de datos de un proceso.

Este archivo es la BASE de todo el simulador: Planificación, Memoria e
Interbloqueo trabajan con objetos Proceso. Si se cambia algo aquí,
avisar al equipo.
"""
from dataclasses import dataclass, field, replace
from enum import Enum


class Estado(Enum):
    """Estados del ciclo de vida de un proceso (modelo de 5 estados)."""
    NUEVO = "Nuevo"
    LISTO = "Listo"
    EJECUCION = "Ejecución"
    BLOQUEADO = "Bloqueado"
    TERMINADO = "Terminado"


@dataclass
class Proceso:
    pid: str            # Identificador, ej. "P1"
    llegada: int        # Tiempo de llegada (unidades de tiempo)
    rafaga: int         # Tiempo de CPU que necesita (ráfaga)
    prioridad: int      # Menor número = mayor prioridad
    memoria: int        # Memoria solicitada en KB
    estado: Estado = field(default=Estado.NUEVO)

    def copia(self) -> "Proceso":
        """Devuelve una copia independiente.

        Los módulos deben simular sobre COPIAS para no alterar la lista
        original que se ve en la pestaña Procesos.
        """
        return replace(self)
