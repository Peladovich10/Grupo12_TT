import csv
import sys

# Forzar la entrada y salida estándar de la consola a UTF-8
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stdin.encoding != "utf-8":
    sys.stdin.reconfigure(encoding="utf-8")

def pausar_simulacion():
    """Pausa la ejecución y espera a que el usuario presione Enter."""
    print("Presionar ENTER para continuar")
    input()

def imprimir_leyendas_globales():
    """Imprime las referencias de las tablas una sola vez antes de iniciar la simulación."""
    print("\n--- REFERENCIAS TABLA GENERAL DE PROCESOS---")
    print("ID         : Identificador único del proceso")
    print("TA         : Tiempo de arribo al sistema")
    print("TI         : Tiempo de irrupción (duración total del proceso)")
    print("TI_REST    : Tiempo de irrupción restante")
    print("TAM(Kb)    : Tamaño en kilobytes del proceso")
    print("EST        : Estado actual del proceso")

    print("\n--- REFERENCIAS TABLA DE MEMORIA ---")
    print("ID_PART     : Identificador de la partición de memoria")
    print("DIR_INICIO  : Dirección de memoria donde inicia la partición (K)")
    print("TAM_PART(Kb): Tamaño total de la partición en KB")
    print("ID_PROC     : ID del proceso asignado a la partición ('Libre' si está vacía)")
    print("FRAG_EXTERNA: Espacio libre contiguo restante fuera de la partición")

class GestorMemoria:

    def __init__(
        self, tam_total=450, dir_inicio=100
    ):  # 100K a 550K para usuarios
        self.tam_total = tam_total
        self.dir_inicio_base = dir_inicio
        # Cada partición: {'id_part': int, 'dir_inicio': int, 'tam': int, 'id_proc': int/None}
        self.particiones = [
            {
                "id_part": 1,
                "dir_inicio": self.dir_inicio_base,
                "tam": self.tam_total,
                "id_proc": None,
            }
        ]
        self.siguiente_id_part = 2

    def asignar_best_fit(self, id_proc, tam_proc):
        """Busca el hueco libre que mejor se adapte (Best-Fit) y lo divide."""
        mejores_candidatos = []

        for idx, part in enumerate(self.particiones):
            if part["id_proc"] is None and part["tam"] >= tam_proc:
                desperdicio = part["tam"] - tam_proc
                mejores_candidatos.append((desperdicio, idx))

        if not mejores_candidatos:
            return False  # No hay espacio suficiente en ninguna partición libre

        # Elegir el de menor desperdicio (Best-Fit)
        mejores_candidatos.sort(key=lambda x: x[0])
        idx_elegido = mejores_candidatos[0][1]
        part_elegida = self.particiones[idx_elegido]

        # Si el tamaño es exacto, solo asignamos el ID de proceso
        if part_elegida["tam"] == tam_proc:
            part_elegida["id_proc"] = id_proc
        else:
            # Se crea una nueva partición exacta para el proceso y el sobrante queda Libre
            tam_restante = part_elegida["tam"] - tam_proc
            dir_nueva = part_elegida["dir_inicio"] + tam_proc

            part_elegida["tam"] = tam_proc
            part_elegida["id_proc"] = id_proc

            nueva_part_libre = {
                "id_part": self.siguiente_id_part,
                "dir_inicio": dir_nueva,
                "tam": tam_restante,
                "id_proc": None,
            }
            self.siguiente_id_part += 1
            self.particiones.insert(idx_elegido + 1, nueva_part_libre)

        return True

    def liberar_memoria(self, id_proc):
        """Libera la partición asignada al proceso y fusiona huecos libres contiguos."""
        for part in self.particiones:
            if part["id_proc"] == id_proc:
                part["id_proc"] = None
                break

        # Fusionar particiones libres contiguas
        i = 0
        while i < len(self.particiones) - 1:
            if (
                self.particiones[i]["id_proc"] is None
                and self.particiones[i + 1]["id_proc"] is None
            ):
                self.particiones[i]["tam"] += self.particiones[i + 1]["tam"]
                self.particiones.pop(i + 1)
            else:
                i += 1

    def obtener_tabla_memoria_salida(self):
        """Formatea las particiones para mostrarlas según el requerimiento especificado."""
        tabla = []
        # La fragmentación externa es el espacio total libre acumulado fuera de la partición
        espacio_libre_total = sum(
            p["tam"] for p in self.particiones if p["id_proc"] is None
        )

        for p in self.particiones:
            tabla.append(
                {
                    "id_part": p["id_part"],
                    "dir_inicio": f"{p['dir_inicio']}K",
                    "tam": p["tam"],
                    "id_proc": p["id_proc"],
                    "frag_ext": espacio_libre_total
                    if p["id_proc"] is None
                    else 0,
                }
            )
        return tabla

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

