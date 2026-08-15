from __future__ import annotations

from pathlib import Path

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)
from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    generar_html_cotizacion,
    normalizar_formato_codigo,
)


def _contacto(
    cliente,
) -> tuple[str, str]:

    if cliente is None:

        return "", ""

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
        or getattr(
            cliente,
            "celular",
            "",
        )
        or "",
    ).strip()

    return correo, telefono


def _construir_pdf_cotizacion(
    cotizacion,
    detalles,
    nombre_cliente: str,
    ruta: str | Path,
) -> Path:

    from aplicacion.reportes.comunes.datos_documento import (
        cotizacion_a_dto,
        empresa_reporte,
    )
    from aplicacion.reportes.ventas.pdf.cotizacion import (
        CotizacionPDF,
    )

    dto = cotizacion_a_dto(
        cotizacion,
        detalles,
        nombre_cliente,
    )

    return CotizacionPDF(
        ruta,
        empresa_reporte(),
        dto,
    ).construir()


def crear_reporte_cotizacion(
    cotizacion,
    detalles,
    nombre_cliente: str,
    *,
    cliente=None,
    formato: str | None = None,
) -> ReporteDocumentoGenerico:

    codigo = normalizar_formato_codigo(
        formato
        or getattr(
            cotizacion,
            "formato_impresion",
            None,
        ),
    )

    correo, telefono = _contacto(
        cliente,
    )

    numero = str(
        cotizacion.numero or "",
    )

    return ReporteDocumentoGenerico(
        titulo="Cotización",
        numero=numero,
        generar_html_fn=lambda: generar_html_cotizacion(
            cotizacion,
            detalles,
            nombre_cliente,
            formato=codigo,
        ),
        nombre_pdf=(
            f"Cotización No. {numero} "
            f"{nombre_cliente}.pdf".strip()
        ),
        correo_destino=correo,
        telefono_destino=telefono,
        asunto_correo=f"Cotización {numero}",
        cuerpo_correo=(
            f"Adjuntamos la cotización {numero}. "
            "Quedamos atentos a su respuesta."
        ),
        texto_whatsapp=(
            f"Cotización {numero} — "
            f"Total ${float(cotizacion.total or 0):,.0f}"
        ),
        construir_pdf_reportlab_fn=lambda ruta: _construir_pdf_cotizacion(
            cotizacion,
            detalles,
            nombre_cliente,
            ruta,
        ),
    )
