def ejecutar_procesos_defecto():
    """Función para ejecutar los procesos cargados por defecto."""
    pass


def cargar_archivo_csv():
    """Función para cargar el archivo .csv con los procesos."""
    pass


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

        opcion = input("Seleccione una opción (1-3): ").strip()

        if opcion == "1":
            print("\n-> Seleccionó: Ejecutar procesos por defecto.")
            ejecutar_procesos_defecto()
        elif opcion == "2":
            print("\n-> Seleccionó: Cargar archivo .csv.")
            cargar_archivo_csv()
        elif opcion == "3":
            print("\nSaliendo del simulador... ¡Hasta luego!")
            break
        else:
            print("\nOpción inválida. Por favor, intente de nuevo.")


if __name__ == "__main__":
    mostrar_menu()
    