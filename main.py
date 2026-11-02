# MENU PRINCIPAL DEL SIMULADOR (CLI), aquí se van a unir todos los modulos.
"""
Menú principal del simulador.
"""

from kernel.semaforo import SemaforoBinario, SemaforoError, demo_condicion_de_carrera
from kernel.deadlock import GestorRecursos, DeadlockError
from kernel.procesos import Planificador, crear_proceso, LISTO, BLOQUEADO
from kernel.memoria import GestorMemoria, MemoriaError

# Un solo semáforo y un solo gestor de recursos para todo el programa
semaforo = SemaforoBinario()
gestor = GestorRecursos()
planificador = Planificador()
memoria = GestorMemoria()

def leer_numero(mensaje):
    texto = input(mensaje).strip()
    try:
        return int(texto)
    except ValueError:
        return texto
def mostrar_menu():
    print("\n================ SIMULADOR DE KERNEL ================")
    print("  --- Punto A: Procesos y Round Robin ---")
    print("   1. Crear un proceso")
    print("   2. Ver cola de listos")
    print("   3. Ejecutar Round Robin (quantum = 3)")
    print("   4. Ver métricas de tiempos")
    print("  --- Punto B: Memoria ---")
    print("   5. Ver estado de la memoria RAM")
    print("  --- Punto C: Semáforo ---")
    print("   6. wait()  - un proceso pide entrar a la sección crítica")
    print("   7. signal() - el dueño sale de la sección crítica")
    print("   8. Escribir en la variable compartida")
    print("   9. Ver estado del semáforo")
    print("  10. Demo de condición de carrera (sin y con semáforo)")
    print("  --- Punto D: Deadlock ---")
    print("  11. Solicitar un recurso (R1 o R2)")
    print("  12. Liberar un recurso")
    print("  13. Simular deadlock")
    print("  14. Detectar deadlock")
    print("  15. Abortar un proceso (kill)")
    print("  16. Ver estado de los recursos")
    print("   0. Salir")

def obtener_proceso_activo(mensaje):
    
    #Pide un PID y lo busca en el planificador
    #Devuelve el PCB si el proceso existe y está activo; si no, muestra
    #un error y devuelve None
    
    pid = leer_numero(mensaje)
    proceso = planificador.buscar_proceso(pid)
    if proceso is None:
        print(f"[ERROR] No existe un proceso activo con PID {pid}. "
              f"Créalo primero con la opción 1.")
    return proceso

def desbloquear(pid):
    #Si el proceso con ese PID está activo, lo regresa a estado Listo
    proceso = planificador.buscar_proceso(pid)
    if proceso is not None:
        proceso.estado = LISTO

def opcion_wait():
    proceso = obtener_proceso_activo("PID del proceso: ")
    if proceso is None:
        return
    pid = proceso.pid
    if semaforo.wait(pid):
        print(f"[OK] P{pid} entra a la sección crítica")
    else:
        proceso.estado = BLOQUEADO
        print(f"[BLOQUEO] La sección está ocupada: P{pid} queda BLOQUEADO en la cola de espera")

def opcion_signal():
    proceso = obtener_proceso_activo("PID del proceso: ")
    if proceso is None:
        return
    pid = proceso.pid
    siguiente = semaforo.signal(pid)
    print(f"[OK] P{pid} sale de la sección crítica")
    if siguiente is None:
        print("     El semáforo queda libre (valor = 1)")
    else:
        desbloquear(siguiente)
        print(f"     P{siguiente} sale de la cola y entra a la sección crítica")

def opcion_escribir():
    proceso = obtener_proceso_activo("PID del proceso: ")
    if proceso is None:
        return
    pid = proceso.pid
    valor = leer_numero("Nuevo valor de la variable: ")
    anterior = semaforo.escribir(pid, valor)
    print(f"[OK] P{pid} cambió la variable compartida: {anterior} -> {valor}")

def opcion_carrera():
    for usar_semaforo in (False, True):
        resultado, pasos = demo_condicion_de_carrera(usar_semaforo)
        print()
        for paso in pasos:
            print("  " + paso)

