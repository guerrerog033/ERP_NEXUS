from __future__ import annotations

from pathlib import Path

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)
from aplicacion.reportes.ventas.nota_credito import (
    _numero_factura_referencia,
)


def _html_nota_debito_venta(
    nota,
    detalles,
    nombre_cliente: str,
    *,
    factura_numero: str = "",
) -> str:

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

    filas = ""

    for detalle in detalles:

        filas += (
            "<tr>"
            f"<td>{detalle.descripcion}</td>"
            f"<td align='right'>{float(detalle.cantidad or 0):,.2f}</td>"
            f"<td align='right'>${float(detalle.total_linea or 0):,.2f}</td>"
            "</tr>"
        )

    return (
        "<h2>Nota débito de venta</h2>"
        f"<p><b>Cliente:</b> {nombre_cliente}</p>"
        f"<p><b>Factura referencia:</b> {referencia}</p>"
        f"<p><b>CUFE factura:</b> "
        f"{getattr(nota, 'factura_cufe', '') or '-'}</p>"
        f"<p><b>Subtotal:</b> ${float(nota.subtotal or 0):,.2f}<br>"
        f"<b>IVA:</b> ${float(nota.iva or 0):,.2f}<br>"
        f"<b>Total:</b> ${float(nota.total or 0):,.2f}</p>"
        "<table border='1' cellspacing='0' "
        "cellpadding='6' width='100%'>"
        "<tr><th>Descripción</th>"
        "<th>Cant.</th><th>Total</th></tr>"
        f"{filas}"
        "</table>"
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
