from PySide6.QtWidgets import QMainWindow


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ERP NEXUS")
        self.resize(1200, 700)