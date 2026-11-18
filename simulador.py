import csv
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

# Forzar la entrada y salida estándar de la consola a UTF-8
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stdin.encoding != "utf-8":
    sys.stdin.reconfigure(encoding="utf-8")

# Parámetros del enunciado
MEMORIA_SO = 100        # K reservados para el Sistema Operativo
MEMORIA_USUARIO = 450   # K disponibles para procesos de usuario
MAX_PROCESOS = 10       # máximo de procesos por simulación
MAX_EN_SISTEMA = 5      # máximo entre Ejecución + Listos + Listos y Suspendidos

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
    def __init__(self, tam_total=450, dir_inicio=100):
        self.tam_total = tam_total
        self.dir_inicio_base = dir_inicio
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
            return False

        mejores_candidatos.sort(key=lambda x: x[0])
        idx_elegido = mejores_candidatos[0][1]
        part_elegida = self.particiones[idx_elegido]

        if part_elegida["tam"] == tam_proc:
            part_elegida["id_proc"] = id_proc
        else:
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

        # Fila del Sistema Operativo fijo
        tabla.append({
            "id_part": 0,
            "dir_inicio": 0,
            "tam": 100,
            "id_proc": "SO",
            "frag_ext": 0,
        })

        for p in self.particiones:
            tabla.append({
                "id_part": p["id_part"],
                "dir_inicio": p["dir_inicio"],
                "tam": p["tam"],
                "id_proc": p["id_proc"],
                "frag_ext": p["tam"] if (p["id_proc"] is None and p["tam"] < self.tam_total) else 0,
            })

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

def mostrar_tablas_evento(tiempo, evento_msg, procesos, particiones_memoria, plural=False):
    """Muestra el estado del sistema cuando ocurre un evento relevante."""
    print("\n" + "=" * 80)
    etiqueta = "EVENTOS" if plural else "EVENTO"
    print(f" TIEMPO t = {tiempo} | {etiqueta}: {evento_msg}")
    print("=" * 80)

    print("\n[TABLA GENERAL DE PROCESOS]")
    print("-" * 80)
    print(f"{'ID':<5} | {'TA':<5} | {'TI':<5} | {'TI_REST':<8} | {'TAM(Kb)':<8} | {'EST':<20}")
    print("-" * 80)

    for p in procesos:
        if p["est"] != "-":
            print(
                f"{p['id']:<5} | {p['ta']:<5} | {p['ti']:<5} | {p['ti_rest']:<8} | {p['tam']:<8} | {estado_legible(p['est']):<20}"
            )
    print("-" * 80)

    print("\n[TABLA DE MEMORIA - PARTICIONES VARIABLES]")
    print("-" * 80)
    print(f"{'ID_PART':<8} | {'DIR_INICIO':<10} | {'TAM_PART(Kb)':<12} | {'ID_PROC':<8} | {'FRAG_EXTERNA':<12}")
    print("-" * 80)

    for part in particiones_memoria:
        if part["id_proc"] is None:
            id_proc_str = "Libre"
        elif part["id_proc"] == "SO":
            id_proc_str = "SO"
        else:
            id_proc_str = f"P{part['id_proc']}"

        frag_str = f"{part['frag_ext']}K" if part["frag_ext"] is not None else "-"
        print(
            f"{part['id_part']:<8} | {part['dir_inicio']:<10} | {part['tam']:<12} | {id_proc_str:<8} | {frag_str:<12}"
        )
    print("-" * 80)

    pausar_simulacion()

