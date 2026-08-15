from __future__ import annotations

import io

import qrcode
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, Spacer, Table, TableStyle

from .estilos import (
    AZUL_CLARO,
    AZUL_NEXUS,
    BLANCO,
    GRIS_BORDE,
    GRIS_CLARO,
)


def texto(valor) -> str:

    if valor is None:

        return ""

    return str(valor)


def dinero(valor) -> str:

    if valor is None:

        valor = 0

    return f"${float(valor):,.0f}".replace(",", ".")


def qr_imagen(
    contenido: str,
    tamaño: float = 28,
):

    if not str(
        contenido or "",
    ).strip():

        return Spacer(
            1,
            1,
        )

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=2,
    )

    qr.add_data(
        contenido,
    )

    qr.make(
        fit=True,
    )

    imagen = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    buffer = io.BytesIO()

    imagen.save(
        buffer,
        format="PNG",
    )

    buffer.seek(
        0,
    )

    return Image(
        buffer,
        width=tamaño,
        height=tamaño,
    )


def tabla_detalle(
    filas,
    estilos,
):

    encabezado = [
        "#",
        "DESCRIPCIÓN",
        "CANT.",
        "PRECIO",
        "DESCUENTO",
        "IMPUESTOS",
        "TOTAL",
    ]

    datos = [
        [
            Paragraph(
                str(valor),
                estilos["normal"],
            )
            for valor in encabezado
        ]
    ]

    for fila in filas:

        datos.append(
            [
                Paragraph(
                    texto(
                        fila.get(
                            "numero",
                        ),
                    ),
                    estilos["centro"],
                ),
                Paragraph(
                    texto(
                        fila.get(
                            "descripcion",
                        ),
                    ),
                    estilos["normal"],
                ),
                Paragraph(
                    texto(
                        fila.get(
                            "cantidad",
                        ),
                    ),
                    estilos["centro"],
                ),
                Paragraph(
                    dinero(
                        fila.get(
                            "precio",
                        ),
                    ),
                    estilos["derecha"],
                ),
                Paragraph(
                    dinero(
                        fila.get(
                            "descuento",
                        ),
                    ),
                    estilos["derecha"],
                ),
                Paragraph(
                    dinero(
                        fila.get(
                            "impuestos",
                        ),
                    ),
                    estilos["derecha"],
                ),
                Paragraph(
                    dinero(
                        fila.get(
                            "total",
                        ),
                    ),
                    estilos["derecha_bold"],
                ),
            ]
        )

    tabla = Table(
        datos,
        colWidths=[
            8 * mm,
            65 * mm,
            14 * mm,
            25 * mm,
            25 * mm,
            25 * mm,
            28 * mm,
        ],
        repeatRows=1,
    )

    tabla.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    AZUL_NEXUS,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    BLANCO,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, 0),
                    "CENTER",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    GRIS_BORDE,
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        BLANCO,
                        GRIS_CLARO,
                    ],
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    return tabla


def bloque_totales(
    subtotal,
    descuento,
    impuestos,
    total,
    estilos,
):

    datos = [
        [
            "",
            Paragraph(
                "SUBTOTAL",
                estilos["normal"],
            ),
            Paragraph(
                dinero(subtotal),
                estilos["derecha"],
            ),
        ],
        [
            "",
            Paragraph(
                "DESCUENTO",
                estilos["normal"],
            ),
            Paragraph(
                dinero(descuento),
                estilos["derecha"],
            ),
        ],
        [
            "",
            Paragraph(
                "IMPUESTOS",
                estilos["normal"],
            ),
            Paragraph(
                dinero(impuestos),
                estilos["derecha"],
            ),
        ],
        [
            "",
            Paragraph(
                "<b>TOTAL</b>",
                estilos["normal"],
            ),
            Paragraph(
                f"<b>{dinero(total)}</b>",
                estilos["derecha_bold"],
            ),
        ],
    ]

    tabla = Table(
        datos,
        colWidths=[
            80 * mm,
            45 * mm,
            40 * mm,
        ],
    )

    tabla.setStyle(
        TableStyle(
            [
                (
                    "LINEABOVE",
                    (1, -1),
                    (-1, -1),
                    1,
                    AZUL_NEXUS,
                ),
                (
                    "BACKGROUND",
                    (1, -1),
                    (-1, -1),
                    AZUL_CLARO,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    return tabla
