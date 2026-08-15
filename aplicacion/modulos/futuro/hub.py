from __future__ import annotations

from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)


class HubModulosFuturos(QWidget):

    titulo = "Módulos futuros"

    MODULOS = (
        ("Producción", "Planificación y órdenes de producción."),
        ("Manufactura", "BOM, rutas y consumo de materiales."),
        ("Confección", "Tallas, colores y órdenes de corte."),
        ("Talleres", "Órdenes de servicio y mano de obra."),
        ("E-commerce", "Catálogo web y checkout."),
        ("Comercio móvil", "App móvil de ventas."),
        ("Portal clientes", "Consulta pedidos y pagos."),
        ("Portal proveedores", "Estado de facturas y pagos."),
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel(
                "Arquitectura preparada. Estos módulos "
                "se activan por edición/licencia y API REST.",
            )
        )

        for nombre, descripcion in self.MODULOS:
            layout.addWidget(
                QLabel(
                    f"<b>{nombre}</b>: {descripcion}",
                )
            )

        layout.addStretch()
