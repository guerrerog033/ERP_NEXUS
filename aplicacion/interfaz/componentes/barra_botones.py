from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
)


class BarraBotones(QWidget):

    nuevo = Signal()
    editar = Signal()
    eliminar = Signal()
    actualizar = Signal()

    def __init__(self):

        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.btn_nuevo = QPushButton("Nuevo")
        self.btn_editar = QPushButton("Editar")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_actualizar = QPushButton("Actualizar")

        layout.addWidget(self.btn_nuevo)
        layout.addWidget(self.btn_editar)
        layout.addWidget(self.btn_eliminar)
        layout.addWidget(self.btn_actualizar)
        layout.addStretch()

        self.setLayout(layout)

        self.btn_nuevo.clicked.connect(self.nuevo.emit)
        self.btn_editar.clicked.connect(self.editar.emit)
        self.btn_eliminar.clicked.connect(self.eliminar.emit)
        self.btn_actualizar.clicked.connect(self.actualizar.emit)