## Simulador de Memoria y Planificación de Procesos

Trabajo Práctico Integrador de la materia Sistemas Operativos.

El proyecto consiste en el desarrollo de un simulador en Python que representa la administración de memoria y la planificación de procesos dentro de un sistema operativo.

Actualmente el simulador permite trabajar con distintos lotes de procesos almacenados en archivos CSV y observar cómo van cambiando sus estados, la asignación de memoria y el uso de la CPU durante la ejecución.

## Características principales

El simulador implementa:

- Gestión de memoria mediante particiones variables.
- Asignación de memoria utilizando el algoritmo Best-Fit.
- Planificación de CPU mediante SRTF.
- Manejo de los estados nuevo, listo, listo/suspendido, en ejecución y finalizado.
- Un máximo de cinco procesos admitidos simultáneamente en el sistema.
- 100 KB de memoria reservados para el Sistema Operativo y 450 KB disponibles para los procesos.
- División de huecos libres cuando un proceso ocupa solo una parte de una partición.
- Liberación de memoria cuando un proceso finaliza.
- Unificación de huecos libres contiguos.
- Expropiación de CPU cuando SRTF encuentra un proceso con menor tiempo restante.
- Visualización del estado general del sistema durante los eventos importantes de la simulación.
- Visualización de la tabla de procesos y de la distribución de memoria.
- Cálculo del tiempo de retorno y del tiempo de espera de cada proceso.
- Cálculo de los promedios de retorno y espera.
- Cálculo del rendimiento general del sistema.

## Archivos de procesos

Los procesos se cargan mediante archivos CSV.

Cada proceso contiene:

- Identificador.
- Tiempo de arribo.
- Tiempo de irrupción.
- Tamaño requerido en memoria.

El programa permite ejecutar un conjunto de procesos cargado por defecto o seleccionar otro archivo CSV disponible dentro de la carpeta del proyecto.

## Funcionamiento general

Durante la simulación se administran distintas colas según el estado de cada proceso.

Los procesos pueden pasar por los siguientes estados:

- Nuevo.
- Listo.
- Listo/Suspendido.
- En Ejecución.
- Finalizado.

Cuando llega un proceso, el simulador intenta asignarle memoria utilizando Best-Fit. Si puede ingresar al sistema, pasa a la cola de Listos. En caso contrario permanece en Listo/Suspendido hasta que pueda ser admitido.

La CPU utiliza SRTF para seleccionar el proceso con menor tiempo de ejecución restante. Si aparece un proceso con menor tiempo restante que el que se encuentra ejecutando, este puede ser desplazado y regresar a la cola de Listos.

Cuando un proceso termina, se libera la memoria que ocupaba y se unifican los huecos libres que hayan quedado contiguos.

## Visualización

Durante los eventos relevantes se muestra información sobre:

- Tiempo actual de la simulación.
- Evento ocurrido.
- Datos de los procesos.
- Tiempo restante de ejecución.
- Estado actual de cada proceso.
- Distribución de las particiones de memoria.
- Procesos asignados a memoria.

La ejecución se pausa en estos puntos hasta que el usuario presiona ENTER.

## Informe final

Una vez finalizados todos los procesos, el simulador presenta un informe estadístico con:

- Tiempo de finalización de cada proceso.
- Tiempo de retorno.
- Tiempo de espera.
- Tiempo promedio de retorno.
- Tiempo promedio de espera.
- Rendimiento del sistema.

## Ejecución

El programa principal se ejecuta desde Python.

Al iniciar, se presenta un menú desde el cual se puede:

- Ejecutar los procesos cargados por defecto.
- Seleccionar otro archivo CSV.
- Salir del programa.
