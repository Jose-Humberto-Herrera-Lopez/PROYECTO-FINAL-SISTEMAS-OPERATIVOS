"""Punto C: semaforo binario para controlar la entrada a una seccion critica.
valor = 1 significa libre; valor = 0 significa ocupado por el PID dueño.
Los PID que llegan mientras esta ocupado esperan su turno en una cola FIFO."""

"""deque es una cola la cual forma a los procesos que esperan su turno aplicando el principio FIFO"""
from collections import deque

"""Error controlado cuando se intenta una operacion no permitida con el semaforo."""
class SemaforoError(Exception):

    """Excepcion propia del semaforo; main.py la captura y muestra su mensaje."""
"""Guarda el valor, el dueño, la cola FIFO y la variable protegida."""
class SemaforoBinario:
    """Se ejecuta al crear SemaforoBinario(); empieza libre y con variable en cero."""
    def __init__(self):
        # 1 es libre; cuando un PID entre, wait lo cambiara a 0.
        self.valor = 1
        # None significa que todavia no hay un proceso dentro.
        self.dueno = None
        # Cada instancia tiene su propia cola de espera.
        self.cola_espera = deque()
        # Este es el dato que solo el dueño puede modificar mediante escribir().
        self.variable_compartida = 0

    """wait pide entrar: True si este PID recibe el semaforo, False si queda en cola.
    Rechaza al dueño que intenta entrar otra vez y a quien ya esta esperando.
    Para cambiar el orden de espera, se revisa esta cola y la entrega del turno."""
    def wait(self, pid):
        # Primero se comprueba el PID antes de cambiar valor, dueño o cola.
        pid = _validar_pid(pid)
        # El mismo PID no puede adquirir dos veces el semaforo.
        if self.dueno == pid:
            raise SemaforoError(f"P{pid} ya esta dentro de la seccion critica")
        # Tampoco puede aparecer dos veces en la cola.
        if pid in self.cola_espera:
            raise SemaforoError(f"P{pid} ya esta esperando en la cola del semaforo")
        # Si esta libre, este PID entra y pasa a ser dueño.
        if self.valor == 1:
            self.valor = 0
            self.dueno = pid
            return True

        # Si esta ocupado, queda al final de la cola y wait devuelve False.
        self.cola_espera.append(pid)
        return False

    """signal permite salir solo al dueño y entrega el turno al primero de la cola.
    Devuelve el nuevo PID dueño, o None si el semaforo queda libre.
    Para permitir signal de otro PID, se cambiaria la comprobacion del dueño."""
    def signal(self, pid):
        # Se comprueba el PID y luego si realmente tiene algo que liberar.
        pid = _validar_pid(pid)
        if self.dueno is None:
            raise SemaforoError (f"La seccion critica esta libre: P{pid} no tiene nada que liberar")
        # Un proceso distinto del dueño no puede ejecutar signal().
        if self.dueno != pid:
            raise SemaforoError(f"P{pid} no puede hacer signal(): el dueno es P{self.dueno}")
        # La funcion auxiliar decide si pasa el turno o queda libre.
        return self._entregar_al_siguiente()

    """Solo el dueño puede cambiar la variable compartida.
    Acepta un entero, lo guarda y devuelve el valor que tenia antes.
    Para admitir texto u otro tipo, se cambia la validacion de nuevo_valor."""
    def escribir(self, pid, nuevo_valor):
        pid =_validar_pid(pid)
        # Tener el semaforo es requisito para escribir la variable.
        if self.dueno != pid:
            raise SemaforoError(f"Acceso denegado: P{pid} no tiene el semaforo. Primero debe hacer wait({pid})")
        # bool se rechaza expresamente porque en Python True tambien es int.
        if isinstance(nuevo_valor, bool) or not isinstance(nuevo_valor, int):
            raise SemaforoError(f"El valor debe ser un numero entero (recibido:{nuevo_valor!r})")
        # Se guarda el valor anterior antes de reemplazarlo, para devolverlo.
        anterior = self.variable_compartida
        self.variable_compartida = nuevo_valor
        return anterior

    """Al abortar un PID, lo quita de la cola o entrega el semaforo si era dueño.
    Devuelve el siguiente dueño o None. No modifica el PCB del planificador.
    Si se pide validar tambien este PID, aqui se agregaria _validar_pid(pid)."""
    def liberar_proceso(self, pid):
        # Si el PID solo esperaba, se elimina de la cola.
        if pid in self.cola_espera:
            self.cola_espera.remove(pid)
        # Si era dueño, se entrega el turno al siguiente.
        if self.dueno == pid:
            return self._entregar_al_siguiente()
        return None

    """True si valor es 1; solo consulta el estado."""
    def esta_libre(self):
        return self.valor == 1

    """Devuelve los datos en un diccionario; list() copia la cola.
    Si se añade un dato al semaforo, se puede incluir aqui para mostrarlo."""
    def estado(self):
        return {
            "valor": self.valor,
            "libre": self.esta_libre(),
            "dueno": self.dueno,
            # La cola interna es deque; se presenta como lista para verla facilmente.
            "cola_espera": list(self.cola_espera),
            "variable_compartida": self.variable_compartida,
        }

    """Convierte el estado en una linea de texto para la consola y la web.
    Para cambiar lo que ve el usuario, se modifica este formato."""
    def describir(self):
        # Si no hay dueño se muestra un guion; si no hay cola se muestra vacia.
        dueno = f"P{self.dueno}" if self.dueno is not None else "-"
        cola = ", ".join(f"P{p}" for p in self.cola_espera) or "(vacia)"
        libre = "libre" if self. esta_libre() else "ocupado"
        return (f"Semaforo = {self.valor} ({libre}) | Dueno: {dueno} | "f"Cola de espera: {cola} | Variable compartida: {self.variable_compartida}")

    """Si nadie espera, deja valor=1 y dueno=None.
    Si alguien espera, le pasa el turno directamente y valor permanece en 0."""
    def _entregar_al_siguiente(self):
        # Con cola vacia ya no hay nadie en la seccion critica.
        if not self.cola_espera:
            self.valor = 1
            self.dueno = None
            return None
        # popleft() elige al primero; el valor sigue en 0 porque ya tiene nuevo dueño.
        self.dueno = self.cola_espera.popleft()
        return self.dueno

