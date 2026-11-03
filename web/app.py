"""Conecta los botones de la web con las mismas clases que usa la terminal.
PyScript ejecuta este archivo en el navegador; las reglas siguen en kernel/."""

from contextlib import redirect_stdout
from io import StringIO

from pyscript import document, when
from kernel.procesos import Planificador, crear_proceso, LISTO, BLOQUEADO
from kernel.memoria import GestorMemoria, MemoriaError
from kernel.semaforo import SemaforoBinario, SemaforoError, demo_condicion_de_carrera
from kernel.deadlock import GestorRecursos, DeadlockError

# Se crea un gestor de cada tipo una sola vez. Así el estado no se pierde
# después de cada clic y los cuatro puntos trabajan con los mismos procesos.
planificador = Planificador()
memoria = GestorMemoria()
semaforo = SemaforoBinario()
gestor = GestorRecursos()

# El color depende del PID para que P2 conserve su tono aunque se borre P1.
COLORES_RAM = ("#6d4ca3", "#2563a6", "#087e70", "#a04765", "#aa641c", "#4a63a9")


def leer(campo):
    """Convierte a entero cuando se puede; deja el texto para que se valide."""
    texto = document.querySelector(campo).value.strip()
    try:
        return int(texto)
    except ValueError:
        return texto


def mostrar(mensaje, tipo="ok"):
    """Añade una línea a la bitácora."""
    linea = document.createElement("div")
    linea.className = "linea " + tipo
    linea.textContent = mensaje
    bitacora = document.querySelector("#bitacora")
    bitacora.appendChild(linea)
    bitacora.scrollTop = bitacora.scrollHeight


def mostrar_salida(funcion):
    """Lleva a la página los print() de los módulos hechos para la terminal."""
    salida = StringIO()
    with redirect_stdout(salida):
        funcion()
    texto = salida.getvalue().strip()
    for linea in texto.splitlines():
        mostrar(linea)
    return texto


def actualizar_barra_memoria(datos):
    """Dibuja un tramo por proceso y deja en gris la parte libre de la RAM."""
    total = datos["capacidad_total"]
    ocupada = datos["memoria_ocupada"]
    libre = datos["memoria_disponible"]
    porcentaje = ocupada * 100 / total

    indicador = document.querySelector("#ram-porcentaje")
    indicador.textContent = f"{porcentaje:.0f}% ocupada"
    indicador.className = "ram-porcentaje"
    if porcentaje == 100:
        indicador.className += " llena"
    elif porcentaje >= 80:
        indicador.className += " alta"
    document.querySelector("#ram-libre").textContent = f"{libre} MB libres"

    barra = document.querySelector("#barra-memoria")
    barra.setAttribute("aria-valuenow", str(round(porcentaje)))
    barra.innerHTML = ""
    leyenda = document.querySelector("#leyenda-memoria")
    leyenda.innerHTML = ""

    for pid, tamano in datos["bloques_asignados"].items():
        color = COLORES_RAM[(pid - 1) % len(COLORES_RAM)]
        parte = tamano * 100 / total
        tramo = document.createElement("div")
        tramo.className = "ram-tramo"
        tramo.style.width = f"{parte:.2f}%"
        tramo.style.backgroundColor = color
        tramo.textContent = f"P{pid}" if parte >= 12 else ""
        tramo.title = f"P{pid}: {tamano} MB"
        barra.appendChild(tramo)

        # La muestra y el texto llevan el mismo color que el tramo de arriba.
        etiqueta = document.createElement("span")
        etiqueta.className = "ram-etiqueta"
        etiqueta.style.color = color
        muestra = document.createElement("span")
        muestra.className = "ram-muestra"
        muestra.style.backgroundColor = color
        etiqueta.appendChild(muestra)
        texto = document.createElement("span")
        texto.textContent = f"P{pid}: {tamano} MB"
        etiqueta.appendChild(texto)
        leyenda.appendChild(etiqueta)

    if libre:
        tramo_libre = document.createElement("div")
        tramo_libre.className = "ram-tramo libre"
        tramo_libre.style.width = f"{libre * 100 / total:.2f}%"
        tramo_libre.textContent = "Libre" if libre * 100 / total >= 12 else ""
        tramo_libre.title = f"Libre: {libre} MB"
        barra.appendChild(tramo_libre)

        etiqueta_libre = document.createElement("span")
        etiqueta_libre.className = "ram-etiqueta ram-libre"
        muestra_libre = document.createElement("span")
        muestra_libre.className = "ram-muestra"
        muestra_libre.style.backgroundColor = "#e5e2dc"
        etiqueta_libre.appendChild(muestra_libre)
        texto_libre = document.createElement("span")
        texto_libre.textContent = f"Libre: {libre} MB"
        etiqueta_libre.appendChild(texto_libre)
        leyenda.appendChild(etiqueta_libre)


