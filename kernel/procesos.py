# Gestión de procesos del PCB y planificación Rount Robin
# Estados de un proceso
NUEVO = "Nuevo"
LISTO = "Listo"
EJECUTANDO = "Ejecutando"
BLOQUEADO = "Bloqueado"
TERMINADO = "Terminado"

class PCB:
    def __init__(self, pid, tamano_memoria, rafaga_total):
        self.pid = pid
        self.estado = NUEVO
        self.tamano_memoria = tamano_memoria
        self.rafaga_total = rafaga_total
        self.rafaga_restante = rafaga_total
        self.tiempo_espera = 0
        self.tiempo_finalizacion = 0

    def __str__(self):
        return (f"PID: {self.pid} | Estado: {self.estado} | "
                f"Memoria: {self.tamano_memoria} MB | "
                f"Ráfaga total: {self.rafaga_total} | "
                f"Ráfaga restante: {self.rafaga_restante}")
