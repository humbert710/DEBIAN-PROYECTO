"""
Colores y estilos comunes. Usar SIEMPRE estas constantes para que todas
las pestañas se vean iguales.
"""
from tkinter import ttk

from core.proceso import Estado

# Paleta (tema oscuro con el rojo de Debian)
FONDO = "#1e1f24"
PANEL = "#2a2c33"
BORDE = "#3a3d46"
TEXTO = "#e8e8ec"
TEXTO_SUAVE = "#9ea2ad"
ACENTO = "#d70a53"        # rojo Debian
ACENTO_HOVER = "#f0266e"

FUENTE = ("Segoe UI", 10)
FUENTE_NEGRITA = ("Segoe UI", 10, "bold")
FUENTE_TITULO = ("Segoe UI", 15, "bold")

# Color de fondo de cada estado (para tablas y gráficos)
COLOR_ESTADO = {
    Estado.NUEVO: "#5c6370",
    Estado.LISTO: "#b8860b",
    Estado.EJECUCION: "#2e8b57",
    Estado.BLOQUEADO: "#b22222",
    Estado.TERMINADO: "#2f6db5",
}

# Colores para distinguir procesos (Gantt, memoria, grafos)
COLORES_PROCESO = [
    "#e06c75", "#61afef", "#98c379", "#e5c07b", "#c678dd",
    "#56b6c2", "#d19a66", "#be5046", "#7f848e", "#ff79c6",
]


def color_proceso(indice: int) -> str:
    return COLORES_PROCESO[indice % len(COLORES_PROCESO)]


def aplicar_tema(root) -> None:
    root.configure(bg=FONDO)
    estilo = ttk.Style(root)
    estilo.theme_use("clam")

    estilo.configure(".", background=FONDO, foreground=TEXTO, font=FUENTE,
                     bordercolor=BORDE, fieldbackground=PANEL)
    estilo.configure("TFrame", background=FONDO)
    estilo.configure("Panel.TFrame", background=PANEL)
    estilo.configure("TLabel", background=FONDO, foreground=TEXTO)
    estilo.configure("Panel.TLabel", background=PANEL, foreground=TEXTO)
    estilo.configure("Suave.TLabel", background=FONDO, foreground=TEXTO_SUAVE)
    estilo.configure("PanelSuave.TLabel", background=PANEL, foreground=TEXTO_SUAVE)
    estilo.configure("Titulo.TLabel", background=FONDO, foreground=TEXTO, font=FUENTE_TITULO)
    estilo.configure("Error.TLabel", background=PANEL, foreground="#ff6b6b")

    estilo.configure("TLabelframe", background=PANEL, bordercolor=BORDE,
                     lightcolor=BORDE, darkcolor=BORDE)
    estilo.configure("TLabelframe.Label", background=PANEL, foreground=TEXTO_SUAVE,
                     font=FUENTE_NEGRITA)

    estilo.configure("TEntry", fieldbackground="#1a1b20", foreground=TEXTO,
                     insertcolor=TEXTO, bordercolor=BORDE, padding=4)
    estilo.map("TEntry", bordercolor=[("focus", ACENTO)])

    estilo.configure("TButton", background=PANEL, foreground=TEXTO, padding=(12, 6),
                     bordercolor=BORDE, focusthickness=0)
    estilo.map("TButton", background=[("active", BORDE)])
    estilo.configure("Acento.TButton", background=ACENTO, foreground="white",
                     bordercolor=ACENTO, font=FUENTE_NEGRITA)
    estilo.map("Acento.TButton", background=[("active", ACENTO_HOVER)])

    estilo.configure("TNotebook", background=FONDO, bordercolor=BORDE, tabmargins=(8, 8, 8, 0))
    estilo.configure("TNotebook.Tab", background=PANEL, foreground=TEXTO_SUAVE,
                     padding=(16, 8), bordercolor=BORDE, font=FUENTE_NEGRITA)
    estilo.map("TNotebook.Tab",
               background=[("selected", ACENTO)],
               foreground=[("selected", "white")])

    estilo.configure("Treeview", background="#1a1b20", fieldbackground="#1a1b20",
                     foreground=TEXTO, rowheight=28, bordercolor=BORDE)
    estilo.configure("Treeview.Heading", background=PANEL, foreground=TEXTO,
                     font=FUENTE_NEGRITA, bordercolor=BORDE, padding=6)
    estilo.map("Treeview", background=[("selected", "#44475a")])
    estilo.map("Treeview.Heading", background=[("active", BORDE)])
