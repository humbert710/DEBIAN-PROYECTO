
import tkinter as tk
from tkinter import messagebox, ttk

from core.memoria import DESCRIPCION_ESTRATEGIA, ESTRATEGIAS, Memoria
from core.sistema import Sistema
from ui import tema


class TabMemoria(ttk.Frame):
    def __init__(self, parent, sistema: Sistema):
        super().__init__(parent, padding=10)
        self.sistema = sistema
        self.memoria = Memoria(sistema.memoria_total)
        self._publicando = False   # evita refrescar de más al publicar resultados
        self._crear_controles()
        self._crear_barra()
        self._crear_tablas()
        sistema.suscribir(self.refrescar)
        self.refrescar()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _crear_controles(self):
        caja = ttk.Frame(self, style="Panel.TFrame", padding=8)
        caja.pack(fill="x")

        ttk.Label(caja, text="Estrategia", style="Panel.TLabel").grid(row=0, column=0, sticky="w")
        self.var_estrategia = tk.StringVar(value=ESTRATEGIAS[0])
        combo = ttk.Combobox(caja, textvariable=self.var_estrategia, values=ESTRATEGIAS,
                             state="readonly", width=12)
        combo.grid(row=0, column=1, sticky="w", padx=(8, 18))
        combo.bind("<<ComboboxSelected>>", lambda _e: self._actualizar_descripcion())

        ttk.Button(caja, text="▶  Asignar seleccionado", style="Acento.TButton",
                   command=self.asignar).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(caja, text="Asignar todos", command=self.asignar_todos).grid(row=0, column=3, padx=(0, 8))
        ttk.Button(caja, text="Liberar seleccionado", command=self.liberar).grid(row=0, column=4, padx=(0, 8))
        ttk.Button(caja, text="Compactar", command=self.compactar).grid(row=0, column=5, padx=(0, 8))
        ttk.Button(caja, text="Reiniciar", command=self.reiniciar).grid(row=0, column=6)

        self.var_desc = tk.StringVar()
        ttk.Label(caja, textvariable=self.var_desc, style="PanelSuave.TLabel").grid(
            row=1, column=0, columnspan=7, sticky="w", pady=(6, 0))
        self._actualizar_descripcion()

    def _crear_barra(self):
        caja = ttk.LabelFrame(self, text=f"  RAM simulada ({self.memoria.total} KB)  ", padding=8)
        caja.pack(fill="x", pady=(6, 0))
        self.canvas = tk.Canvas(caja, height=80, bg="#1a1b20", highlightthickness=0)
        self.canvas.pack(fill="x")
        self.canvas.bind("<Configure>", lambda _e: self._dibujar())
        self.var_stats = tk.StringVar()
        ttk.Label(caja, textvariable=self.var_stats, style="Panel.TLabel",
                  font=tema.FUENTE_NEGRITA).pack(anchor="w", pady=(6, 0))

    def _crear_tablas(self):
        fila = ttk.Frame(self)
        fila.pack(fill="both", expand=True, pady=(6, 0))
        fila.columnconfigure((0, 1), weight=1, uniform="t")
        fila.rowconfigure(0, weight=1)

        caja_p = ttk.LabelFrame(fila, text="  Procesos  ", padding=8)
        caja_p.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.tabla_p = ttk.Treeview(caja_p, columns=("pid", "memoria", "estado"),
                                    show="headings", selectmode="browse")
        for col, titulo in (("pid", "Proceso"), ("memoria", "Pide (KB)"), ("estado", "En memoria")):
            self.tabla_p.heading(col, text=titulo)
            self.tabla_p.column(col, anchor="center", width=100)
        self.tabla_p.pack(fill="both", expand=True)

        caja_b = ttk.LabelFrame(fila, text="  Bloques de memoria  ", padding=8)
        caja_b.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        self.tabla_b = ttk.Treeview(caja_b, columns=("inicio", "fin", "tamano", "uso"),
                                    show="headings", selectmode="none")
        for col, titulo in (("inicio", "Inicio (KB)"), ("fin", "Fin (KB)"),
                            ("tamano", "Tamaño (KB)"), ("uso", "Contenido")):
            self.tabla_b.heading(col, text=titulo)
            self.tabla_b.column(col, anchor="center", width=90)
        self.tabla_b.pack(fill="both", expand=True)

    def _actualizar_descripcion(self):
        self.var_desc.set(DESCRIPCION_ESTRATEGIA[self.var_estrategia.get()])

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    def _proceso_seleccionado(self):
        seleccion = self.tabla_p.selection()
        if not seleccion:
            messagebox.showinfo("Memoria", "Seleccione un proceso de la tabla.", parent=self)
            return None
        return next((p for p in self.sistema.procesos if p.pid == seleccion[0]), None)

    def asignar(self):
        p = self._proceso_seleccionado()
        if p is None:
            return
        try:
            self.memoria.asignar(p.pid, p.memoria, self.var_estrategia.get())
        except ValueError as error:
            messagebox.showwarning("Memoria", str(error), parent=self)
        self._actualizar()

    def asignar_todos(self):
        """Asigna en orden de la lista a todos los que aún no están en memoria."""
        fallos = []
        for p in self.sistema.procesos:
            if self.memoria.bloque_de(p.pid):
                continue
            try:
                self.memoria.asignar(p.pid, p.memoria, self.var_estrategia.get())
            except ValueError as error:
                fallos.append(str(error))
        self._actualizar()
        if fallos:
            messagebox.showwarning("Memoria", "No se pudo asignar:\n\n" + "\n\n".join(fallos), parent=self)

    def liberar(self):
        p = self._proceso_seleccionado()
        if p is None:
            return
        try:
            self.memoria.liberar(p.pid)
        except ValueError as error:
            messagebox.showwarning("Memoria", str(error), parent=self)
        self._actualizar()

    def compactar(self):
        self.memoria.compactar()
        self._actualizar()

    def reiniciar(self):
        self.memoria.reiniciar()
        self._actualizar()

    def refrescar(self):
        """Se llama cuando cambian los procesos: libera los que ya no existen."""
        if self._publicando:
            return
        quitados = self.memoria.quitar_ausentes([p.pid for p in self.sistema.procesos])
        self._mostrar()
        if quitados:
            self.after_idle(self._publicar)   # fuera del aviso en curso

    def _actualizar(self):
        self._mostrar()
        self._publicar()

    def _publicar(self):
        """Envía el estado de la memoria a la pestaña Resultados."""
        m = self.memoria
        self._publicando = True
        try:
            self.sistema.registrar_resultado("memoria", {
                "Estrategia": self.var_estrategia.get(),
                "Procesos en memoria": str(len(m.ocupados())),
                "Memoria usada": f"{m.memoria_usada()} KB",
                "Memoria libre": f"{m.memoria_libre()} KB",
                "Huecos libres": str(len(m.huecos())),
                "Fragmentación externa": f"{m.fragmentacion_externa():.1f} %",
            })
        finally:
            self._publicando = False

    # ------------------------------------------------------------------
    # Resultados y dibujo
    # ------------------------------------------------------------------
    def _colores(self):
        return {p.pid: tema.color_proceso(i) for i, p in enumerate(self.sistema.procesos)}

    def _mostrar(self):
        m = self.memoria
        seleccion = self.tabla_p.selection()
        self.tabla_p.delete(*self.tabla_p.get_children())
        for p in self.sistema.procesos:
            b = m.bloque_de(p.pid)
            self.tabla_p.insert("", "end", iid=p.pid, values=(
                p.pid, p.memoria, f"Sí ({b.inicio}–{b.fin})" if b else "No"))
        if seleccion and self.tabla_p.exists(seleccion[0]):
            self.tabla_p.selection_set(seleccion[0])

        self.tabla_b.delete(*self.tabla_b.get_children())
        for b in m.bloques:
            self.tabla_b.insert("", "end", values=(
                b.inicio, b.fin, b.tamano, "Libre" if b.libre else b.pid))

        self.var_stats.set(
            f"Usada: {m.memoria_usada()} KB   Libre: {m.memoria_libre()} KB   "
            f"Huecos: {len(m.huecos())}   Hueco mayor: {m.hueco_mayor()} KB   "
            f"Fragmentación externa: {m.fragmentacion_externa():.1f} %")
        self._dibujar()

    def _dibujar(self):
        c = self.canvas
        c.delete("all")
        ancho = max(c.winfo_width(), 200)
        x0, y0, alto = 10, 8, 40
        escala = (ancho - 2 * x0) / self.memoria.total
        colores = self._colores()

        for b in self.memoria.bloques:
            xa = x0 + b.inicio * escala
            xb = x0 + b.fin * escala
            relleno = tema.PANEL if b.libre else colores.get(b.pid, tema.ACENTO)
            c.create_rectangle(xa, y0, xb, y0 + alto, fill=relleno, outline=tema.FONDO)
            if xb - xa > 34:
                c.create_text((xa + xb) / 2, y0 + alto / 2,
                              text="libre" if b.libre else b.pid,
                              fill=tema.TEXTO_SUAVE if b.libre else tema.FONDO,
                              font=tema.FUENTE_NEGRITA)
            c.create_text(xa, y0 + alto + 14, text=str(b.inicio), fill=tema.TEXTO_SUAVE, anchor="w")
        c.create_text(x0 + self.memoria.total * escala, y0 + alto + 14,
                      text=str(self.memoria.total), fill=tema.TEXTO_SUAVE, anchor="e")
