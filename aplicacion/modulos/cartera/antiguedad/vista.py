from __future__ import annotations



from PySide6.QtWidgets import (

    QComboBox,

    QLabel,

    QTableWidgetItem,

)



from aplicacion.framework.ui.inquiry_page import InquiryPage

from aplicacion.modulos.cartera.servicios import (

    ServicioCartera,

)





class CarteraAntiguedadPage(InquiryPage):



    titulo = "Antigüedad de saldos"



    _NOMBRE_EXPORT = "cartera_antiguedad"



    _COLUMNAS = [

        "Rango",

        "Saldo",

    ]



    def _crear_filtros(self) -> None:



        self._layout_filtros.addWidget(

            QLabel("Cartera:"),

        )



        self.tipo = QComboBox()



        self.tipo.addItem(

            "Cuentas por cobrar",

            "cxc",

        )



        self.tipo.addItem(

            "Cuentas por pagar",

            "cxp",

        )



        self._layout_filtros.addWidget(

            self.tipo,

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

        self._filas_reporte: list[dict] = []



    def _consultar(self) -> None:



        filas = ServicioCartera.antiguedad(

            tipo=self.tipo.currentData(),

        )

        self._filas_reporte = filas



        self.tabla.setRowCount(

            len(filas),

        )



        total = 0.0



        for i, fila in enumerate(filas):



            total += fila["saldo"]



            self.tabla.setItem(

                i,

                0,

                QTableWidgetItem(

                    fila["rango"],

                ),

            )



            self.tabla.setItem(

                i,

                1,

                QTableWidgetItem(

                    f"{fila['saldo']:,.2f}",

                ),

            )



        fila_total = len(filas)



        self.tabla.setRowCount(

            fila_total + 1,

        )



        self.tabla.setItem(

            fila_total,

            0,

            QTableWidgetItem(

                "Total",

            ),

        )



        self.tabla.setItem(

            fila_total,

            1,

            QTableWidgetItem(

                f"{total:,.2f}",

            ),

        )



        self.tabla.resizeColumnsToContents()

    def _exportar_pdf_reporte(
        self,
    ) -> None:

        if not getattr(
            self,
            "_filas_reporte",
            None,
        ):

            self._consultar()

        from aplicacion.framework.reportes.impresion_util import (
            abrir_centro_impresion,
        )
        from aplicacion.reportes.cartera.reportes import (
            crear_reporte_antiguedad_cartera,
        )

        titulo = (
            "Cuentas por cobrar"
            if self.tipo.currentData() == "cxc"
            else "Cuentas por pagar"
        )

        reporte = crear_reporte_antiguedad_cartera(
            self._filas_reporte,
            titulo_cartera=titulo,
        )

        abrir_centro_impresion(
            reporte,
            parent=self,
        )

