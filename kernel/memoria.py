class MemoriaError(Exception):
    """Out of Memory"""
    pass

class GestorMemoria:
    def __init__(self, capacidad_total_mb=100):
        self.capacidad_total = capacidad_total_mb
        self.memoria_disponible = capacidad_total_mb
        self.bloques_asignados = {}  # {pid: tamano}

    def asignar_memoria(self, pid, tamano):
        if not isinstance(tamano, int) or tamano <= 0:
            raise MemoriaError(f"El tamaño de memoria debe ser un entero positivo (recibido: {tamano})")
        
        if tamano > self.memoria_disponible:
            raise MemoriaError(
                f"Error: Out of Memory Proceso P{pid} requiere {tamano} MB, "
                f"pero solo hay {self.memoria_disponible} MB disponibles de {self.capacidad_total} MB."
            )
        
        self.memoria_disponible -= tamano
        self.bloques_asignados[pid] = tamano
        return True

    def liberar_memoria(self, pid):
        if pid in self.bloques_asignados:
            tamano = self.bloques_asignados.pop(pid)
            self.memoria_disponible += tamano
            return True
        return False

    def estado_memoria(self):
        return {
            "capacidad_total": self.capacidad_total,
            "memoria_disponible": self.memoria_disponible,
            "memoria_ocupada": self.capacidad_total - self.memoria_disponible,
            "bloques_asignados": self.bloques_asignados
        }
# Gestión de memoria RAM de 100MB y el error de Out Of Memory