def cargar_procesos_desde_csv(ruta_csv):
    """Lee un archivo CSV y devuelve una lista de diccionarios de procesos."""
    procesos = []
    try:
        # utf-8-sig: tolera archivos guardados con BOM (por ejemplo, desde Excel)
        with open(ruta_csv, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                procesos.append(
                    {
                        "id": int(row["ID"]),
                        "ta": int(row["TA"]),
                        "ti": int(row["TI"]),
                        "ti_rest": int(row["TI"]),
                        "tam": int(row["TAM(Kb)"]),
                        "est": "-",
                    }
                )
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta_csv}'.")
        return None
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return None

    # Se permiten como máximo MAX_PROCESOS procesos por simulación.
    if len(procesos) > MAX_PROCESOS:
        ignorados = ", ".join(f"P{p['id']}" for p in procesos[MAX_PROCESOS:])
        print(
            f"\nAviso: el archivo tiene {len(procesos)} procesos y solo se permiten "
            f"{MAX_PROCESOS} por simulación. Se ignoran: {ignorados}."
        )
        procesos = procesos[:MAX_PROCESOS]

    # Un proceso que no entra en la memoria de usuario nunca podría ejecutarse
    # (quedaría suspendido para siempre), y con TI <= 0 la simulación no terminaría.
    validos = []
    for p in procesos:
        if p["tam"] > MEMORIA_USUARIO:
            print(
                f"\nAviso: P{p['id']} pide {p['tam']}K y la memoria para procesos es de "
                f"{MEMORIA_USUARIO}K, nunca podría cargarse. Se descarta de la simulación."
            )
        elif p["ti"] <= 0 or p["tam"] <= 0 or p["ta"] < 0:
            print(
                f"\nAviso: P{p['id']} tiene datos inválidos (se requiere TA >= 0, TI > 0 y "
                f"TAM > 0). Se descarta de la simulación."
            )
        else:
            validos.append(p)

    if not validos:
        print("\nNo hay procesos válidos para simular.")
        return None
    return validos

def redondear(valor, decimales):
    """Redondea como se hace a mano (0.5 hacia arriba); format() redondea los empates hacia el par."""
    return Decimal(valor).quantize(Decimal(1).scaleb(-decimales), rounding=ROUND_HALF_UP)

def mostrar_informe_estadistico(procesos, tiempo_total):
    """Muestra el informe estadístico con tiempos de retorno, espera y rendimiento."""
    print("\n" + "=" * 80)
    print(" INFORME ESTADÍSTICO FINAL DE LA SIMULACIÓN")
    print("=" * 80)

    print(f"{'ID':<5} | {'TA':<5} | {'TI':<5} | {'T. FIN':<8} | {'T. RETORNO':<12} | {'T. ESPERA':<10}")
    print("-" * 80)

    sum_retorno = 0
    sum_espera = 0

    for p in procesos:
        ret = p["retorno"]
        esp = p["espera"]
        sum_retorno += ret
        sum_espera += esp
        print(f"{p['id']:<5} | {p['ta']:<5} | {p['ti']:<5} | {p['tiempo_fin']:<8} | {ret:<12} | {esp:<10}")

    cant = len(procesos)
    prom_retorno = Decimal(sum_retorno) / Decimal(cant)
    prom_espera = Decimal(sum_espera) / Decimal(cant)
    rendimiento = Decimal(cant) / Decimal(tiempo_total) if tiempo_total > 0 else Decimal(0)

    print("-" * 80)
    print(f"Tiempo promedio de Retorno: {redondear(prom_retorno, 2)} unidades de tiempo")
    print(f"Tiempo promedio de Espera : {redondear(prom_espera, 2)} unidades de tiempo")
    print(f"Rendimiento del sistema   : {redondear(rendimiento, 4)} trabajos/unidad de tiempo")
    print("=" * 80 + "\n")

def contar_en_sistema(proceso_en_ejecucion, cola_listos, cola_listos_suspendidos):
    """Procesos en Ejecución + Listos + Listos y Suspendidos (tope: MAX_EN_SISTEMA)."""
    return (
        (1 if proceso_en_ejecucion else 0)
        + len(cola_listos)
        + len(cola_listos_suspendidos)
    )

