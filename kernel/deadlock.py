"""Punto D: Interbloqueo (DeadLock)
Dos recursos exclusivos (R1 y R2), simulacion de espera circular, deteccion del deadlock y resolucion abortando un proceso
Deadlock = espera circular, 
P1 tiene R1 y R2
P2 tiene R2 y pide R1
-> ninguno puede avanzar nunca"""

"""deque = cola para los procesos que esperan un recurso"""
from collections import deque

"""Error controlado de recursos (por ejemplo, liberar un recurso que no es propio)"""
class DeadlockError(Exception):

    """Cada recurso guarda su nombre, dueño y quien lo esta esperando, es exclusivo y solo un proceso lo puede tener una vez"""
class Recurso:
    def __init__(self, nombre):
            self.nombre = nombre           # "R1" o "R2"
            self.dueno = None              # PID del proceso que lo tiene
            self.cola_espera = deque()     # PIDs esperando este recurso, en orden de llegada
    def esta_libre(self):
            return self.dueno is None

"""Crea dos recursos que son R1 y R2, la funcion si esta libre, lo asigna y devuelve true mientras este libre, si esta ocupado el proceso
el proceso se forma en la cola y devuelve false, queda bloqueado y evita dos errores, pedir un recurso que ya se tiene y que un proceso
bloqueado pida otro recurso"""
class GestorRecursos:
    def __init__(self):
        self.recursos = {"R1": Recurso("R1"), "R2": Recurso("R2")}
    def solicitar(self, pid, nombre):
        pid = _validar_pid(pid)
        recurso = self._obtener(nombre)
        if recurso.dueno == pid:
            raise DeadlockError(f"P{pid} ya tiene {recurso.nombre}")
        if self._esta_esperando(pid):
            raise DeadlockError(f"P{pid} está bloqueado esperando un recurso y no puede pedir otro")
        if recurso.esta_libre():
            recurso.dueno = pid
            return True
        recurso.cola_espera.append(pid)
        return False

    """"Definiendo la funcion solo el dueno puede liberar el recurso y este paso al siguiente de la cola, es la solucion del deadlock
    trabajandolo con la funcion abortar_proceso el cual hace que saca el proceso de todas las colas donde estaba esperando o libera
    recursos que tenia y se los entrega a quien los esta esperando"""
    def liberar(self, pid, nombre):
            """Solo el dueño puede liberar. Devuelve el PID que recibe el recurso, o None si queda libre."""
            pid = _validar_pid(pid)
            recurso = self._obtener(nombre)
            if recurso.dueno != pid:
                raise DeadlockError(f"P{pid} no puede liberar {recurso.nombre}: no es su dueño")
            return self._entregar_al_siguiente(recurso)
    def abortar_proceso(self, pid):
        pid = _validar_pid(pid)
        for recurso in self.recursos.values():
            if pid in recurso.cola_espera:
                recurso.cola_espera.remove(pid)
        entregas = []
        for recurso in self.recursos.values():
            if recurso.dueno == pid:
                siguiente = self._entregar_al_siguiente(recurso)
                entregas.append((recurso.nombre, siguiente))
        return entregas

    """Mapa de quien esta esperando a quien, se define esta funcion. Con detectar sigue las flechas empezando por cada proceso y
    si lo encuentra, devuelve los procesos del ciclo y visitados se utiliza para recorrer dos veces el mismo proceso"""
    def grafo_de_espera(self):
        grafo = {}
        for recurso in self.recursos.values():
            if recurso.dueno is None:
                continue
            for pid in recurso.cola_espera:
                grafo[pid] = recurso.dueno
        return grafo
    def detectar_deadlock(self):
        grafo = self.grafo_de_espera()
        visitados = set()
        for inicio in grafo:
            if inicio in visitados:
                continue
            camino = []
            actual = inicio
            while actual is not None and actual not in visitados:
                visitados.add(actual)
                camino.append(actual)
                actual = grafo.get(actual)
            if actual is not None and actual in camino:
                return camino[camino.index(actual):]
        return []

    """Utilizamos describir ciclo para convertir el ciclo en un texto facil de leer, para la alerta y para el reporte y simular
    deadlock lo vamos a utilizar para simularlo, tener una demo, una prueba del interbloqueo"""
    def describir_ciclo(self, ciclo):
        partes = []
        for pid in ciclo:
            tiene = ", ".join(r.nombre for r in self.recursos.values() if r.dueno == pid)
            espera = ", ".join(r.nombre for r in self.recursos.values() if pid in r.cola_espera)
            partes.append(f"P{pid} (tiene {tiene}, espera {espera})")
        return " -> ".join(partes) + f" -> P{ciclo[0]}"
    def simular_deadlock(self, pid_a, pid_b):
        pid_a = _validar_pid(pid_a)
        pid_b = _validar_pid(pid_b)
        if pid_a == pid_b:
            raise DeadlockError("Se necesitan dos procesos distintos para simular el deadlock")
        for recurso in self.recursos.values():
            if not recurso.esta_libre():
                raise DeadlockError(f"{recurso.nombre} está ocupado por P{recurso.dueno}. Libéralo antes de simular")
        pasos = []
        self.solicitar(pid_a, "R1")
        pasos.append(f"P{pid_a} pide R1: asignado")
        self.solicitar(pid_b, "R2")
        pasos.append(f"P{pid_b} pide R2: asignado")
        self.solicitar(pid_a, "R2")
        pasos.append(f"P{pid_a} pide R2: lo tiene P{pid_b}, P{pid_a} queda BLOQUEADO")
        self.solicitar(pid_b, "R1")
        pasos.append(f"P{pid_b} pide R1: lo tiene P{pid_a}, P{pid_b} queda BLOQUEADO")
        return pasos

    """Aca utilizamos estado y describir para datos web y texto para modo consola, desde obtener aceptadmos datos y rechazamos,
    utilizamos esperando si un proceso esta bloqueado, y entregar pasa el recurso al primero de la cola o lo deja libre"""
    def estado(self):
        return {
            nombre: {"dueno": r.dueno, "cola_espera": list(r.cola_espera)}
            for nombre, r in self.recursos.items()
        }
    def describir(self):
        lineas = []
        for r in self.recursos.values():
            dueno = f"P{r.dueno}" if r.dueno is not None else "libre"
            cola = ", ".join(f"P{p}" for p in r.cola_espera) or "(vacía)"
            lineas.append(f"{r.nombre}: dueño {dueno} | esperando: {cola}")
        return "\n".join(lineas)
    def _obtener(self, nombre):
        clave = str(nombre).strip().upper()
        if clave not in self.recursos:
            raise DeadlockError(f"El recurso '{nombre}' no existe. Usa R1 o R2")
        return self.recursos[clave]
    def _esta_esperando(self, pid):
        return any(pid in r.cola_espera for r in self.recursos.values())
    def _entregar_al_siguiente(self, recurso):
        if not recurso.cola_espera:
            recurso.dueno = None
            return None
        recurso.dueno = recurso.cola_espera.popleft()
        return recurso.dueno