def actualizar():
    """Redibuja la cola, la RAM, el semáforo y los recursos."""
    cola = "\n".join(f"{n}. {p}" for n, p in
                     enumerate(planificador.cola_listos, start=1))
    document.querySelector("#estado-procesos").textContent = (
        cola or "La cola de listos está vacía."
    )
    datos = memoria.estado_memoria()
    bloques = "\n".join(f"P{pid}: {mb} MB"
                        for pid, mb in datos["bloques_asignados"].items())
    document.querySelector("#estado-memoria").textContent = (
        f"RAM total: {datos['capacidad_total']} MB | "
        f"Ocupada: {datos['memoria_ocupada']} MB | "
        f"Libre: {datos['memoria_disponible']} MB\n"
        + (bloques or "No hay procesos ocupando memoria.")
    )
    actualizar_barra_memoria(datos)
    document.querySelector("#estado-semaforo").textContent = semaforo.describir()
    document.querySelector("#estado-recursos").textContent = gestor.describir()


def seguro(funcion):
    """Si un dato es incorrecto, muestra el error y mantiene la página abierta."""
    def envoltura(evento):
        try:
            funcion()
        except (ValueError, MemoriaError, SemaforoError, DeadlockError) as error:
            mostrar(f"[ERROR] {error}", "error")
        finally:
            actualizar()
    return envoltura


def proceso_activo(campo):
    """Comprueba que el PID ya exista en la cola del planificador."""
    pid = leer(campo)
    proceso = planificador.buscar_proceso(pid)
    if proceso is None:
        raise ValueError(f"No existe un proceso activo con PID {pid}. Créalo primero en el punto A.")
    return proceso


def sincronizar_estado(pid):
    """Devuelve un proceso a Listo solo si ya no está en ninguna cola de espera."""
    proceso = planificador.buscar_proceso(pid)
    if proceso is None:
        return
    espera_semaforo = pid in semaforo.cola_espera
    espera_recurso = any(pid in r.cola_espera for r in gestor.recursos.values())
    proceso.estado = BLOQUEADO if espera_semaforo or espera_recurso else LISTO


def alerta_si_hay_deadlock():
    ciclo = gestor.detectar_deadlock()
    if ciclo:
        mostrar("[DEADLOCK] ¡ALERTA! " + gestor.describir_ciclo(ciclo), "deadlock")


# A: el PCB se crea con la clase existente y solo entra a la cola si hay RAM.
@when("click", "#btn-crear")
@seguro
def boton_crear():
    tamano = document.querySelector("#tamano").value.strip()
    rafaga = document.querySelector("#rafaga").value.strip()
    proceso = crear_proceso(tamano, rafaga)
    try:
        memoria.asignar_memoria(proceso.pid, proceso.tamano_memoria)
    except MemoriaError:
        mostrar("[OUT OF MEMORY] El proceso no entró a la cola.", "error")
        raise
    planificador.agregar_proceso(proceso)
    mostrar(f"[OK] Proceso creado: {proceso}")


@when("click", "#btn-cola")
@seguro
def boton_cola():
    mostrar_salida(planificador.mostrar_cola_listos)


@when("click", "#btn-round-robin")
@seguro
def boton_round_robin():
    # El método de kernel/ ejecuta toda la cola. Antes se evita que un
    # bloqueado reciba CPU mientras espera un semáforo o recurso.
    bloqueados = [f"P{p.pid}" for p in planificador.cola_listos
                  if p.estado == BLOQUEADO]
    if bloqueados:
        mostrar(f"[ERROR] No se puede ejecutar Round Robin: {', '.join(bloqueados)} "
                "está(n) bloqueado(s). Libera lo que esperan primero.", "error")
        return
    mostrar_salida(planificador.ejecutar_round_robin)
    for proceso in planificador.terminados:
        # Un proceso terminado tampoco puede seguir siendo dueño de un
        # semáforo o recurso; se limpia su registro antes de mostrar la RAM.
        gestor.abortar_proceso(proceso.pid)
        semaforo.liberar_proceso(proceso.pid)
        if memoria.liberar_memoria(proceso.pid):
            mostrar(f"[MEMORIA] Se liberaron {proceso.tamano_memoria} MB de P{proceso.pid}")
    document.querySelector("#estado-metricas").textContent = (
        mostrar_salida(planificador.mostrar_metricas)
    )


@when("click", "#btn-metricas")
@seguro
def boton_metricas():
    document.querySelector("#estado-metricas").textContent = (
        mostrar_salida(planificador.mostrar_metricas)
    )


# B: la memoria se reserva al crear y se libera al terminar o abortar.
@when("click", "#btn-memoria")
@seguro
def boton_memoria():
    datos = memoria.estado_memoria()
    mostrar(f"[MEMORIA] {datos['memoria_ocupada']} MB ocupados; "
            f"{datos['memoria_disponible']} MB libres de {datos['capacidad_total']} MB")


