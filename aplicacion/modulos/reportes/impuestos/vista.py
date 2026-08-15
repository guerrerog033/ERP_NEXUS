from __future__ import annotations

from aplicacion.framework.ui.report_period_page import (
    ReportPeriodPage,
)


class ReporteRetencionesPage(ReportPeriodPage):

    titulo = "Retenciones aplicadas"

    _METODO = "retenciones_aplicadas"
    _NOMBRE_EXPORT = "retenciones"

    _COLUMNAS = [
        "Número",
        "Fecha",
        "Tipo",
        "Tercero",
        "Retenciones",
        "Base",
        "Total",
    ]

    _CAMPOS = [
        "numero",
        "fecha",
        "tipo",
        "cliente",
        "retenciones",
        "base",
        "total",
    ]

    _NUMERICAS = {5, 6}
    _CAMPO_TOTAL = "base"
