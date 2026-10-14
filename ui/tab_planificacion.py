"""
Pestaña 2 — Planificación del procesador.

Simula FCFS, SJF (no expropiativo) y Round Robin sobre COPIAS de
`sistema.procesos`. Muestra el diagrama de Gantt, los tiempos de espera,
retorno y respuesta por proceso, sus promedios y una comparación de los 3
algoritmos. La lógica está en core/planificacion.py.
"""
import tkinter as tk
from tkinter import messagebox, ttk

from core.planificacion import ALGORITMOS, OCIOSO, simular
from core.sistema import Sistema
from ui import tema


class TabPlanificacion(ttk.Frame):
    def __init__(self, parent, sistema: Sistema):
        super().__init__(parent, padding=10)
        self.sistema = sistema
        self._estilo_combobox()
        self.resultado = None
        self._publicando = False   # evita borrar la pantalla al publicar resultados
        self._huella = None        # datos de los procesos con los que se simuló
        self._crear_controles()
        self._crear_gantt()
        self._crear_comparacion()
        self._crear_tabla()
        sistema.suscribir(self.refrescar)
        self.refrescar()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _estilo_combobox(self):
        estilo = ttk.Style(self)
        estilo.configure("Compacto.Treeview", rowheight=22)
        estilo.configure("Compacto.Treeview.Heading", padding=3)
        estilo.map("TCombobox",
                   fieldbackground=[("readonly", "#1a1b20")],
                   foreground=[("readonly", tema.TEXTO)],
                   selectbackground=[("readonly", "#1a1b20")],
                   selectforeground=[("readonly", tema.TEXTO)])
        self.option_add("*TCombobox*Listbox.background", tema.PANEL)
        self.option_add("*TCombobox*Listbox.foreground", tema.TEXTO)
        self.option_add("*TCombobox*Listbox.selectBackground", tema.ACENTO)
        self.option_add("*TCombobox*Listbox.selectForeground", "white")

    def _crear_controles(self):
        caja = ttk.Frame(self, style="Panel.TFrame", padding=8)
        caja.pack(fill="x")

        ttk.Label(caja, text="Algoritmo", style="Panel.TLabel").grid(row=0, column=0, sticky="w")
        self.var_alg = tk.StringVar(value=ALGORITMOS[0])
        combo = ttk.Combobox(caja, textvariable=self.var_alg, values=ALGORITMOS,
                             state="readonly", width=14)
        combo.grid(row=0, column=1, sticky="w", padx=(8, 18))
        combo.bind("<<ComboboxSelected>>", lambda _e: self._actualizar_quantum())

        ttk.Label(caja, text="Quantum", style="Panel.TLabel").grid(row=0, column=2, sticky="w")
        self.var_q = tk.StringVar(value="3")
        self.entrada_q = ttk.Spinbox(caja, from_=1, to=999, width=6, textvariable=self.var_q)
        self.entrada_q.grid(row=0, column=3, sticky="w", padx=(8, 18))

        ttk.Button(caja, text="▶  Simular", style="Acento.TButton",
                   command=self.simular).grid(row=0, column=4, padx=(0, 8))
        ttk.Button(caja, text="Comparar los 3",
                   command=self.comparar).grid(row=0, column=5)
        ttk.Label(caja, text="   (el quantum solo se usa con Round Robin)",
                  style="PanelSuave.TLabel").grid(row=0, column=6, sticky="w")
        self._actualizar_quantum()

    def _crear_gantt(self):
        caja = ttk.LabelFrame(self, text="  Diagrama de Gantt  ", padding=8)
        caja.pack(fill="x", pady=(6, 0))
        self.canvas = tk.Canvas(caja, height=76, bg="#1a1b20", highlightthickness=0)
        scroll = ttk.Scrollbar(caja, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=scroll.set)
        self.canvas.pack(fill="x")
        self.scroll = scroll   # solo se muestra si el Gantt no cabe

    def _crear_tabla(self):
        caja = ttk.LabelFrame(self, text="  Tiempos por proceso  ", padding=8)
        caja.pack(fill="both", expand=True, pady=(6, 0))
        cols = ("pid", "llegada", "rafaga", "primera", "fin", "espera", "retorno", "respuesta")
        nombres = ("Proceso", "Llegada", "Ráfaga", "1.ª ejecución", "Finaliza",
                   "Espera", "Retorno", "Respuesta")
        self.var_prom = tk.StringVar()
        ttk.Label(caja, textvariable=self.var_prom, style="Panel.TLabel",
                  font=tema.FUENTE_NEGRITA, wraplength=980, justify="left"
                  ).pack(side="bottom", anchor="w", pady=(8, 0))
        self.tabla = ttk.Treeview(caja, columns=cols, show="headings", height=4, style="Compacto.Treeview")
        for c, n in zip(cols, nombres):
            self.tabla.heading(c, text=n)
            self.tabla.column(c, width=90, anchor="center")
        self.tabla.pack(fill="both", expand=True)

    def _crear_comparacion(self):
        caja = ttk.LabelFrame(self, text="  Comparación de algoritmos  ", padding=8)
        caja.pack(side="bottom", fill="x", pady=(6, 0))
        cols = ("alg", "espera", "retorno", "respuesta", "util", "prod")
        nombres = ("Algoritmo", "Espera prom.", "Retorno prom.", "Respuesta prom.",
                   "Uso CPU %", "Procesos / unidad")
        self.tabla_c = ttk.Treeview(caja, columns=cols, show="headings", height=3, style="Compacto.Treeview")
        for c, n in zip(cols, nombres):
            self.tabla_c.heading(c, text=n)
            self.tabla_c.column(c, width=120, anchor="center")
        self.tabla_c.pack(fill="x")

    def _actualizar_quantum(self):
        estado = "normal" if self.var_alg.get() == "Round Robin" else "disabled"
        self.entrada_q.configure(state=estado)

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    def _procesos(self):
        """Copias de los procesos: la lista original no se toca."""
        return [p.copia() for p in self.sistema.procesos]

    def simular(self):
        quantum = self.var_q.get() if self.var_alg.get() == "Round Robin" else None
        try:
            self.resultado = simular(self.var_alg.get(), self._procesos(), quantum)
        except ValueError as error:
            messagebox.showwarning("Planificación", str(error), parent=self)
            return
        self._mostrar(self.resultado)
        self._publicar(self.resultado)

    def comparar(self):
        try:
            quantum = self.var_q.get()
            resultados = [simular(a, self._procesos(), quantum) for a in ALGORITMOS]
        except ValueError as error:
            messagebox.showwarning("Planificación", str(error), parent=self)
            return
        self.tabla_c.delete(*self.tabla_c.get_children())
        for r in resultados:
            nombre = r.algoritmo + (f" (q={r.quantum})" if r.quantum else "")
            self.tabla_c.insert("", "end", values=(
                nombre, f"{r.espera_promedio:.2f}", f"{r.retorno_promedio:.2f}",
                f"{r.respuesta_promedio:.2f}", f"{r.utilizacion:.1f}",
                f"{r.productividad:.3f}"))

    def _publicar(self, r):
        """Envía el resumen a la pestaña Resultados."""
        self._publicando = True
        try:
            self.sistema.registrar_resultado("planificacion", r.resumen())
        finally:
            self._publicando = False

    def _huella_procesos(self):
        return tuple((p.pid, p.llegada, p.rafaga) for p in self.sistema.procesos)

    def refrescar(self):
        """Se llama cuando cambian los procesos: los resultados viejos ya no valen.

        Sistema también avisa cuando otro módulo publica resultados; en ese caso
        los procesos no cambiaron y la simulación en pantalla se conserva."""
        if self._publicando:
            return
        huella = self._huella_procesos()
        if huella == self._huella:
            return
        self._huella = huella
        self.resultado = None
        self.tabla.delete(*self.tabla.get_children())
        self.tabla_c.delete(*self.tabla_c.get_children())
        self.canvas.delete("all")
        n = len(self.sistema.procesos)
        self.var_prom.set(
            f"{n} proceso(s) listos. Elija un algoritmo y pulse «Simular»." if n
            else "No hay procesos. Créelos en la pestaña «1 · Procesos» (o use «Cargar ejemplo»).")

    # ------------------------------------------------------------------
    # Resultados y dibujo
    # ------------------------------------------------------------------
    def _mostrar(self, r):
        self.tabla.delete(*self.tabla.get_children())
        for m in r.metricas:
            self.tabla.insert("", "end", values=(
                m.pid, m.llegada, m.rafaga, m.primera_ejecucion, m.finalizacion,
                m.espera, m.retorno, m.respuesta))
        q = f" (quantum {r.quantum})" if r.quantum else ""
        self.var_prom.set(
            f"{r.algoritmo}{q}  |  Espera: {r.espera_promedio:.2f}   "
            f"Retorno: {r.retorno_promedio:.2f}   Respuesta: {r.respuesta_promedio:.2f}  |  "
            f"CPU: {r.utilizacion:.1f} %   {r.productividad:.3f} proc/unidad")
        self._dibujar_gantt(r)

    def _dibujar_gantt(self, r):
        c = self.canvas
        c.delete("all")
        color = {m.pid: tema.color_proceso(i) for i, m in enumerate(r.metricas)}
        color[OCIOSO] = tema.BORDE

        inicio, fin = r.gantt[0].inicio, r.gantt[-1].fin
        total = max(fin - inicio, 1)
        escala = max(24, min(60, 1000 / total))   # píxeles por unidad de tiempo
        x0, y0, alto = 20, 8, 34

        for s in r.gantt:
            xa = x0 + (s.inicio - inicio) * escala
            xb = x0 + (s.fin - inicio) * escala
            c.create_rectangle(xa, y0, xb, y0 + alto, fill=color[s.pid], outline=tema.FONDO)
            ocioso = s.pid == OCIOSO
            c.create_text((xa + xb) / 2, y0 + alto / 2, text="—" if ocioso else s.pid,
                          fill=tema.TEXTO_SUAVE if ocioso else tema.FONDO,
                          font=tema.FUENTE_NEGRITA)
            c.create_text(xa, y0 + alto + 14, text=f"{s.inicio:g}", fill=tema.TEXTO_SUAVE)
        c.create_text(x0 + (fin - inicio) * escala, y0 + alto + 14,
                      text=f"{fin:g}", fill=tema.TEXTO_SUAVE)
        ancho = x0 * 2 + total * escala
        c.configure(scrollregion=(0, 0, ancho, 70))
        c.update_idletasks()
        if ancho > c.winfo_width():
            self.scroll.pack(fill="x")
        else:
            self.scroll.pack_forget()

