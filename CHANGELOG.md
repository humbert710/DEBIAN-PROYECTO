# Historial de versiones

## v0.3.0 — 2026-10-14
**Agregado**
- Pestaña **Memoria** conectada a `core/memoria.py`: First Fit, Best Fit y Worst Fit,
  asignar (uno o todos), liberar, compactar y reiniciar; barra visual de la RAM,
  tabla de bloques, fragmentación externa y publicación en Resultados.

**Corregido**
- `ui/tab_concurrencia.py`: docstring sin cerrar que impedía arrancar la aplicación.
- Concurrencia publica en Resultados texto legible en vez de diccionarios crudos.
- Planificación ya no borra su Gantt cuando otro módulo publica resultados;
  solo se limpia si cambian los procesos.
- Memoria libera y republica cuando se elimina un proceso de la pestaña Procesos.

## v0.1.0 — 2026-10-07
**Agregado**
- Ventana principal con 6 pestañas y tema oscuro (rojo Debian).
- `core/proceso.py`: clase `Proceso` con ID, llegada, ráfaga, prioridad, memoria y estado
  (Nuevo, Listo, Ejecución, Bloqueado, Terminado).
- `core/sistema.py`: estado compartido entre pestañas y registro de resultados.
- Pestaña **Procesos**: formulario con validaciones, tabla con colores por estado,
  ID automático, eliminar, limpiar y datos de ejemplo.
- Pestaña **Resultados**: tarjetas resumen y resultados publicados por cada módulo.
- Pestañas Planificación, Concurrencia, Interbloqueo y Memoria con sus requisitos (pendientes).