# C: wait() y signal() usan la cola de kernel/semaforo.py.
@when("click", "#btn-wait")
@seguro
def boton_wait():
    proceso = proceso_activo("#pid-sem")
    if semaforo.wait(proceso.pid):
        mostrar(f"[OK] P{proceso.pid} entra a la sección crítica")
    else:
        proceso.estado = BLOQUEADO
        mostrar(f"[BLOQUEO] P{proceso.pid} queda en la cola del semáforo", "bloqueo")


@when("click", "#btn-signal")
@seguro
def boton_signal():
    proceso = proceso_activo("#pid-sem")
    siguiente = semaforo.signal(proceso.pid)
    mostrar(f"[OK] P{proceso.pid} sale de la sección crítica")
    if siguiente is not None:
        sincronizar_estado(siguiente)
        mostrar(f"[OK] P{siguiente} sale de la cola y entra a la sección crítica")


@when("click", "#btn-escribir")
@seguro
def boton_escribir():
    proceso = proceso_activo("#pid-sem")
    valor = leer("#valor")
    anterior = semaforo.escribir(proceso.pid, valor)
    mostrar(f"[OK] P{proceso.pid} cambió la variable compartida: {anterior} -> {valor}")


@when("click", "#btn-estado-sem")
@seguro
def boton_estado_sem():
    mostrar(semaforo.describir())


@when("click", "#btn-carrera")
@seguro
def boton_carrera():
    for usar_semaforo in (False, True):
        resultado, pasos = demo_condicion_de_carrera(usar_semaforo)
        for paso in pasos:
            mostrar(paso, "ok" if usar_semaforo else "bloqueo")


# D: también se exigen PID existentes para pedir recursos o simular deadlock.
@when("click", "#btn-solicitar")
@seguro
def boton_solicitar():
    proceso = proceso_activo("#pid-rec")
    recurso = document.querySelector("#recurso").value
    if gestor.solicitar(proceso.pid, recurso):
        mostrar(f"[OK] {recurso} asignado a P{proceso.pid}")
    else:
        proceso.estado = BLOQUEADO
        mostrar(f"[BLOQUEO] P{proceso.pid} espera {recurso}", "bloqueo")
        alerta_si_hay_deadlock()


@when("click", "#btn-liberar")
@seguro
def boton_liberar():
    proceso = proceso_activo("#pid-rec")
    recurso = document.querySelector("#recurso").value
    siguiente = gestor.liberar(proceso.pid, recurso)
    mostrar(f"[OK] P{proceso.pid} liberó {recurso}")
    if siguiente is not None:
        sincronizar_estado(siguiente)
        mostrar(f"[OK] {recurso} pasa a P{siguiente}, que se desbloquea")


@when("click", "#btn-simular")
@seguro
def boton_simular():
    proceso_a = proceso_activo("#pid-rec")
    proceso_b = proceso_activo("#pid-rec-b")
    for paso in gestor.simular_deadlock(proceso_a.pid, proceso_b.pid):
        mostrar(paso, "bloqueo" if "BLOQUEADO" in paso else "ok")
    proceso_a.estado = BLOQUEADO
    proceso_b.estado = BLOQUEADO
    alerta_si_hay_deadlock()


@when("click", "#btn-detectar")
@seguro
def boton_detectar():
    ciclo = gestor.detectar_deadlock()
    if ciclo:
        mostrar("[DEADLOCK] " + gestor.describir_ciclo(ciclo), "deadlock")
    else:
        mostrar("[OK] No hay deadlock")


@when("click", "#btn-estado-rec")
@seguro
def boton_estado_rec():
    mostrar(gestor.describir())


@when("click", "#btn-abortar")
@seguro
def boton_abortar():
    proceso = proceso_activo("#pid-rec")
    pid = proceso.pid
    habia_deadlock = bool(gestor.detectar_deadlock())
    entregas = gestor.abortar_proceso(pid)
    siguiente_semaforo = semaforo.liberar_proceso(pid)
    libero_memoria = memoria.liberar_memoria(pid)
    planificador.quitar_proceso(pid)
    mostrar(f"[ALERTA] P{pid} abortado", "bloqueo")
    if libero_memoria:
        mostrar(f"[MEMORIA] Se liberaron {proceso.tamano_memoria} MB de P{pid}")
    if siguiente_semaforo is not None:
        sincronizar_estado(siguiente_semaforo)
        mostrar(f"[OK] El semáforo pasa a P{siguiente_semaforo}")
    for recurso, nuevo_dueno in entregas:
        if nuevo_dueno is None:
            mostrar(f"[OK] {recurso} queda libre")
        else:
            sincronizar_estado(nuevo_dueno)
            mostrar(f"[OK] {recurso} pasa a P{nuevo_dueno}")
    if habia_deadlock and not gestor.detectar_deadlock():
        mostrar("[OK] Deadlock resuelto: se rompió la espera circular")


# Muestra el estado inicial cuando PyScript termina de cargar.
actualizar()
document.querySelector("#cargando").remove()
mostrar("[SISTEMA] Simulador listo")