def simular_srtf_y_memoria(procesos, ruta_csv):
    memoria = GestorMemoria(tam_total=MEMORIA_USUARIO, dir_inicio=MEMORIA_SO)

    # Procesos que todavía no arribaron (el orden es estable: a igual TA se respeta el del archivo)
    cola_por_arribar = sorted(procesos, key=lambda x: x["ta"])
    # Procesos que ya arribaron pero no fueron admitidos porque el sistema está completo
    cola_nuevos = []

    cola_listos = []
    cola_listos_suspendidos = []
    proceso_en_ejecucion = None
    mensaje_fin_pendiente = None

    tiempo_actual = 0
    procesos_completados = 0
    total_procesos = len(procesos)

    imprimir_leyendas_globales()
    print(f"\n========== INICIANDO SIMULACIÓN DESDE '{ruta_csv}' ==========")

    while procesos_completados < total_procesos:
        hubo_evento = False
        mensajes_evento = []

        # Si un proceso finalizó al cierre del instante anterior, su evento
        # pertenece a este mismo instante y se muestra junto con los demás.
        msg_fin_instante = mensaje_fin_pendiente
        mensaje_fin_pendiente = None
        if msg_fin_instante:
            hubo_evento = True

        # 1) Todo proceso que arriba queda primero en estado Nuevo (N).
        arribos_hoy = [p for p in cola_por_arribar if p["ta"] == tiempo_actual]
        for p in arribos_hoy:
            cola_por_arribar.remove(p)
            p["est"] = "N"
            cola_nuevos.append(p)

        # 2) Los Listos y Suspendidos ya forman parte del sistema, así que tienen
        #    prioridad sobre los Nuevos para ocupar la memoria que haya disponible.
        i = 0
        while i < len(cola_listos_suspendidos):
            p_susp = cola_listos_suspendidos[i]

            if memoria.asignar_best_fit(p_susp["id"], p_susp["tam"]):
                cola_listos_suspendidos.pop(i)
                p_susp["est"] = "L"
                cola_listos.append(p_susp)
                mensajes_evento.append(f"Activación de P{p_susp['id']}: Pasa a Memoria -> Cola de Listos (L)")
                hubo_evento = True
            else:
                i += 1

        # 3) Admisión de los Nuevos (por orden de llegada) mientras haya lugar:
        #    Ejecución + Listos + Listos y Suspendidos nunca puede superar MAX_EN_SISTEMA.
        while cola_nuevos and contar_en_sistema(
            proceso_en_ejecucion, cola_listos, cola_listos_suspendidos
        ) < MAX_EN_SISTEMA:
            p = cola_nuevos.pop(0)
            origen = "Arribo" if p["ta"] == tiempo_actual else "Admisión"

            if memoria.asignar_best_fit(p["id"], p["tam"]):
                p["est"] = "L"
                cola_listos.append(p)
                mensajes_evento.append(f"{origen} de P{p['id']}: Asignado a Memoria -> Cola de Listos (L)")
            else:
                p["est"] = "S"
                cola_listos_suspendidos.append(p)
                mensajes_evento.append(f"{origen} de P{p['id']}: Sin memoria -> Cola de Listos/Suspendidos (S)")

            hubo_evento = True

        # Los que arribaron en este instante y no pudieron ser admitidos siguen en Nuevo.
        for p in arribos_hoy:
            if p["est"] == "N":
                mensajes_evento.append(
                    f"Arribo de P{p['id']}: Sistema completo ({MAX_EN_SISTEMA} procesos) -> queda en estado Nuevo (N)"
                )
                hubo_evento = True

        # 4) Planificación SRTF: solo compiten los procesos que están en memoria (Listos).
        #    El proceso en ejecución solo es desplazado si otro tiene un tiempo restante
        #    estrictamente menor (en un empate no hay cambio de contexto).
        if cola_listos:
            siguiente_cpu = min(
                cola_listos, key=lambda x: (x["ti_rest"], x["ta"], x["id"])
            )

            if proceso_en_ejecucion is None:
                proceso_en_ejecucion = siguiente_cpu
                cola_listos.remove(siguiente_cpu)
                proceso_en_ejecucion["est"] = "E"
                mensajes_evento.append(f"CPU asignada a P{proceso_en_ejecucion['id']} (E)")
                hubo_evento = True
            elif siguiente_cpu["ti_rest"] < proceso_en_ejecucion["ti_rest"]:
                proceso_anterior = proceso_en_ejecucion
                proceso_anterior["est"] = "L"
                cola_listos.append(proceso_anterior)

                proceso_en_ejecucion = siguiente_cpu
                cola_listos.remove(siguiente_cpu)
                proceso_en_ejecucion["est"] = "E"

                mensajes_evento.append(f"Apropiación SRTF: P{siguiente_cpu['id']} desplaza a P{proceso_anterior['id']} en CPU")
                hubo_evento = True

        if hubo_evento:
            msg_unificado = " | ".join(mensajes_evento)
            if msg_fin_instante:
                if msg_unificado:
                    msg_unificado = msg_fin_instante + "\n" + msg_unificado
                else:
                    msg_unificado = msg_fin_instante
            mostrar_tablas_evento(
                tiempo_actual,
                msg_unificado,
                procesos,
                memoria.obtener_tabla_memoria_salida(),
                plural=bool(msg_fin_instante) and bool(mensajes_evento) or len(mensajes_evento) > 1,
            )

        tiempo_actual += 1

        if proceso_en_ejecucion:
            proceso_en_ejecucion["ti_rest"] -= 1

            if proceso_en_ejecucion["ti_rest"] == 0:
                proceso_en_ejecucion["est"] = "F"
                proceso_en_ejecucion["tiempo_fin"] = tiempo_actual
                proceso_en_ejecucion["retorno"] = tiempo_actual - proceso_en_ejecucion["ta"]
                proceso_en_ejecucion["espera"] = proceso_en_ejecucion["retorno"] - proceso_en_ejecucion["ti"]

                memoria.liberar_memoria(proceso_en_ejecucion["id"])
                procesos_completados += 1

                mensaje_fin_pendiente = f"Proceso P{proceso_en_ejecucion['id']} FINALIZÓ (F) -> Memoria Liberada"
                proceso_en_ejecucion = None

    # Si el último proceso finalizó, no hay otra iteración que lo muestre.
    if mensaje_fin_pendiente:
        mostrar_tablas_evento(
            tiempo_actual,
            mensaje_fin_pendiente,
            procesos,
            memoria.obtener_tabla_memoria_salida(),
        )

    mostrar_informe_estadistico(procesos, tiempo_actual)

