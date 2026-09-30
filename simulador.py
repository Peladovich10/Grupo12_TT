import csv
import sys

# Forzar la entrada y salida estándar de la consola a UTF-8
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stdin.encoding != "utf-8":
    sys.stdin.reconfigure(encoding="utf-8")


def imprimir_leyenda_tabla_general():
    """Imprime el significado de cada columna de la Tabla General."""
    print("--- REFERENCIAS TABLA GENERAL ---")
    print("ID         : Identificador único del proceso")
    print("TA         : Tiempo de arribo al sistema")
    print("TI         : Tiempo de irrupción (duración total del proceso)")
    print("TI_REST    : Tiempo de irrupción restante")
    print("TAM(Kb)    : Tamaño en kilobytes del proceso")
    print(
        "EST        : Estado actual [N: Nuevo | S: Listo y Suspendido | L: Listo | E: En Ejecución | F: Finalizado]"
    )


def imprimir_leyenda_tabla_memoria():
    """Imprime el significado de cada columna de la Tabla de Memoria."""
    print("--- REFERENCIAS TABLA DE MEMORIA ---")
    print("ID_PART     : Identificador de la partición de memoria")
    print("DIR_INICIO  : Dirección de memoria donde inicia la partición (K)")
    print("TAM_PART(Kb): Tamaño total de la partición en KB")
    print(
        "ID_PROC     : ID del proceso asignado a la partición ('Libre' si está vacía)"
    )
    print(
        "FRAG_EXTERNA: Espacio libre contiguo restante fuera de la partición"
    )


def mostrar_tablas_evento(tiempo, evento_msg, procesos, particiones_memoria):
    """Muestra el estado del sistema cuando ocurre un evento relevante."""
    print("\n" + "=" * 80)
    print(f" TIEMPO t = {tiempo} | EVENTO: {evento_msg}")
    print("=" * 80)

    # 1. TABLA GENERAL DE PROCESOS
    print("\n[TABLA GENERAL DE PROCESOS]")
    imprimir_leyenda_tabla_general()
    print("-" * 80)
    print(
        f"{'ID':<5} | {'TA':<5} | {'TI':<5} | {'TI_REST':<8} | {'TAM(Kb)':<8} | {'EST':<5}"
    )
    print("-" * 80)

    for p in procesos:
        print(
            f"{p['id']:<5} | {p['ta']:<5} | {p['ti']:<5} | {p['ti_rest']:<8} | {p['tam']:<8} | {p['est']:<5}"
        )
    print("-" * 80)

    # 2. TABLA DE MEMORIA
    print("\n[TABLA DE MEMORIA - PARTICIONES VARIABLES]")
    imprimir_leyenda_tabla_memoria()
    print("-" * 80)
    print(
        f"{'ID_PART':<8} | {'DIR_INICIO':<10} | {'TAM_PART(Kb)':<12} | {'ID_PROC':<8} | {'FRAG_EXTERNA':<12}"
    )
    print("-" * 80)

    for part in particiones_memoria:
        id_proc_str = (
            f"P{part['id_proc']}" if part["id_proc"] is not None else "Libre"
        )
        frag_str = (
            f"{part['frag_ext']}K" if part["frag_ext"] is not None else "-"
        )
        print(
            f"{part['id_part']:<8} | {part['dir_inicio']:<10} | {part['tam']:<12} | {id_proc_str:<8} | {frag_str:<12}"
        )
    print("-" * 80)


def cargar_procesos_desde_csv(ruta_csv):
    """Lee un archivo CSV y devuelve una lista de diccionarios de procesos."""
    procesos = []
    try:
        with open(ruta_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                procesos.append(
                    {
                        "id": int(row["ID"]),
                        "ta": int(row["TA"]),
                        "ti": int(row["TI"]),
                        "ti_rest": int(row["TI"]),
                        "tam": int(row["TAM(Kb)"]),
                        "est": "-",  # Estado inicial antes de arribar
                    }
                )
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta_csv}'.")
        return None
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return None
    return procesos


def ejecutar_simulacion(ruta_csv):
    """
    Función principal encargada de ejecutar la simulación de procesos
    y mostrar el estado del sistema cuando ocurre un evento.
    """
    procesos = cargar_procesos_desde_csv(ruta_csv)
    if not procesos:
        return

    # Estructura inicial de memoria (ejemplo ilustrativo de inicio MVT)
    # Memoria Usuario total: 450K (de 100K a 550K)
    particiones_memoria = [
        {
            "id_part": 1,
            "dir_inicio": "100K",
            "tam": 450,
            "id_proc": None,
            "frag_ext": 450,
        }
    ]

    print(
        f"\nIniciando simulación con los procesos cargados desde '{ruta_csv}'..."
    )

    # Ejemplo de simulación demostrativa de eventos
    # (A medida que desarrollemos el algoritmo SRTF y Best-Fit,
    # estas llamadas se generarán dinámicamente en el bucle del tiempo)

    # Evento 1: Arribo de Proceso 1
    procesos[0]["est"] = "E"
    particiones_memoria = [
        {
            "id_part": 1,
            "dir_inicio": "100K",
            "tam": 120,
            "id_proc": 1,
            "frag_ext": 330,
        }
    ]
    mostrar_tablas_evento(
        tiempo=0,
        evento_msg="Arribo de Proceso P1 (Nuevo -> En Ejecución)",
        procesos=procesos,
        particiones_memoria=particiones_memoria,
    )

    # Evento 2: Arribo de Proceso 2
    procesos[1]["est"] = "L"
    particiones_memoria.append(
        {
            "id_part": 2,
            "dir_inicio": "220K",
            "tam": 200,
            "id_proc": 2,
            "frag_ext": 130,
        }
    )
    mostrar_tablas_evento(
        tiempo=1,
        evento_msg="Arribo de Proceso P2 (Nuevo -> Listo)",
        procesos=procesos,
        particiones_memoria=particiones_memoria,
    )


def ejecutar_procesos_defecto():
    """Ejecuta la simulación utilizando el archivo por defecto."""
    ejecutar_simulacion("procesos_defecto.csv")


def cargar_archivo_csv():
    """Solicita la ruta de un archivo CSV personalizado y ejecuta la simulación."""
    ruta = input("\nIngrese la ruta del archivo .csv: ").strip()
    ejecutar_simulacion(ruta)


def mostrar_menu():
    """Muestra el menú principal y gestiona la selección del usuario."""
    while True:
        print("\n" + "=" * 50)
        print(" SIMULADOR DE MEMORIA Y PLANIFICACIÓN DE PROCESOS")
        print("=" * 50)
        print("1) Ejecutar procesos cargados por defecto.")
        print("2) Cargar archivo .csv con los procesos.")
        print("3) Salir")
        print("=" * 50)

        opcion = input("Seleccione una opción (1-3) y presione ENTER: ").strip()

        if opcion == "1":
            ejecutar_procesos_defecto()
        elif opcion == "2":
            cargar_archivo_csv()
        elif opcion == "3":
            print("\nSaliendo...")
            break
        else:
            print("\nOpción inválida. Por favor, intente de nuevo.")


if __name__ == "__main__":
    mostrar_menu()