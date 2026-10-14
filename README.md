# DebianSim — Simulador visual de administración de recursos del SO

Proyecto final · **Sistemas Operativos I (029)** · Universidad Mariano Gálvez de Guatemala
**Equipo Debian** · Entrega: 18 de octubre de 2026

Aplicación gráfica que simula procesos, planificación del procesador, concurrencia y
sincronización, interbloqueos y gestión de memoria.

## Integrantes

| Nombre | Carné | Módulo a cargo |
|---|---|---|
| Edwin Humberto Noj Castillo | 2190-24-23230 | Coordinación, esqueleto, Procesos, Resultados |
| _pendiente_ | | Planificación |
|Mynor Antonio Pérez Herrera| 2190-24-9339 | Concurrencia |
| _pendiente_ | | Interbloqueo |
| _pendiente_ | | Memoria |

## Cómo ejecutarlo

Requisitos: **Python 3.10 o superior** (Tkinter ya viene incluido en Windows).
No hay que instalar librerías externas.

```bash
python main.py
```

> En Linux/Debian, si sale `No module named tkinter`: `sudo apt install python3-tk`

## Estructura del proyecto

```
DebianSim/
├── main.py                  ← ventana principal y pestañas
├── core/                    ← LÓGICA (sin interfaz)
│   ├── proceso.py           ← clase Proceso y estados
│   ├── sistema.py           ← estado compartido entre pestañas
│   ├── planificacion.py     ← (v0.2) FCFS, SJF, RR
│   ├── concurrencia.py      ← (v0.3) hilos y Lock
│   ├── memoria.py           ← (v0.3) First/Best/Worst Fit
│   └── interbloqueo.py      ← (v0.4) detección y recuperación
├── ui/                      ← INTERFAZ (una pestaña por archivo)
│   ├── tema.py              ← colores y estilos (usar siempre estos)
│   ├── tab_procesos.py      ← ✅ listo
│   ├── tab_planificacion.py ← ✅ listo
│   ├── tab_concurrencia.py  ← ✅ listo
│   ├── tab_interbloqueo.py
│   ├── tab_memoria.py       ← ✅ listo
│   └── tab_resultados.py    ← ✅ listo
└── docs/                    ← informe, acta, RACI, WBS, minutas
```

**Regla:** la lógica (cálculos, algoritmos) va en `core/` y la interfaz en `ui/`.
Así los algoritmos se pueden probar y explicar por separado.

## Cómo se conectan los módulos

Todas las pestañas reciben el mismo objeto `sistema` (ver `core/sistema.py`):

```python
self.sistema.procesos                     # procesos creados en la pestaña 1
p.copia()                                 # simular SIEMPRE sobre copias
self.sistema.suscribir(self.refrescar)    # avisarme cuando cambien los procesos
self.sistema.registrar_resultado("memoria", {"Fragmentación": "18 %"})  # aparece en Resultados
```

## Versiones

| Versión | Fecha meta | Contenido |
|---|---|---|
| v0.1 | 7 oct | Esqueleto + Procesos + Resultados |
| v0.2 | 11 oct | Planificación |
| v0.3 | 13 oct | Concurrencia + Memoria |
| v0.4 | 15 oct | Interbloqueo |
| v1.0 | 17 oct | Pruebas, pulido, lista para defensa |

Ver `CHANGELOG.md` para el detalle de cambios.

## Forma de trabajo en Git

1. Antes de empezar: **Pull** (bajar lo último).
2. Trabajar **solo en tus archivos** del módulo asignado.
3. Commits pequeños con mensajes claros: `Planificación: agrego algoritmo FCFS`.
4. **Push** al terminar. Cada quien sube con **su propia cuenta** (cuenta para la nota).
