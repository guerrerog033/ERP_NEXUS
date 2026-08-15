from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from aplicacion.framework.reportes.pdf.estilos import (
    estilos_reportlab,
)


def construir_bloque_firmas(
    *,
    recibido_por: str = "",
    documento: str = "",
    transportador: str = "",
    vehiculo: str = "",
    estilos=None,
):

    if estilos is None:

        estilos = estilos_reportlab()

    filas = [
        [
            "Recibido por",
            "Documento",
            "Firma",
            "Fecha",
        ],
        [
            recibido_por,
            documento,
            "",
            "",
        ],
    ]

    extras = []

    if transportador:

        extras.append(
            Paragraph(
                f"<b>Transportador:</b> {transportador}",
                estilos["normal"],
            ),
        )

    if vehiculo:

        extras.append(
            Paragraph(
                f"<b>Vehículo:</b> {vehiculo}",
                estilos["normal"],
            ),
        )

    tabla = Table(
        filas,
        colWidths=[
            120,
            120,
            120,
            120,
        ],
    )

    tabla.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    "grey",
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    "#E8F0F8",
                ),
                (
                    "TOPPADDING",
                    (0, 1),
                    (-1, 1),
                    18,
                ),
            ],
        ),
    )

    bloque = [
        Spacer(
            1,
            6 * mm,
        ),
        *extras,
        tabla,
    ]

    return bloque
