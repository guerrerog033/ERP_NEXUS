from __future__ import annotations

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)
from aplicacion.reportes.comunes.reporte_tabular import (
    crear_reporte_tabular,
)


def crear_reporte_antiguedad_cartera(
    filas: list[dict],
    *,
    titulo_cartera: str,
    nombre_pdf: str | None = None,
) -> ReporteDocumentoGenerico:

    columnas = [
        "Rango",
        "Saldo",
    ]

    filas_pdf: list[list[str]] = []
    total = 0.0

    for fila in filas:

        saldo = float(
            fila.get(
                "saldo",
                0,
            )
            or 0,
        )

        total += saldo

        filas_pdf.append(
            [
                str(
                    fila.get(
                        "rango",
                        "",
                    ),
                ),
                f"{saldo:,.2f}",
            ],
        )

    filas_pdf.append(
        [
            "Total",
            f"{total:,.2f}",
        ],
    )

    return crear_reporte_tabular(
        titulo="Antigüedad de saldos",
        numero=titulo_cartera,
        subtitulo="Distribución por vencimiento",
        columnas=columnas,
        filas=filas_pdf,
        pie=f"Total cartera: {total:,.2f}",
        nombre_pdf=(
            nombre_pdf
            or f"Antiguedad {titulo_cartera}.pdf"
        ),
    )


def crear_reporte_resumen_cartera(
    filas: list[dict],
    *,
    nombre_pdf: str | None = None,
) -> ReporteDocumentoGenerico:

    from aplicacion.interfaz.kpis_inicio import (
        formatear_moneda,
    )

    columnas = [
        "Concepto",
        "Valor",
    ]

    filas_pdf = [
        [
            str(
                fila.get(
                    "concepto",
                    "",
                ),
            ),
            formatear_moneda(
                fila.get(
                    "valor",
                    0,
                ),
            ),
        ]
        for fila in filas
    ]

    return crear_reporte_tabular(
        titulo="Resumen de cartera",
        numero="Consolidado",
        subtitulo="CxC, CxP y vencidos",
        columnas=columnas,
        filas=filas_pdf,
        nombre_pdf=(
            nombre_pdf
            or "Resumen cartera.pdf"
        ),
    )
