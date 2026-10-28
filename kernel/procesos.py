# Gestión de procesos del PCB y planificación Rount Robin

from collections import deque

# Estados de un proceso
NUEVO = "Nuevo"
LISTO = "Listo"
EJECUTANDO = "Ejecutando"
BLOQUEADO = "Bloqueado"
TERMINADO = "Terminado"

class PCB: 

    # Bloque de control de procesos 
    # Representa la información que el kernel guarda en cada proceso

    def __init__(self, pid, tamano_memoria, rafaga_total):
        # Datos para calcular el PCB
        self.pid = pid                         # ID de cada proceso
        self.estado = NUEVO                    # Cada proceso es NUEVO al crearse
        self.tamano_memoria = tamano_memoria   # La memoria en MB que ocupa el proceso
        self.rafaga_total = rafaga_total       # Tiempo que la CPU necesita para ejecutar
        self.rafaga_restante = rafaga_total    # En un principio la rafaga restante es igual a la total

        #Datos para calcular Round Robin
        self.tiempo_espera = 0                 # Tiempo que el proceso ha estado esperando
        self.tiempo_finalizacion = 0                   # Tiempo en que el proceso termina de ejecutarse

        #Impresión de los datos del PCB
    def __str__(self):
        """Devuelve el PCB como texto legible para mostrarlo en consola."""
        return (f"PID: {self.pid} | Estado: {self.estado} | " #la f es f-string, permite poner variables dentro de un string
                f"Memoria: {self.tamano_memoria} MB | "
                f"Ráfaga total: {self.rafaga_total} | "
                f"Ráfaga restante: {self.rafaga_restante}")


# Restricciones del sistema en caso hayan pruebas de datos ingresados

RAM_TOTAL = 100
siguiente_pid = 1

def validar_entero_positivo(texto, nombre_campo):

    #Valida que el texto ingresado sea un número entero
    #Si el dato ingresado no es entero falla con el ValueError.
    try:
        numero = int(texto)
    except ValueError:
        raise ValueError(f"{nombre_campo} debe ser un número entero y positivo, el dato ingresado es: '{texto}'")


    #Esta parte valida que el número sea mayor a 0
    if numero <= 0:
        raise ValueError(f"{nombre_campo} debe ser un número mayor que 0 , el dato ingresado es: '{texto}'")

    return numero

#En esta sección se validarán los datos ingresados y creará un nuevo proceso (PCB)}

def crear_proceso(tamano_texto, rafaga_texto):

    #El global permite modificar la variable siguiente_pid
    global siguiente_pid

    #Ahora aquí se validan los formatos, deben ser enteros positivos
    tamano = validar_entero_positivo(tamano_texto, "El tamaño de lamemoria" )
    rafaga = validar_entero_positivo(rafaga_texto, "La ráfaga del CPU" )

    #Valida si el tamaño es mayor al limite de ram que se puede usar muestra una alerta
    if tamano > RAM_TOTAL:
        raise ValueError(f"El tamaño de la memoria del proceso no puede ser mayor a {RAM_TOTAL} MB, el dato ingresado es: '{tamano}'")

    #Si en dado caso todo es valido entonces se crea el proceso y se avanza con el contador
    proceso = PCB(siguiente_pid, tamano, rafaga)
    siguiente_pid += 1  #se suma uno al siguiente PID para el próximo proceso que se cree
    return proceso


QUANTUM = 3 # Es el tiempo máximo del CPU que se tarda por cada turno


