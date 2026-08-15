from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from aplicacion.framework.lookup import LookupWidget
from aplicacion.framework.ui.card import Card
from aplicacion.maestros.terceros.cliente_lookup import (
    ClienteLookup,
)
from aplicacion.modulos.inventario.widgets.selector_producto import (
    SelectorProducto,
)
from aplicacion.modulos.ventas.pos.servicios import (
    ServicioPOSVenta,
)
from aplicacion.recursos.estilos.tema import habilitar_fondo_qss


COL_DESCRIPCION = 0
COL_CANTIDAD = 1
COL_PRECIO = 2
COL_TOTAL = 3
COL_BORRAR = 4


class POSVentaPage(QWidget):

    titulo = "Punto de venta"

    icono = "ventas"

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.setObjectName(
            "POSVentaPage",
        )

        habilitar_fondo_qss(
            self,
        )

        self._construir()

    def _construir(self):

        layout = QVBoxLayout(
            self,
        )

        layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )

        card = Card(
            "Venta rápida",
        )

        cabecera = QWidget()
        fila = QHBoxLayout(
            cabecera,
        )

        fila.addWidget(
            QLabel("Cliente:"),
        )

        self.cliente = LookupWidget(
            ClienteLookup(),
        )

        fila.addWidget(
            self.cliente,
            1,
        )

        card.contenido.addWidget(
            cabecera,
        )

        captura = QHBoxLayout()

        captura.addWidget(
            QLabel("Producto:"),
        )

        self.producto = SelectorProducto(
            self,
        )

        captura.addWidget(
            self.producto,
            1,
        )

        captura.addWidget(
            QLabel("Cantidad:"),
        )

        self.cantidad = QDoubleSpinBox()
        self.cantidad.setRange(
            0.01,
            99999,
        )
        self.cantidad.setValue(
            1,
        )

        captura.addWidget(
            self.cantidad,
        )

        btn_agregar = QPushButton(
            "Agregar",
        )
        btn_agregar.clicked.connect(
            self._agregar_producto,
        )

        captura.addWidget(
            btn_agregar,
        )

        card.contenido.addLayout(
            captura,
        )

        self.tabla = QTableWidget(
            0,
            5,
        )
        self.tabla.setHorizontalHeaderLabels(
            [
                "Producto",
                "Cantidad",
                "Precio",
                "Total",
                "",
            ],
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            COL_DESCRIPCION,
            QHeaderView.Stretch,
        )

        card.contenido.addWidget(
            self.tabla,
        )

        self.lbl_stock_alerta = QLabel(
            "",
        )
        self.lbl_stock_alerta.setWordWrap(
            True,
        )
        self.lbl_stock_alerta.setStyleSheet(
            "color:#B45309;font-weight:600;",
        )

        card.contenido.addWidget(
            self.lbl_stock_alerta,
        )

        pago = QHBoxLayout()

        pago.addWidget(
            QLabel("Pago:"),
        )

        self.metodo_pago = QComboBox()
        self.metodo_pago.addItem(
            "Efectivo",
            "efectivo",
        )
        self.metodo_pago.addItem(
            "Tarjeta",
            "tarjeta",
        )
        self.metodo_pago.addItem(
            "Transferencia",
            "transferencia",
        )
        self.metodo_pago.currentIndexChanged.connect(
            self._cambio_metodo_pago,
        )

        pago.addWidget(
            self.metodo_pago,
        )

        pago.addWidget(
            QLabel("Recibido:"),
        )

        self.recibido = QDoubleSpinBox()
        self.recibido.setRange(
            0,
            999999999,
        )
        self.recibido.setDecimals(
            0,
        )
        self.recibido.valueChanged.connect(
            self._actualizar_cambio,
        )

        pago.addWidget(
            self.recibido,
        )

        self.lbl_cambio = QLabel(
            "Cambio: $0",
        )
        self.lbl_cambio.setStyleSheet(
            "font-size:15px;font-weight:600;color:#065F46;",
        )

        pago.addWidget(
            self.lbl_cambio,
        )
        pago.addStretch()

        card.contenido.addLayout(
            pago,
        )

        self._total_venta = 0.0

        pie = QHBoxLayout()

        self.chk_emitir = QCheckBox(
            "Emitir FE DIAN al facturar",
        )

        self.chk_ticket = QCheckBox(
            "Imprimir ticket térmico",
        )
        self.chk_ticket.setChecked(
            True,
        )

        pie.addWidget(
            self.chk_emitir,
        )
        pie.addWidget(
            self.chk_ticket,
        )
        pie.addStretch()

        self.lbl_total = QLabel(
            "Total: $0",
        )
        self.lbl_total.setStyleSheet(
            "font-size:18px;font-weight:700;color:#1B4F8A;",
        )

        pie.addWidget(
            self.lbl_total,
        )

        btn_limpiar = QPushButton(
            "Limpiar",
        )
        btn_limpiar.clicked.connect(
            self._limpiar,
        )

        btn_facturar = QPushButton(
            "Facturar",
        )
        btn_facturar.setObjectName(
            "BotonPrimario",
        )
        btn_facturar.clicked.connect(
            self._facturar,
        )

        pie.addWidget(
            btn_limpiar,
        )
        pie.addWidget(
            btn_facturar,
        )

        card.contenido.addLayout(
            pie,
        )

        layout.addWidget(
            card,
        )

    def _agregar_producto(self):

        resultado = self.producto.resultado

        if resultado is None:

            QMessageBox.warning(
                self,
                "Punto de venta",
                "Seleccione un producto.",
            )

            return

        producto = resultado.objeto

        if producto is None:

            QMessageBox.warning(
                self,
                "Punto de venta",
                "No se pudo resolver el producto.",
            )

            return

        descripcion = str(
            resultado.texto
            or producto.nombre
            or "",
        )

        from aplicacion.maestros.productos.servicios import (
            ServicioProducto,
        )

        try:

            item = ServicioProducto.resolver_item(
                resultado.valor,
                resultado.producto_variante_id,
            )

        except ValueError:

            QMessageBox.warning(
                self,
                "Punto de venta",
                "No se pudo resolver el producto.",
            )

            return

        precio = float(
            item.get(
                "precio_venta",
            )
            or 0,
        )

        impuesto_id = item.get(
            "impuesto_venta_id",
        )

        if not impuesto_id:

            from aplicacion.maestros.impuestos.iva_catalogo import (
                id_iva_predeterminado,
            )

            impuesto_id = id_iva_predeterminado()

        precio_incluye_iva = bool(
            item.get(
                "precio_incluye_iva",
            ),
        )

        cantidad = float(
            self.cantidad.value(),
        )

        fila = self.tabla.rowCount()
        self.tabla.insertRow(
            fila,
        )

        item = QTableWidgetItem(
            descripcion,
        )
        item.setData(
            Qt.ItemDataRole.UserRole,
            {
                "producto_id": producto.id,
                "producto_variante_id": (
                    resultado.producto_variante_id
                ),
                "impuesto_id": impuesto_id,
                "precio_incluye_iva": precio_incluye_iva,
            },
        )

        self.tabla.setItem(
            fila,
            COL_DESCRIPCION,
            item,
        )

        self.tabla.setItem(
            fila,
            COL_CANTIDAD,
            QTableWidgetItem(
                f"{cantidad:.2f}",
            ),
        )

        self.tabla.setItem(
            fila,
            COL_PRECIO,
            QTableWidgetItem(
                f"{precio:,.0f}",
            ),
        )

        total_linea = cantidad * precio

        self.tabla.setItem(
            fila,
            COL_TOTAL,
            QTableWidgetItem(
                f"{total_linea:,.0f}",
            ),
        )

        btn = QPushButton("X")
        btn.clicked.connect(
            lambda: self._borrar_linea(
                btn,
            ),
        )
        self.tabla.setCellWidget(
            fila,
            COL_BORRAR,
            btn,
        )

        self._recalcular_total()

        self._actualizar_alertas_stock()

    def _actualizar_alertas_stock(
        self,
    ) -> None:

        lineas = self._lineas()

        if not lineas:

            self.lbl_stock_alerta.setText(
                "",
            )

            return

        bloqueantes, avisos = (
            ServicioPOSVenta.alertas_stock(
                lineas,
            )
        )

        mensajes = bloqueantes + avisos

        if mensajes:

            self.lbl_stock_alerta.setText(
                "\n".join(
                    mensajes,
                ),
            )

        else:

            self.lbl_stock_alerta.setText(
                "",
            )

    def _cambio_metodo_pago(
        self,
    ) -> None:

        es_efectivo = (
            self.metodo_pago.currentData()
            == "efectivo"
        )

        self.recibido.setEnabled(
            es_efectivo,
        )

        if not es_efectivo:

            self.recibido.setValue(
                self._total_venta,
            )

        self._actualizar_cambio()

    def _actualizar_cambio(
        self,
    ) -> None:

        recibido = float(
            self.recibido.value(),
        )

        cambio = max(
            0.0,
            recibido
            - self._total_venta,
        )

        self.lbl_cambio.setText(
            f"Cambio: ${cambio:,.0f}",
        )

    def _borrar_linea(
        self,
        boton,
    ):

        for fila in range(
            self.tabla.rowCount(),
        ):

            if (
                self.tabla.cellWidget(
                    fila,
                    COL_BORRAR,
                )
                is boton
            ):

                self.tabla.removeRow(
                    fila,
                )
                break

        self._recalcular_total()
        self._actualizar_alertas_stock()

    def _recalcular_total(self):

        total = 0.0

        for fila in range(
            self.tabla.rowCount(),
        ):

            cantidad = float(
                self.tabla.item(
                    fila,
                    COL_CANTIDAD,
                ).text(),
            )

            precio = float(
                self.tabla.item(
                    fila,
                    COL_PRECIO,
                ).text().replace(
                    ",",
                    "",
                )
            )

            total += cantidad * precio

        self._total_venta = total

        self.lbl_total.setText(
            f"Total: ${total:,.0f}",
        )

        if (
            self.metodo_pago.currentData()
            != "efectivo"
        ):

            self.recibido.setValue(
                total,
            )

        self._actualizar_cambio()

    def _lineas(self) -> list[dict]:

        lineas = []

        for fila in range(
            self.tabla.rowCount(),
        ):

            item = self.tabla.item(
                fila,
                COL_DESCRIPCION,
            )

            datos = item.data(
                Qt.ItemDataRole.UserRole,
            )

            cantidad = float(
                self.tabla.item(
                    fila,
                    COL_CANTIDAD,
                ).text(),
            )

            precio = float(
                self.tabla.item(
                    fila,
                    COL_PRECIO,
                ).text().replace(
                    ",",
                    "",
                )
            )

            lineas.append(
                {
                    "producto_id": datos.get(
                        "producto_id",
                    ),
                    "producto_variante_id": datos.get(
                        "producto_variante_id",
                    ),
                    "descripcion": item.text(),
                    "cantidad": cantidad,
                    "precio_unitario": precio,
                    "impuesto_id": datos.get(
                        "impuesto_id",
                    ),
                    "precio_incluye_iva": datos.get(
                        "precio_incluye_iva",
                        False,
                    ),
                    "total_linea": cantidad * precio,
                }
            )

        return lineas

    def _limpiar(self):

        self.tabla.setRowCount(
            0,
        )
        self.cliente.establecer(
            None,
        )
        self.producto.establecer(
            None,
        )
        self.cantidad.setValue(
            1,
        )
        self.metodo_pago.setCurrentIndex(
            0,
        )
        self.recibido.setValue(
            0,
        )
        self._total_venta = 0.0
        self._recalcular_total()
        self.lbl_stock_alerta.setText(
            "",
        )

    def _facturar(self):

        if (
            self.metodo_pago.currentData()
            == "efectivo"
            and self.recibido.value()
            < self._total_venta
        ):

            QMessageBox.warning(
                self,
                "Punto de venta",
                "El valor recibido debe cubrir el total.",
            )

            return

        lineas = self._lineas()

        bloqueantes, avisos = (
            ServicioPOSVenta.alertas_stock(
                lineas,
            )
        )

        if bloqueantes:

            QMessageBox.warning(
                self,
                "Punto de venta",
                "\n".join(
                    bloqueantes,
                ),
            )

            return

        if avisos:

            respuesta = QMessageBox.question(
                self,
                "Punto de venta",
                (
                    "Advertencias de stock:\n\n"
                    + "\n".join(
                        avisos,
                    )
                    + "\n\n¿Desea continuar con la venta?"
                ),
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
            )

            if (
                respuesta
                != QMessageBox.StandardButton.Yes
            ):

                return

        try:

            recibido = float(
                self.recibido.value(),
            )

            cambio = max(
                0.0,
                recibido
                - self._total_venta,
            )

            factura = ServicioPOSVenta.facturar(
                cliente_id=self.cliente.valor(),
                lineas=lineas,
                emitir_dian=self.chk_emitir.isChecked(),
                recibido=recibido,
                cambio=cambio,
                metodo_pago=str(
                    self.metodo_pago.currentData(),
                ),
                imprimir_ticket=self.chk_ticket.isChecked(),
                cliente_nombre=str(
                    getattr(
                        self.cliente.resultado,
                        "texto",
                        "",
                    )
                    or self.cliente.txt.text()
                    or "",
                ),
                parent=self,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Punto de venta",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Punto de venta",
            (
                f"Factura {factura.numero} creada "
                f"por ${float(factura.total or 0):,.0f}.\n"
                f"Cambio: ${cambio:,.0f}."
            ),
        )

        self._limpiar()
