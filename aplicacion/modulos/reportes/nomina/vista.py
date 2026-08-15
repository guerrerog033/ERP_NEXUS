from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QTableWidgetItem,
)

from aplicacion.framework.ui.inquiry_page import InquiryPage
from aplicacion.interfaz.kpis_inicio import (
    formatear_moneda,
)
from aplicacion.modulos.nomina.servicios import (
    ServicioNomina,
)


class ReporteNominaPage(InquiryPage):

    titulo = "Resumen de nómina"

    _NOMBRE_EXPORT = "reporte_nomina"

    _COLUMNAS = [
        "Código",
        "Empleado",
        "Devengado",
        "Deducciones",
        "Neto",
        "Aportes patronales",
    ]

    def _crear_filtros(self) -> None:

        self._layout_filtros.addWidget(
            QLabel("Periodo:"),
        )

        self.periodo = QComboBox()

        self._cargar_periodos()

        self._layout_filtros.addWidget(
            self.periodo,
            1,
        )

        self.lbl_total = QLabel()

        self._layout_filtros.addWidget(
            self.lbl_total,
        )

    def _cargar_periodos(self) -> None:

        self.periodo.clear()

        periodos = ServicioNomina.listar_periodos()

        if not periodos:

            self.periodo.addItem(
                "Sin periodos",
                None,
            )

            return

        for periodo in periodos:

            self.periodo.addItem(
                ServicioNomina.nombre_periodo(
                    periodo,
                )
                + f" ({periodo.estado})",
                periodo.id,
            )

    def _consultar(self) -> None:

        periodo_id = self.periodo.currentData()

        if periodo_id is None:

            self.tabla.setRowCount(0)

            self.lbl_total.setText("")

            return

        filas = ServicioNomina.listar_resumen_periodo(
            periodo_id,
        )

        self.tabla.setRowCount(
            len(filas),
        )

        for i, fila in enumerate(filas):

            valores = [
                fila["codigo"],
                fila["empleado"],
                formatear_moneda(
                    fila["devengado"],
                ),
                formatear_moneda(
                    fila["deducciones"],
                ),
                formatear_moneda(
                    fila["neto"],
                ),
                formatear_moneda(
                    fila["aportes"],
                ),
            ]

            for j, valor in enumerate(
                valores,
            ):

                self.tabla.setItem(
                    i,
                    j,
                    QTableWidgetItem(
                        valor,
                    ),
                )

        totales = ServicioNomina.totales_periodo(
            periodo_id,
        )

        self.lbl_total.setText(
            "Neto total: "
            f"{formatear_moneda(totales['neto'])}"
        )

        self.tabla.resizeColumnsToContents()
