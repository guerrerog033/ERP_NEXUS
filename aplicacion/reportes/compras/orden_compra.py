from __future__ import annotations

from pathlib import Path

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)


def _construir_pdf_orden_compra(
    orden,
    detalles,
    nombre_proveedor: str,
    ruta: str | Path,
    *,
    documento_proveedor: str = "",
) -> Path:

    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
        orden_compra_a_dto,
    )
    from aplicacion.reportes.compras.pdf.orden_compra import (
        OrdenCompraPDF,
    )

    dto = orden_compra_a_dto(
        orden,
        detalles,
        nombre_proveedor,
        documento_proveedor=documento_proveedor,
    )

    return OrdenCompraPDF(
        ruta,
        empresa_reporte(),
        dto,
    ).construir()


def crear_reporte_orden_compra(
    orden,
    detalles,
    nombre_proveedor: str,
    *,
    proveedor=None,
) -> ReporteDocumentoGenerico:

    numero = str(
        orden.numero or "",
    )

    documento = ""

    if proveedor is not None:

        documento = str(
            getattr(
                proveedor,
                "numero_documento",
                "",
            )
            or "",
        )

    return ReporteDocumentoGenerico(
        titulo="Orden de compra",
        numero=numero,
        generar_html_fn=lambda: __import__(
            "aplicacion.modulos.compras.ordenes.formatos_impresion",
            fromlist=[
                "generar_html_orden_compra",
            ],
        ).generar_html_orden_compra(
            orden,
            detalles,
            nombre_proveedor,
            documento_proveedor=documento,
        ),
        nombre_pdf=f"Orden compra {numero}.pdf",
        construir_pdf_reportlab_fn=lambda ruta: _construir_pdf_orden_compra(
            orden,
            detalles,
            nombre_proveedor,
            ruta,
            documento_proveedor=documento,
        ),
    )