def estado_legible(est):
    """Devuelve el nombre completo del estado para mostrar en la tabla."""
    mapa = {
        "N": "Nuevo",
        "S": "Listo y Suspendido",
        "L": "Listo",
        "E": "En Ejecución",
        "F": "Finalizado",
        "-": "-",
    }
    return mapa.get(est, est)

def mostrar_tablas_evento(tiempo, evento_msg, procesos, particiones_memoria):
    """Muestra el estado del sistema cuando ocurre un evento relevante."""
    print("\n" + "=" * 80)
    print(f" TIEMPO t = {tiempo} | EVENTO: {evento_msg}")
    print("=" * 80)

    # 1. TABLA GENERAL DE PROCESOS
    print("\n[TABLA GENERAL DE PROCESOS]")
    print("-" * 80)
    print(
        f"{'ID':<5} | {'TA':<5} | {'TI':<5} | {'TI_REST':<8} | {'TAM(Kb)':<8} | {'EST':<20}"
    )
    print("-" * 80)

    for p in procesos:
        print(
            f"{p['id']:<5} | {p['ta']:<5} | {p['ti']:<5} | {p['ti_rest']:<8} | {p['tam']:<8} | {estado_legible(p['est']):<20}"
        )
    print("-" * 80)

    # 2. TABLA DE MEMORIA
    print("\n[TABLA DE MEMORIA - PARTICIONES VARIABLES]")
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

    pausar_simulacion()

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

def mostrar_informe_estadistico(procesos, tiempo_total):
    """Muestra el informe estadístico con tiempos de retorno, espera y rendimiento."""
    print("\n" + "=" * 80)
    print(" INFORME ESTADÍSTICO FINAL DE LA SIMULACIÓN")
    print("=" * 80)

    print(
        f"{'ID':<5} | {'TA':<5} | {'TI':<5} | {'T. FIN':<8} | {'T. RETORNO':<12} | {'T. ESPERA':<10}"
    )
    print("-" * 80)

    sum_retorno = 0
    sum_espera = 0

    for p in procesos:
        ret = p["retorno"]
        esp = p["espera"]
        sum_retorno += ret
        sum_espera += esp
        print(
            f"{p['id']:<5} | {p['ta']:<5} | {p['ti']:<5} | {p['tiempo_fin']:<8} | {ret:<12} | {esp:<10}"
        )

    cant = len(procesos)
    prom_retorno = sum_retorno / cant
    prom_espera = sum_espera / cant
    rendimiento = cant / tiempo_total if tiempo_total > 0 else 0

    print("-" * 80)
    print(f"Tiempo promedio de Retorno: {prom_retorno:.2f} unidades de tiempo")
    print(f"Tiempo promedio de Espera : {prom_espera:.2f} unidades de tiempo")
    print(
        f"Rendimiento del sistema   : {rendimiento:.4f} trabajos/unidad de tiempo"
    )
    print("=" * 80 + "\n")

