from __future__ import annotations



from PySide6.QtCore import QDate, Qt, QTimer

from PySide6.QtGui import QKeySequence, QShortcut

from PySide6.QtWidgets import (

    QAbstractItemView,

    QComboBox,

    QDateEdit,

    QDialog,

    QDialogButtonBox,

    QDoubleSpinBox,

    QFormLayout,

    QHBoxLayout,

    QInputDialog,

    QLabel,

    QLineEdit,

    QMessageBox,

    QPushButton,

    QTableWidget,

    QTableWidgetItem,

    QVBoxLayout,

)



from aplicacion.framework.lookup import LookupWidget

from aplicacion.framework.ui.inquiry_page import InquiryPage

from aplicacion.maestros.terceros.proveedor_lookup import (

    ProveedorLookup,

)

from aplicacion.modulos.compras.ordenes.formatos_impresion import (
    formatos_combo,
)

from aplicacion.modulos.compras.ordenes.servicios import (

    ServicioOrdenCompra,

)

from aplicacion.modulos.ventas.cotizaciones.servicios import (
    ServicioCotizacion,
)

from aplicacion.modulos.compras.ordenes.impresion import (
    exportar_pdf_orden_compra,
    imprimir_orden_compra,
)

from aplicacion.modulos.inventario.widgets.selector_producto import (

    SelectorProducto,

)





