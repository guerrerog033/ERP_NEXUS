from __future__ import annotations

from pathlib import Path

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)


def _construir_pdf_recibo_caja(
    recibo,
    ruta: str | Path,
    *,
    nombre_cliente: str,
    documento_cliente: str = "",
    correo_cliente: str = "",
) -> Path:

    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
        recibo_caja_a_dto,
    )
    from aplicacion.reportes.tesoreria.pdf.recibo_caja import (
        ReciboCajaPDF,
    )

    dto = recibo_caja_a_dto(
        recibo,
        nombre_cliente=nombre_cliente,
        documento_cliente=documento_cliente,
        correo_cliente=correo_cliente,
    )

    return ReciboCajaPDF(
        ruta,
        empresa_reporte(),
        dto,
    ).construir()


def crear_reporte_recibo_caja(
    recibo,
    *,
    nombre_cliente: str,
    documento_cliente: str = "",
    correo_cliente: str = "",
    telefono_cliente: str = "",
) -> ReporteDocumentoGenerico:

    numero = str(
        recibo.numero or "",
    )

    return ReporteDocumentoGenerico(
        titulo="Recibo de caja",
        numero=numero,
        generar_html_fn=lambda: __import__(
            "aplicacion.modulos.tesoreria.recibos_caja.formatos_impresion",
            fromlist=[
                "generar_html_recibo",
            ],
        ).generar_html_recibo(
            recibo,
            nombre_cliente=nombre_cliente,
            documento_cliente=documento_cliente,
            correo_cliente=correo_cliente,
        ),
        nombre_pdf=f"Recibo caja {numero}.pdf",
        correo_destino=correo_cliente,
        telefono_destino=telefono_cliente,
        texto_whatsapp=(
            f"Recibo de caja {numero} — "
            f"${float(recibo.valor_total or 0):,.0f}"
        ),
        formato_pagina="media_carta",
        construir_pdf_reportlab_fn=lambda ruta: _construir_pdf_recibo_caja(
            recibo,
            ruta,
            nombre_cliente=nombre_cliente,
            documento_cliente=documento_cliente,
            correo_cliente=correo_cliente,
        ),
    )
