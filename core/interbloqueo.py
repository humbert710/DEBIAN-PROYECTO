"""
Módulo de Interbloqueos — LÓGICA.

Modelo: grafo de asignación de recursos con recursos de UNA sola instancia.
Con una instancia por recurso, un ciclo en el grafo equivale a un deadlock.

    asignación:  recurso  ->  proceso   (el proceso TIENE el recurso)
    solicitud:   proceso  ->  recurso   (el proceso ESPERA el recurso)

Estrategia implementada: DETECCIÓN (búsqueda de ciclos con DFS sobre el
grafo de espera) y RECUPERACIÓN (terminar un proceso del ciclo y liberar
sus recursos).

La interfaz vive en ui/tab_interbloqueo.py; aquí no se importa tkinter,
así este archivo se puede probar y explicar por separado.
"""
from dataclasses import dataclass


@dataclass
class Ciclo:
    """Ciclo encontrado. Cada arista es (proceso_que_espera, recurso, titular)."""
    aristas: list[tuple[str, str, str]]

    @property
    def procesos(self) -> list[str]:
        return [p for p, _, _ in self.aristas]

    @property
    def recursos(self) -> list[str]:
        return [r for _, r, _ in self.aristas]

    def texto(self) -> str:
        """Ej.: 'P1 → R2 → P2 → R1 → P1'"""
        partes = []
        for p, r, _ in self.aristas:
            partes += [p, r]
        partes.append(self.aristas[0][0])
        return " → ".join(partes)


