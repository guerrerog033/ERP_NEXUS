from __future__ import annotations

from pathlib import Path

from aplicacion.nucleo.configuracion import Configuracion

from .generador_pdf import exportar_html_pdf
from .reporte_base import ReporteDocumentoBase


def resolver_motor_pdf(
    reporte: ReporteDocumentoBase,
    *,
    motor: str | None = None,
) -> str:

    if motor:

        return motor

    configurado = Configuracion.obtener(
        "impresion",
        "motor_pdf",
    )

    if configurado in {
        "html",
        "reportlab",
    }:

        return str(
            configurado,
        )

    if reporte.soporta_pdf_reportlab():

        return "reportlab"

    return "html"


def exportar_pdf_reporte(
    reporte: ReporteDocumentoBase,
    ruta: str | Path,
    *,
    formato_pagina: str | None = None,
    motor: str | None = None,
) -> str:

    destino = str(
        ruta,
    )

    motor_resuelto = resolver_motor_pdf(
        reporte,
        motor=motor,
    )

    if motor_resuelto == "reportlab":

        try:

            return str(
                reporte.construir_pdf_reportlab(
                    destino,
                ),
            )

        except Exception:

            if not Configuracion.obtener(
                "impresion",
                "motor_pdf_html_respaldo",
                True,
            ):

                raise

    return exportar_html_pdf(
        reporte.generar_html(),
        destino,
        formato_pagina=(
            formato_pagina
            or reporte.formato_pagina_predeterminado()
        ),
    )
