"""
#PUNTO C: Concurrencia y sincronizacion
Semaforo binario con wait() y signal() y una seccion critica que protege una variable global compartida
Valor = 1-> la seccion critica esta libre
Valor = 0-> la seccion critica esta ocupada por el dueño
"""

"""deque es una cola la cual forma a los procesos que esperan su turno aplicando el principio FIFO"""
from collections import deque

"""Error controlado del semaforo, cuando alguien haga algo no permitido como un signal de un proceseo que no es el dueño,
lanza este mensaje de error"""
class SemaforoError(Exception):

    """
    Clase que implementa semaforo binario y definidmos los valores iniciales, 1 = libre, 0 = ocupado, PID del proceso, cola para PIDs de
    Espera y orden de llegada, y la variable global
    """
class SemaforoBinario:
    def __init__(self):
        self.valor = 1
        self.dueno = None
        self.cola_espera = deque()
        self.variable_compartida = 0

    """Primero validamos el PID, evitamos dos errores, que un proceso entre dos veces o se forme dos veces en la cola, usamos lo valores
    1 si esta libre para que cierre el semaforo y 0 si esta ocupado para que entre a la cola de espera"""
    def wait(self, pid):
        pid = _validar_pid(pid)
        if self.dueno == pid:
            raise SemaforoError(f"P{pid} ya esta dentro de la seccion critica")
        if pid in self.cola_espera:
            raise SemaforoError(f"P{pid} ya esta esperando en la cola del semaforo")
        if self.valor == 1:
            self.valor = 0
            self.dueno = pid
            return True

        self.cola_espera.append(pid)
        return False

    """validamos para poder salir de la seccion critica, si no hay nadie dentro, no hay nada que liberar, si quien libera no es el dueno
    error, solo puede salir quien entro, si todo esta bien, si todo esta bien, pasa al siguiente de la cola"""
    def signal(self, pid):
        pid = _validar_pid(pid)
        if self.dueno is None:
            raise SemaforoError (f"La seccion critica esta libre: P{pid} no tiene nada que liberar")
        if self.dueno != pid:
            raise SemaforoError(f"P{pid} no puede hacer signal(): el dueno es P{self.dueno}")
        return self._entregar_al_siguiente()

    """Estamos realizando la exclusion mutua lo cual solo quien tiene el semaforo puede tocar la variable, aca solo aceptamos
    valores enteros y rechazamos textos, decimales, booleanos, etc"""
    def escribir(self, pid, nuevo_valor):
        pid =_validar_pid(pid)
        if self.dueno != pid:
            raise SemaforoError(f"Acceso denegado: P{pid} no tiene el semaforo. Primero debe hacer wait({pid})")
        if isinstance(nuevo_valor, bool) or not isinstance(nuevo_valor, int):
            raise SemaforoError(f"El valor debe ser un numero entero (recibido:{nuevo_valor!r})")
        anterior = self.variable_compartida
        self.variable_compartida = nuevo_valor
        return anterior

    """si el proceso estaba esperando lo saca de la cola y si era el dueno lo pasa la seccion al siguiente, asi el semaforo
    no se queda bloqueado y puede seguir funcionando, no se quedara bloqueado en ningun proceso"""
    def liberar_proceso(self, pid):
        if pid in self.cola_espera:
            self.cola_espera.remove(pid)
        if self.dueno == pid:
            return self._entregar_al_siguiente()
        return None

    def esta_libre(self):
        return self.valor == 1

    """funcion que devuelve los datos como diccionario, nos ayuda para la web con PyScript"""
    def estado(self):
        return {
            "valor": self.valor,
            "libre": self.esta_libre(),
            "dueno": self.dueno,
            "cola_espera": list(self.cola_espera),
            "variable_compartida": self.variable_compartida,
        }

    """funcion que devuelve como texto para leer"""
    def describir(self):
        dueno = f"P{self.dueno}" if self.dueno is not None else "-"
        cola = ", ".join(f"P{p}" for p in self.cola_espera) or "(vacia)"
        libre = "libre" if self. esta_libre() else "ocupado"
        return (f"Semaforo = {self.valor} ({libre}) | Dueno: {dueno} | "f"Cola de espera: {cola} | Variable compartida: {self.variable_compartida}")

    """pasa la seccion al primero de la cola, o lo deja libre, aca si nadie espera, libera el semaforo y si hay alguien saca al primero de
    la cola y lo hace nuevo dueno, el valor queda en 0 porque la seccion pasa directo a este proceso"""
    def _entregar_al_siguiente(self):
        if not self.cola_espera:
            self.valor = 1
            self.dueno = None
            return None
        self.dueno = self.cola_espera.popleft()
        return self.dueno