class GrafoRecursos:
    def __init__(self):
        self.reiniciar()

    # ------------------------------------------------------------------
    # Construcción del grafo
    # ------------------------------------------------------------------
    def reiniciar(self) -> None:
        self.procesos: list[str] = []
        self.recursos: list[str] = []
        self.asignaciones: dict[str, str] = {}          # recurso -> proceso
        self.solicitudes: list[tuple[str, str]] = []    # (proceso, recurso), orden de llegada

    def agregar_proceso(self, pid: str | None = None) -> str:
        if pid is None:
            n = 1
            while f"P{n}" in self.procesos:
                n += 1
            pid = f"P{n}"
        if pid in self.procesos:
            raise ValueError(f"Ya existe el proceso {pid}.")
        self.procesos.append(pid)
        return pid

    def agregar_recurso(self, rid: str | None = None) -> str:
        if rid is None:
            n = 1
            while f"R{n}" in self.recursos:
                n += 1
            rid = f"R{n}"
        if rid in self.recursos:
            raise ValueError(f"Ya existe el recurso {rid}.")
        self.recursos.append(rid)
        return rid

    def solicitar(self, pid: str, rid: str) -> str:
        """El proceso pide un recurso.

        Devuelve 'asignado' si estaba libre o 'espera' si lo tiene otro proceso.
        """
        self._validar(pid, rid)
        if self.asignaciones.get(rid) == pid:
            raise ValueError(f"{pid} ya tiene el recurso {rid}.")
        if (pid, rid) in self.solicitudes:
            raise ValueError(f"{pid} ya está esperando el recurso {rid}.")
        if rid not in self.asignaciones:
            self.asignaciones[rid] = pid
            return "asignado"
        self.solicitudes.append((pid, rid))
        return "espera"

    def liberar(self, rid: str) -> tuple[str, str] | None:
        """Libera un recurso. Si alguien lo esperaba, se lo da al primero de la fila.

        Devuelve (proceso, recurso) del que lo recibe, o None.
        """
        if rid not in self.asignaciones:
            raise ValueError(f"El recurso {rid} ya está libre.")
        del self.asignaciones[rid]
        return self._entregar(rid)

    def _entregar(self, rid: str) -> tuple[str, str] | None:
        for solicitud in self.solicitudes:
            if solicitud[1] == rid:
                self.solicitudes.remove(solicitud)
                self.asignaciones[rid] = solicitud[0]
                return solicitud
        return None

    def _validar(self, pid: str, rid: str) -> None:
        if pid not in self.procesos:
            raise ValueError(f"No existe el proceso {pid}.")
        if rid not in self.recursos:
            raise ValueError(f"No existe el recurso {rid}.")

    def recursos_de(self, pid: str) -> list[str]:
        return [r for r, p in self.asignaciones.items() if p == pid]

    # ------------------------------------------------------------------
    # Escenarios
    # ------------------------------------------------------------------
    def cargar_procesos(self, pids: list[str]) -> int:
        """Agrega al grafo los procesos que aún no estén. Devuelve cuántos agregó."""
        nuevos = 0
        for pid in pids:
            if pid not in self.procesos:
                self.procesos.append(pid)
                nuevos += 1
        return nuevos

    def provocar_deadlock(self, pids: list[str] | None = None) -> str:
        """Arma el deadlock clásico con dos procesos y dos recursos.

            A tiene R1 y pide R2   |   B tiene R2 y pide R1

        Si se pasan al menos 2 pids se usan los dos primeros; si no, P1 y P2.
        Devuelve una descripción del escenario.
        """
        a, b = pids[:2] if pids and len(pids) >= 2 else ("P1", "P2")
        self.reiniciar()
        self.agregar_proceso(a)
        self.agregar_proceso(b)
        self.agregar_recurso("R1")
        self.agregar_recurso("R2")
        self.solicitar(a, "R1")
        self.solicitar(b, "R2")
        self.solicitar(a, "R2")
        self.solicitar(b, "R1")
        return f"{a} tiene R1 y pide R2; {b} tiene R2 y pide R1."

    # ------------------------------------------------------------------
    # Detección
    # ------------------------------------------------------------------
    def _grafo_espera(self) -> dict[str, list[tuple[str, str]]]:
        """proceso -> [(recurso que pide, proceso que lo tiene)]"""
        espera: dict[str, list[tuple[str, str]]] = {p: [] for p in self.procesos}
        for pid, rid in self.solicitudes:
            titular = self.asignaciones.get(rid)
            if titular is not None and titular != pid:
                espera[pid].append((rid, titular))
        return espera

    def detectar_ciclo(self) -> Ciclo | None:
        """DFS sobre el grafo de espera. Devuelve el primer ciclo o None."""
        espera = self._grafo_espera()
        color: dict[str, int] = {}          # 0 sin visitar, 1 en curso, 2 terminado
        camino: list[tuple[str, str, str]] = []

        def dfs(p: str):
            color[p] = 1
            for rid, titular in espera[p]:
                arista = (p, rid, titular)
                if color.get(titular, 0) == 1:          # volvimos a un nodo del camino
                    camino.append(arista)
                    inicio = next(i for i, (a, _, _) in enumerate(camino) if a == titular)
                    return camino[inicio:]
                if color.get(titular, 0) == 0:
                    camino.append(arista)
                    ciclo = dfs(titular)
                    if ciclo:
                        return ciclo
                    camino.pop()
            color[p] = 2
            return None

        for p in self.procesos:
            if color.get(p, 0) == 0:
                aristas = dfs(p)
                if aristas:
                    return Ciclo(aristas)
        return None

    def coffman(self) -> list[tuple[str, str, bool]]:
        """Las 4 condiciones de Coffman evaluadas sobre el estado ACTUAL.

        Devuelve [(nombre, explicación, se_cumple)]. Hay deadlock solo si
        se cumplen las cuatro a la vez.
        """
        espera = self._grafo_espera()
        hay_espera = any(espera.values())
        retiene_y_espera = any(espera[p] and self.recursos_de(p) for p in self.procesos)
        return [
            ("Exclusión mutua",
             "un recurso, un proceso a la vez.",
             bool(self.asignaciones)),
            ("Retención y espera",
             "retiene uno y pide otro.",
             retiene_y_espera),
            ("No apropiación",
             "no se puede quitar a la fuerza.",
             hay_espera),
            ("Espera circular",
             "procesos esperándose en círculo.",
             self.detectar_ciclo() is not None),
        ]

    # ------------------------------------------------------------------
    # Recuperación
    # ------------------------------------------------------------------
    def elegir_victima(self, ciclo: Ciclo) -> str:
        """Del ciclo, el proceso que retiene MENOS recursos (menor costo de terminarlo)."""
        return min(ciclo.procesos, key=lambda p: (len(self.recursos_de(p)), p))

    def terminar_proceso(self, pid: str) -> list[tuple[str, str]]:
        """Elimina el proceso, libera sus recursos y se los entrega a quien esperaba.

        Devuelve la lista de (proceso, recurso) que recibieron un recurso.
        """
        if pid not in self.procesos:
            raise ValueError(f"No existe el proceso {pid}.")
        liberados = self.recursos_de(pid)
        self.procesos.remove(pid)
        self.solicitudes = [s for s in self.solicitudes if s[0] != pid]
        for rid in liberados:
            del self.asignaciones[rid]
        entregas = []
        for rid in liberados:
            entrega = self._entregar(rid)
            if entrega:
                entregas.append(entrega)
        return entregas

    def recuperar(self) -> tuple[str, list[str], list[tuple[str, str]]] | None:
        """Detección + recuperación: termina un proceso del ciclo.

        Devuelve (proceso_terminado, recursos_liberados, entregas) o None si no hay deadlock.
        """
        ciclo = self.detectar_ciclo()
        if ciclo is None:
            return None
        victima = self.elegir_victima(ciclo)
        liberados = self.recursos_de(victima)
        entregas = self.terminar_proceso(victima)
        return victima, liberados, entregas