"""Acepta PID enteros positivos; rechaza bool, cero, negativos y texto.
Lanza SemaforoError antes de modificar el estado. Para aceptar PID 0, cambiar esta regla."""
def _validar_pid(pid):
    if isinstance(pid, bool) or not isinstance(pid, int) or pid < 1:
        raise SemaforoError(f"El PID debe ser un numero entero positivo (recibido: {pid!r})")
    return pid

"""Demo guiada de dos hilos que suman 1 a un contador local inicialmente en 0.
Sin semaforo ambos leen 0 y queda 1; con turnos ordenados queda 2.
No crea hilos reales ni usa la variable_compartida de SemaforoBinario."""
def demo_condicion_de_carrera(con_semaforo):
    pasos = []
    contador = 0

    # Sin semaforo, se intercalan las lecturas antes de que alguien escriba.
    if not con_semaforo:
        pasos.append("Carrera SIN semaforo: H1 y H2 suman 1 a un contador que vale 0")
        # H1 lee cero, pero aun no ha actualizado el contador.
        lectura_h1 = contador
        pasos.append(f"H1 lee el contador = {lectura_h1}")
        # H2 tambien lee cero: ambos calcularan desde un valor antiguo.
        lectura_h2 = contador
        pasos.append(f"H2 lee el contador = {lectura_h2} (H1 todavia no escribe)")
        # H1 escribe uno; H2 despues sobrescribe con uno y se pierde un aumento.
        contador = lectura_h1 + 1
        pasos.append(f"H1 calcula {lectura_h1} + 1 y escribe {contador}")
        contador = lectura_h2 + 1
        pasos.append(f"H2 calcula {lectura_h2} + 1 y escribe {contador} (sobreescribe lo de H1)")
        pasos.append(f"Resultado: {contador}, se esperaba 2 -> CONDICION DE CARRERA")
        return contador, pasos
    # Con semaforo, la demo ordena primero el turno de H1 y luego el de H2.
    pasos.append("Carrera CON semáforo: H1 y H2 suman 1 a un contador que vale 0")
    # Este semaforo es local a la demo; no es el mismo objeto usado por main.py.
    semaforo = SemaforoBinario()
    semaforo.wait(1)
    pasos.append("H1 hace wait(): entra a la sección crítica (semáforo = 0)")
    semaforo.wait(2)
    pasos.append("H2 hace wait(): la sección está ocupada, H2 queda BLOQUEADO")
    # H1 actualiza el contador mientras es dueño.
    lectura_h1 = contador
    contador = lectura_h1 + 1
    pasos.append(f"H1 lee {lectura_h1}, calcula {lectura_h1} + 1 y escribe {contador}")
    # signal entrega el turno a H2, que ahora puede leer el valor actualizado.
    siguiente = semaforo.signal(1)
    pasos.append(f"H1 hace signal(): sale y entra H{siguiente}")
    # H2 lee uno y llega a dos.
    lectura_h2 = contador
    contador = lectura_h2 + 1
    pasos.append(f"H2 lee {lectura_h2}, calcula {lectura_h2} + 1 y escribe {contador}")
    # Nadie mas espera: signal deja el semaforo libre.
    semaforo.signal(2)
    pasos.append("H2 hace signal(): sale (semáforo = 1)")
    pasos.append(f"Resultado: {contador}, se esperaba 2 -> el semáforo garantizó la exclusión mutua")
    return contador, pasos

"""Esta demo corre solo al ejecutar semaforo.py directamente, no al importarlo desde main.py."""
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
