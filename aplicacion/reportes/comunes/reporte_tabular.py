from __future__ import annotations

from pathlib import Path

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)
from aplicacion.framework.reportes.reporte_tabla import (
    html_reporte_tabla,
)


def _construir_pdf_tabular(
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


def filas_dict_a_tabla_pdf(
    filas: list[dict],
    campos: list[str],
    *,
    columnas_numericas: set[int] | None = None,
    formateadores: dict | None = None,
) -> list[list[str]]:

    numericas = columnas_numericas or set()
    formateadores = formateadores or {}

    filas_pdf: list[list[str]] = []

    for fila in filas:

        valores: list[str] = []

        for indice, campo in enumerate(
            campos,
        ):

            valor = fila.get(
                campo,
                "",
            )

            if indice in formateadores:

                valores.append(
                    str(
                        formateadores[
                            indice
                        ](
                            valor,
                        ),
                    ),
                )

            elif indice in numericas:

                valores.append(
                    f"{float(valor or 0):,.2f}",
                )

            else:

                valores.append(
                    str(
                        valor or "",
                    ),
                )

        filas_pdf.append(
            valores,
        )

    return filas_pdf


def crear_reporte_tabular(
    *,
    titulo: str,
    numero: str,
    subtitulo: str = "",
    columnas: list[str],
    filas: list[list[str]],
    pie: str = "",
    nombre_pdf: str | None = None,
) -> ReporteDocumentoGenerico:

    dto = {
        "titulo": titulo,
        "numero": numero,
        "subtitulo": subtitulo,
        "columnas": columnas,
        "filas": filas,
        "pie": pie,
    }

    html = html_reporte_tabla(
        titulo=titulo,
        subtitulo=subtitulo,
        columnas=columnas,
        filas=filas,
        pie=pie,
    )

    return ReporteDocumentoGenerico(
        titulo=titulo,
        numero=numero,
        generar_html_fn=lambda: html,
        nombre_pdf=(
            nombre_pdf
            or f"{titulo} {numero}.pdf"
        ),
        formato_pagina="carta",
        construir_pdf_reportlab_fn=lambda ruta: _construir_pdf_tabular(
            dto,
            ruta,
        ),
    )
