from __future__ import annotations

from pathlib import Path

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)
from aplicacion.modulos.ventas.remisiones.formatos_impresion import (
    generar_html_remision,
)


def _construir_pdf_remision(
    remision,
    detalles,
    nombre_cliente: str,
    ruta: str | Path,
) -> Path:

    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
        remision_a_dto,
    )
    from aplicacion.reportes.ventas.pdf.remision import (
        RemisionPDF,
    )

    dto = remision_a_dto(
        remision,
        detalles,
        nombre_cliente,
    )

    return RemisionPDF(
        ruta,
        empresa_reporte(),
        dto,
    ).construir()


def crear_reporte_remision(
    remision,
    detalles,
    nombre_cliente: str,
    *,
    cliente=None,
    formato: str | None = None,
) -> ReporteDocumentoGenerico:

    numero = str(
        remision.numero or "",
    )

    correo = ""
    telefono = ""

    if cliente is not None:

        correo = str(
            getattr(
                cliente,
                "correo",
                "",
            )
            or "",
        ).strip()

        telefono = str(
            getattr(
                cliente,
                "telefono",
                "",
            )
            or "",
        ).strip()

    return ReporteDocumentoGenerico(
        titulo="Remisión",
        numero=numero,
        generar_html_fn=lambda: generar_html_remision(
            remision,
            detalles,
            nombre_cliente,
            formato=formato,
        ),
        nombre_pdf=f"Remisión {numero}.pdf",
        correo_destino=correo,
        telefono_destino=telefono,
        texto_whatsapp=f"Remisión {numero} — despacho registrado",
        construir_pdf_reportlab_fn=lambda ruta: _construir_pdf_remision(
            remision,
            detalles,
            nombre_cliente,
            ruta,
        ),
    )
