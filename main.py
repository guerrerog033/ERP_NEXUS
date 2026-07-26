import sys

from PySide6.QtWidgets import QApplication

from aplicacion.interfaz.login import Login


def main():

    app = QApplication(sys.argv)

    ventana = Login()

    ventana.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()