
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
 
