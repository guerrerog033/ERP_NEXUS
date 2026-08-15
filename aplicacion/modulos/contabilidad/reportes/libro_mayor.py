from __future__ import annotations



from PySide6.QtCore import QDate

from PySide6.QtWidgets import (

    QDateEdit,

    QLabel,

    QMessageBox,

    QTableWidgetItem,

)



from aplicacion.framework.lookup import LookupWidget

from aplicacion.framework.ui.inquiry_page import InquiryPage

from aplicacion.modulos.contabilidad.plan_cuentas.cuenta_lookup import (

    PlanCuentaLookup,

)

from aplicacion.modulos.contabilidad.servicio_reportes import (

    ServicioReportesContables,

)





class LibroMayorPage(InquiryPage):



    titulo = "Libro mayor"



    _NOMBRE_EXPORT = "libro_mayor"



    _COLUMNAS = [

        "Fecha",

        "Comprobante",

        "Descripción",

        "Débito",

        "Crédito",

        "Saldo",

    ]



    def __init__(self, parent=None):



        self.servicio = ServicioReportesContables()



        super().__init__(parent)



    def _crear_filtros(self) -> None:



        self._layout_filtros.addWidget(

            QLabel("Cuenta:"),

        )



        self.cuenta = LookupWidget(

            PlanCuentaLookup(),

            self,

        )



        self._layout_filtros.addWidget(

            self.cuenta,

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

        self._resultado_reporte: dict | None = None



    def _consultar(self) -> None:



        cuenta_id = self.cuenta.valor()



        if cuenta_id is None:



            QMessageBox.warning(

                self,

                "Libro mayor",

                "Seleccione una cuenta contable.",

            )



            return



        desde = self.fecha_desde.date().toPython()



        hasta = self.fecha_hasta.date().toPython()



        try:



            resultado = self.servicio.libro_mayor(

                cuenta_id=cuenta_id,

                fecha_desde=desde,

                fecha_hasta=hasta,

            )



        except ValueError as error:



            QMessageBox.warning(

                self,

                "Libro mayor",

                str(error),

            )



            return



        cuenta = resultado["cuenta"]

        self._resultado_reporte = resultado

        filas = resultado["filas"]



        self.tabla.setRowCount(

            len(filas),

        )



        for i, fila in enumerate(filas):



            self.tabla.setItem(

                i,

                0,

                QTableWidgetItem(

                    str(fila["fecha"]),

                ),

            )



            self.tabla.setItem(

                i,

                1,

                QTableWidgetItem(

                    fila["numero"],

                ),

            )



            self.tabla.setItem(

                i,

                2,

                QTableWidgetItem(

                    fila["descripcion"] or "",

                ),

            )



            self.tabla.setItem(

                i,

                3,

                QTableWidgetItem(

                    f"{fila['debito']:,.2f}",

                ),

            )



            self.tabla.setItem(

                i,

                4,

                QTableWidgetItem(

                    f"{fila['credito']:,.2f}",

                ),

            )



            self.tabla.setItem(

                i,

                5,

                QTableWidgetItem(

                    f"{fila['saldo']:,.2f}",

                ),

            )



        self.tabla.resizeColumnsToContents()



        if filas:



            saldo_final = filas[-1]["saldo"]



            self.setToolTip(

                f"Cuenta {cuenta.codigo} · "

                f"Saldo final {saldo_final:,.2f}",

            )

    def _exportar_pdf_reporte(
        self,
    ) -> None:

        if not getattr(
            self,
            "_resultado_reporte",
            None,
        ):

            self._consultar()

        if not self._resultado_reporte:

            return

        from aplicacion.framework.reportes.impresion_util import (
            abrir_centro_impresion,
        )
        from aplicacion.reportes.contabilidad.libro_mayor import (
            crear_reporte_libro_mayor,
        )

        desde = self.fecha_desde.date().toString(
            "dd/MM/yyyy",
        )

        hasta = self.fecha_hasta.date().toString(
            "dd/MM/yyyy",
        )

        reporte = crear_reporte_libro_mayor(
            self._resultado_reporte,
            periodo=f"{desde} - {hasta}",
        )

        abrir_centro_impresion(
            reporte,
            parent=self,
        )

