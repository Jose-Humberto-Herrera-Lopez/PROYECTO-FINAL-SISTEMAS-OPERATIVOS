# MENU PRINCIPAL DEL SIMULADOR (CLI), aquí se van a unir todos los modulos.
from memoria import GestorMemoria, MemoriaError
from proceso import PCB, LISTO
from semaforo import SemaforoBinario, SemaforoError

def main():
    print("--- INICIANDO SIMULADOR DE S.O. ---")
    
    # Inicializar componentes globales del SO
    ram = GestorMemoria(capacidad_total_mb=100)
    semaforo = SemaforoBinario()
    procesos_activos = []

    # Funcion simulada para crear procesos 
    def crear_proceso(pid, tamano, rafaga):
        try:
            print(f"\nIntentando crear Proceso P{pid} ({tamano} MB)...")
            # 1. Validar espacio en RAM (100 MB)
            ram.asignar_memoria(pid, tamano)
            
            # 2. Se crea el PCB
            p = PCB(pid, tamano, rafaga)
            p.estado = LISTO
            procesos_activos.append(p)
            
            print(f"-> [ÉXITO] Creado: {p}")
            print(f"-> RAM disponible: {ram.memoria_disponible} MB / 100 MB")
            
        except MemoriaError as e:
            # Captura de Out of Memory
            print(f"-> [ERROR OOM RECHAZADO]: {e}")

    # Pruebas de procesos
    crear_proceso(pid=1, tamano=30, rafaga=5)
    crear_proceso(pid=2, tamano=50, rafaga=8)
    
    # Proceso debee fallar porque excede los MB
    crear_proceso(pid=3, tamano=30, rafaga=4) 

    # Liberar memoria de un proceso al terminar
    print("\nTermina el Proceso P1, liberando sus 30 MB...")
    ram.liberars_memoria = ram.liberar_memoria(1)
    print(f"RAM disponible ahora: {ram.memoria_disponible} MB")

    crear_proceso(pid=3, tamano=30, rafaga=4)

if __name__ == "__main__":
    main()
