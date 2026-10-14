# DebianSim — Simulador visual de administración de recursos del SO

Proyecto final · **Sistemas Operativos I (029)** · Universidad Mariano Gálvez de Guatemala
**Equipo Debian** · Entrega: 18 de octubre de 2026

Aplicación gráfica que simula procesos, planificación del procesador, concurrencia y
sincronización, interbloqueos y gestión de memoria.

## Integrantes

| Nombre | Carné | Módulo a cargo |
|---|---|---|
| Edwin Humberto Noj Castillo | 2190-24-23230 | Coordinación, esqueleto, Procesos, Resultados |
| Yónatan Sebastián Cuin Senté | 2190-24-18358 | Planificación |
|Mynor Antonio Pérez Herrera| 2190-24-9339 | Concurrencia |
| Erick José Hernández Ramírez | 2190-24-13674 | Interbloqueo |
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
│   ├── tab_procesos.py      
│   ├── tab_planificacion.py 
│   ├── tab_concurrencia.py  
│   ├── tab_interbloqueo.py
│   ├── tab_memoria.py       
│   └── tab_resultados.py    
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


