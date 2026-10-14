"""
Pestaña — Interbloqueos.

Muestra el grafo de asignación de recursos (procesos = círculos,
recursos = cuadros), detecta ciclos (deadlock), los resalta en rojo,
evalúa las 4 condiciones de Coffman y permite recuperarse terminando
un proceso del ciclo.

La lógica está en core/interbloqueo.py; aquí solo hay interfaz.
"""

import math
import re
import tkinter as tk
from tkinter import messagebox, ttk

from core.interbloqueo import Ciclo, GrafoRecursos
from core.sistema import Sistema
from ui import tema

RADIO = 24                  # radio del círculo de un proceso
LADO = 22                   # mitad del lado del cuadro de un recurso
COLOR_ASIGNACION = "#98c379"
COLOR_SOLICITUD = "#e5c07b"
COLOR_CICLO = "#ff4d4d"
COLOR_OK = "#98c379"
COLOR_NO = "#7f848e"


class TabInterbloqueo(ttk.Frame):
    def __init__(self, parent, sistema: Sistema):
        super().__init__(parent)
        self.sistema = sistema
        self.grafo = GrafoRecursos()
        self.ciclo: Ciclo | None = None     # ciclo resaltado en rojo
        self.terminados: list[str] = []     # procesos terminados por recuperación
        self._construir()
        self._refrescar()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _construir(self) -> None:
        estilo = ttk.Style(self)
        estilo.configure("Interbloqueo.TCombobox", background=tema.PANEL, foreground=tema.TEXTO,
                         fieldbackground="#1a1b20", arrowcolor=tema.TEXTO,
                         bordercolor=tema.BORDE, padding=3)

        raiz = ttk.Frame(self, padding=(14, 10))
        raiz.pack(fill="both", expand=True)

        encabezado = ttk.Frame(raiz)
        encabezado.pack(fill="x", pady=(0, 8))
        ttk.Label(encabezado, text="Interbloqueos", style="Titulo.TLabel").pack(side="left")
        ttk.Label(encabezado, text="   Grafo de asignación de recursos · detección y recuperación",
                  style="Suave.TLabel").pack(side="left", pady=(4, 0))

        cuerpo = ttk.Frame(raiz)
        cuerpo.pack(fill="both", expand=True)

        # ---------- Panel izquierdo: controles ----------
        izq = ttk.Frame(cuerpo)
        izq.pack(side="left", fill="y", padx=(0, 12))

        caja = ttk.LabelFrame(izq, text="  Escenario  ", padding=8)
        caja.pack(fill="x")
        ttk.Button(caja, text="⚠  Provocar deadlock", style="Acento.TButton",
                   command=self._provocar).pack(fill="x", pady=2)
        ttk.Button(caja, text="Usar procesos de la pestaña 1",
                   command=self._usar_procesos).pack(fill="x", pady=2)
        fila = ttk.Frame(caja, style="Panel.TFrame")
        fila.pack(fill="x", pady=2)
        ttk.Button(fila, text="+ Proceso", command=self._agregar_proceso).pack(
            side="left", fill="x", expand=True, padx=(0, 2))
        ttk.Button(fila, text="+ Recurso", command=self._agregar_recurso).pack(
            side="left", fill="x", expand=True, padx=(2, 0))
        ttk.Button(caja, text="Reiniciar", command=self._reiniciar).pack(fill="x", pady=2)

        caja = ttk.LabelFrame(izq, text="  Análisis  ", padding=8)
        caja.pack(fill="x", pady=(8, 0))
        ttk.Button(caja, text="Detectar deadlock", style="Acento.TButton",
                   command=self._detectar).pack(fill="x", pady=2)
        ttk.Button(caja, text="Recuperar (terminar un proceso)",
                   command=self._recuperar).pack(fill="x", pady=2)

        caja = ttk.LabelFrame(izq, text="  Asignación manual  ", padding=8)
        caja.pack(fill="x", pady=(8, 0))
        rejilla = ttk.Frame(caja, style="Panel.TFrame")
        rejilla.pack(fill="x")
        rejilla.columnconfigure(1, weight=1)
        ttk.Label(rejilla, text="Proceso", style="Panel.TLabel").grid(row=0, column=0, sticky="w", pady=2)
        self.cb_proceso = ttk.Combobox(rejilla, state="readonly", width=10,
                                       style="Interbloqueo.TCombobox")
        self.cb_proceso.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=2)
        ttk.Label(rejilla, text="Recurso", style="Panel.TLabel").grid(row=1, column=0, sticky="w", pady=2)
        self.cb_recurso = ttk.Combobox(rejilla, state="readonly", width=10,
                                       style="Interbloqueo.TCombobox")
        self.cb_recurso.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=2)
        fila = ttk.Frame(caja, style="Panel.TFrame")
        fila.pack(fill="x", pady=(6, 0))
        ttk.Button(fila, text="Solicitar", command=self._solicitar).pack(
            side="left", fill="x", expand=True, padx=(0, 2))
        ttk.Button(fila, text="Liberar", command=self._liberar).pack(
            side="left", fill="x", expand=True, padx=(2, 0))

        # ---------- Panel derecho: grafo + Coffman + bitácora ----------
        der = ttk.Frame(cuerpo)
        der.pack(side="left", fill="both", expand=True)

        # Se empaqueta primero lo de abajo para que nunca quede cortado;
        # el canvas ocupa el espacio que sobre.
        inferior = ttk.Frame(der)
        inferior.pack(side="bottom", fill="x", pady=(8, 0))

        self.canvas = tk.Canvas(der, bg="#1a1b20", highlightthickness=1,
                                highlightbackground=tema.BORDE, height=200)
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _e: self._dibujar())

        caja = ttk.LabelFrame(inferior, text="  Bitácora  ", padding=6)
        caja.pack(side="right", fill="y", padx=(8, 0))
        self.bitacora = tk.Text(caja, height=7, width=34, bg="#1a1b20", fg=tema.TEXTO,
                                font=("Consolas", 9), relief="flat", wrap="word",
                                state="disabled")
        self.bitacora.pack(fill="both", expand=True)
        self.bitacora.tag_configure("alerta", foreground=COLOR_CICLO)
        self.bitacora.tag_configure("ok", foreground=COLOR_OK)

        caja = ttk.LabelFrame(inferior, text="  Condiciones de Coffman  ", padding=8)
        caja.pack(side="left", fill="both", expand=True)
        self.filas_coffman: list[tuple[tk.Label, tk.Label]] = []
        for _ in range(4):
            fila = tk.Frame(caja, bg=tema.PANEL)
            fila.pack(fill="x", pady=1)
            marca = tk.Label(fila, text="○", bg=tema.PANEL, fg=COLOR_NO,
                             font=tema.FUENTE_NEGRITA, width=2)
            marca.pack(side="left")
            texto = tk.Label(fila, text="", bg=tema.PANEL, fg=tema.TEXTO,
                             font=tema.FUENTE, anchor="w", justify="left")
            texto.pack(side="left", fill="x")
            self.filas_coffman.append((marca, texto))
        self.lbl_veredicto = tk.Label(caja, text="", bg=tema.PANEL, fg=tema.TEXTO_SUAVE,
                                      font=tema.FUENTE_NEGRITA, anchor="w")
        self.lbl_veredicto.pack(fill="x", pady=(4, 0))

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    def _provocar(self) -> None:
        pids = [p.pid for p in self.sistema.procesos]
        escenario = self.grafo.provocar_deadlock(pids)
        self.ciclo = None
        self.terminados.clear()
        self._log(f"Escenario armado: {escenario} Pulsa «Detectar deadlock».")
        self._refrescar()

    def _usar_procesos(self) -> None:
        pids = [p.pid for p in self.sistema.procesos]
        if not pids:
            messagebox.showinfo("Interbloqueo",
                                "Todavía no hay procesos. Créalos (o carga el ejemplo) "
                                "en la pestaña Procesos.")
            return
        nuevos = self.grafo.cargar_procesos(pids)
        if not self.grafo.recursos:
            self.grafo.agregar_recurso()
            self.grafo.agregar_recurso()
        self._log(f"Se agregaron {nuevos} proceso(s) de la pestaña 1.")
        self._refrescar()

    def _agregar_proceso(self) -> None:
        self._log(f"Proceso {self.grafo.agregar_proceso()} agregado.")
        self._refrescar()

    def _agregar_recurso(self) -> None:
        self._log(f"Recurso {self.grafo.agregar_recurso()} agregado.")
        self._refrescar()

    def _reiniciar(self) -> None:
        self.grafo.reiniciar()
        self.ciclo = None
        self.terminados.clear()
        self._log("Grafo reiniciado.")
        self._refrescar()

    def _solicitar(self) -> None:
        pid, rid = self.cb_proceso.get(), self.cb_recurso.get()
        try:
            resultado = self.grafo.solicitar(pid, rid)
        except ValueError as error:
            messagebox.showwarning("Interbloqueo", str(error))
            return
        if resultado == "asignado":
            self._log(f"{rid} estaba libre → se asignó a {pid}.")
        else:
            self._log(f"{rid} lo tiene otro proceso → {pid} queda esperando.")
        self.ciclo = None
        self._refrescar()

    def _liberar(self) -> None:
        rid = self.cb_recurso.get()
        try:
            entrega = self.grafo.liberar(rid)
        except ValueError as error:
            messagebox.showwarning("Interbloqueo", str(error))
            return
        self._log(f"{rid} liberado." + (f" Pasa a {entrega[0]}, que lo esperaba." if entrega else ""))
        self.ciclo = None
        self._refrescar()

    def _detectar(self) -> None:
        self.ciclo = self.grafo.detectar_ciclo()
        if self.ciclo:
            self._log(f"DEADLOCK detectado. Ciclo: {self.ciclo.texto()}", "alerta")
        else:
            self._log("Sin deadlock: no hay ciclos en el grafo.", "ok")
        self._publicar()
        self._refrescar()

    def _recuperar(self) -> None:
        resultado = self.grafo.recuperar()
        if resultado is None:
            self.ciclo = None
            self._log("No hay deadlock que recuperar.", "ok")
            self._refrescar()
            return
        victima, liberados, entregas = resultado
        self.terminados.append(victima)
        self._log(f"Se terminó {victima} (el que retenía menos recursos). "
                  f"Liberó: {', '.join(liberados) or 'ninguno'}.", "ok")
        for pid, rid in entregas:
            self._log(f"{rid} pasa a {pid}, que lo esperaba.")
        self.ciclo = self.grafo.detectar_ciclo()
        if self.ciclo:
            self._log(f"Todavía hay deadlock: {self.ciclo.texto()}. Vuelve a recuperar.", "alerta")
        else:
            self._log("Deadlock resuelto.", "ok")
        self._publicar()
        self._refrescar()

    def _publicar(self) -> None:
        """Envía el resumen a la pestaña Resultados."""
        g = self.grafo
        datos = {
            "Procesos en el grafo": str(len(g.procesos)),
            "Recursos": str(len(g.recursos)),
            "Estado": "DEADLOCK" if self.ciclo else "Sin deadlock",
            "Ciclo": self.ciclo.texto() if self.ciclo else "—",
            "Procesos terminados": ", ".join(self.terminados) or "ninguno",
        }
        self.sistema.registrar_resultado("interbloqueo", datos)

    # ------------------------------------------------------------------
    # Refresco de pantalla
    # ------------------------------------------------------------------
    def _refrescar(self) -> None:
        g = self.grafo
        self.cb_proceso["values"] = g.procesos
        self.cb_recurso["values"] = g.recursos
        if self.cb_proceso.get() not in g.procesos:
            self.cb_proceso.set(g.procesos[0] if g.procesos else "")
        if self.cb_recurso.get() not in g.recursos:
            self.cb_recurso.set(g.recursos[0] if g.recursos else "")
        self._dibujar()
        self._actualizar_coffman()

    def _log(self, mensaje: str, etiqueta: str = "") -> None:
        self.bitacora.configure(state="normal")
        self.bitacora.insert("end", "• " + mensaje + "\n", etiqueta)
        self.bitacora.see("end")
        self.bitacora.configure(state="disabled")

    def _actualizar_coffman(self) -> None:
        condiciones = self.grafo.coffman()
        for (marca, texto), (nombre, explicacion, cumple) in zip(self.filas_coffman, condiciones):
            marca.configure(text="✔" if cumple else "○", fg=COLOR_OK if cumple else COLOR_NO)
            texto.configure(text=f"{nombre}: {explicacion}",
                            fg=tema.TEXTO if cumple else tema.TEXTO_SUAVE)
        if all(c for _, _, c in condiciones):
            self.lbl_veredicto.configure(
                text="Se cumplen las 4 → hay deadlock", fg=COLOR_CICLO)
        else:
            self.lbl_veredicto.configure(
                text="Deadlock solo si se cumplen las 4 a la vez", fg=tema.TEXTO_SUAVE)

    # ------------------------------------------------------------------
    # Dibujo del grafo
    # ------------------------------------------------------------------
    @staticmethod
    def _color(pid: str, indice: int) -> str:
        numero = re.search(r"\d+", pid)
        return tema.color_proceso(int(numero.group()) - 1 if numero else indice)

    @staticmethod
    def _flecha(c: tk.Canvas, a, b, color, ancho, punteada) -> None:
        (x1, y1), (x2, y2) = a, b
        d = math.hypot(x2 - x1, y2 - y1)
        if d == 0:
            return
        ux, uy = (x2 - x1) / d, (y2 - y1) / d
        margen = RADIO + 3
        c.create_line(x1 + ux * margen, y1 + uy * margen,
                      x2 - ux * margen, y2 - uy * margen,
                      fill=color, width=ancho, arrow="last", arrowshape=(11, 13, 5),
                      dash=(6, 4) if punteada else ())

    def _dibujar(self) -> None:
        c, g = self.canvas, self.grafo
        c.delete("all")
        ancho = c.winfo_width() if c.winfo_width() > 50 else 700
        alto = c.winfo_height() if c.winfo_height() > 50 else 330

        if not g.procesos and not g.recursos:
            c.create_text(ancho / 2, alto / 2, fill=tema.TEXTO_SUAVE, font=tema.FUENTE,
                          text="El grafo está vacío.\nPulsa «Provocar deadlock» o agrega procesos y recursos.",
                          justify="center")
            return

        # Posiciones: procesos arriba, recursos abajo
        pos: dict[str, tuple[float, float]] = {}
        for i, pid in enumerate(g.procesos):
            pos[pid] = (ancho * (i + 1) / (len(g.procesos) + 1), alto * 0.28)
        for i, rid in enumerate(g.recursos):
            pos[rid] = (ancho * (i + 1) / (len(g.recursos) + 1), alto * 0.74)

        # Aristas que forman el ciclo (se pintan en rojo)
        rojas: set[tuple[str, str, str]] = set()
        if self.ciclo:
            for p, r, titular in self.ciclo.aristas:
                rojas.add(("sol", p, r))
                rojas.add(("asig", r, titular))

        for rid, pid in g.asignaciones.items():
            roja = ("asig", rid, pid) in rojas
            self._flecha(c, pos[rid], pos[pid], COLOR_CICLO if roja else COLOR_ASIGNACION,
                         4 if roja else 2, False)
        for pid, rid in g.solicitudes:
            roja = ("sol", pid, rid) in rojas
            self._flecha(c, pos[pid], pos[rid], COLOR_CICLO if roja else COLOR_SOLICITUD,
                         4 if roja else 2, True)

        # Nodos
        en_ciclo_p = set(self.ciclo.procesos) if self.ciclo else set()
        en_ciclo_r = set(self.ciclo.recursos) if self.ciclo else set()
        for i, pid in enumerate(g.procesos):
            x, y = pos[pid]
            roja = pid in en_ciclo_p
            c.create_oval(x - RADIO, y - RADIO, x + RADIO, y + RADIO,
                          fill=self._color(pid, i),
                          outline=COLOR_CICLO if roja else tema.TEXTO, width=4 if roja else 1)
            c.create_text(x, y, text=pid, fill="#16171b", font=tema.FUENTE_NEGRITA)
        for rid in g.recursos:
            x, y = pos[rid]
            roja = rid in en_ciclo_r
            c.create_rectangle(x - LADO, y - LADO, x + LADO, y + LADO, fill=tema.PANEL,
                               outline=COLOR_CICLO if roja else tema.TEXTO_SUAVE,
                               width=4 if roja else 2)
            c.create_text(x, y, text=rid, fill=tema.TEXTO, font=tema.FUENTE_NEGRITA)

        # Leyenda
        y0 = 14
        for texto, color, punteada in (("asignación (recurso → proceso)", COLOR_ASIGNACION, False),
                                       ("solicitud (proceso → recurso)", COLOR_SOLICITUD, True),
                                       ("ciclo / deadlock", COLOR_CICLO, False)):
            c.create_line(12, y0, 42, y0, fill=color, width=3, dash=(6, 4) if punteada else ())
            c.create_text(50, y0, text=texto, fill=tema.TEXTO_SUAVE, anchor="w", font=("Segoe UI", 9))
            y0 += 18
