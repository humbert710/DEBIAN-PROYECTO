# Historial de versiones

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
