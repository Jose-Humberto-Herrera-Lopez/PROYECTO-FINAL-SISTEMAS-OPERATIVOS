"""Punto D: simulacion de interbloqueo con R1 y R2, recursos exclusivos.
P1 tiene R1 y espera R2; P2 tiene R2 y espera R1.
Ambos forman una espera circular. El gestor detecta el ciclo y puede romperlo abortando un PID."""

"""deque = cola para los procesos que esperan un recurso, se utiliza para la cola de espera (FIFO)"""
from collections import deque

"""Error controlado de recursos (por ejemplo, liberar un recurso que no es propio)"""
class DeadlockError(Exception):

    """Excepcion para operaciones de recursos no validas."""
"""Construccion del recurso que estamos utilizando: nombre, dueño y cola de espera."""
class Recurso:
    """Se ejecuta al crear Recurso("R1") o Recurso("R2"); self es esa ficha concreta."""
    def __init__(self, nombre):
            # self es esta ficha concreta, por ejemplo el objeto R1.
            self.nombre = nombre           # definimos el nombre del recurso como por ejemplo "R1" o "R2" etc.
            self.dueno = None              # PID del proceso que lo tiene, None ya que al inicio nadie lo tiene
            self.cola_espera = deque()     # PIDs esperando este recurso, en orden de llegada
    """True significa que dueno es None; solo consulta, no asigna el recurso."""
    def esta_libre(self):                  # Evaluamos si el recurso esta libre
            return self.dueno is None

