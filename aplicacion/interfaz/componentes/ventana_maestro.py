from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout
)

from PySide6.QtCore import Qt


class VentanaMaestro(QWidget):

    def __init__(self, titulo):

        super().__init__()

        self.setWindowTitle(f"ERP NEXUS - {titulo}")

        self.resize(1200, 700)

        self.layout_principal = QVBoxLayout()

        self.layout_principal.setContentsMargins(
            25,
            20,
            25,
            20
        )

        self.layout_principal.setSpacing(15)

        self.lbl_titulo = QLabel(titulo)

        self.lbl_titulo.setAlignment(Qt.AlignCenter)

        self.lbl_titulo.setStyleSheet("""
            font-size:26px;
            font-weight:bold;
        """)

        self.layout_principal.addWidget(
            self.lbl_titulo
        )

        self.setLayout(
            self.layout_principal
        )