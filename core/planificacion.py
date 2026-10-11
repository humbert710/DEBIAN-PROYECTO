"""Algoritmos de planificación del CPU: FCFS, SJF (no apropiativo) y Round Robin.

Módulo independiente de la interfaz. Solo LEE los procesos (nunca los modifica),
así que simula siempre sobre datos propios y la lista original queda intacta.

Fórmulas (las mismas que enseña el docente):
    Retorno   = finalización - llegada
    Espera    = retorno - ráfaga de CPU
    Respuesta = primera ejecución - llegada
"""
from collections import deque
from dataclasses import dataclass, field

OCIOSO = "Ocioso"  # tramo del Gantt donde la CPU espera a que llegue un proceso

# Nombres de campo aceptados en los procesos del proyecto (por si difieren).
_ALIAS = {
    "pid": ("id", "pid", "nombre"),
    "llegada": ("llegada", "tiempo_llegada", "arrival"),
    "rafaga": ("rafaga", "ráfaga", "burst", "duracion"),
}


@dataclass
class Segmento:
    """Un tramo del diagrama de Gantt."""
    pid: str
    inicio: float
    fin: float


@dataclass
class Metrica:
    """Tiempos de un proceso al terminar la simulación."""
    pid: str
    llegada: float
    rafaga: float
    primera_ejecucion: float
    finalizacion: float
    espera: float
    retorno: float
    respuesta: float


@dataclass
class Resultado:
    algoritmo: str
    quantum: int | None
    gantt: list = field(default_factory=list)      # lista de Segmento
    metricas: list = field(default_factory=list)   # lista de Metrica (orden de entrada)
    tiempo_total: float = 0                        # desde la primera llegada hasta el final
    tiempo_ocupado: float = 0                      # suma de tramos con CPU trabajando

    def _promedio(self, campo):
        return sum(getattr(m, campo) for m in self.metricas) / len(self.metricas)

    @property
    def espera_promedio(self):
        return self._promedio("espera")

    @property
    def retorno_promedio(self):
        return self._promedio("retorno")

    @property
    def respuesta_promedio(self):
        return self._promedio("respuesta")

    @property
    def utilizacion(self):
        """% del tiempo en que la CPU estuvo trabajando."""
        return 100 * self.tiempo_ocupado / self.tiempo_total if self.tiempo_total else 0

    @property
    def productividad(self):
        """Procesos terminados por unidad de tiempo."""
        return len(self.metricas) / self.tiempo_total if self.tiempo_total else 0

    def resumen(self):
        """Datos para sistema.registrar_resultado('planificacion', ...).
        La pestaña Resultados espera texto, así que todo va como str."""
        nombre = self.algoritmo + (f" (quantum {self.quantum})" if self.quantum else "")
        return {
            "Algoritmo": nombre,
            "Espera promedio": f"{self.espera_promedio:.2f}",
            "Retorno promedio": f"{self.retorno_promedio:.2f}",
            "Respuesta promedio": f"{self.respuesta_promedio:.2f}",
            "Uso de CPU": f"{self.utilizacion:.1f} %",
            "Productividad": f"{self.productividad:.3f} proc/unidad",
        }


@dataclass
class _P:
    """Copia interna de un proceso (solo lo que necesita la planificación)."""
    pid: str
    llegada: float
    rafaga: float
    orden: int  # posición original, para desempatar


# ---------------------------------------------------------------- validación
def _campo(proceso, clave):
    for nombre in _ALIAS[clave]:
        if isinstance(proceso, dict) and nombre in proceso:
            return proceso[nombre]
        if hasattr(proceso, nombre):
            return getattr(proceso, nombre)
    raise ValueError(f"Un proceso no tiene el campo '{_ALIAS[clave][0]}'.")


def _numero(valor, nombre, pid):
    try:
        n = float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{nombre} del proceso {pid} no es un número: {valor!r}.")
    if n != n or n in (float("inf"), float("-inf")):
        raise ValueError(f"{nombre} del proceso {pid} no es válido.")
    return int(n) if n == int(n) else n


def _preparar(procesos):
    """Valida y copia los procesos. Lanza ValueError con mensaje claro."""
    procesos = list(procesos or [])
    if not procesos:
        raise ValueError("No hay procesos para planificar. Cree al menos uno.")
    copias, vistos = [], set()
    for i, p in enumerate(procesos):
        pid = str(_campo(p, "pid"))
        if pid in vistos:
            raise ValueError(f"El ID {pid} está repetido.")
        vistos.add(pid)
        llegada = _numero(_campo(p, "llegada"), "La llegada", pid)
        rafaga = _numero(_campo(p, "rafaga"), "La ráfaga", pid)
        if llegada < 0:
            raise ValueError(f"La llegada del proceso {pid} no puede ser negativa.")
        if rafaga <= 0:
            raise ValueError(f"La ráfaga del proceso {pid} debe ser mayor que 0.")
        copias.append(_P(pid, llegada, rafaga, i))
    return copias


