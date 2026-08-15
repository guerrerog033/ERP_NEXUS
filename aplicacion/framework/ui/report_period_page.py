from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QLabel,
    QPushButton,
)

from aplicacion.interfaz.kpis_inicio import (
    formatear_moneda,
)
from aplicacion.modulos.reportes.servicios import (
    ServicioReportes,
)
from aplicacion.modulos.reportes.utilidades import (
    llenar_tabla_reporte,
)

from .inquiry_page import InquiryPage


class ReportPeriodPage(InquiryPage):
    """
    Consulta declarativa por rango de fechas sobre ServicioReportes.
    """

    _METODO = ""
    _NOMBRE_EXPORT = "reporte"

    _COLUMNAS: list[str] = []
    _CAMPOS: list[str] = []
    _NUMERICAS: set[int] = set()
    _CAMPO_TOTAL = ""

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

        self.lbl_total = QLabel()

        self._layout_filtros.addWidget(
            self.lbl_total,
        )

        self._filas_reporte: list[dict] = []

    def _agregar_botones_filtro(
        self,
    ) -> None:

        self.btn_pdf = QPushButton(
            "Exportar PDF",
        )

        self.btn_pdf.clicked.connect(
            self._exportar_pdf_reporte,
        )

        self._layout_filtros.addWidget(
            self.btn_pdf,
        )

    def _consultar(self) -> None:

        metodo = getattr(
            ServicioReportes,
            self._METODO,
        )

        filas = metodo(
            fecha_desde=self.fecha_desde.date().toPython(),
            fecha_hasta=self.fecha_hasta.date().toPython(),
        )

        self._filas_reporte = filas

        llenar_tabla_reporte(
            self.tabla,
            self._COLUMNAS,
            filas,
            campos=self._CAMPOS,
            columnas_numericas=self._NUMERICAS,
        )

        if self._CAMPO_TOTAL:

            total = ServicioReportes.totales_documentos(
                filas,
                self._CAMPO_TOTAL,
            )

            self.lbl_total.setText(
                f"Total: {formatear_moneda(total)}",
            )

        elif hasattr(
            self,
            "lbl_total",
        ):

            self.lbl_total.setText("")

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
        from aplicacion.interfaz.kpis_inicio import (
            formatear_moneda,
        )
        from aplicacion.reportes.reportes_periodo import (
            crear_reporte_periodo,
        )

        desde = self.fecha_desde.date().toString(
            "dd/MM/yyyy",
        )

        hasta = self.fecha_hasta.date().toString(
            "dd/MM/yyyy",
        )

        periodo = f"{desde} - {hasta}"

        pie = ""

        if (
            self._CAMPO_TOTAL
            and self._filas_reporte
        ):

            total = ServicioReportes.totales_documentos(
                self._filas_reporte,
                self._CAMPO_TOTAL,
            )

            pie = (
                f"Total: {formatear_moneda(total)}"
            )

        formateadores = None

        if hasattr(
            self,
            "_FORMATEADORES_PDF",
        ):

            formateadores = self._FORMATEADORES_PDF

        reporte = crear_reporte_periodo(
            titulo=self.titulo,
            filas=self._filas_reporte,
            columnas=self._COLUMNAS,
            campos=self._CAMPOS,
            periodo=periodo,
            pie=pie,
            columnas_numericas=self._NUMERICAS,
            formateadores=formateadores,
            nombre_pdf=(
                f"{self._NOMBRE_EXPORT} "
                f"{periodo}.pdf"
            ),
        )

        abrir_centro_impresion(
            reporte,
            parent=self,
        )
