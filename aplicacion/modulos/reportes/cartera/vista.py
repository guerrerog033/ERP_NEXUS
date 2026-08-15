from __future__ import annotations



from aplicacion.framework.ui.inquiry_page import InquiryPage

from aplicacion.interfaz.kpis_inicio import (

    formatear_moneda,

)

from aplicacion.modulos.reportes.servicios import (

    ServicioReportes,

)

from aplicacion.modulos.reportes.utilidades import (

    llenar_tabla_reporte,

)





class ReporteCarteraPage(InquiryPage):



    titulo = "Resumen de cartera"



    _NOMBRE_EXPORT = "resumen_cartera"

    _TITULO_BOTON = "Actualizar"

    def _agregar_botones_filtro(
        self,
    ) -> None:

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



        filas = ServicioReportes.resumen_cartera()

        self._filas_reporte = filas



        llenar_tabla_reporte(

            self.tabla,

            [

                "Concepto",

                "Valor",

            ],

            filas,

            campos=[

                "concepto",

                "valor",

            ],

            columnas_numericas={1},

            formateadores={

                1: formatear_moneda,

            },

        )

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
            crear_reporte_resumen_cartera,
        )

        reporte = crear_reporte_resumen_cartera(
            self._filas_reporte,
        )

        abrir_centro_impresion(
            reporte,
            parent=self,
        )