def simular_srtf_y_memoria(procesos, ruta_csv):
    memoria = GestorMemoria(tam_total=450, dir_inicio=100)

    cola_nuevos = [p for p in procesos]
    cola_nuevos.sort(key=lambda x: x["ta"])

    cola_listos = []
    cola_listos_suspendidos = []
    proceso_en_ejecucion = None

    tiempo_actual = 0
    procesos_completados = 0
    total_procesos = len(procesos)

    imprimir_leyendas_globales()

    print(f"\n========== INICIANDO SIMULACIÓN DESDE '{ruta_csv}' ==========")

    while procesos_completados < total_procesos:
        hubo_evento = False
        mensajes_evento = []

        # 1. Admitir procesos que arriban en el instante 'tiempo_actual'
        arribos_hoy = [p for p in cola_nuevos if p["ta"] == tiempo_actual]
        for p in arribos_hoy:
            cola_nuevos.remove(p)
            p["est"] = "N"

            # Cantidad en sistema = Ejecución + Listos + Listos/Suspendidos
            procesos_en_sistema = (
                (1 if proceso_en_ejecucion else 0)
                + len(cola_listos)
                + len(cola_listos_suspendidos)
            )

            # Intentar asignar memoria
            memoria_asignada = memoria.asignar_best_fit(p["id"], p["tam"])

            if memoria_asignada and procesos_en_sistema < 5:
                p["est"] = "L"
                cola_listos.append(p)
                mensajes_evento.append(
                    f"Arribo de P{p['id']}: Asignado a Memoria -> Cola de Listos (L)"
                )
            else:
                # Si no hay memoria o ya hay 5 procesos en sistema -> Listo y Suspendido
                if memoria_asignada:
                    # Se le asignó pero superaba el límite de 5, revertimos la asignación
                    memoria.liberar_memoria(p["id"])

                p["est"] = "S"
                cola_listos_suspendidos.append(p)
                mensajes_evento.append(
                    f"Arribo de P{p['id']}: Sin cupo/memoria -> Cola de Listos/Suspendidos (S)"
                )

            hubo_evento = True

        # 2. Desuspender procesos si hay espacio en el sistema (< 5) y memoria disponible
        i = 0
        while i < len(cola_listos_suspendidos):
            p_susp = cola_listos_suspendidos[i]
            procesos_en_sistema = (
                (1 if proceso_en_ejecucion else 0)
                + len(cola_listos)
                + len(cola_listos_suspendidos)
            )

            if procesos_en_sistema <= 5 and memoria.asignar_best_fit(
                p_susp["id"], p_susp["tam"]
            ):
                cola_listos_suspendidos.pop(i)
                p_susp["est"] = "L"
                cola_listos.append(p_susp)
                mensajes_evento.append(
                    f"Desuspensión de P{p_susp['id']}: Pasa a Memoria -> Cola de Listos (L)"
                )
                hubo_evento = True
            else:
                i += 1

        # 3. Planificación SRTF: Evaluar si un proceso listo debe desbancar al actual (Apropiativo)
        candidatos_cpu = [p for p in cola_listos]
        if proceso_en_ejecucion:
            candidatos_cpu.append(proceso_en_ejecucion)

        if candidatos_cpu:
            # Seleccionar el de menor tiempo de irrupción restante (ti_rest)
            candidatos_cpu.sort(key=lambda x: (x["ti_rest"], x["ta"], x["id"]))
            siguiente_cpu = candidatos_cpu[0]

            if proceso_en_ejecucion is None:
                proceso_en_ejecucion = siguiente_cpu
                cola_listos.remove(siguiente_cpu)
                proceso_en_ejecucion["est"] = "E"
                mensajes_evento.append(
                    f"CPU asignada a P{proceso_en_ejecucion['id']} (E)"
                )
                hubo_evento = True
            elif siguiente_cpu["id"] != proceso_en_ejecucion["id"]:
                # Apropiación por SRTF
                proceso_anterior = proceso_en_ejecucion
                proceso_anterior["est"] = "L"
                cola_listos.append(proceso_anterior)

                proceso_en_ejecucion = siguiente_cpu
                cola_listos.remove(siguiente_cpu)
                proceso_en_ejecucion["est"] = "E"

                mensajes_evento.append(
                    f"Apropiación SRTF: P{siguiente_cpu['id']} desplaza a P{proceso_anterior['id']} en CPU"
                )
                hubo_evento = True

        # Mostrar tablas si ocurrió un evento relevante en este instante
        if hubo_evento:
            msg_unificado = " | ".join(mensajes_evento)
            mostrar_tablas_evento(
                tiempo_actual,
                msg_unificado,
                procesos,
                memoria.obtener_tabla_memoria_salida(),
            )

        # 4. Avanzar el tiempo 1 unidad y ejecutar el proceso activo
        tiempo_actual += 1

        if proceso_en_ejecucion:
            proceso_en_ejecucion["ti_rest"] -= 1

            # Verificar si el proceso terminó
            if proceso_en_ejecucion["ti_rest"] == 0:
                proceso_en_ejecucion["est"] = "F"
                proceso_en_ejecucion["tiempo_fin"] = tiempo_actual
                proceso_en_ejecucion["retorno"] = (
                    tiempo_actual - proceso_en_ejecucion["ta"]
                )
                proceso_en_ejecucion["espera"] = (
                    proceso_en_ejecucion["retorno"]
                    - proceso_en_ejecucion["ti"]
                )

                memoria.liberar_memoria(proceso_en_ejecucion["id"])
                procesos_completados += 1

                msg_fin = f"Proceso P{proceso_en_ejecucion['id']} FINALIZÓ (F) -> Memoria Liberada"
                proceso_en_ejecucion = None

                # Mostrar actualización del evento de finalización
                mostrar_tablas_evento(
                    tiempo_actual,
                    msg_fin,
                    procesos,
                    memoria.obtener_tabla_memoria_salida(),
                )

    # Al finalizar todos los procesos, mostramos el informe estadístico
    mostrar_informe_estadistico(procesos, tiempo_actual)

def ejecutar_simulacion(ruta_csv):
    """Carga los procesos del archivo CSV e inicia el motor de simulación."""
    procesos = cargar_procesos_desde_csv(ruta_csv)
    if not procesos:
        return

    simular_srtf_y_memoria(procesos, ruta_csv)

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