"""rechaza textos, negativos y el 0"""
def _validar_pid(pid):
    if isinstance(pid, bool) or not isinstance(pid, int) or pid < 1:
        raise SemaforoError(f"El PID debe ser un numero entero positivo (recibido: {pid!r})")
    return pid

"""Simulacion de 2 hilos (H1 y H2) que suman a 1 contador que vale 0. Lo correcto es 2. Sin semaforo da 1, con semaforo da 2.
Devuelve un resultado, lista de pasos, aca guarda cada paso en una lista para mostrarlos en el reporte"""
def demo_condicion_de_carrera(con_semaforo):
    pasos = []
    contador = 0

    if not con_semaforo:
        pasos.append("Carrera SIN semaforo: H1 y H2 suman 1 a un contador que vale 0")
        lectura_h1 = contador
        pasos.append(f"H1 lee el contador = {lectura_h1}")
        lectura_h2 = contador
        pasos.append(f"H2 lee el contador = {lectura_h2} (H1 todavia no escribe)")
        contador = lectura_h1 + 1
        pasos.append(f"H1 calcula {lectura_h1} + 1 y escribe {contador}")
        contador = lectura_h2 + 1
        pasos.append(f"H2 calcula {lectura_h2} + 1 y escribe {contador} (sobreescribe lo de H1)")
        pasos.append(f"Resultado: {contador}, se esperaba 2 -> CONDICION DE CARRERA")
        return contador, pasos
    pasos.append("Carrera CON semáforo: H1 y H2 suman 1 a un contador que vale 0")
    semaforo = SemaforoBinario()
    semaforo.wait(1)
    pasos.append("H1 hace wait(): entra a la sección crítica (semáforo = 0)")
    semaforo.wait(2)
    pasos.append("H2 hace wait(): la sección está ocupada, H2 queda BLOQUEADO")
    lectura_h1 = contador
    contador = lectura_h1 + 1
    pasos.append(f"H1 lee {lectura_h1}, calcula {lectura_h1} + 1 y escribe {contador}")
    siguiente = semaforo.signal(1)
    pasos.append(f"H1 hace signal(): sale y entra H{siguiente}")
    lectura_h2 = contador
    contador = lectura_h2 + 1
    pasos.append(f"H2 lee {lectura_h2}, calcula {lectura_h2} + 1 y escribe {contador}")
    semaforo.signal(2)
    pasos.append("H2 hace signal(): sale (semáforo = 1)")
    pasos.append(f"Resultado: {contador}, se esperaba 2 -> el semáforo garantizó la exclusión mutua")
    return contador, pasos

"""Ejecucion del proyecto en demo, desde archivo directo sin utilizacion de main, solo es para pruebas"""
if __name__ == "__main__":
    s = SemaforoBinario()
    print("P1 wait ->", s.wait(1))          #
    print("P2 wait ->", s.wait(2))          
    print(s.describir())
    print("P1 signal ->", s.signal(1))     
    print(s.describir())
    try:
        s.signal(1)                         
    except SemaforoError as error:
        print("Error esperado:", error)
    try:
        s.wait("abc")                      
    except SemaforoError as error:
        print("Error esperado:", error)
    for usar_semaforo in (False, True):
        resultado, pasos = demo_condicion_de_carrera(usar_semaforo)
        print()
        for paso in pasos:
            print("  " + paso)