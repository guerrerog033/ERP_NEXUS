import sys

from PySide6.QtWidgets import QApplication

from aplicacion.base_datos.registro_modelos import (
    importar_modelos,
)
from aplicacion.interfaz.ventana_principal import VentanaPrincipal
from aplicacion.recursos.estilos.tema import aplicar_tema

# Registro único de modelos ORM (misma fuente que startup y Alembic).
importar_modelos()


def crear_aplicacion():

    app = QApplication(
        sys.argv,
    )

    aplicar_tema(
        app,
    )

    return app


def main():

    app = crear_aplicacion()

    ventana = VentanaPrincipal()

    ventana.show()

    sys.exit(
        app.exec(),
    )


if __name__ == "__main__":

    main()