class _DialogoOrdenCompra(QDialog):



    def __init__(

        self,

        parent=None,

    ):



        super().__init__(parent)



        self.setWindowTitle(

            "Nueva orden de compra",

        )



        self.resize(

            760,

            520,

        )



        self._lineas: list[dict] = []



        layout = QVBoxLayout(self)



        form = QFormLayout()



        self.proveedor = LookupWidget(

            ProveedorLookup(),

            self,

        )



        form.addRow(

            "Proveedor:",

            self.proveedor,

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



        self.formato = QComboBox()

        for etiqueta, codigo in formatos_combo():

            self.formato.addItem(
                etiqueta,
                codigo,
            )

        indice_formato = self.formato.findData(
            ServicioCotizacion.formato_predeterminado(),
        )

        if indice_formato >= 0:

            self.formato.setCurrentIndex(
                indice_formato,
            )

        form.addRow(

            "Formato de impresión:",

            self.formato,

        )



        layout.addLayout(form)



        captura = QHBoxLayout()



        self.producto = SelectorProducto(

            self,

        )



        self.cantidad = QDoubleSpinBox()



        self.cantidad.setMinimum(0.01)

        self.cantidad.setMaximum(

            999999999,

        )



        self.cantidad.setDecimals(2)

        self.cantidad.setValue(1)



        self.costo = QDoubleSpinBox()



        self.costo.setMinimum(0)

        self.costo.setMaximum(

            999999999,

        )



        self.costo.setDecimals(2)



        self.producto.seleccionado.connect(

            self._producto_seleccionado,

        )



        btn_agregar = QPushButton(

            "Agregar línea",

        )

        self.btn_agregar = btn_agregar



        btn_agregar.clicked.connect(

            self._agregar_linea,

        )



        captura.addWidget(

            QLabel("Producto:"),

        )



        captura.addWidget(

            self.producto,

            1,

        )



        captura.addWidget(

            QLabel("Cant:"),

        )



        captura.addWidget(

            self.cantidad,

        )



        captura.addWidget(

            QLabel("Costo:"),

        )



        captura.addWidget(

            self.costo,

        )



        captura.addWidget(

            btn_agregar,

        )



        layout.addLayout(captura)



        self.tabla = QTableWidget()



        self.tabla.setColumnCount(4)



        self.tabla.setHorizontalHeaderLabels(

            [

                "Producto",

                "Cantidad",

                "Costo",

                "Total",

            ],

        )



        # Las celdas son solo lectura: _lineas es la fuente de verdad
        # y editar la tabla no la actualizaba.
        self.tabla.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers,
        )
        self.tabla.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows,
        )
        self.tabla.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection,
        )



        layout.addWidget(

            self.tabla,

        )



        pie = QHBoxLayout()

        self.btn_quitar = QPushButton(
            "Quitar línea",
        )
        self.btn_quitar.setToolTip(
            "Quitar la línea seleccionada (Supr)",
        )
        self.btn_quitar.clicked.connect(
            self._quitar_linea,
        )

        QShortcut(
            QKeySequence(Qt.Key.Key_Delete),
            self.tabla,
            self._quitar_linea,
            context=Qt.ShortcutContext.WidgetShortcut,
        )

        self.lbl_total = QLabel()
        self.lbl_total.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter,
        )

        pie.addWidget(self.btn_quitar)
        pie.addStretch(1)
        pie.addWidget(self.lbl_total)

        layout.addLayout(pie)

        self._actualizar_total()



        botones = QDialogButtonBox(

            QDialogButtonBox.Save

            | QDialogButtonBox.Cancel,

        )



        botones.accepted.connect(

            self._guardar,

        )



        botones.rejected.connect(

            self.reject,

        )



        layout.addWidget(botones)



        # Enter en cant/costo avanza como una planilla (producto →
        # cant → costo → agregar); ver keyPressEvent.
        self.cantidad.lineEdit().returnPressed.connect(
            lambda: self._enfocar_spin(self.costo),
        )
        self.costo.lineEdit().returnPressed.connect(
            self._agregar_linea,
        )

        self._foco_inicial_aplicado = False



    def keyPressEvent(
        self,
        event,
    ):
        """
        QDialog convierte un Enter no consumido en un clic al botón
        por defecto, y QDialogButtonBox marca Guardar como tal al
        mostrarse: Enter en "Cant." guardaba la orden a medio
        capturar. Enter sobre un botón enfocado lo maneja el propio
        botón y no llega acá.
        """

        if event.key() in (
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
        ):

            event.accept()

            return

        super().keyPressEvent(event)



    def showEvent(
        self,
        event,
    ):

        super().showEvent(event)

        if not self._foco_inicial_aplicado:

            self._foco_inicial_aplicado = True

            QTimer.singleShot(
                0,
                self._aplicar_foco_inicial,
            )



    def _aplicar_foco_inicial(self) -> None:
        """
        Al abrir: si falta el proveedor, foco en su selector; si ya
        está, foco en el buscador de producto para empezar a cargar
        líneas.
        """

        if self.proveedor.valor() is None:

            self.proveedor.btn.setFocus()

            return

        self.producto.btn_buscar.setFocus()



    @staticmethod
    def _enfocar_spin(
        spin,
    ) -> None:

        spin.setFocus()
        spin.selectAll()



    def _actualizar_total(self) -> None:

        total = sum(
            linea["cantidad"] * linea["costo_unitario"]
            for linea in self._lineas
        )

        self.lbl_total.setText(
            f"{len(self._lineas)} línea(s) · "
            f"Total: <b>{total:,.2f}</b>",
        )

        self.btn_quitar.setEnabled(
            bool(self._lineas),
        )



    def _quitar_linea(self) -> None:

        fila = self.tabla.currentRow()

        if fila < 0 or fila >= len(self._lineas):

            return

        del self._lineas[fila]

        self.tabla.removeRow(fila)

        self._actualizar_total()

        if self._lineas:

            self.tabla.selectRow(
                min(fila, len(self._lineas) - 1),
            )

        else:

            self.producto.btn_buscar.setFocus()



    def _producto_seleccionado(

        self,

        _resultado,

    ):



        costo = self.producto.costo_sugerido()



        if costo > 0:



            self.costo.setValue(

                costo,

            )

        if self.producto.producto_id is not None:

            self._enfocar_spin(self.cantidad)



    def _agregar_linea(self):

        if self.producto.producto_id is None:

            # Enter en "Costo" dispara returnPressed dos veces para
            # una sola tecla (lo hace QAbstractSpinBox al validar su
            # texto): la primera agrega la línea y limpia el
            # producto, la segunda llega con el campo ya vacío. Sin
            # esta guarda, cada línea agregada con Enter mostraba
            # además "Seleccione un producto" de la nada.
            if getattr(
                self,
                "_linea_agregada_recientemente",
                False,
            ):

                return

            QMessageBox.warning(

                self,

                "Orden de compra",

                "Seleccione un producto.",

            )

            self.producto.btn_buscar.setFocus()



            return



        cantidad = self.cantidad.value()

        costo = self.costo.value()

        total = cantidad * costo



        descripcion = (

            self.producto.resultado.texto

            if self.producto.resultado

            else "Producto"

        )



        self._lineas.append(

            {

                "producto_id": self.producto.producto_id,

                "producto_variante_id": (

                    self.producto.producto_variante_id

                ),

                "descripcion": descripcion,

                "cantidad": cantidad,

                "costo_unitario": costo,

            },

        )



        fila = self.tabla.rowCount()



        self.tabla.insertRow(fila)



        self.tabla.setItem(

            fila,

            0,

            QTableWidgetItem(

                f"{self.producto.resultado.codigo} - {descripcion}",

            ),

        )



        self.tabla.setItem(

            fila,

            1,

            QTableWidgetItem(

                f"{cantidad:,.2f}",

            ),

        )



        self.tabla.setItem(

            fila,

            2,

            QTableWidgetItem(

                f"{costo:,.2f}",

            ),

        )



        self.tabla.setItem(

            fila,

            3,

            QTableWidgetItem(

                f"{total:,.2f}",

            ),

        )



        self.producto.establecer(None)

        self.cantidad.setValue(1)

        self.costo.setValue(0)

        self._linea_agregada_recientemente = True

        QTimer.singleShot(
            0,
            lambda: setattr(
                self,
                "_linea_agregada_recientemente",
                False,
            ),
        )

        self._actualizar_total()

        self.tabla.scrollToBottom()

        self.producto.btn_buscar.setFocus()



    def _guardar(self):



        proveedor_id = self.proveedor.valor()



        if proveedor_id is None:



            QMessageBox.warning(

                self,

                "Orden de compra",

                "Seleccione un proveedor.",

            )

            self.proveedor.btn.setFocus()



            return



        if self.producto.producto_id is not None:

            # Producto elegido en la captura pero nunca agregado:
            # guardar sin él lo perdería en silencio.
            QMessageBox.warning(
                self,
                "Orden de compra",
                "Hay un producto seleccionado que no se agregó. "
                "Use «Agregar línea» o límpielo antes de guardar.",
            )

            self.btn_agregar.setFocus()

            return



        if not self._lineas:

            QMessageBox.warning(
                self,
                "Orden de compra",
                "Agregue al menos una línea.",
            )

            self.producto.btn_buscar.setFocus()

            return



        try:



            ServicioOrdenCompra.guardar(

                proveedor_id=proveedor_id,

                fecha=self.fecha.date().toPython(),

                observaciones=self.observaciones.text(),

                lineas=self._lineas,

                formato_impresion=self.formato.currentData(),

            )



        except ValueError as error:



            QMessageBox.warning(

                self,

                "Orden de compra",

                str(error),

            )



            return



        self.accept()