def _agregar(segmentos, pid, inicio, fin):
    """Agrega un tramo; si continúa el anterior del mismo proceso, lo une."""
    if segmentos and segmentos[-1].pid == pid and segmentos[-1].fin == inicio:
        segmentos[-1].fin = fin
    else:
        segmentos.append(Segmento(pid, inicio, fin))


def _armar(algoritmo, quantum, procs, segmentos):
    """Calcula las métricas a partir del Gantt (igual para los tres algoritmos)."""
    primera, final = {}, {}
    for s in segmentos:
        if s.pid == OCIOSO:
            continue
        primera.setdefault(s.pid, s.inicio)
        final[s.pid] = s.fin
    metricas = []
    for p in procs:
        retorno = final[p.pid] - p.llegada
        metricas.append(Metrica(
            pid=p.pid, llegada=p.llegada, rafaga=p.rafaga,
            primera_ejecucion=primera[p.pid], finalizacion=final[p.pid],
            espera=retorno - p.rafaga, retorno=retorno,
            respuesta=primera[p.pid] - p.llegada,
        ))
    inicio = min(p.llegada for p in procs)
    fin = max(s.fin for s in segmentos)
    ocupado = sum(s.fin - s.inicio for s in segmentos if s.pid != OCIOSO)
    return Resultado(algoritmo, quantum, segmentos, metricas, fin - inicio, ocupado)


# --------------------------------------------------------------- algoritmos
def fcfs(procesos):
    """First Come, First Served: en orden de llegada, sin interrupciones."""
    procs = _preparar(procesos)
    segmentos, t = [], 0
    for p in sorted(procs, key=lambda x: (x.llegada, x.orden)):
        if t < p.llegada:
            if t > 0 or segmentos:
                segmentos.append(Segmento(OCIOSO, t, p.llegada))
            t = p.llegada
        _agregar(segmentos, p.pid, t, t + p.rafaga)
        t += p.rafaga
    return _armar("FCFS", None, procs, segmentos)


def sjf(procesos):
    """Shortest Job First (no apropiativo): entre los que ya llegaron,
    corre el de menor ráfaga hasta terminar. Empate: el que llegó primero."""
    procs = _preparar(procesos)
    pendientes = list(procs)
    segmentos, t = [], min(p.llegada for p in procs)
    while pendientes:
        listos = [p for p in pendientes if p.llegada <= t]
        if not listos:
            siguiente = min(p.llegada for p in pendientes)
            segmentos.append(Segmento(OCIOSO, t, siguiente))
            t = siguiente
            continue
        p = min(listos, key=lambda x: (x.rafaga, x.llegada, x.orden))
        pendientes.remove(p)
        _agregar(segmentos, p.pid, t, t + p.rafaga)
        t += p.rafaga
    return _armar("SJF", None, procs, segmentos)


def round_robin(procesos, quantum):
    """Round Robin: cada proceso usa la CPU a lo sumo `quantum` unidades y,
    si no termina, vuelve al final de la cola. Si un proceso llega justo cuando
    otro agota su quantum, el que llega entra a la cola primero."""
    try:
        quantum = float(quantum)
    except (TypeError, ValueError):
        raise ValueError("El quantum debe ser un número.")
    if quantum <= 0:
        raise ValueError("El quantum debe ser mayor que 0.")
    quantum = int(quantum) if quantum == int(quantum) else quantum

    procs = _preparar(procesos)
    por_llegar = deque(sorted(procs, key=lambda x: (x.llegada, x.orden)))
    restante = {p.pid: p.rafaga for p in procs}
    cola, segmentos = deque(), []
    t, terminados = por_llegar[0].llegada, 0

    def admitir():
        while por_llegar and por_llegar[0].llegada <= t:
            cola.append(por_llegar.popleft())

    while terminados < len(procs):
        admitir()
        if not cola:
            siguiente = por_llegar[0].llegada
            segmentos.append(Segmento(OCIOSO, t, siguiente))
            t = siguiente
            continue
        p = cola.popleft()
        uso = min(quantum, restante[p.pid])
        _agregar(segmentos, p.pid, t, t + uso)
        t += uso
        restante[p.pid] -= uso
        admitir()                     # los que llegaron durante la ejecución
        if restante[p.pid] > 0:
            cola.append(p)            # y luego el que fue interrumpido
        else:
            terminados += 1
    return _armar("Round Robin", quantum, procs, segmentos)


ALGORITMOS = ("FCFS", "SJF", "Round Robin")


def simular(nombre, procesos, quantum=None):
    """Atajo: ejecuta el algoritmo por nombre (el que elige la interfaz)."""
    if nombre == "FCFS":
        return fcfs(procesos)
    if nombre == "SJF":
        return sjf(procesos)
    if nombre == "Round Robin":
        return round_robin(procesos, quantum)
    raise ValueError(f"Algoritmo desconocido: {nombre}")
