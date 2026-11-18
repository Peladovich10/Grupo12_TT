# HowTo - Simulador de Asignación de Memoria y Planificación de Procesos

**Grupo 12**:

Simulador de un sistema monoprocesador con memoria de **particiones variables (MVT)**, política de asignación **Best-Fit** y planificación de CPU **SRTF**.

## Contenido del paquete

```
Grupo12_TT/
├── simulador.py            Programa (código fuente, se ejecuta con Python)
├── procesos_defecto.csv    Lote que se ejecuta con la opción 1 del menú
├── lote1.csv ... lote6.csv Lotes de prueba
└── README.md               Esta guía
```

> Los `.csv` deben estar **en la misma carpeta** que `simulador.py`.

## Parámetros de la simulación

| Parámetro | Valor |
|---|---|
| Memoria para el Sistema Operativo | 100K (direcciones 0 a 100) |
| Memoria para procesos de usuario | 450K (direcciones 100 a 550) |
| Máximo de procesos por lote | 10 |
| Máximo de procesos en Ejecución + Listos + Listos y Suspendidos | 5 |
| Asignación de memoria | Best-Fit (hueco libre más justo) |
| Planificación de CPU | SRTF (con apropiación) |
| Estados | Nuevo, Listo, Listo y Suspendido, En Ejecución, Finalizado |

## Requisitos

* Python 3.7 o superior (no requiere instalar librerías externas).
* `simulador.py` y los `.csv` en la misma carpeta.

Para verificar la instalación: `python --version` (en Windows también puede usarse `py --version`).

## Ejecución

1. Abrir una terminal en la carpeta del proyecto.
2. Ejecutar:

   ```
   python simulador.py
   ```

   (en Windows, si `python` no es reconocido: `py simulador.py`)

3. Aparece el menú:

   ```
   1) Ejecutar procesos cargados por defecto.
   2) Cargar archivo .csv con los procesos.
   3) Salir
   ```

   * **Opción 1:** ejecuta `procesos_defecto.csv`.
   * **Opción 2:** lista los `.csv` de la carpeta (excepto `procesos_defecto.csv`); se elige uno ingresando su número. Si se presiona solo ENTER se cancela la selección.
   * **Opción 3:** sale del programa.

## Formato del archivo de procesos

Archivo CSV separado por comas, con esta primera línea de encabezado (exactamente):

```
ID,TA,TI,TAM(Kb)
```

| Columna | Significado |
|---|---|
| `ID` | Identificador del proceso |
| `TA` | Tiempo de arribo |
| `TI` | Tiempo de irrupción (duración total en CPU) |
| `TAM(Kb)` | Tamaño en memoria, en K |

Ejemplo:

```
ID,TA,TI,TAM(Kb)
1,0,5,200
2,1,3,150
3,2,4,30
```

Reglas de validación al cargar el archivo:

* Se admiten como máximo **10 procesos**; los demás se ignoran y se informa cuáles.
* Un proceso que pide **más de 450K** nunca podría cargarse: se descarta con un aviso.
* Se descartan procesos con datos inválidos (`TA < 0`, `TI <= 0` o `TAM <= 0`).
* Los procesos descartados o ignorados **no aparecen** en el informe final ni en los promedios.

## Desarrollo de la simulación

La simulación **no corre de forma ininterrumpida**: se detiene y muestra el estado del sistema cada vez que ocurre un evento (arribo de un proceso, finalización, asignación de CPU, apropiación SRTF o carga a memoria de un proceso suspendido). Para continuar se presiona **ENTER**.

En cada pausa se muestra:

* **Instante de tiempo (`t`)** y el/los eventos ocurridos.
* **Tabla general de procesos:** ID, TA, TI, tiempo de irrupción restante (`TI_REST`), tamaño y estado. El proceso con estado _En Ejecución_ es el que ocupa la CPU; los estados _Listo_, _Listo y Suspendido_ y _Nuevo_ indican a qué cola pertenece cada proceso.
* **Tabla de memoria:** ID de partición, dirección de inicio, tamaño, proceso asignado (`Libre` si está vacía) y fragmentación. La primera fila corresponde al Sistema Operativo.

### Estados de los procesos

| Estado | Significado |
|---|---|
| Nuevo | Ya arribó pero el sistema está completo (5 procesos); espera para ser admitido |
| Listo | Admitido y con memoria asignada; espera la CPU |
| Listo y Suspendido | Admitido pero sin memoria disponible; espera que se libere un hueco |
| En Ejecución | Ocupa la CPU |
| Finalizado | Terminó; su memoria fue liberada |

## Informe final

Al terminar el último proceso se muestra, para cada proceso, el tiempo de finalización, el **tiempo de retorno** (`fin - arribo`) y el **tiempo de espera** (`retorno - irrupción`), y además:

* Tiempo promedio de retorno.
* Tiempo promedio de espera.
* **Rendimiento del sistema** = trabajos terminados / tiempo total de la simulación (medido desde `t = 0`).

## Decisiones de diseño

La consigna no fija estos puntos, por lo que se adoptaron los siguientes criterios:

* **Memoria:** el espacio libre es un único hueco al inicio. Al asignar con Best-Fit se elige el hueco libre más justo (a igual tamaño, el de menor dirección) y se lo divide en la partición del proceso y un hueco con el resto. Al liberar, los huecos libres contiguos se fusionan. Como cada partición se corta al tamaño exacto del proceso, la fragmentación interna es siempre 0; la columna `FRAG_EXTERNA` muestra el tamaño de cada hueco libre cuando la memoria no está totalmente libre.
* **Admisión:** los procesos que arriban quedan primero en estado _Nuevo_ y se admiten por orden de llegada mientras haya menos de 5 procesos entre Ejecución, Listos y Listos y Suspendidos.
* **Prioridad de memoria:** cuando se libera memoria, primero se intenta cargar a los Listos y Suspendidos (por orden de suspensión, pudiendo pasar uno más chico si el primero no entra) y luego se admiten Nuevos.
* **SRTF:** solo compiten por la CPU los procesos en memoria (Listos). Un proceso en ejecución solo es desplazado si otro tiene un tiempo restante **estrictamente menor** (en un empate no hay cambio de contexto). Si hay varios candidatos con igual tiempo restante, se elige el de menor tiempo de arribo y luego el de menor ID.
* **Tiempo:** unidades enteras; un proceso que arriba o termina en el instante `t` se atiende en ese mismo instante.

## Lotes de prueba incluidos

| Archivo | Qué prueba |
|---|---|
| `procesos_defecto.csv` | Lote de la opción 1 del menú: 10 procesos con apropiaciones SRTF, procesos en estado Nuevo y Listo y Suspendido, y memoria fragmentada |
| `lote1.csv` | Procesos espaciados; CPU ociosa al inicio (primer arribo en `t = 3`) |
| `lote2.csv` | 5 procesos en `t = 0` que no entran todos en memoria → Listo y Suspendido |
| `lote3.csv` | Sistema completo (5 procesos): P8 queda en estado Nuevo; memoria fragmentada |
| `lote4.csv` | 10 procesos con apropiaciones SRTF, Nuevos y Suspendidos |
| `lote5.csv` | Un proceso de 451K (no entra en memoria): se descarta con aviso |
| `lote6.csv` | 12 procesos: se ignoran P11 y P12 (máximo 10) |
