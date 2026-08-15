from __future__ import annotations



from PySide6.QtCore import QDate

from PySide6.QtWidgets import (

    QComboBox,

    QDateEdit,

    QDialog,

    QDialogButtonBox,

    QDoubleSpinBox,

    QFormLayout,

    QHBoxLayout,

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



        layout.addWidget(

            self.tabla,

        )



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



    def _producto_seleccionado(

        self,

        _resultado,

    ):



        costo = self.producto.costo_sugerido()



        if costo > 0:



            self.costo.setValue(

                costo,

            )



    def _agregar_linea(self):



        if self.producto.producto_id is None:



            QMessageBox.warning(

                self,

                "Orden de compra",

                "Seleccione un producto.",

            )



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



    def _guardar(self):



        proveedor_id = self.proveedor.valor()



        if proveedor_id is None:



            QMessageBox.warning(

                self,

                "Orden de compra",

                "Seleccione un proveedor.",

            )



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

    ]



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