"""Administrador que coordina los recursos, tanto R1 como R2."""
class GestorRecursos:
    """Crea las dos fichas de recursos al iniciar un gestor nuevo."""
    def __init__(self):
        # Para agregar R3 habria que crearlo aqui y ofrecerlo en el menu y la web.
        self.recursos = {"R1": Recurso("R1"), "R2": Recurso("R2")}          # Cada clave guarda un objeto Recurso independiente
    """True: se asigno ahora. False: el PID entro a la cola. Error: solicitud invalida.
    Para prevenir deadlock por orden de recursos, la regla se agregaria aqui."""
    def solicitar(self, pid, nombre):
        pid = _validar_pid(pid)                                             # Comprobamos que el PID sea un entero positivo
        recurso = self._obtener(nombre)                                     # Buscamos el objeto R1 o R2 por su nombre
        if recurso.dueno == pid:                                            # Si el PID ya lo tiene, lanzamos error
            raise DeadlockError(f"P{pid} ya tiene {recurso.nombre}")
        # Un PID que ya espera un recurso no puede iniciar otra espera.
        if self._esta_esperando(pid):
            raise DeadlockError(f"P{pid} está bloqueado esperando un recurso y no puede pedir otro")
        # Si nadie lo posee, se convierte inmediatamente en el nuevo dueño.
        if recurso.esta_libre():
            recurso.dueno = pid                                             # Si el recurso esta libre, lo asigna y devuelve true
            return True
        # Si esta ocupado, espera al final de la cola FIFO sin quitarlo al dueño actual.
        recurso.cola_espera.append(pid)                                     # Lo agregamos a la cola y luego devolvemos False
        return False

    """Solo el dueño puede liberar un recurso; pasa al primero de la cola o queda libre.
    Devuelve el nuevo PID dueño, o None si no habia nadie esperando."""
    def liberar(self, pid, nombre):
            pid = _validar_pid(pid)
            recurso = self._obtener(nombre)
            if recurso.dueno != pid:
                raise DeadlockError(f"P{pid} no puede liberar {recurso.nombre}: no es su dueño")
            return self._entregar_al_siguiente(recurso)
    """Retira el PID de las colas y entrega todos los recursos que tenia.
    Solo cambia este gestor: no termina un PCB ni libera memoria del proyecto."""
    def abortar_proceso(self, pid):
        pid = _validar_pid(pid)
        # Primero sale de las colas para que el PID abortado no reciba un recurso despues.
        for recurso in self.recursos.values():
            if pid in recurso.cola_espera:
                recurso.cola_espera.remove(pid)
        entregas = []
        # Despues entrega cada recurso que era suyo y registra a quien paso.
        for recurso in self.recursos.values():
            if recurso.dueno == pid:
                siguiente = self._entregar_al_siguiente(recurso)
                entregas.append((recurso.nombre, siguiente))
        return entregas

    """Construye el grafo de espera: PID que espera -> PID dueño.
    Por ejemplo, {1: 2} significa que P1 espera algo que tiene P2.
    Si un PID pudiera esperar varios recursos a la vez, habria que guardar varias flechas."""
    def grafo_de_espera(self):
        grafo = {}
        for recurso in self.recursos.values():
            if recurso.dueno is None:
                continue
            for pid in recurso.cola_espera:
                grafo[pid] = recurso.dueno
        return grafo
    """Sigue las flechas del grafo y devuelve el primer ciclo encontrado, o [].
    visitados evita repetir trabajo; camino identifica si se regreso a la ruta actual.
    Si se piden todos los ciclos, esta funcion tendria que acumularlos."""
    def detectar_deadlock(self):
        grafo = self.grafo_de_espera()
        visitados = set()
        for inicio in grafo:
            if inicio in visitados:
                continue
            # Se empieza una ruta nueva desde este PID.
            camino = []
            actual = inicio
            while actual is not None and actual not in visitados:
                visitados.add(actual)
                camino.append(actual)
                # Si actual espera, avanzamos al dueño; si no espera, .get devuelve None.
                actual = grafo.get(actual)
            # Volver a un PID de este mismo camino significa que se cerro un ciclo.
            if actual is not None and actual in camino:
                return camino[camino.index(actual):]
        return []

    """Recibe un ciclo no vacio como [2, 1] y explica que tiene y espera cada PID."""
    def describir_ciclo(self, ciclo):
        partes = []
        for pid in ciclo:
            # Busca en las dos fichas que recurso posee y cual esta esperando.
            tiene = ", ".join(r.nombre for r in self.recursos.values() if r.dueno == pid)
            espera = ", ".join(r.nombre for r in self.recursos.values() if pid in r.cola_espera)
            partes.append(f"P{pid} (tiene {tiene}, espera {espera})")
        # Se repite el primer PID al final para que se vea el cierre del ciclo.
        return " -> ".join(partes) + f" -> P{ciclo[0]}"
    """Arma la demo: A toma R1, B toma R2, A espera R2 y B espera R1.
    Devuelve los mensajes; la deteccion se hace despues con detectar_deadlock().
    Para simular otro orden o mas recursos, se cambian estas solicitudes."""
    def simular_deadlock(self, pid_a, pid_b):
        pid_a = _validar_pid(pid_a)
        pid_b = _validar_pid(pid_b)
        if pid_a == pid_b:
            raise DeadlockError("Se necesitan dos procesos distintos para simular el deadlock")
        # La demo necesita R1 y R2 libres para comenzar desde un estado conocido.
        for recurso in self.recursos.values():
            if not recurso.esta_libre():
                raise DeadlockError(f"{recurso.nombre} está ocupado por P{recurso.dueno}. Libéralo antes de simular")
        pasos = []
        # Las dos primeras solicitudes se asignan.
        self.solicitar(pid_a, "R1")
        pasos.append(f"P{pid_a} pide R1: asignado")
        self.solicitar(pid_b, "R2")
        pasos.append(f"P{pid_b} pide R2: asignado")
        # Las dos siguientes quedan en espera y forman el ciclo.
        self.solicitar(pid_a, "R2")
        pasos.append(f"P{pid_a} pide R2: lo tiene P{pid_b}, P{pid_a} queda BLOQUEADO")
        self.solicitar(pid_b, "R1")
        pasos.append(f"P{pid_b} pide R1: lo tiene P{pid_a}, P{pid_b} queda BLOQUEADO")
        return pasos

    """Devuelve dueño y cola de cada recurso como diccionario; list() copia la cola."""
    def estado(self):
        return {
            nombre: {"dueno": r.dueno, "cola_espera": list(r.cola_espera)}
            for nombre, r in self.recursos.items()
        }
    """Convierte el estado en texto para la consola y la web."""
    def describir(self):
        lineas = []
        for r in self.recursos.values():
            dueno = f"P{r.dueno}" if r.dueno is not None else "libre"
            cola = ", ".join(f"P{p}" for p in r.cola_espera) or "(vacía)"
            lineas.append(f"{r.nombre}: dueño {dueno} | esperando: {cola}")
        return "\n".join(lineas)
    """Acepta nombres como " r1 " y devuelve el objeto; rechaza otros nombres.
    Si se agregan recursos, este metodo debe aceptarlos a traves del diccionario."""
    def _obtener(self, nombre):
        clave = str(nombre).strip().upper()
        if clave not in self.recursos:
            # Si se agrega R3, tambien hay que actualizar este mensaje.
            raise DeadlockError(f"El recurso '{nombre}' no existe. Usa R1 o R2")
        return self.recursos[clave]
    """True si el PID ya aparece en la cola de cualquiera de los recursos.
    Para permitir varias solicitudes pendientes por PID, hay que revisar esta regla."""
    def _esta_esperando(self, pid):
        return any(pid in r.cola_espera for r in self.recursos.values())
    """Entrega al primero en llegar (FIFO), o deja el recurso libre si nadie espera.
    Para atender por prioridad se cambiaria esta seleccion."""
    def _entregar_al_siguiente(self, recurso):
        if not recurso.cola_espera:
            recurso.dueno = None
            return None
        # popleft() extrae al primero; ese PID deja de esperar y pasa a ser dueño.
        recurso.dueno = recurso.cola_espera.popleft()
        return recurso.dueno

"""Acepta solo PID enteros positivos; rechaza bool, cero, negativos y texto.
Lanza DeadlockError antes de modificar recursos. Para aceptar PID 0, se cambia esta regla."""
def _validar_pid(pid):
    if isinstance(pid, bool) or not isinstance(pid, int) or pid < 1:
        raise DeadlockError(f"El PID debe ser un número entero positivo (recibido: {pid!r})")
    return pid

"""Esta demo corre solo al ejecutar deadlock.py directamente, no al importarlo desde main.py."""
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
