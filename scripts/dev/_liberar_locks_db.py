from aplicacion.base_datos.locks import liberar_locks_terceros
from aplicacion.base_datos.migraciones import ejecutar_migraciones

if __name__ == "__main__":

    liberar_locks_terceros()
    ejecutar_migraciones()
    print("Listo.")
