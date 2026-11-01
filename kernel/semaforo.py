#Semaforo binario con wait y signal
from collections import deque

class SemaforoError(Exception):
    pass

class SemaforoBinario:
    def __init__(self):
        self.valor = 1
        self.dueno = None
        self.cola_espera = deque()
        self.variable_compartida = 0

    def wait(self, pid):
        pid = _validar_pid(pid)
        if self.dueno == pid:
            raise SemaforoError(f"P{pid} ya esta dentro de la seccion critica")
        if pid in self.cola_espera:
            raise SemaforoError(f"P{pid} ya esta esperando en la cola del semaforo")
        if self.valor == 1:
            self.valor = 0
            self.dueno = pid
            return False
        else:
            self.cola_espera.append(pid)
            return True

    def signal(self, pid):
        pid = _validar_pid(pid)
        if self.dueno is None:
            raise SemaforoError(f"La seccion critica esta libre: P{pid} no tiene nada que liberar")
        if self.dueno != pid:
            raise SemaforoError(f"P{pid} no puede hacer signal(): el dueno es P{self.dueno}")
        return self._entregar_al_siguiente()

    def escribir(self, pid, nuevo_valor):
        pid = _validar_pid(pid)
        if self.dueno != pid:
            raise SemaforoError(f"Acceso denegado: P{pid} no tiene el semaforo.")
        if isinstance(nuevo_valor, bool) or not isinstance(nuevo_valor, int):
            raise SemaforoError(f"El valor debe ser un numero entero.")
        anterior = self.variable_compartida
        self.variable_compartida = nuevo_valor
        return anterior

    def esta_libre(self):
        return self.valor == 1

    def _entregar_al_siguiente(self):
        if not self.cola_espera:
            self.valor = 1
            self.dueno = None
            return None
        self.dueno = self.cola_espera.popleft()
        return self.dueno

def _validar_pid(pid):
    if isinstance(pid, bool) or not isinstance(pid, int) or pid < 1:
        raise SemaforoError(f"El PID debe ser un numero entero positivo (recibido: {pid!r})")
    return pid
