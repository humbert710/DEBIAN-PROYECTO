"""
Pestaña 1 — Gestión de procesos.

Permite crear, eliminar y visualizar procesos. Los procesos quedan en
`sistema.procesos` y los demás módulos los usan desde ahí.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from core.proceso import Proceso, Estado
from core.sistema import Sistema
from ui import tema


class TabProcesos(ttk.Frame):
    COLUMNAS = ("pid", "llegada", "rafaga", "prioridad", "memoria", "estado")
    ENCABEZADOS = ("ID", "Llegada", "Ráfaga CPU", "Prioridad", "Memoria (KB)", "Estado")

    def __init__(self, parent, sistema: Sistema):
        super().__init__(parent, padding=16)
        self.sistema = sistema
        self._crear_formulario()
        self._crear_tabla()
        self._crear_leyenda()
        sistema.suscribir(self.refrescar)
        self.refrescar()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _crear_formulario(self):
        form = ttk.LabelFrame(self, text="  Nuevo proceso  ", padding=14)
        form.pack(fill="x")

        self.vars = {
            "pid": tk.StringVar(),
            "llegada": tk.StringVar(value="0"),
            "rafaga": tk.StringVar(),
            "prioridad": tk.StringVar(value="1"),
            "memoria": tk.StringVar(),
        }
        campos = [
            ("ID", "pid", "Ej. P1"),
            ("Llegada", "llegada", "≥ 0"),
            ("Ráfaga CPU", "rafaga", "> 0"),
            ("Prioridad", "prioridad", "1 = más alta"),
            ("Memoria (KB)", "memoria", f"1 – {self.sistema.memoria_total}"),
        ]
        for col, (etiqueta, clave, ayuda) in enumerate(campos):
            ttk.Label(form, text=etiqueta, style="Panel.TLabel").grid(
                row=0, column=col, sticky="w", padx=(0, 12))
            entrada = ttk.Entry(form, textvariable=self.vars[clave], width=13)
            entrada.grid(row=1, column=col, sticky="we", padx=(0, 12), pady=3)
            entrada.bind("<Return>", lambda _e: self.agregar())
            ttk.Label(form, text=ayuda, style="PanelSuave.TLabel").grid(
                row=2, column=col, sticky="w")
            if clave == "pid":
                self.entrada_pid = entrada

        ttk.Button(form, text="➕  Agregar proceso", style="Acento.TButton",
                   command=self.agregar).grid(row=1, column=len(campos), padx=(8, 0))

        self.lbl_error = ttk.Label(form, text="", style="Error.TLabel")
        self.lbl_error.grid(row=3, column=0, columnspan=len(campos) + 1,
                            sticky="w", pady=(8, 0))

    def _crear_tabla(self):
        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(16, 6))
        self.lbl_resumen = ttk.Label(barra, text="", style="Suave.TLabel")
        self.lbl_resumen.pack(side="left")
        ttk.Button(barra, text="Limpiar todo", command=self.limpiar).pack(side="right")
        ttk.Button(barra, text="Eliminar seleccionado",
                   command=self.eliminar).pack(side="right", padx=6)
        ttk.Button(barra, text="Cargar ejemplo",
                   command=self.sistema.cargar_ejemplo).pack(side="right")

        marco = ttk.Frame(self)
        marco.pack(fill="both", expand=True)
        self.tabla = ttk.Treeview(marco, columns=self.COLUMNAS, show="headings",
                                  selectmode="browse")
        for col, titulo in zip(self.COLUMNAS, self.ENCABEZADOS):
            self.tabla.heading(col, text=titulo)
            self.tabla.column(col, anchor="center", width=120)
        scroll = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tabla.bind("<Delete>", lambda _e: self.eliminar())

        # Un color de fila por estado
        for estado, color in tema.COLOR_ESTADO.items():
            self.tabla.tag_configure(estado.name, background=color, foreground="white")

    def _crear_leyenda(self):
        leyenda = ttk.Frame(self)
        leyenda.pack(fill="x", pady=(8, 0))
        ttk.Label(leyenda, text="Estados:", style="Suave.TLabel").pack(side="left")
        for estado in Estado:
            tk.Label(leyenda, text=f"  {estado.value}  ", bg=tema.COLOR_ESTADO[estado],
                     fg="white", font=tema.FUENTE).pack(side="left", padx=4)

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    def _leer_entero(self, clave: str, nombre: str, minimo: int, maximo=None) -> int:
        texto = self.vars[clave].get().strip()
        if not texto:
            raise ValueError(f"El campo «{nombre}» es obligatorio.")
        try:
            valor = int(texto)
        except ValueError:
            raise ValueError(f"«{nombre}» debe ser un número entero.") from None
        if valor < minimo:
            raise ValueError(f"«{nombre}» debe ser mayor o igual a {minimo}.")
        if maximo is not None and valor > maximo:
            raise ValueError(f"«{nombre}» no puede ser mayor que {maximo}.")
        return valor

    def agregar(self):
        try:
            pid = self.vars["pid"].get().strip() or self.sistema.siguiente_pid()
            if " " in pid or len(pid) > 10:
                raise ValueError("El ID no debe tener espacios ni más de 10 caracteres.")
            proceso = Proceso(
                pid=pid,
                llegada=self._leer_entero("llegada", "Llegada", 0),
                rafaga=self._leer_entero("rafaga", "Ráfaga CPU", 1),
                prioridad=self._leer_entero("prioridad", "Prioridad", 1),
                memoria=self._leer_entero("memoria", "Memoria", 1, self.sistema.memoria_total),
            )
            self.sistema.agregar_proceso(proceso)
        except ValueError as error:
            self.lbl_error.configure(text=f"⚠  {error}")
            return

        self.lbl_error.configure(text="")
        self.vars["pid"].set("")
        self.vars["rafaga"].set("")
        self.vars["memoria"].set("")
        self.entrada_pid.focus_set()

    def eliminar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            self.lbl_error.configure(text="⚠  Seleccioná un proceso de la tabla para eliminarlo.")
            return
        self.sistema.eliminar_proceso(seleccion[0])

    def limpiar(self):
        if self.sistema.procesos and messagebox.askyesno(
                "Limpiar procesos", "¿Eliminar todos los procesos registrados?"):
            self.sistema.limpiar_procesos()

    def refrescar(self):
        self.tabla.delete(*self.tabla.get_children())
        for p in self.sistema.procesos:
            self.tabla.insert("", "end", iid=p.pid, tags=(p.estado.name,),
                              values=(p.pid, p.llegada, p.rafaga, p.prioridad,
                                      p.memoria, p.estado.value))
        total_mem = sum(p.memoria for p in self.sistema.procesos)
        self.lbl_resumen.configure(
            text=f"{len(self.sistema.procesos)} procesos  ·  "
                 f"memoria solicitada: {total_mem} KB de {self.sistema.memoria_total} KB"
                 f"  ·  (si dejás el ID vacío se asigna {self.sistema.siguiente_pid()})")
