from __future__ import annotations

from pathlib import Path

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)


def _construir_pdf_factura_compra(
    factura,
    detalles,
    nombre_proveedor: str,
    ruta: str | Path,
    *,
    documento_proveedor: str = "",
    correo_proveedor: str = "",
) -> Path:

    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
        factura_compra_a_dto,
    )
    from aplicacion.reportes.compras.pdf.factura_compra import (
        FacturaCompraPDF,
    )

    dto = factura_compra_a_dto(
        factura,
        detalles,
        nombre_proveedor,
        documento_proveedor=documento_proveedor,
        correo_proveedor=correo_proveedor,
    )

    return FacturaCompraPDF(
        ruta,
        empresa_reporte(),
        dto,
    ).construir()


def crear_reporte_factura_compra(
    factura,
    detalles,
    nombre_proveedor: str,
    *,
    proveedor=None,
) -> ReporteDocumentoGenerico:

    numero = str(
        factura.numero or "",
    )

    documento = ""
    correo = ""

    if proveedor is not None:

        documento = str(
            getattr(
                proveedor,
                "numero_documento",
                "",
            )
            or "",
        )

        correo = str(
            getattr(
                proveedor,
                "correo",
                "",
            )
            or "",
        ).strip()

    return ReporteDocumentoGenerico(
        titulo="Factura de compra",
        numero=numero,
        generar_html_fn=lambda: __import__(
            "aplicacion.modulos.compras.facturas.formatos_impresion",
            fromlist=[
                "generar_html_factura_compra",
            ],
        ).generar_html_factura_compra(
            factura,
            detalles,
            nombre_proveedor,
            documento_proveedor=documento,
            correo_proveedor=correo,
        ),
        nombre_pdf=f"Factura compra {numero}.pdf",
        correo_destino=correo,
        construir_pdf_reportlab_fn=lambda ruta: _construir_pdf_factura_compra(
            factura,
            detalles,
            nombre_proveedor,
            ruta,
            documento_proveedor=documento,
            correo_proveedor=correo,
        ),
    )
