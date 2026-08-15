from __future__ import annotations

from aplicacion.framework.ui.report_period_page import (
    ReportPeriodPage,
)


class ReporteVentasPage(ReportPeriodPage):

    titulo = "Ventas por periodo"

    _METODO = "ventas_por_periodo"
    _NOMBRE_EXPORT = "ventas_periodo"

    _COLUMNAS = [
        "Número",
        "Fecha",
        "Cliente",
        "Subtotal",
        "IVA",
        "Total",
        "Saldo",
        "Estado pago",
    ]

    _CAMPOS = [
        "numero",
        "fecha",
        "cliente",
        "subtotal",
        "iva",
        "total",
        "saldo",
        "estado_pago",
    ]

    _NUMERICAS = {3, 4, 5, 6}
    _CAMPO_TOTAL = "total"