def ejecutar_simulacion(ruta_csv):
    """Carga los procesos del archivo CSV e inicia el motor de simulación."""
    procesos = cargar_procesos_desde_csv(ruta_csv)
    if not procesos:
        return

    simular_srtf_y_memoria(procesos, ruta_csv)

def ejecutar_procesos_defecto():
    """Ejecuta la simulación utilizando el archivo por defecto."""
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_csv = os.path.join(ruta_base, "procesos_defecto.csv")
    ejecutar_simulacion(ruta_csv)

def cargar_archivo_csv():
    """Muestra los CSV disponibles en la carpeta raíz y permite elegir uno por número."""
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    csv_disponibles = []

    for nombre in sorted(os.listdir(ruta_base)):
        if nombre.lower().endswith(".csv") and nombre != "procesos_defecto.csv":
            csv_disponibles.append(nombre)

    if not csv_disponibles:
        print("\nNo se encontraron archivos .csv adicionales en la carpeta raíz del proyecto.")
        print("Puede agregar un archivo CSV nuevo en la misma carpeta y volver a intentarlo.")
        return

    print("\nIngresar el número del .csv que desea ejecutar")
    for i, nombre in enumerate(csv_disponibles, start=1):
        print(f"{i}) {nombre}")

    while True:
        opcion_csv = input("\nSeleccione un archivo (1-{}): ".format(len(csv_disponibles))).strip()

        if opcion_csv.lower() in {"", "salir", "cancelar"}:
            print("\nSelección cancelada.")
            return

        try:
            indice = int(opcion_csv) - 1
        except ValueError:
            print("Entrada inválida. Debe ingresar un número válido.")
            continue

        if 0 <= indice < len(csv_disponibles):
            ruta = os.path.join(ruta_base, csv_disponibles[indice])
            ejecutar_simulacion(ruta)
            return

        print(f"Número fuera de rango. Debe elegir entre 1 y {len(csv_disponibles)}.")

def mostrar_menu():
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
    input("\nPresione Enter para salir...")