
from dataclasses import dataclass
 
ESTRATEGIAS = ("First Fit", "Best Fit", "Worst Fit")
 
DESCRIPCION_ESTRATEGIA = {
    "First Fit": "Usa el primer hueco libre donde cabe el proceso, recorriendo la memoria desde el inicio.",
    "Best Fit": "Usa el hueco más pequeño donde cabe el proceso; el sobrante que queda es el mínimo.",
    "Worst Fit": "Usa el hueco más grande; el sobrante que queda es grande y puede servir a otro proceso.",
}
 
 
@dataclass(eq=False)
class Bloque:
    inicio: int          # KB donde empieza
    tamano: int          # KB que ocupa
    pid: str | None = None   # None = hueco libre
 
    @property
    def libre(self) -> bool:
        return self.pid is None
 
    @property
    def fin(self) -> int:
        return self.inicio + self.tamano
 
 
class Memoria:
    def __init__(self, total: int):
        self.total = total
        self.bloques: list[Bloque] = []
        self.reiniciar()
 
    # ---------- Consultas ----------
    def huecos(self) -> list[Bloque]:
        return [b for b in self.bloques if b.libre]
 
    def ocupados(self) -> list[Bloque]:
        return [b for b in self.bloques if not b.libre]
 
    def bloque_de(self, pid: str) -> Bloque | None:
        for b in self.bloques:
            if b.pid == pid:
                return b
        return None
 
    def memoria_usada(self) -> int:
        return sum(b.tamano for b in self.ocupados())
 
    def memoria_libre(self) -> int:
        return sum(b.tamano for b in self.huecos())
 
    def hueco_mayor(self) -> int:
        tamanos = [b.tamano for b in self.huecos()]
        return max(tamanos) if tamanos else 0
 
    def fragmentacion_externa(self) -> float:
        """Porcentaje de la memoria libre que NO está en el hueco más grande."""
        libre = self.memoria_libre()
        if libre == 0:
            return 0.0
        return (1 - self.hueco_mayor() / libre) * 100
 
    # ---------- Estrategias ----------
    def elegir_hueco(self, tamano: int, estrategia: str) -> Bloque | None:
        """Devuelve el hueco elegido según la estrategia, o None si no cabe."""
        elegido = None
        for hueco in self.huecos():
            if hueco.tamano < tamano:
                continue                      # no cabe aquí
            if estrategia == "First Fit":
                return hueco                  # el primero que sirve
            if elegido is None:
                elegido = hueco
            elif estrategia == "Best Fit" and hueco.tamano < elegido.tamano:
                elegido = hueco               # uno más pequeño
            elif estrategia == "Worst Fit" and hueco.tamano > elegido.tamano:
                elegido = hueco               # uno más grande
        return elegido
 
    # ---------- Operaciones ----------
    def asignar(self, pid: str, tamano: int, estrategia: str) -> Bloque:
        """Coloca el proceso en memoria. Lanza ValueError si no se puede."""
        if estrategia not in ESTRATEGIAS:
            raise ValueError(f"Estrategia desconocida: {estrategia}.")
        if self.bloque_de(pid):
            raise ValueError(f"{pid} ya está en memoria.")
 
        hueco = self.elegir_hueco(tamano, estrategia)
        if hueco is None:
            libre = self.memoria_libre()
            if libre >= tamano:
                raise ValueError(
                    f"{pid} pide {tamano} KB. Hay {libre} KB libres, pero repartidos en "
                    f"{len(self.huecos())} huecos y el mayor es de {self.hueco_mayor()} KB "
                    f"(fragmentación externa).")
            raise ValueError(f"{pid} pide {tamano} KB y solo hay {libre} KB libres.")
 
        # El proceso ocupa el inicio del hueco; el resto sigue libre.
        nuevo = Bloque(hueco.inicio, tamano, pid)
        posicion = self.bloques.index(hueco)
        self.bloques.insert(posicion, nuevo)
        hueco.inicio += tamano
        hueco.tamano -= tamano
        if hueco.tamano == 0:
            self.bloques.remove(hueco)
        return nuevo
 
    def liberar(self, pid: str) -> None:
        bloque = self.bloque_de(pid)
        if bloque is None:
            raise ValueError(f"{pid} no está en memoria.")
        bloque.pid = None
        self._unir_huecos()
 
    def compactar(self) -> None:
        """Mueve todos los procesos al inicio y deja un solo hueco al final."""
        nuevos = []
        inicio = 0
        for b in self.ocupados():
            nuevos.append(Bloque(inicio, b.tamano, b.pid))
            inicio += b.tamano
        if inicio < self.total:
            nuevos.append(Bloque(inicio, self.total - inicio))
        self.bloques = nuevos
 
    def reiniciar(self) -> None:
        self.bloques = [Bloque(0, self.total)]
 
    def quitar_ausentes(self, pids_validos: list[str]) -> list[str]:
        """Libera los bloques de procesos que ya no existen en la pestaña Procesos."""
        quitados = [b.pid for b in self.ocupados() if b.pid not in pids_validos]
        for pid in quitados:
            self.liberar(pid)
        return quitados
 
    def _unir_huecos(self) -> None:
        """Une huecos libres que quedaron uno al lado del otro."""
        unidos: list[Bloque] = []
        for b in self.bloques:
            if unidos and unidos[-1].libre and b.libre:
                unidos[-1].tamano += b.tamano
            else:
                unidos.append(b)
        self.bloques = unidos
 