class OrdenesCompraPage(InquiryPage):



    titulo = "Órdenes de compra"



    _NOMBRE_EXPORT = "ordenes_compra"

    _TITULO_BOTON = "Actualizar"



    _COLUMNAS = [

        "Número",

        "Fecha",

        "Proveedor",

        "Total",

        "Estado",

        "Aprobación",

    ]

    _ETIQUETAS_APROBACION = {
        "no_aplica": "",
        "pendiente_nivel1": "Pendiente de aprobación",
        "pendiente_nivel2": "Pendiente 2da. aprobación",
        "aprobada": "Aprobada",
        "rechazada": "Rechazada",
    }



    def _crear_filtros(self) -> None:



        btn_nuevo = QPushButton(

            "Nueva orden",

        )



        btn_nuevo.clicked.connect(

            self._nueva,

        )

        btn_imprimir = QPushButton(

            "Imprimir",

        )

        btn_imprimir.clicked.connect(

            self._imprimir_seleccionada,

        )

        btn_pdf = QPushButton(

            "Exportar PDF",

        )

        btn_pdf.clicked.connect(

            self._exportar_pdf_seleccionada,

        )

        btn_aprobar = QPushButton(
            "Aprobar",
        )

        btn_aprobar.clicked.connect(
            self._aprobar_seleccionada,
        )

        btn_rechazar = QPushButton(
            "Rechazar",
        )

        btn_rechazar.clicked.connect(
            self._rechazar_seleccionada,
        )

        self._filas: list[dict] = []

        self._layout_filtros.addWidget(

            btn_nuevo,

        )

        self._layout_filtros.addWidget(

            btn_imprimir,

        )

        self._layout_filtros.addWidget(

            btn_pdf,

        )

        self._layout_filtros.addWidget(
            btn_aprobar,
        )

        self._layout_filtros.addWidget(
            btn_rechazar,
        )



    def _nueva(self) -> None:



        dialogo = _DialogoOrdenCompra(

            self,

        )



        if dialogo.exec():



            self._consultar()



    def _consultar(self) -> None:



        filas = ServicioOrdenCompra.listar()

        self._filas = filas



        self.tabla.setRowCount(

            len(filas),

        )



        for indice, fila in enumerate(

            filas,

        ):



            valores = [

                fila["numero"],

                str(fila["fecha"]),

                fila["proveedor"],

                f"{fila['total']:,.2f}",

                fila["estado"],

                self._ETIQUETAS_APROBACION.get(
                    fila["estado_aprobacion"],
                    fila["estado_aprobacion"],
                ),

            ]



            for columna, valor in enumerate(

                valores,

            ):



                self.tabla.setItem(

                    indice,

                    columna,

                    QTableWidgetItem(

                        valor,

                    ),

                )



        self.tabla.resizeColumnsToContents()

    def _orden_seleccionada(
        self,
    ) -> dict | None:

        fila = self.tabla.currentRow()

        if fila < 0 or fila >= len(
            self._filas,
        ):

            QMessageBox.information(

                self,

                "Orden de compra",

                "Seleccione una orden en la tabla.",

            )

            return None

        return self._filas[fila]

    def _imprimir_seleccionada(
        self,
    ) -> None:

        fila = self._orden_seleccionada()

        if fila is None:

            return

        try:

            (
                orden,
                detalles,
                nombre,
                proveedor,
            ) = ServicioOrdenCompra.datos_impresion(
                fila["id"],
            )

        except ValueError as error:

            QMessageBox.warning(

                self,

                "Orden de compra",

                str(error),

            )

            return

        imprimir_orden_compra(

            orden,

            detalles,

            nombre,

            parent=self,

            proveedor=proveedor,

        )

    def _exportar_pdf_seleccionada(
        self,
    ) -> None:

        fila = self._orden_seleccionada()

        if fila is None:

            return

        try:

            (
                orden,
                detalles,
                nombre,
                proveedor,
            ) = ServicioOrdenCompra.datos_impresion(
                fila["id"],
            )

        except ValueError as error:

            QMessageBox.warning(

                self,

                "Orden de compra",

                str(error),

            )

            return

        exportar_pdf_orden_compra(

            orden,

            detalles,

            nombre,

            parent=self,

            proveedor=proveedor,

        )

    def _usuario_actual(self) -> str:

        from aplicacion.framework.app_context import (
            AppContext,
        )

        usuario = getattr(
            AppContext,
            "usuario",
            None,
        )

        if usuario is None:

            return "Sistema"

        return (
            getattr(usuario, "nombre", None)
            or getattr(usuario, "usuario", None)
            or "Sistema"
        )

    def _aprobar_seleccionada(self) -> None:

        fila = self._orden_seleccionada()

        if fila is None:

            return

        estado = fila["estado_aprobacion"]

        try:

            if estado == "pendiente_nivel1":

                ServicioOrdenCompra.aprobar_nivel1(
                    fila["id"],
                    self._usuario_actual(),
                )

            elif estado == "pendiente_nivel2":

                ServicioOrdenCompra.aprobar_nivel2(
                    fila["id"],
                    self._usuario_actual(),
                )

            else:

                QMessageBox.information(
                    self,
                    "Orden de compra",
                    "Esta orden no está pendiente de "
                    "aprobación.",
                )

                return

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Orden de compra",
                str(error),
            )

            return

        self._consultar()

    def _rechazar_seleccionada(self) -> None:

        fila = self._orden_seleccionada()

        if fila is None:

            return

        if fila["estado_aprobacion"] not in (
            "pendiente_nivel1",
            "pendiente_nivel2",
        ):

            QMessageBox.information(
                self,
                "Orden de compra",
                "Esta orden no está pendiente de aprobación.",
            )

            return

        motivo, aceptado = QInputDialog.getText(
            self,
            "Rechazar orden de compra",
            "Motivo del rechazo (opcional):",
        )

        if not aceptado:

            return

        try:

            ServicioOrdenCompra.rechazar_aprobacion(
                fila["id"],
                self._usuario_actual(),
                motivo,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Orden de compra",
                str(error),
            )

            return

        self._consultar()

