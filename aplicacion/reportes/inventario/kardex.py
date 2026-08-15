from __future__ import annotations

from pathlib import Path

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)
from aplicacion.framework.reportes.reporte_tabla import (
    html_reporte_tabla,
)


def _construir_pdf_kardex(
    dto: dict,
    ruta: str | Path,
) -> Path:

    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
    )
    from aplicacion.framework.reportes.pdf.tabla_reporte import (
        TablaReportePDF,
    )

    return TablaReportePDF(
        ruta,
        empresa_reporte(),
        dto,
    ).construir()


def crear_reporte_kardex(
    filas: list[dict],
    *,
    numero: str,
    subtitulo: str,
    nombre_pdf: str | None = None,
) -> ReporteDocumentoGenerico:

    from aplicacion.reportes.comunes.datos_inventario import (
        kardex_inventario_a_dto,
    )

    dto = kardex_inventario_a_dto(
        filas,
        numero=numero,
        subtitulo=subtitulo,
    )

    html = html_reporte_tabla(
        titulo="Kardex de inventario",
        subtitulo=subtitulo,
        columnas=dto[
            "columnas"
        ],
        filas=dto[
            "filas"
        ],
    )

    return ReporteDocumentoGenerico(
        titulo="Kardex de inventario",
        numero=numero,
        generar_html_fn=lambda: html,
        nombre_pdf=(
            nombre_pdf
            or f"Kardex {numero}.pdf"
        ),
        formato_pagina="carta",
        construir_pdf_reportlab_fn=lambda ruta: _construir_pdf_kardex(
            dto,
            ruta,
        ),
    )