"""Nos ayuda a detectar error en el deadlock"""
def _validar_pid(pid):
    if isinstance(pid, bool) or not isinstance(pid, int) or pid < 1:
        raise DeadlockError(f"El PID debe ser un número entero positivo (recibido: {pid!r})")
    return pid

"""Prueba del deadlock a nivel consola"""
if __name__ == "__main__":
    g = GestorRecursos()
    print("1. Simulación del deadlock")
    for paso in g.simular_deadlock(1, 2):
        print("  " + paso)
    print(g.describir())
    print("\n2. Detección")
    ciclo = g.detectar_deadlock()
    if ciclo:
        print("  ¡DEADLOCK DETECTADO!", g.describir_ciclo(ciclo))
    else:
        print("  No hay deadlock")
    print("\n3. Resolución: abortar P1")
    for recurso, nuevo_dueno in g.abortar_proceso(1):
        print(f"  {recurso} pasa a P{nuevo_dueno}" if nuevo_dueno else f"  {recurso} queda libre")
    print(g.describir())
    print("  ¿Sigue el deadlock?", "Sí" if g.detectar_deadlock() else "No, se rompió el ciclo")
    print("\n4. Errores esperados")
    for prueba in (lambda: g.solicitar(3, "R3"),
                lambda: g.liberar(5, "R1"),
                lambda: g.solicitar("abc", "R1"),
                lambda: g.simular_deadlock(1, 1)):
        try:
            prueba()
        except DeadlockError as error:
            print("  Error esperado:", error)