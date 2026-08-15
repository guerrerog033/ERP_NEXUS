from __future__ import annotations

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QLabel,
    QPushButton,
    QTableWidgetItem,
)

from aplicacion.framework.ui.inquiry_page import InquiryPage
from aplicacion.modulos.inventario.bodegas.servicios import (
    ServicioBodega,
)
from aplicacion.modulos.inventario.servicios import (
    ServicioInventario,
)
from aplicacion.modulos.inventario.widgets.selector_producto import (
    SelectorProducto,
)


class KardexPage(InquiryPage):

    titulo = "Kardex"

    _NOMBRE_EXPORT = "kardex"

    _COLUMNAS = [
        "Fecha",
        "Bodega",
        "Código",
        "Producto",
        "Variante",
        "Tipo",
        "Cantidad",
        "Costo",
        "Referencia",
        "Saldo",
    ]

    def _crear_filtros(self) -> None:

        self._layout_filtros.addWidget(
            QLabel("Bodega:"),
        )

        self.bodega = QComboBox()

        self.bodega.addItem(
            "Todas",
            None,
        )

        for bodega in ServicioBodega.listar_activas():

            self.bodega.addItem(
                f"{bodega.codigo} - {bodega.nombre}",
                bodega.id,
            )

        self._layout_filtros.addWidget(
            self.bodega,
        )

        self._layout_filtros.addWidget(
            QLabel("Producto:"),
        )

        self.producto = SelectorProducto(
            self,
        )

        self._layout_filtros.addWidget(
            self.producto,
            1,
        )

        self._layout_filtros.addWidget(
            QLabel("Desde:"),
        )

        self.fecha_desde = QDateEdit()

        self.fecha_desde.setCalendarPopup(
            True,
        )

        self.fecha_desde.setDate(
            QDate.currentDate().addMonths(
                -1,
            ),
        )

        self._layout_filtros.addWidget(
            self.fecha_desde,
        )

        self._layout_filtros.addWidget(
            QLabel("Hasta:"),
        )

        self.fecha_hasta = QDateEdit()

        self.fecha_hasta.setCalendarPopup(
            True,
        )

        self.fecha_hasta.setDate(
            QDate.currentDate(),
        )

        self._layout_filtros.addWidget(
            self.fecha_hasta,
        )

        self.btn_pdf = QPushButton(
            "Exportar PDF",
        )

        self.btn_pdf.clicked.connect(
            self._exportar_pdf_reporte,
        )

        self._layout_filtros.addWidget(
            self.btn_pdf,
        )

        self._filas_reporte: list[dict] = []

    def _consultar(self) -> None:

        filas = ServicioInventario.consultar_kardex(
            bodega_id=self.bodega.currentData(),
            producto_id=self.producto.producto_id,
            fecha_desde=self.fecha_desde.date().toPython(),
            fecha_hasta=self.fecha_hasta.date().toPython(),
        )

        self._filas_reporte = filas

        self.tabla.setRowCount(
            len(filas),
        )

        for i, fila in enumerate(filas):

            valores = [
                str(fila["fecha"]),
                fila["bodega"],
                fila["codigo"],
                fila["producto"],
                fila["variante"],
                fila["tipo"],
                f"{fila['cantidad']:,.2f}",
                f"{fila['costo_unitario']:,.2f}",
                fila["referencia"],
                f"{fila['saldo']:,.2f}",
            ]

            for columna, valor in enumerate(
                valores,
            ):

                item = QTableWidgetItem(
                    valor,
                )

                if columna in (
                    6,
                    7,
                    9,
                ):

                    item.setTextAlignment(
                        Qt.AlignRight
                        | Qt.AlignVCenter,
                    )

                self.tabla.setItem(
                    i,
                    columna,
                    item,
                )

        self.tabla.resizeColumnsToContents()

    def _exportar_pdf_reporte(
        self,
    ) -> None:

        if not self._filas_reporte:

            self._consultar()

        from aplicacion.framework.reportes.impresion_util import (
            abrir_centro_impresion,
        )
        from aplicacion.reportes.inventario.kardex import (
            crear_reporte_kardex,
        )

        desde = self.fecha_desde.date().toString(
            "dd/MM/yyyy",
        )

        hasta = self.fecha_hasta.date().toString(
            "dd/MM/yyyy",
        )

        producto = (
            self.producto.resultado.texto
            if self.producto.resultado
            else "Todos"
        )

        reporte = crear_reporte_kardex(
            self._filas_reporte,
            numero=f"{desde} - {hasta}",
            subtitulo=(
                f"Bodega: {self.bodega.currentText()} | "
                f"Producto: {producto}"
            ),
            nombre_pdf=(
                f"Kardex {desde} {hasta}.pdf"
            ),
        )

        abrir_centro_impresion(
            reporte,
            parent=self,
        )
