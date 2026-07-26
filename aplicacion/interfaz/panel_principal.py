from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt


class PanelPrincipal(QWidget):
    def __init__(self, usuario):
        super().__init__()

        layout = QVBoxLayout()

        titulo = QLabel(f"Bienvenido, {usuario.nombre}")
        titulo.setAlignment(Qt.AlignCenter)

        titulo.setStyleSheet("""
            font-size:24px;
            font-weight:bold;
        """)

        layout.addWidget(titulo)

        self.setLayout(layout)