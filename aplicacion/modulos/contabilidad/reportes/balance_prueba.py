from __future__ import annotations



from PySide6.QtCore import QDate

from PySide6.QtWidgets import (

    QDateEdit,

    QLabel,

    QTableWidgetItem,

)



from aplicacion.framework.ui.inquiry_page import InquiryPage

from aplicacion.modulos.contabilidad.servicio_reportes import (

    ServicioReportesContables,

)





class BalancePruebaPage(InquiryPage):



    titulo = "Balance de prueba"



    _NOMBRE_EXPORT = "balance_prueba"



    _COLUMNAS = [

        "Código",

        "Cuenta",

        "Débito",

        "Crédito",

        "Saldo",

    ]



    def __init__(self, parent=None):



        self.servicio = ServicioReportesContables()



        super().__init__(parent)



    def _crear_filtros(self) -> None:



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

        from PySide6.QtWidgets import QPushButton

        self.btn_pdf = QPushButton(
            "Exportar PDF",
        )

        self.btn_pdf.clicked.connect(
            self._exportar_pdf_reporte,
        )

        self._layout_filtros.addWidget(
            self.btn_pdf,
        )

        self._filas_reporte: list = []

        self._resultado_reporte: dict | None = None



    def _consultar(self) -> None:



        desde = self.fecha_desde.date().toPython()



        hasta = self.fecha_hasta.date().toPython()



        resultado = self.servicio.balance_prueba(

            fecha_desde=desde,

            fecha_hasta=hasta,

        )



        filas = resultado["filas"]

        self._filas_reporte = filas

        self._resultado_reporte = resultado



        self.tabla.setRowCount(

            len(filas),

        )



        for i, fila in enumerate(filas):



            self.tabla.setItem(

                i,

                0,

                QTableWidgetItem(

                    fila["codigo"],

                ),

            )



            self.tabla.setItem(

                i,

                1,

                QTableWidgetItem(

                    fila["nombre"],

                ),

            )



            self.tabla.setItem(

                i,

                2,

                QTableWidgetItem(

                    f"{fila['debito']:,.2f}",

                ),

            )



            self.tabla.setItem(

                i,

                3,

                QTableWidgetItem(

                    f"{fila['credito']:,.2f}",

                ),

            )



            self.tabla.setItem(

                i,

                4,

                QTableWidgetItem(

                    f"{fila['saldo']:,.2f}",

                ),

            )



        total_fila = len(filas)



        self.tabla.setRowCount(

            total_fila + 1,

        )



        self.tabla.setItem(

            total_fila,

            0,

            QTableWidgetItem(

                "",

            ),

        )



        self.tabla.setItem(

            total_fila,

            1,

            QTableWidgetItem(

                "Totales",

            ),

        )



        self.tabla.setItem(

            total_fila,

            2,

            QTableWidgetItem(

                f"{resultado['total_debito']:,.2f}",

            ),

        )



        self.tabla.setItem(

            total_fila,

            3,

            QTableWidgetItem(

                f"{resultado['total_credito']:,.2f}",

            ),

        )



        self.tabla.setItem(

            total_fila,

            4,

            QTableWidgetItem(

                f"{resultado['total_debito'] - resultado['total_credito']:,.2f}",

            ),

        )



        self.tabla.resizeColumnsToContents()

    def _exportar_pdf_reporte(
        self,
    ) -> None:

        if not getattr(
            self,
            "_resultado_reporte",
            None,
        ):

            self._consultar()

        from aplicacion.framework.reportes.impresion_util import (
            abrir_centro_impresion,
        )
        from aplicacion.reportes.contabilidad.balance_prueba import (
            crear_reporte_balance_prueba,
        )

        desde = self.fecha_desde.date().toString(
            "dd/MM/yyyy",
        )

        hasta = self.fecha_hasta.date().toString(
            "dd/MM/yyyy",
        )

        reporte = crear_reporte_balance_prueba(
            self._resultado_reporte,
            periodo=f"{desde} - {hasta}",
            nombre_pdf=(
                f"Balance prueba {desde} {hasta}.pdf"
            ),
        )

        abrir_centro_impresion(
            reporte,
            parent=self,
        )

