from __future__ import annotations

from pathlib import Path

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)


def _construir_pdf_comprobante_egreso(
    comprobante,
    ruta: str | Path,
    *,
    nombre_proveedor: str,
    documento_proveedor: str = "",
) -> Path:

    from aplicacion.reportes.comunes.datos_documento import (
        comprobante_egreso_a_dto,
        empresa_reporte,
    )
    from aplicacion.reportes.tesoreria.pdf.comprobante_egreso import (
        ComprobanteEgresoPDF,
    )

    dto = comprobante_egreso_a_dto(
        comprobante,
        nombre_proveedor=nombre_proveedor,
        documento_proveedor=documento_proveedor,
    )

    return ComprobanteEgresoPDF(
        ruta,
        empresa_reporte(),
        dto,
    ).construir()


def crear_reporte_comprobante_egreso(
    comprobante,
    *,
    nombre_proveedor: str,
    documento_proveedor: str = "",
) -> ReporteDocumentoGenerico:

    numero = str(
        comprobante.numero or "",
    )

    return ReporteDocumentoGenerico(
        titulo="Comprobante de egreso",
        numero=numero,
        generar_html_fn=lambda: __import__(
            "aplicacion.modulos.tesoreria.comprobantes_egreso.formatos_impresion",
            fromlist=[
                "generar_html_comprobante",
            ],
        ).generar_html_comprobante(
            comprobante,
            nombre_proveedor=nombre_proveedor,
            documento_proveedor=documento_proveedor,
        ),
        nombre_pdf=f"Comprobante egreso {numero}.pdf",
        formato_pagina="media_carta",
        construir_pdf_reportlab_fn=lambda ruta: _construir_pdf_comprobante_egreso(
            comprobante,
            ruta,
            nombre_proveedor=nombre_proveedor,
            documento_proveedor=documento_proveedor,
        ),
    )
