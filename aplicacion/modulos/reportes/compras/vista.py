from __future__ import annotations

from aplicacion.framework.ui.report_period_page import (
    ReportPeriodPage,
)


class ReporteComprasPage(ReportPeriodPage):

    titulo = "Compras por periodo"

    _METODO = "compras_por_periodo"
    _NOMBRE_EXPORT = "compras_periodo"

    _COLUMNAS = [
        "Número",
        "Fecha",
        "Proveedor",
        "Factura prov.",
        "Subtotal",
        "IVA",
        "Total",
        "Saldo",
        "Estado pago",
    ]

    _CAMPOS = [
        "numero",
        "fecha",
        "proveedor",
        "numero_proveedor",
        "subtotal",
        "iva",
        "total",
        "saldo",
        "estado_pago",
    ]

    _NUMERICAS = {4, 5, 6, 7}
    _CAMPO_TOTAL = "total"
