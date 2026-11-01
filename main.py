# MENU PRINCIPAL DEL SIMULADOR (CLI), aquí se van a unir todos los modulos.

from núcleo.memoria import GestorMemoria, MemoriaError
from núcleo.procesos import PCB, LISTO
from núcleo.semaforo import SemaforoBinario, SemaforoError

def menu_memoria():
    print("\n--- PRUEBAS DE GESTIóN DE MEMORIA ---")
    try:
        ram = GestorMemoria(100)
        print(f"RAM inicializada con capacidad de: {ram.capacidad_total_mb} MB")
        
        print("\nIntentando asignar 30 MB...")
        ram.asignar_memoria("PID-1", 30)
        print(f"-> Éxito. RAM disponible: {ram.memoria_disponible} MB")
        
        print("\nIntentando asignar 50 MB...")
        ram.asignar_memoria("PID-2", 50)
        print(f"-> Éxito. RAM disponible: {ram.memoria_disponible} MB")
        
        print("\nLiberando 30 MB del proceso PID-1...")
        ram.liberar_memoria("PID-1")
        print(f"-> RAM disponible ahora: {ram.memoria_disponible} MB")
        
    except MemoriaError as e:
        print(f"-> [ERROR DE MEMORIA]: {e}")

def menu_procesos():
    print("\n--- PRUEBAS DE PROCESOS (PCB) ---")
    procesos_activos = []
    
    p1 = PCB("PID-1", 30, 5)
    p1.estado = LISTO
    procesos_activos.append(p1)
    
    print(f"Proceso creado exitosamente: {p1}")
    print(f"Total de procesos en lista LISTO: {len(procesos_activos)}")

def menu_semaforo():
    print("\n--- PRUEBAS DE SEMÁFOROS ---")
    try:
        semaforo = SemaforoBinario()
        print("Semaforo binario inicializado.")
        semaforo.wait()
        print("-> Señal de WAIT ejecutada.")
        semaforo.signal()
        print("-> Señal de SIGNAL ejecutada.")
    except SemaforoError as e:
        print(f"-> [ERROR EN SEMÁFORO]: {e}")

def Principal():
    while True:
        print("   SIMULADOR DE SISTEMAS OPERATIVOS     ")
        print("1. Ejecutar pruebas de Memoria")
        print("2. Ejecutar pruebas de Procesos (PCB)")
        print("3. Ejecutar pruebas de Semáforos")
        print("4. Salir")
        
        opcion = input("\nSelecciona una opción (1-4): ").strip()
        if opcion == "1":
            menu_memoria()
        elif opcion == "2":
            menu_procesos()
        elif opcion == "3":
            menu_semaforo()
        elif opcion == "4":
            print("\nSaliendo del simulador. ¡Hasta luego!")
            break
        else:
            print("\n[!] Opcion invalida. Por favor, ingresa un numero del 1 al 4.")

if __name__ == "__main__":
    Principal()
