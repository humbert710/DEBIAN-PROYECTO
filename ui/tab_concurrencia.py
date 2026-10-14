"""
Pestaña 3 — Concurrencia y sincronización.

Corre core/concurrencia.py en hilos aparte y compara el saldo de una
cuenta compartida sin sincronización y con threading.Lock.
"""
import queue
import threading
import tkinter as tk

from core import concurrencia
from ui import tema

# Colores del tema compartido; los que tema.py quizá no define llevan valor por defecto.
BG = tema.FONDO
FG = tema.TEXTO
MUTED = tema.TEXTO_SUAVE
ACCENT = tema.ACENTO
PANEL = getattr(tema, "PANEL", "#22262e")
BORDE = getattr(tema, "BORDE", "#343a46")
OK = getattr(tema, "OK", "#3fb950")
MAL = getattr(tema, "ERROR", "#e5484d")
MONO = ("Consolas", 12)


class _Panel(tk.Frame):
    """Un escenario (sin sincronización o con Lock)."""

    CAMPOS = (
        ("esperado", "Valor esperado"),
        ("obtenido", "Valor obtenido"),
        ("diferencia", "Diferencia"),
        ("tiempo", "Tiempo (s)"),
    )

    def __init__(self, parent, titulo, descripcion):
        super().__init__(parent, bg=PANEL, highlightbackground=BORDE,
                         highlightthickness=1)
        tk.Label(self, text=titulo, bg=PANEL, fg=FG,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(12, 0))
        tk.Label(self, text=descripcion, bg=PANEL, fg=MUTED, wraplength=380,
                 justify="left").pack(anchor="w", padx=14, pady=(2, 10))
        self._vals = {}
        for clave, etiqueta in self.CAMPOS:
            fila = tk.Frame(self, bg=PANEL)
            fila.pack(fill="x", padx=14, pady=3)
            tk.Label(fila, text=etiqueta, bg=PANEL, fg=MUTED).pack(side="left")
            lbl = tk.Label(fila, text="—", bg=PANEL, fg=FG, font=MONO)
            lbl.pack(side="right")
            self._vals[clave] = lbl
        self.estado = tk.Label(self, text="Sin ejecutar", bg=PANEL, fg=MUTED,
                               font=("Segoe UI", 11, "bold"))
        self.estado.pack(anchor="w", padx=14, pady=(10, 14))

    def limpiar(self):
        for lbl in self._vals.values():
            lbl.config(text="—", fg=FG)
        self.estado.config(text="Sin ejecutar", fg=MUTED)

    def ejecutando(self):
        self.limpiar()
        self.estado.config(text="Ejecutando hilos...", fg=MUTED)

    def mostrar(self, r):
        color = OK if r["correcto"] else MAL
        self._vals["esperado"].config(text=f"{r['esperado']:,}")
        self._vals["obtenido"].config(text=f"{r['obtenido']:,}", fg=color)
        self._vals["diferencia"].config(text=f"{r['diferencia']:+,}", fg=color)
        self._vals["tiempo"].config(text=f"{r['tiempo_s']}")
        self.estado.config(
            text="Correcto: saldo consistente" if r["correcto"]
            else "Condición de carrera: saldo incorrecto",
            fg=color)


