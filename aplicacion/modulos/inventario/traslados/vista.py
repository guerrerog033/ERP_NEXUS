from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
)

from aplicacion.framework.base.page import Page

from aplicacion.modulos.inventario.bodegas.servicios import (
    ServicioBodega,
)
from aplicacion.modulos.inventario.servicios import (
    ServicioInventario,
)
from aplicacion.modulos.inventario.widgets.selector_producto import (
    SelectorProducto,
)


class TrasladosInventarioPage(Page):

    titulo = "Traslados"

    def _crear_ui(self) -> None:

        super()._crear_ui()

        self._construir()

    def _construir(self):

        layout = self.layout_principal

        form = QFormLayout()

        self.bodega_origen = QComboBox()
        self.bodega_destino = QComboBox()

        for bodega in ServicioBodega.listar_activas():

            texto = (
                f"{bodega.codigo} - {bodega.nombre}"
            )

            self.bodega_origen.addItem(
                texto,
                bodega.id,
            )

            self.bodega_destino.addItem(
                texto,
                bodega.id,
            )

        form.addRow(
            "Bodega origen:",
            self.bodega_origen,
        )

        form.addRow(
            "Bodega destino:",
            self.bodega_destino,
        )

        self.producto = SelectorProducto(
            self,
        )

        self.producto.seleccionado.connect(
            self._producto_seleccionado,
        )

        form.addRow(
            "Producto:",
            self.producto,
        )

        self.cantidad = QDoubleSpinBox()

        self.cantidad.setMinimum(0.01)
        self.cantidad.setMaximum(
            999999999,
        )

        self.cantidad.setDecimals(2)

        form.addRow(
            "Cantidad:",
            self.cantidad,
        )

        self.fecha = QDateEdit()

        self.fecha.setCalendarPopup(
            True,
        )

        self.fecha.setDate(
            QDate.currentDate(),
        )

        form.addRow(
            "Fecha:",
            self.fecha,
        )

        self.observaciones = QLineEdit()

        form.addRow(
            "Observaciones:",
            self.observaciones,
        )

        layout.addLayout(form)

        botones = QHBoxLayout()

        btn = QPushButton("Registrar traslado")

        btn.clicked.connect(
            self._guardar,
        )

        botones.addWidget(btn)
        botones.addStretch()

        layout.addLayout(botones)
        layout.addStretch()

    def _producto_seleccionado(
        self,
        _resultado,
    ):

        self.cantidad.setFocus()

    def _limpiar_formulario(
        self,
    ):

        self.observaciones.clear()
        self.cantidad.setValue(0.01)

    def _guardar(self):

        origen = self.bodega_origen.currentData()
        destino = self.bodega_destino.currentData()

        if origen is None or destino is None:

            QMessageBox.warning(
                self,
                "Traslados",
                "Seleccione bodegas válidas.",
            )

            return

        if self.producto.producto_id is None:

            QMessageBox.warning(
                self,
                "Traslados",
                "Seleccione un producto.",
            )

            return

        try:

            ServicioInventario.registrar_traslado(
                bodega_origen_id=origen,
                bodega_destino_id=destino,
                producto_id=self.producto.producto_id,
                producto_variante_id=(
                    self.producto.producto_variante_id
                ),
                cantidad=self.cantidad.value(),
                fecha=self.fecha.date().toPython(),
                observaciones=self.observaciones.text(),
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Traslados",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Traslados",
            "Traslado registrado correctamente.",
        )

        self._limpiar_formulario()
        self.cantidad.setFocus()
