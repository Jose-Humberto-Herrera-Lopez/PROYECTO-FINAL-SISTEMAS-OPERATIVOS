"""
Versión web de los Puntos C y D con PyScript.
Este archivo corre DENTRO del navegador y usa los mismos módulos de la CLI:
kernel/semaforo.py y kernel/deadlock.py (no se reescribe la lógica).
"""

from pyscript import document, when
from kernel.semaforo import SemaforoBinario, SemaforoError, demo_condicion_de_carrera
from kernel.deadlock import GestorRecursos, DeadlockError
semaforo = SemaforoBinario()
gestor = GestorRecursos()

def leer(id_campo):
    """Lee una caja de texto. Si es número lo convierte a entero; si no, lo deja como texto
    para que los módulos muestren su propio error."""
    texto = document.querySelector(id_campo).value.strip()
    try:
        return int(texto)
    except ValueError:
        return texto

def mostrar(mensaje, tipo="ok"):
    """Agrega una línea a la bitácora de la página (tipo: ok, bloqueo, error, deadlock)."""
    linea = document.createElement("div")
    linea.className = "linea " + tipo
    linea.textContent = mensaje
    bitacora = document.querySelector("#bitacora")
    bitacora.appendChild(linea)
    bitacora.scrollTop = bitacora.scrollHeight

def actualizar():
    """Redibuja el estado del semáforo y de los recursos."""
    document.querySelector("#estado-semaforo").textContent = semaforo.describir()
    document.querySelector("#estado-recursos").textContent = gestor.describir()

def seguro(funcion):
    """Ejecuta una acción y, si hay un error controlado, lo muestra en rojo en vez de romper la página."""
    def envoltura(evento):
        try:
            funcion()
        except (SemaforoError, DeadlockError) as error:
            mostrar(f"[ERROR] {error}", "error")
        actualizar()
    return envoltura

def alerta_si_hay_deadlock():
    ciclo = gestor.detectar_deadlock()
    if ciclo:
        mostrar("[DEADLOCK] ¡ALERTA! " + gestor.describir_ciclo(ciclo), "deadlock")

@when("click", "#btn-wait")
@seguro
def boton_wait():
    pid = leer("#pid-sem")
    if semaforo.wait(pid):
        mostrar(f"[OK] P{pid} entra a la sección crítica")
    else:
        mostrar(f"[BLOQUEO] Sección ocupada: P{pid} queda BLOQUEADO en la cola", "bloqueo")

@when("click", "#btn-signal")
@seguro
def boton_signal():
    pid = leer("#pid-sem")
    siguiente = semaforo.signal(pid)
    mostrar(f"[OK] P{pid} sale de la sección crítica")
    if siguiente is not None:
        mostrar(f"[OK] P{siguiente} sale de la cola y entra a la sección crítica")

@when("click", "#btn-escribir")
@seguro
def boton_escribir():
    pid = leer("#pid-sem")
    valor = leer("#valor")
    anterior = semaforo.escribir(pid, valor)
    mostrar(f"[OK] P{pid} cambió la variable compartida: {anterior} -> {valor}")

@when("click", "#btn-carrera")
@seguro
def boton_carrera():
    for usar_semaforo in (False, True):
        resultado, pasos = demo_condicion_de_carrera(usar_semaforo)
        for paso in pasos:
            mostrar(paso, "ok" if usar_semaforo else "bloqueo")

@when("click", "#btn-solicitar")
@seguro
def boton_solicitar():
    pid = leer("#pid-rec")
    recurso = document.querySelector("#recurso").value
    if gestor.solicitar(pid, recurso):
        mostrar(f"[OK] {recurso} asignado a P{pid}")
    else:
        mostrar(f"[BLOQUEO] {recurso} ocupado: P{pid} queda BLOQUEADO esperando", "bloqueo")
        alerta_si_hay_deadlock()

@when("click", "#btn-liberar")
@seguro
def boton_liberar():
    pid = leer("#pid-rec")
    recurso = document.querySelector("#recurso").value
    siguiente = gestor.liberar(pid, recurso)
    mostrar(f"[OK] P{pid} liberó {recurso}")
    if siguiente is not None:
        mostrar(f"[OK] {recurso} pasa a P{siguiente}, que se desbloquea")

@when("click", "#btn-simular")
@seguro
def boton_simular():
    for paso in gestor.simular_deadlock(1, 2):
        mostrar(paso, "bloqueo" if "BLOQUEADO" in paso else "ok")
    alerta_si_hay_deadlock()

@when("click", "#btn-detectar")
@seguro
def boton_detectar():
    ciclo = gestor.detectar_deadlock()
    if ciclo:
        mostrar("[DEADLOCK] Deadlock detectado: " + gestor.describir_ciclo(ciclo), "deadlock")
    else:
        mostrar("[OK] No hay deadlock")

@when("click", "#btn-abortar")
@seguro
def boton_abortar():
    pid = leer("#pid-rec")
    habia_deadlock = bool(gestor.detectar_deadlock())
    entregas = gestor.abortar_proceso(pid)
    semaforo.liberar_proceso(pid)
    mostrar(f"[ALERTA] P{pid} abortado", "bloqueo")
    for recurso, nuevo_dueno in entregas:
        mostrar(f"[OK] {recurso} pasa a P{nuevo_dueno}" if nuevo_dueno else f"[OK] {recurso} queda libre")
    if habia_deadlock and not gestor.detectar_deadlock():
        mostrar("[OK] Deadlock resuelto: se rompió la espera circular")

# Al cargar la página
actualizar()
document.querySelector("#cargando").remove()
mostrar("[SISTEMA] Simulador listo")