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

    def __str__(self):
        """Devuelve el PCB como texto legible para mostrarlo en consola."""
        return (f"PID: {self.pid} | Estado: {self.estado} | "
                f"Memoria: {self.tamano_memoria} MB | "
                f"Ráfaga total: {self.rafaga_total} | "
                f"Ráfaga restante: {self.rafaga_restante}")

