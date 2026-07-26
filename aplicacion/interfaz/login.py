from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
)

from aplicacion.autenticacion.servicios import autenticar
from aplicacion.interfaz.dashboard import Dashboard


class Login(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ERP NEXUS - Inicio de sesión")
        self.resize(350, 220)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Usuario"))

        self.txt_usuario = QLineEdit()
        layout.addWidget(self.txt_usuario)

        layout.addWidget(QLabel("Contraseña"))

        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.txt_password)

        self.btn_login = QPushButton("Iniciar sesión")
        self.btn_login.clicked.connect(self.iniciar_sesion)
        layout.addWidget(self.btn_login)

        self.setLayout(layout)

      def iniciar_sesion(self):

        usuario = self.txt_usuario.text().strip()
        password = self.txt_password.text()

        resultado = autenticar(usuario, password)

        if resultado:
            self.dashboard = Dashboard(resultado)
            self.dashboard.show()
            self.close()

        else:
            QMessageBox.warning(
                self,
                "Error",
                "Usuario o contraseña incorrectos."
            )