def opcion_solicitar():
    proceso = obtener_proceso_activo("PID del proceso: ")
    if proceso is None:
        return
    pid = proceso.pid
    recurso = input("Recurso (R1 o R2): ")
    if gestor.solicitar(pid, recurso):
        print(f"[OK] {recurso.strip().upper()} asignado a P{pid}")
    else:
        proceso.estado = BLOQUEADO
        print(f"[BLOQUEO] {recurso.strip().upper()} está ocupado: P{pid} queda BLOQUEADO esperando")
        alerta_si_hay_deadlock()

def opcion_liberar():
    proceso = obtener_proceso_activo("PID del proceso: ")
    if proceso is None:
        return
    pid = proceso.pid
    recurso = input("Recurso (R1 o R2): ")
    siguiente = gestor.liberar(pid, recurso)
    print(f"[OK] P{pid} liberó {recurso.strip().upper()}")
    if siguiente is not None:
        desbloquear(siguiente)
        print(f"     {recurso.strip().upper()} pasa a P{siguiente}, que se desbloquea")

def opcion_simular():
    proceso_a = obtener_proceso_activo("PID del proceso A: ")
    proceso_b = obtener_proceso_activo("PID del proceso B: ")
    if proceso_a is None or proceso_b is None:
        return
    pid_a = proceso_a.pid
    pid_b = proceso_b.pid
    for paso in gestor.simular_deadlock(pid_a, pid_b):
        print("  " + paso)
    proceso_a.estado = BLOQUEADO
    proceso_b.estado = BLOQUEADO
    alerta_si_hay_deadlock()

def opcion_detectar():
    ciclo = gestor.detectar_deadlock()
    if ciclo:
        print("[DEADLOCK] ¡Deadlock detectado!", gestor.describir_ciclo(ciclo))
        print(f"           Para romperlo usa la opción 15 y aborta P{ciclo[0]} o P{ciclo[1]}")
    else:
        print("[OK] No hay deadlock: el grafo de espera no tiene ciclos")

def retirar_proceso(pid):

    #Al abortar un proceso: si tenía la sección crítica se la entrega al
    #siguiente de la cola, y lo saca de la cola de listos del planificador.
    
    siguiente = semaforo.liberar_proceso(pid)
    if siguiente is not None:
        desbloquear(siguiente)
    planificador.quitar_proceso(pid)

def opcion_abortar():
    proceso = obtener_proceso_activo("PID del proceso a abortar: ")
    if proceso is None:
        return
    pid = proceso.pid
    habia_deadlock = bool(gestor.detectar_deadlock())
    entregas = gestor.abortar_proceso(pid)
    
    # Si el proceso abortado tenía memoria asignada, se libera.
    if memoria.liberar_memoria(pid):
        print(f"[MEMORIA] Se liberó la memoria de P{pid}")

    retirar_proceso(pid)  # suelta la sección crítica y lo saca de la cola de listos
    print(f"[ALERTA] P{pid} abortado")
    for recurso, nuevo_dueno in entregas:
        if nuevo_dueno is None:
            print(f"         {recurso} queda libre")
        else:
            print(f"         {recurso} pasa a P{nuevo_dueno}, que se desbloquea")
    if habia_deadlock and not gestor.detectar_deadlock():
        print("[OK] Deadlock resuelto: se rompió la espera circular")

def alerta_si_hay_deadlock():
    ciclo = gestor.detectar_deadlock()
    if ciclo:
        print("[DEADLOCK] ¡ALERTA! Deadlock detectado:", gestor.describir_ciclo(ciclo))

