# Proyecto de Sistemas Operativos
Liderado por Angie, Kevin y Humberto

# Proyecto de Sistemas Operativos
Liderado por Angie, Kevin y Humberto

Simulador de funciones de un kernel
Proyecto de Sistemas Operativos I desarrollado por Angie, Kevin y Humberto. El programa simula funciones básicas de un kernel mediante un menú en la terminal: gestión de procesos, planificación Round Robin, memoria RAM, semáforo binario y detección de deadlock.

Es un simulador educativo. Los procesos, la CPU y la memoria que muestra el programa son representaciones dentro de Python; no modifica los procesos ni la RAM reales del equipo.
Integrantes y aportes
- Humberto: procesos, PCB y planificación Round Robin.
- Angie: gestión de memoria RAM.
- Kevin: semáforo binario y deadlock.
- Integración: menú principal que conecta los módulos.
Funciones del simulador
Procesos y Round Robin
Cada proceso tiene un PID y un bloque de control de proceso (PCB). El PCB guarda su estado, memoria asignada, ráfaga total y ráfaga restante de CPU.

Los procesos entran a una cola. Round Robin les da turnos de hasta 3 unidades de tiempo. Si un proceso aún tiene ráfaga pendiente, vuelve al final de la cola. Al finalizar, el programa permite consultar sus tiempos de finalización, retorno y espera.
Memoria RAM
El simulador dispone de 100 MB de RAM. Al crear un proceso se intenta reservar la cantidad de memoria solicitada. Si no hay espacio suficiente, se muestra un error Out of Memory y el proceso no entra a la cola de listos.

La memoria asignada se libera cuando el proceso termina o se aborta.
Semáforo binario
El semáforo controla el acceso a una variable compartida. Su valor es 1 cuando la sección crítica está libre y 0 cuando está ocupada.
- wait() permite entrar si está libre. Si está ocupado, el proceso entra a una cola de espera.
- signal() permite que el dueño salga y entrega el turno al siguiente proceso de la cola, si existe.
- Solo el proceso que tiene el semáforo puede escribir en la variable compartida.
También se incluye una demostración de condición de carrera, primero sin semáforo y después con semáforo.
Deadlock
El simulador administra dos recursos exclusivos: R1 y R2. Cada recurso puede tener un dueño y una cola de procesos que lo esperan.

Se puede formar una espera circular cuando un proceso tiene R1 y espera R2, mientras otro tiene R2 y espera R1. El programa detecta el ciclo mediante un grafo de espera. Para resolverlo, permite abortar uno de los procesos y liberar los recursos que tenía.
Requisitos
- Python 3 instalado. El proyecto se probó localmente con Python 3.14.
- Una terminal para ejecutar el programa.
- No se necesitan paquetes externos para la versión de terminal.
Cómo ejecutar
Abrir una terminal en la carpeta principal del proyecto, donde está main.py, y ejecutar:
python main.py
En el menú, escribir el número de la opción deseada y presionar Enter. Para cerrar el programa, elegir 0.
Opciones del menú
Procesos y Round Robin
- 1: crear un proceso indicando su memoria en MB y su ráfaga de CPU.
- 2: ver la cola de procesos.
- 3: ejecutar Round Robin.
- 4: ver las métricas de los procesos terminados.
Memoria
- 5: ver la RAM total, ocupada y disponible, además de la memoria asignada a cada proceso.
Semáforo
- 6: ejecutar wait() con un proceso.
- 7: ejecutar signal() con el dueño del semáforo.
- 8: escribir en la variable compartida.
- 9: ver el estado del semáforo.
- 10: mostrar la demostración de condición de carrera.
Deadlock
- 11: solicitar R1 o R2.
- 12: liberar un recurso.
- 13: simular un deadlock con dos procesos.
- 14: detectar si existe un deadlock.
- 15: abortar un proceso.
- 16: ver el dueño y la cola de espera de cada recurso.
La opción 0 cierra el simulador.

Antes de utilizar el semáforo o los recursos, es necesario crear procesos con la opción 1. Para las demás opciones se utilizan los PID que el programa muestra al crearlos.
Pruebas sugeridas
Probar procesos y memoria
1. Elegir 1 y crear un proceso de 20 MB con ráfaga 7.
2. Elegir 1 y crear otro de 30 MB con ráfaga 4.
3. Elegir 2 para ver ambos procesos en la cola.
4. Elegir 5 para comprobar cuánta RAM está ocupada.
5. Elegir 3 para ejecutar Round Robin.
6. Elegir 4 para consultar las métricas.
7. Elegir 5 nuevamente para comprobar que se liberó la memoria de los procesos terminados.
Probar falta de memoria
Iniciar nuevamente el programa. Crear un proceso de 80 MB e intentar crear otro de 30 MB. El segundo debe ser rechazado porque la memoria total es de 100 MB.
Probar el semáforo
1. Crear dos procesos y anotar sus PID.
2. Elegir 6 con el primer PID. Este entra a la sección crítica.
3. Elegir 6 con el segundo PID. Este queda en la cola de espera.
4. Elegir 9 para revisar el dueño y la cola.
5. Elegir 7 con el primer PID. El semáforo pasa al segundo proceso.
6. Elegir 8 con el segundo PID e ingresar un número para la variable compartida.
7. Elegir 7 con el segundo PID para dejar libre el semáforo.
La opción 10 muestra por separado la demostración de condición de carrera.
Probar deadlock
1. Iniciar nuevamente el programa y crear dos procesos.
2. Elegir 13 e introducir los PID de esos procesos para formar la espera circular.
3. Elegir 14 para detectar el deadlock.
4. Elegir 16 para ver qué recurso tiene y espera cada proceso.
5. Elegir 15 y abortar uno de los procesos.
6. Elegir 14 nuevamente para comprobar que se rompió la espera circular.
Archivos principales
- main.py: muestra el menú y conecta los módulos.
- kernel/procesos.py: define el PCB, crea procesos y ejecuta Round Robin.
- kernel/memoria.py: asigna y libera memoria RAM.
- kernel/semaforo.py: implementa el semáforo binario y la demostración de condición de carrera.
- kernel/deadlock.py: administra los recursos, detecta ciclos de espera y aborta procesos.
Alcance
La demostración de condición de carrera muestra una secuencia de pasos para explicar el problema; no inicia hilos reales. El proyecto busca mostrar de forma práctica cómo se relacionan los procesos, la memoria, la sincronización y los recursos dentro de un sistema operativo.