# MENU PRINCIPAL DEL SIMULADOR (CLI), aquí se van a unir todos los modulos.
"""
Menú principal del simulador.
"""

from kernel.semaforo import SemaforoBinario, SemaforoError, demo_condicion_de_carrera
from kernel.deadlock import GestorRecursos, DeadlockError

# Un solo semáforo y un solo gestor de recursos para todo el programa
semaforo = SemaforoBinario()
gestor = GestorRecursos()

def leer_numero(mensaje):
    texto = input(mensaje).strip()
    try:
        return int(texto)
    except ValueError:
        return texto
def mostrar_menu():
    print("\n================ SIMULADOR DE KERNEL ================")
    print("  --- Punto C: Semáforo ---")
    print("   1. wait()  - un proceso pide entrar a la sección crítica")
    print("   2. signal() - el dueño sale de la sección crítica")
    print("   3. Escribir en la variable compartida")
    print("   4. Ver estado del semáforo")
    print("   5. Demo de condición de carrera (sin y con semáforo)")
    print("  --- Punto D: Deadlock ---")
    print("   6. Solicitar un recurso (R1 o R2)")
    print("   7. Liberar un recurso")
    print("   8. Simular deadlock")
    print("   9. Detectar deadlock")
    print("  10. Abortar un proceso (kill)")
    print("  11. Ver estado de los recursos")
    print("   0. Salir")

def opcion_wait():
    pid = leer_numero("PID del proceso: ")
    if semaforo.wait(pid):
        print(f"[OK] P{pid} entra a la sección crítica")
    else:
        print(f"[BLOQUEO] La sección está ocupada: P{pid} queda BLOQUEADO en la cola de espera")
def opcion_signal():
    pid = leer_numero("PID del proceso: ")
    siguiente = semaforo.signal(pid)
    print(f"[OK] P{pid} sale de la sección crítica")
    if siguiente is None:
        print("     El semáforo queda libre (valor = 1)")
    else:
        print(f"     P{siguiente} sale de la cola y entra a la sección crítica")
def opcion_escribir():
    pid = leer_numero("PID del proceso: ")
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
    pid = leer_numero("PID del proceso: ")
    recurso = input("Recurso (R1 o R2): ")
    if gestor.solicitar(pid, recurso):
        print(f"[OK] {recurso.strip().upper()} asignado a P{pid}")
    else:
        print(f"[BLOQUEO] {recurso.strip().upper()} está ocupado: P{pid} queda BLOQUEADO esperando")
        alerta_si_hay_deadlock()
def opcion_liberar():
    pid = leer_numero("PID del proceso: ")
    recurso = input("Recurso (R1 o R2): ")
    siguiente = gestor.liberar(pid, recurso)
    print(f"[OK] P{pid} liberó {recurso.strip().upper()}")
    if siguiente is not None:
        print(f"     {recurso.strip().upper()} pasa a P{siguiente}, que se desbloquea")
def opcion_simular():
    pid_a = leer_numero("PID del proceso A: ")
    pid_b = leer_numero("PID del proceso B: ")
    for paso in gestor.simular_deadlock(pid_a, pid_b):
        print("  " + paso)
    alerta_si_hay_deadlock()
def opcion_detectar():
    ciclo = gestor.detectar_deadlock()
    if ciclo:
        print("[DEADLOCK] ¡Deadlock detectado!", gestor.describir_ciclo(ciclo))
        print(f"           Para romperlo usa la opción 10 y aborta P{ciclo[0]} o P{ciclo[1]}")
    else:
        print("[OK] No hay deadlock: el grafo de espera no tiene ciclos")
def opcion_abortar():
    pid = leer_numero("PID del proceso a abortar: ")
    habia_deadlock = bool(gestor.detectar_deadlock())
    entregas = gestor.abortar_proceso(pid)
    semaforo.liberar_proceso(pid)  # si tenía la sección crítica, también la suelta
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

OPCIONES = {
    # --- Punto A (Humberto) y Punto B (Angie): aquí agregan sus números ---
    "1": opcion_wait,
    "2": opcion_signal,
    "3": opcion_escribir,
    "4": lambda: print(semaforo.describir()),
    "5": opcion_carrera,
    "6": opcion_solicitar,
    "7": opcion_liberar,
    "8": opcion_simular,
    "9": opcion_detectar,
    "10": opcion_abortar,
    "11": lambda: print(gestor.describir()),
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