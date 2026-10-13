"""módulo 3 · Concurrencia y sincronización.

Escenario: una cuenta bancaria compartida por varios hilos. La mitad
deposita y la otra mitad retira el mismo monto.

- Sin sincronización: leer-modificar-escribir NO es atómico, así que los
  hilos se pisan entre sí (condición de carrera) y el saldo final es incorrecto.
  
- Con Lock: la sección crítica queda protegida con threading.Lock y el
  saldo final siempre coincide con el esperado.

Este archivo NO toca la interfaz: solo calcula y devuelve datos.
"""
import threading
import time


class CuentaBancaria:
    def __init__(self, saldo_inicial=0, usar_lock=False):
        self.saldo = saldo_inicial
        self.usar_lock = usar_lock
        self._lock = threading.Lock()

    def _aplicar(self, monto):
        # Sección crítica: leer -> modificar -> escribir.
        actual = self.saldo
        time.sleep(0)  # cede el GIL: hace visible la condición de carrera
        self.saldo = actual + monto

    def mover(self, monto):
        """Suma (depósito) o resta (retiro, monto negativo) al saldo."""
        if self.usar_lock:
            with self._lock:
                self._aplicar(monto)
        else:
            self._aplicar(monto)


def _trabajador(cuenta, monto, operaciones):
    for _ in range(operaciones):
        cuenta.mover(monto)


def simular(usar_lock, n_hilos=8, operaciones=30, monto=10, saldo_inicial=1000):
    
    """Ejecuta el escenario y devuelve un diccionario con el resultado.

    Es bloqueante: desde la interfaz hay que llamarla en un hilo aparte.
    """
    cuenta = CuentaBancaria(saldo_inicial, usar_lock)
    depositantes = (n_hilos + 1) // 2
    retiradores = n_hilos - depositantes

    hilos = [
        threading.Thread(target=_trabajador, args=(cuenta, monto, operaciones))
        for _ in range(depositantes)
    ] + [
        threading.Thread(target=_trabajador, args=(cuenta, -monto, operaciones))
        for _ in range(retiradores)
    ]

    inicio = time.perf_counter()
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    duracion = time.perf_counter() - inicio

    esperado = saldo_inicial + (depositantes - retiradores) * operaciones * monto
    obtenido = cuenta.saldo
    return {
        "con_lock": usar_lock,
        "hilos": n_hilos,
        "operaciones": operaciones,
        "saldo_inicial": saldo_inicial,
        "esperado": esperado,
        "obtenido": obtenido,
        "diferencia": obtenido - esperado,
        "correcto": obtenido == esperado,
        "tiempo_s": round(duracion, 4),
    }