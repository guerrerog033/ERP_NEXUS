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


class AjustesInventarioPage(Page):

    titulo = "Ajustes de inventario"

    def _crear_ui(self) -> None:

        super()._crear_ui()

        self._construir()

    def _construir(self):

        layout = self.layout_principal

        form = QFormLayout()

        self.bodega = QComboBox()

        for bodega in ServicioBodega.listar_activas():

            self.bodega.addItem(
                f"{bodega.codigo} - {bodega.nombre}",
                bodega.id,
            )

        form.addRow(
            "Bodega:",
            self.bodega,
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

        self.tipo = QComboBox()

        self.tipo.addItem(
            "Entrada",
            "entrada",
        )

        self.tipo.addItem(
            "Salida",
            "salida",
        )

        form.addRow(
            "Tipo:",
            self.tipo,
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

        self.costo = QDoubleSpinBox()

        self.costo.setMinimum(0)
        self.costo.setMaximum(
            999999999,
        )

        self.costo.setDecimals(2)

        form.addRow(
            "Costo unitario:",
            self.costo,
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

        btn = QPushButton("Registrar ajuste")

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

        costo = self.producto.costo_sugerido()

        if costo > 0:

            self.costo.setValue(
                costo,
            )

        self.cantidad.setFocus()

    def _limpiar_formulario(
        self,
        *,
        mantener_producto: bool = True,
    ):

        self.observaciones.clear()
        self.cantidad.setValue(0.01)

        if not mantener_producto:

            self.producto.establecer(
                None,
            )

            self.costo.setValue(0)

    def _guardar(self):

        if self.bodega.currentData() is None:

            QMessageBox.warning(
                self,
                "Ajustes",
                "Seleccione una bodega.",
            )

            return

        if self.producto.producto_id is None:

            QMessageBox.warning(
                self,
                "Ajustes",
                "Seleccione un producto.",
            )

            return

        try:

            ServicioInventario.registrar_ajuste(
                bodega_id=self.bodega.currentData(),
                producto_id=self.producto.producto_id,
                producto_variante_id=(
                    self.producto.producto_variante_id
                ),
                tipo=self.tipo.currentData(),
                cantidad=self.cantidad.value(),
                costo_unitario=self.costo.value(),
                fecha=self.fecha.date().toPython(),
                observaciones=self.observaciones.text(),
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Ajustes",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Ajustes",
            "Ajuste registrado correctamente.",
        )

        self._limpiar_formulario()
        self.cantidad.setFocus()