class Planificador:
    #Esta clase se encarga de los procesos con el algoritmo Round Robin
    #Administra la cola de listos y el reloj de la CPU

    def __init__(self, quantum=QUANTUM):

        # Esta es la cola de listos, son los procesos que esperan turno del CPU
        self.cola_listos = deque()

        # Este es el tiempo máximo que un proceso puede usar la CPU por turno
        self.quantum = quantum

        # Este es el reloj del sistema, avanza cada vez que el proceso se ejecuta avanza
        self.tiempo_actual = 0

        # Este es para los rocesos que ya terminaron, calcula las métricas al final
        self.terminados = []

    def agregar_proceso(self, proceso):
        #Coloca el proceso al final de la cola de listos, y cambia su status de nuevo a listo
        proceso.estado = LISTO
        self.cola_listos.append(proceso)

    def mostrar_cola_listos(self):
        #Aqui se muestran en consola los procesos que esperan en la cola
        if not self.cola_listos:
            print("La cola de listos se encuentra vacia")
            return
        
        print("Procesos en la cola de listos: ")
        #Aqui se usa enumerate por que ayuda a mostrar la posicion de cada proceso en la cola
        for posicion, proceso in enumerate(self.cola_listos, start=1):

            print(f"{posicion}. {proceso}")


    def ejecutar_round_robin(self):

        #Aqui se ejecutan los procesos de la cola de listos con el algoritmo de Round Robin
        
        #Si no existen procesos, no hay nada que se deba ejecutar
        if not self.cola_listos:
            print("No hay procesos en la cola de listos para ejecutar.")
            return

        print(f"Inicio de la planificación Round Robin (quantum = {self.quantum})")

        #El proceso se repetira media vez queden procesos esperando en cola
        while self.cola_listos:

            #El proceso que esta al frente de la cola se toma y pasa a ejecución
            proceso = self.cola_listos.popleft()
            proceso.estado = EJECUTANDO

            #En esta parte se decide cuanto tiempo se va a usar la CPU en ese proceso
            tiempo_uso = min(self.quantum, proceso.rafaga_restante)

            #En esta sección se avanza el reloj del sistema y se reduce la ráfaga restante del proceso
            inicio = self.tiempo_actual
            self.tiempo_actual += tiempo_uso
            proceso.rafaga_restante -= tiempo_uso

            #En esta parte se muestra en consola lo que ocurrio en este turno del CPU
            print(f"[t={inicio} a t={self.tiempo_actual}] PID {proceso.pid} se ejecuta "
                  f"{tiempo_uso} unidad(es). Ráfaga restante: {proceso.rafaga_restante}")

            #Ahora si ya no quedan rafagas entonces el proceso se da por finalizado
            if proceso.rafaga_restante == 0:
                proceso.estado = TERMINADO
                proceso.tiempo_finalizacion = self.tiempo_actual
                self.terminados.append(proceso)  #append significa agregar al final, la lista crece en uno y se mete en la ultima posicion
                print(f"    PID {proceso.pid} terminó en t={self.tiempo_actual}")

            #Si todavía llegase a tener ráfagas restantes, el proceso vuelve a la cola de listos y se coloca al final de la cola
            else:
                proceso.estado = LISTO
                self.cola_listos.append(proceso)
                print(f"    PID {proceso.pid} vuelve a la cola de listos.")

        print("Todos los procesos han terminado.")

    
    def mostrar_metricas(self):
        #Calcula e imprime el tiempo de retorno y de espera de cada proceso terminado, junto con sus promedios

        #Si ningún proceso  ha terminado no existen datos para calcular
        if not self.terminados:
            print("No hay procesos terminados para calcular nada.")
            return  

        print("Las metricas del Round Robin:")
        
        # Encabezado de la tabla. Los :<n hacen que cada columna ocupe n espacios
        # alineada a la izquierda, para que los datos queden ordenados.
        print(f"{'PID':<6}{'Ráfaga':<9}{'Finalización':<15}{'Retorno':<10}{'Espera':<8}")

        #Estos son acumuladores que me ayudarán a calcular el promedio al final}
        suma_retorno = 0
        suma_espera = 0

        #Se recorren los procesos en el orden en que terminaron
        for proceso in self.terminados:

            #El tiempo de retorno es finalización - llegada
            tiempo_retorno = proceso.tiempo_finalizacion

            #El tiempo de espera es igual a retorno - rafaga total da el tiempo que paso en cola sin usar la CPU
            proceso.tiempo_espera = tiempo_retorno - proceso.rafaga_total

            #Aqui se suman los valores para calcular los promedios después
            suma_retorno += tiempo_retorno
            suma_espera += proceso.tiempo_espera

            #Aqui se imprime
            print(f"{proceso.pid:<6}{proceso.rafaga_total:<9}"
                  f"{proceso.tiempo_finalizacion:<15}{tiempo_retorno:<10}"
                  f"{proceso.tiempo_espera:<8}")

        # Promedio es igual a la suma de todos los valores dividido cantidad de procesos.
        # :.2f muestra el resultado con 2 decimales.
        cantidad = len(self.terminados)
        print()
        print(f"Tiempo de retorno promedio: {suma_retorno / cantidad:.2f}")
        print(f"Tiempo de espera promedio: {suma_espera / cantidad:.2f}")


# SECCIÓN DE PRUEBAS DE LA CLASE PCB Y DEL PLANIFICADOR ROUND ROBIN
if __name__ == "__main__":
    #  ejemplos de algunos casos como escribirían algunos usuarios
    casos = [("20", "7"), ("abc", "5"), ("", "5"), ("-5", "3"),
             ("10", "0"), ("3.5", "2"), ("200", "4"), ("35", "4")]

    # Se crea el planificador que recibirá los procesos válidos
    planificador = Planificador()

    # Se prueba cada caso, si esta bien ingresado se crea, si no, se muestra el motivo
    for tamano, rafaga in casos:
        try:
            p = crear_proceso(tamano, rafaga)
            print("Creado:", p)
            # Si el proceso es válido, entra a la cola de listos
            planificador.agregar_proceso(p)
        except ValueError as error:
            print("Rechazado:", error)

    # Se muestra cómo quedó la cola de listos al final
    print()
    planificador.mostrar_cola_listos()

    #Se ejecuta el algoritmo de Round Robin con los procesos en cola
    print()
    planificador.ejecutar_round_robin()

    print()
    planificador.mostrar_metricas()