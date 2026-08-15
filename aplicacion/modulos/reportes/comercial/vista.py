from __future__ import annotations

from aplicacion.framework.ui.report_period_page import (
    ReportPeriodPage,
)
from aplicacion.interfaz.kpis_inicio import (
    formatear_moneda,
)
from aplicacion.modulos.reportes.servicios import (
    ServicioReportes,
)


class ReportePipelineComercialPage(
    ReportPeriodPage,
):

    titulo = "Pipeline comercial"

    _METODO = "pipeline_comercial"

    _NOMBRE_EXPORT = "pipeline_comercial"

    _COLUMNAS = [
        "Cotización",
        "Fecha",
        "Cliente",
        "Estado cot.",
        "Total cot.",
        "Pedido",
        "Remisión",
        "Factura",
        "Saldo",
        "Cobrado",
        "Etapa",
    ]

    _CAMPOS = [
        "cotizacion_numero",
        "cotizacion_fecha",
        "cliente",
        "cotizacion_estado",
        "cotizacion_total",
        "pedido_numero",
        "remision_numero",
        "factura_numero",
        "saldo_pendiente",
        "valor_cobrado",
        "etapa_actual",
    ]

    _NUMERICAS = {4, 8, 9}

    _CAMPO_TOTAL = "cotizacion_total"

    def _consultar(
        self,
    ) -> None:

        super()._consultar()

        if not self._filas_reporte:

            return

        resumen = ServicioReportes.pipeline_comercial_resumen(
            self._filas_reporte,
        )

        partes = [
            (
                f"{etapa}: {datos['cantidad']}"
            )
            for etapa, datos in resumen.items()
            if datos["cantidad"]
        ]

        if not partes:

            return

        total = ServicioReportes.totales_documentos(
            self._filas_reporte,
            self._CAMPO_TOTAL,
        )

        self.lbl_total.setText(
            f"Total cotizaciones: "
            f"{formatear_moneda(total)}"
            f"  |  "
            + "  |  ".join(
                partes,
            ),
        )
