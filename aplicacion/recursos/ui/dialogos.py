from PySide6.QtWidgets import QMessageBox


class Dialogos:

    @staticmethod
    def informacion(parent, mensaje, titulo="Información"):

        QMessageBox.information(
            parent,
            titulo,
            mensaje
        )

    @staticmethod
    def error(parent, mensaje, titulo="Error"):

        QMessageBox.warning(
            parent,
            titulo,
            mensaje
        )

    @staticmethod
    def confirmacion(
        parent,
        mensaje,
        titulo="Confirmación"
    ):

        respuesta = QMessageBox.question(
            parent,
            titulo,
            mensaje,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        return respuesta == QMessageBox.Yes

    @staticmethod
    def advertencia(parent, mensaje, titulo="Advertencia"):

        QMessageBox.warning(
            parent,
            titulo,
            mensaje
        )

    @staticmethod
    def critica(parent, mensaje, titulo="Error crítico"):

        QMessageBox.critical(
            parent,
            titulo,
            mensaje
        )