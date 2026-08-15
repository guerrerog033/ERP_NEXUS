from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)


class BarraBusqueda(QWidget):

    buscar = Signal(str)
    limpiar = Signal()

    def __init__(self):

        super().__init__()

        layout = QHBoxLayout()

        layout.setContentsMargins(0, 0, 0, 0)

        self.txt_busqueda = QLineEdit()

        self.txt_busqueda.setPlaceholderText(
            "Buscar..."
        )

        self.btn_buscar = QPushButton("Buscar")
        self.btn_limpiar = QPushButton("Limpiar")

        layout.addWidget(self.txt_busqueda)
        layout.addWidget(self.btn_buscar)
        layout.addWidget(self.btn_limpiar)

        self.setLayout(layout)

        self.btn_buscar.clicked.connect(
            self.emitir_busqueda
        )

        self.btn_limpiar.clicked.connect(
            self.limpiar_busqueda
        )

        self.txt_busqueda.returnPressed.connect(
            self.emitir_busqueda
        )

    def emitir_busqueda(self):

        self.buscar.emit(
            self.txt_busqueda.text().strip()
        )

    def limpiar_busqueda(self):

        self.txt_busqueda.clear()

        self.limpiar.emit()