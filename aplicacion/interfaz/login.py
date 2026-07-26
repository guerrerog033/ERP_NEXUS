from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QComboBox,
    QCheckBox,
)


class Login(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ERP NEXUS")
        self.resize(450, 400)

        layout = QVBoxLayout()

        titulo = QLabel("ERP NEXUS")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.empresa = QComboBox()
        self.empresa.addItem("Seleccione una empresa")

        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("Usuario")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Contraseña")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.recordar = QCheckBox("Recordar usuario")

        self.boton = QPushButton("Iniciar sesión")

        layout.addWidget(titulo)
        layout.addWidget(self.empresa)
        layout.addWidget(self.usuario)
        layout.addWidget(self.password)
        layout.addWidget(self.recordar)
        layout.addWidget(self.boton)

        self.setLayout(layout)