from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout


class BarraSuperior(QWidget):

    def __init__(self, usuario):
        super().__init__()

        layout = QHBoxLayout()

        titulo = QLabel("ERP NEXUS")

        usuario_lbl = QLabel(
            f"Usuario: {usuario.nombre}"
        )

        layout.addWidget(titulo)

        layout.addStretch()

        layout.addWidget(usuario_lbl)

        self.setLayout(layout)