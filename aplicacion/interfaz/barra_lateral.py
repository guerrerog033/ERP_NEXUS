from PySide6.QtWidgets import QListWidget


class BarraLateral(QListWidget):

    def __init__(self):
        super().__init__()

        self.addItems([
            "Dashboard",
            "Ventas",
            "Compras",
            "Inventario",
            "Contabilidad",
            "Tesorería",
            "Bancos",
            "CRM",
            "Nómina",
            "Reportes",
            "Configuración",
        ])