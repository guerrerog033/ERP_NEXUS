from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QFrame,
)


class Dialog(QDialog):

    def __init__(
        self,
        titulo="",
        ancho=700,
        alto=500,
        parent=None
    ):

        super().__init__(parent)

        self.setModal(True)

        self.resize(
            ancho,
            alto
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            25,
            20,
            25,
            20
        )

        layout.setSpacing(15)

        if titulo:

            lbl = QLabel(titulo)

            lbl.setObjectName(
                "tituloDialogo"
            )

            layout.addWidget(lbl)

            linea = QFrame()

            linea.setFrameShape(
                QFrame.HLine
            )

            layout.addWidget(linea)

        self.contenido = QVBoxLayout()

        self.contenido.setSpacing(15)

        layout.addLayout(
            self.contenido,
            1
        )

        self.setStyleSheet("""

        QDialog{

            background:white;

        }

        QLabel#tituloDialogo{

            font-size:22px;

            font-weight:bold;

            color:#1F2937;

        }

        """)

    def setContenido(
        self,
        layout
    ):

        self.contenido.addLayout(
            layout
        )