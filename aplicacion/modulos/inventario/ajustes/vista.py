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

        self.lote_serie = QComboBox()

        self.lote_serie.setEditable(
            True,
        )

        self.lote_serie.setInsertPolicy(
            QComboBox.InsertPolicy.NoInsert,
        )

        form.addRow(
            "Lote/Serie:",
            self.lote_serie,
        )

        self._etiqueta_lote_serie = form.labelForField(
            self.lote_serie,
        )

        self._etiqueta_lote_serie.hide()

        self.lote_serie.hide()

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

        self._actualizar_lote_serie()

        self.cantidad.setFocus()

    def _actualizar_lote_serie(
        self,
    ) -> None:

        from aplicacion.maestros.productos.servicios import (
            ServicioProducto,
        )
        from aplicacion.modulos.inventario.lote_serie_servicio import (
            ServicioLoteSerie,
        )

        self.lote_serie.clear()

        producto_id = self.producto.producto_id

        producto = (
            ServicioProducto.obtener_por_id(
                producto_id,
            )
            if producto_id
            else None
        )

        requiere_lote_serie = bool(
            producto
            and (
                producto.maneja_lote
                or producto.maneja_serie
            )
        )

        self._etiqueta_lote_serie.setVisible(
            requiere_lote_serie,
        )

        self.lote_serie.setVisible(
            requiere_lote_serie,
        )

        if not requiere_lote_serie:

            return

        for registro in ServicioLoteSerie.listar(
            producto_id,
        ):

            self.lote_serie.addItem(
                registro.numero,
                registro.id,
            )

        self.lote_serie.setCurrentIndex(
            -1,
        )

        self.lote_serie.setEditText(
            "",
        )

    def _limpiar_formulario(
        self,
        *,
        mantener_producto: bool = True,
    ):

        self.observaciones.clear()
        self.cantidad.setValue(0.01)

        if mantener_producto:

            self._actualizar_lote_serie()

        else:

            self.producto.establecer(
                None,
            )

            self._etiqueta_lote_serie.hide()

            self.lote_serie.clear()

            self.lote_serie.hide()

            self.costo.setValue(0)

    def _resolver_lote_serie(
        self,
    ) -> int | None:
        """
        None si el producto no maneja lote/serie. Si el usuario
        eligió uno existente del combo, su id. Si escribió un
        número nuevo (no está en la lista), lo crea antes de
        registrar el movimiento — flujo típico de una entrada de
        un lote que aún no existía en el sistema.
        """

        if self.lote_serie.isHidden():

            return None

        indice = self.lote_serie.currentIndex()

        if indice >= 0:

            return self.lote_serie.currentData()

        numero = self.lote_serie.currentText().strip()

        if not numero:

            raise ValueError(
                "Este producto controla existencia por lote o "
                "número de serie: indique cuál.",
            )

        from aplicacion.modulos.inventario.lote_serie_servicio import (
            ServicioLoteSerie,
        )

        nuevo = ServicioLoteSerie.guardar(
            {
                "producto_id": self.producto.producto_id,
                "numero": numero,
            },
        )

        return nuevo.id

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

            lote_serie_id = self._resolver_lote_serie()

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Ajustes",
                str(error),
            )

            return

        try:

            ServicioInventario.registrar_ajuste(
                bodega_id=self.bodega.currentData(),
                producto_id=self.producto.producto_id,
                producto_variante_id=(
                    self.producto.producto_variante_id
                ),
                lote_serie_id=lote_serie_id,
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
