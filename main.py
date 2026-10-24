import sys

from PySide6.QtWidgets import QApplication

from aplicacion.base_datos.registro_modelos import (
    importar_modelos,
)
from aplicacion.interfaz.ventana_principal import VentanaPrincipal
from aplicacion.recursos.estilos.tema import aplicar_tema

# Registro único de modelos ORM (misma fuente que startup y Alembic).
importar_modelos()


def _instalar_manejo_errores() -> None:
    """
    Un error inesperado en un botón ya no cierra el programa: se
    guarda en logs/errores.log, se muestra en la consola y se avisa
    con un mensaje.
    """

    import traceback
    from datetime import datetime
    from pathlib import Path

    def manejar(tipo, valor, rastro):

        texto = "".join(
            traceback.format_exception(
                tipo,
                valor,
                rastro,
            ),
        )

        print(
            texto,
            file=sys.stderr,
        )

        try:

            carpeta = Path(__file__).resolve().parent / "logs"

            carpeta.mkdir(
                exist_ok=True,
            )

            with open(
                carpeta / "errores.log",
                "a",
                encoding="utf-8",
            ) as archivo:

                archivo.write(
                    f"\n=== {datetime.now():%Y-%m-%d %H:%M:%S} ===\n{texto}",
                )

        except OSError:

            pass

        try:

            from PySide6.QtWidgets import QMessageBox

            if QApplication.instance() is not None:

                QMessageBox.warning(
                    None,
                    "Error inesperado",
                    "Ocurrió un error, pero puede seguir trabajando.\n\n"
                    f"{tipo.__name__}: {valor}\n\n"
                    "El detalle quedó en logs/errores.log.",
                )

        except Exception:

            pass

    sys.excepthook = manejar


def crear_aplicacion():

    app = QApplication(
        sys.argv,
    )

    aplicar_tema(
        app,
    )

    return app


def main():

    _instalar_manejo_errores()

    app = crear_aplicacion()

    ventana = VentanaPrincipal()

    ventana.show()

    sys.exit(
        app.exec(),
    )


if __name__ == "__main__":

    main()
