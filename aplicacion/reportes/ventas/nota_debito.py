from __future__ import annotations

from pathlib import Path

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)
from aplicacion.reportes.ventas.nota_credito import (
    _numero_factura_referencia,
    generar_html_nota_venta,
)


def generar_html_nota_debito_venta(
    nota,
    detalles,
    nombre_cliente: str,
    *,
    factura_numero: str = "",
) -> str:

    return generar_html_nota_venta(
        nota,
        detalles,
        nombre_cliente,
        tipo="debito",
        factura_numero=factura_numero,
    )


def _html_nota_debito_venta(
    nota,
    detalles,
    nombre_cliente: str,
    *,
    factura_numero: str = "",
) -> str:

    return generar_html_nota_debito_venta(
        nota,
        detalles,
        nombre_cliente,
        factura_numero=factura_numero,
    )


def _construir_pdf_nota_debito(
    nota,
    detalles,
    nombre_cliente: str,
    ruta: str | Path,
    *,
    factura_numero: str = "",
) -> Path:

    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
        nota_debito_venta_a_dto,
    )
    from aplicacion.reportes.ventas.pdf.nota_venta import (
        NotaVentaPDF,
    )

    cufe = str(
        getattr(
            nota,
            "cufe",
            "",
        )
        or "",
    ).strip()

    electronica = bool(
        cufe,
    )

    dto = nota_debito_venta_a_dto(
        nota,
        detalles,
        nombre_cliente,
        electronica=electronica,
        factura_numero=(
            factura_numero
            or _numero_factura_referencia(
                getattr(
                    nota,
                    "factura_id",
                    None,
                ),
            )
        ),
    )

    titulo = (
        "NOTA DÉBITO ELECTRÓNICA"
        if electronica
        else "NOTA DÉBITO DE VENTA"
    )

    return NotaVentaPDF(
        ruta,
        empresa_reporte(),
        dto,
        titulo=titulo,
        electronica=electronica,
    ).construir()


def crear_reporte_nota_debito_venta(
    nota,
    detalles,
    nombre_cliente: str,
    *,
    factura_numero: str = "",
) -> ReporteDocumentoGenerico:

    numero = str(
        nota.numero or "",
    )

    referencia = (
        factura_numero
        or _numero_factura_referencia(
            getattr(
                nota,
                "factura_id",
                None,
            ),
        )
    )

    return ReporteDocumentoGenerico(
        titulo="Nota débito de venta",
        numero=numero,
        generar_html_fn=lambda: _html_nota_debito_venta(
            nota,
            detalles,
            nombre_cliente,
            factura_numero=referencia,
        ),
        nombre_pdf=f"Nota debito {numero}.pdf",
        construir_pdf_reportlab_fn=lambda ruta: _construir_pdf_nota_debito(
            nota,
            detalles,
            nombre_cliente,
            ruta,
            factura_numero=referencia,
        ),
    )