def opcion_crear_proceso():
    tamano = input("Tamaño en memoria (MB): ")
    rafaga = input("Rafaga del CPU: ")

    # Validación de formato en el modulo del proceso
    try:
        proceso = crear_proceso(tamano, rafaga)
    except ValueError as error:
        print(f"ERROR CAPA 8 {error}")
        return

    #Validacion de espacio en la RAM
    try:
        memoria.asignar_memoria(proceso.pid, proceso.tamano_memoria)
    except MemoriaError as error:
        print(f"[OUT OF MEMORY] {error}")
        print("     El proceso fue rechazado y no entra a la cola de listos.")
        return

    planificador.agregar_proceso(proceso)
    print("TODO EN ORDEN, proceso creado y agregado a la cola de listos")
    print(f" {proceso}")

def opcion_ejecutar_round_robin():
    """Ejecuta Round Robin y libera la memoria de los procesos que terminaron."""
    planificador.ejecutar_round_robin()

    # Un proceso terminado ya no necesita su memoria, así que se libera.
    # liberar_memoria devuelve False si ya se había liberado antes,
    # por eso solo se muestra el mensaje la primera vez.
    bloqueados = []
    for proceso in planificador.cola_listos:
        if proceso.estado == BLOQUEADO:
            bloqueados.append(f"P{proceso.pid}")

    if bloqueados:
        print(f"[ERROR] No se puede ejecutar Round Robin: {', '.join(bloqueados)} "
              f"está(n) bloqueado(s).")
        print("        Usa signal(), libera recursos o aborta un proceso primero.")
        return

    planificador.ejecutar_round_robin()

    # Un proceso terminado ya no necesita su memoria, así que se libera.
    # liberar_memoria devuelve False si ya se había liberado antes,
    # por eso solo se muestra el mensaje la primera vez.
    for proceso in planificador.terminados:
        if memoria.liberar_memoria(proceso.pid):
            print(f"[MEMORIA] Se liberaron {proceso.tamano_memoria} MB de P{proceso.pid}")

def opcion_ver_memoria():
    """Muestra cuánta RAM está ocupada y libre, y qué procesos la usan."""
    # estado_memoria devuelve un diccionario con los datos de la RAM.
    estado = memoria.estado_memoria()
    print(f"RAM total: {estado['capacidad_total']} MB")
    print(f"Ocupada:   {estado['memoria_ocupada']} MB")
    print(f"Libre:     {estado['memoria_disponible']} MB")

    if not estado["bloques_asignados"]:
        print("No hay procesos ocupando memoria.")
        return

    print("Procesos en memoria:")
    # .items() recorre el diccionario en parejas (pid, tamaño).
    for pid, tamano in estado["bloques_asignados"].items():
        print(f"  P{pid}: {tamano} MB")

OPCIONES = {
    # --- Punto A: Procesos y Round Robin (Humberto) ---
    "1": opcion_crear_proceso,
    "2": planificador.mostrar_cola_listos,
    "3": opcion_ejecutar_round_robin,
    "4": planificador.mostrar_metricas,
    # --- Punto B: Memoria (Angie) ---
    "5": opcion_ver_memoria,
    # --- Punto C: Semáforo (Kevin) ---
    "6": opcion_wait,
    "7": opcion_signal,
    "8": opcion_escribir,
    "9": lambda: print(semaforo.describir()),
    "10": opcion_carrera,
    # --- Punto D: Deadlock (Kevin) ---
    "11": opcion_solicitar,
    "12": opcion_liberar,
    "13": opcion_simular,
    "14": opcion_detectar,
    "15": opcion_abortar,
    "16": lambda: print(gestor.describir()),
}

def main():
    while True:
        mostrar_menu()
        try:
            opcion = input("Elige una opción: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSimulador cerrado.")
            break
        if opcion == "0":
            print("Simulador cerrado.")
            break
        accion = OPCIONES.get(opcion)
        if accion is None:
            print(f"[ERROR] La opción '{opcion}' no existe. Elige un número del menú")
            continue
        try:
            accion()
        except (SemaforoError, DeadlockError) as error:
            print(f"[ERROR] {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nSimulador cerrado.")
            break
        except Exception as error:  # red de seguridad: el programa nunca se cae
            print(f"[ERROR] Error inesperado: {error}")

if __name__ == "__main__":
    main()