class TabConcurrencia(tk.Frame):
    def __init__(self, parent, sistema=None):
        super().__init__(parent, bg=BG)
        self.sistema = sistema
        self._cola = queue.Queue()
        self._resultados = {}
        self._construir()
        self.after(100, self._sondear)  # arranca el sondeo en el hilo principal

    # ---------- construcción ----------
    def _construir(self):
        tk.Label(self, text="Concurrencia y sincronización", bg=BG, fg=FG,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=30, pady=(24, 0))
        tk.Label(self, text="Cuenta bancaria compartida por varios hilos "
                 "(threading.Thread)", bg=BG, fg=MUTED).pack(anchor="w", padx=30)

        barra = tk.Frame(self, bg=BG)
        barra.pack(fill="x", padx=30, pady=16)
        self._hilos = self._spin(barra, "Hilos", 2, 32, 8)
        self._ops = self._spin(barra, "Operaciones por hilo", 100, 20000, 2000)
        self._saldo = self._spin(barra, "Saldo inicial", 0, 1000000, 1000)
        self.btn = tk.Button(barra, text="Ejecutar simulación", command=self._ejecutar,
                             bg=ACCENT, fg="white", relief="flat", padx=14, pady=4)
        self.btn.pack(side="right")

        paneles = tk.Frame(self, bg=BG)
        paneles.pack(fill="x", padx=30)
        paneles.columnconfigure((0, 1), weight=1, uniform="p")
        self.p_sin = _Panel(paneles, "Sin sincronización",
                            "Los hilos leen y escriben el saldo sin protección.")
        self.p_con = _Panel(paneles, "Con Lock",
                            "La sección crítica se protege con threading.Lock.")
        self.p_sin.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.p_con.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self.conclusion = tk.Label(self, text="", bg=BG, fg=MUTED, wraplength=900,
                                   justify="left")
        self.conclusion.pack(anchor="w", padx=30, pady=14)

    def _spin(self, parent, texto, minimo, maximo, valor):
        tk.Label(parent, text=texto, bg=BG, fg=MUTED).pack(side="left")
        sp = tk.Spinbox(parent, from_=minimo, to=maximo, width=8)
        sp.delete(0, "end")
        sp.insert(0, valor)
        sp.pack(side="left", padx=(6, 18))
        return sp

    # ---------- ejecución ----------
    def _leer(self, spin, defecto):
        try:
            return max(0, int(spin.get()))
        except ValueError:
            return defecto

    def _ejecutar(self):
        n = max(2, self._leer(self._hilos, 8))
        ops = max(1, self._leer(self._ops, 2000))
        saldo = self._leer(self._saldo, 1000)

        self.btn.config(state="disabled")
        self.conclusion.config(text="")
        self._resultados = {}
        self.p_sin.ejecutando()
        self.p_con.ejecutando()

        for clave, usar_lock in (("sin_sincronizacion", False), ("con_lock", True)):
            threading.Thread(target=self._correr, daemon=True,
                             args=(clave, usar_lock, n, ops, saldo)).start()

    def _correr(self, clave, usar_lock, n, ops, saldo):
        # Corre en un hilo secundario: solo deja datos en la cola.
        r = concurrencia.simular(usar_lock, n_hilos=n, operaciones=ops,
                                 saldo_inicial=saldo)
        self._cola.put((clave, r))

    # ---------- actualización de la interfaz (hilo principal) ----------
    def _sondear(self):
        while True:
            try:
                clave, r = self._cola.get_nowait()
            except queue.Empty:
                break
            (self.p_sin if clave == "sin_sincronizacion" else self.p_con).mostrar(r)
            self._resultados[clave] = r
            if len(self._resultados) == 2:
                self._terminar()
        self.after(100, self._sondear)

    def _terminar(self):
        sin, con = self._resultados["sin_sincronizacion"], self._resultados["con_lock"]
        if not sin["correcto"] and con["correcto"]:
            msg = ("Sin Lock el saldo se desvió "
                   f"{sin['diferencia']:+,} unidades (condición de carrera). "
                   "Con Lock el resultado coincide con el esperado.")
        elif sin["correcto"]:
            msg = ("Esta vez no se observó la carrera sin Lock (es no determinista). "
                   "Sube hilos u operaciones y vuelve a ejecutar.")
        else:
            msg = "Revisar: el escenario con Lock no coincidió con el valor esperado."
        self.conclusion.config(text=msg)
        self.btn.config(state="normal")
        if self.sistema is not None:
            self.sistema.registrar_resultado("concurrencia", {
                "sin_sincronizacion": sin,
                "con_lock": con,
            })