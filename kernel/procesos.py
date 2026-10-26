# Gestión de procesos del PCB y planificación Rount Robin



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


if __name__ == "__main__":
    #  ejemplos de algunos casos como exribirían algunos usuarios
    casos = [("20", "7"), ("abc", "5"), ("", "5"), ("-5", "3"),
             ("10", "0"), ("3.5", "2"), ("200", "4"), ("35", "4")]

    # Se prueba cada caso: si esta bien ingresado se crea, si no, se muestra el motivo
    for tamano, rafaga in casos:
        try:
            p = crear_proceso(tamano, rafaga)
            print("Creado:", p)
        except ValueError as error:
            print("Rechazado:", error)

