from __future__ import annotations



from PySide6.QtCore import QDate

from PySide6.QtWidgets import (

    QDateEdit,

    QLabel,

    QPushButton,

    QTableWidgetItem,

)



from aplicacion.framework.ui.inquiry_page import InquiryPage

from aplicacion.modulos.contabilidad.servicio_reportes import (

    ServicioReportesContables,

)





class EstadoResultadosPage(InquiryPage):



    titulo = "Estado de resultados"



    _NOMBRE_EXPORT = "estado_resultados"



    _COLUMNAS = [

        "Código",

        "Cuenta",

        "Valor",

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



        desde = self.fecha_desde.date().toPython()

        hasta = self.fecha_hasta.date().toPython()



        resultado = self.servicio.estado_resultados(

            fecha_desde=desde,

            fecha_hasta=hasta,

        )



        self._resultado_reporte = resultado



        filas_vista: list[tuple[str, str, float]] = []

        secciones = (
            (
                "Ingresos",
                "ingresos",
                "total_ingresos",
            ),
            (
                "Costos de venta",
                "costos_venta",
                "total_costos_venta",
            ),
            (
                "Gastos operacionales",
                "gastos",
                "total_gastos",
            ),
        )

        for titulo, clave, clave_total in secciones:

            filas_vista.append(
                (
                    "",
                    titulo,
                    0.0,
                ),
            )

            for fila in resultado.get(
                clave,
                [],
            ):

                filas_vista.append(
                    (
                        fila["codigo"],
                        fila["nombre"],
                        fila["valor"],
                    ),
                )

            filas_vista.append(
                (
                    "",
                    f"Total {titulo.lower()}",
                    float(
                        resultado.get(
                            clave_total,
                            0,
                        )
                        or 0,
                    ),
                ),
            )

            if clave == "costos_venta":

                filas_vista.append(
                    (
                        "",
                        "Utilidad bruta",
                        float(
                            resultado.get(
                                "utilidad_bruta",
                                0,
                            )
                            or 0,
                        ),
                    ),
                )

        filas_vista.append(
            (
                "",
                "Utilidad neta",
                float(
                    resultado.get(
                        "utilidad_neta",
                        0,
                    )
                    or 0,
                ),
            ),
        )



        self.tabla.setRowCount(

            len(filas_vista),

        )



        for i, (

            codigo,

            cuenta,

            valor,

        ) in enumerate(filas_vista):



            self.tabla.setItem(

                i,

                0,

                QTableWidgetItem(

                    codigo,

                ),

            )

            self.tabla.setItem(

                i,

                1,

                QTableWidgetItem(

                    cuenta,

                ),

            )



            texto_valor = (
                f"{valor:,.2f}"
                if codigo
                or cuenta.startswith(
                    "Total",
                )
                or cuenta
                in (
                    "Utilidad bruta",
                    "Utilidad neta",
                )
                else ""
            )



            self.tabla.setItem(

                i,

                2,

                QTableWidgetItem(

                    texto_valor,

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

        from aplicacion.reportes.contabilidad.estado_resultados import (

            crear_reporte_estado_resultados,

        )



        desde = self.fecha_desde.date().toString(

            "dd/MM/yyyy",

        )

        hasta = self.fecha_hasta.date().toString(

            "dd/MM/yyyy",

        )



        reporte = crear_reporte_estado_resultados(

            self._resultado_reporte,

            periodo=f"{desde} - {hasta}",

            nombre_pdf=(

                f"Estado resultados {desde} {hasta}.pdf"

            ),

        )



        abrir_centro_impresion(

            reporte,

            parent=self,

        )

