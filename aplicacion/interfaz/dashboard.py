from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)

from aplicacion.interfaz.barra_superior import BarraSuperior
from aplicacion.interfaz.barra_lateral import BarraLateral
from aplicacion.interfaz.panel_principal import PanelPrincipal


class Dashboard(QMainWindow):

    def __init__(self, usuario):
        super().__init__()

        self.setWindowTitle("ERP NEXUS")
        self.resize(1400, 800)

        contenedor = QWidget()

        layout_principal = QVBoxLayout()

        layout_principal.addWidget(
            BarraSuperior(usuario)
        )

        contenido = QHBoxLayout()

        contenido.addWidget(
            BarraLateral(),
            1
        )

        contenido.addWidget(
            PanelPrincipal(usuario),
            4
        )

        layout_principal.addLayout(contenido)

        contenedor.setLayout(layout_principal)

        self.setCentralWidget(contenedor)