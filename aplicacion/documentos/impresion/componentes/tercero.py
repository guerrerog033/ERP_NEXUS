from __future__ import annotations

from reportlab.platypus import (
    Paragraph,
    Table,
    TableStyle,
)

from aplicacion.framework.reportes.pdf.estilos import (
    AZUL_CLARO,
    GRIS_BORDE,
    estilos_reportlab,
)


def construir_bloque_tercero(
    tercero: dict,
    *,
    titulo: str = "CLIENTE",
    estilos=None,
):

    if estilos is None:

        estilos = estilos_reportlab()

    documento = str(
        tercero.get(
            "documento",
            tercero.get(
                "nit",
                "",
            ),
        )
        or "",
    ).strip()

    dv = str(
        tercero.get(
            "dv",
            "",
        )
        or "",
    ).strip()

    if (
        documento
        and dv
        and not documento.endswith(
            f"-{dv}",
        )
    ):

        documento = f"{documento}-{dv}"

    filas = [
        [
            Paragraph(
                f"<b>{titulo}</b>",
                estilos["normal"],
            ),
        ],
        [
            Paragraph(
                f"<b>Nombre:</b> {tercero.get('nombre', '')}",
                estilos["normal"],
            ),
        ],
        [
            Paragraph(
                f"<b>Documento:</b> {documento}",
                estilos["normal"],
            ),
        ],
        [
            Paragraph(
                f"<b>Dirección:</b> {tercero.get('direccion', '')}",
                estilos["normal"],
            ),
        ],
        [
            Paragraph(
                (
                    f"<b>Ciudad:</b> {tercero.get('ciudad', '')}"
                    f" · <b>Depto:</b> {tercero.get('departamento', '')}"
                ).strip(),
                estilos["normal"],
            ),
        ],
        [
            Paragraph(
                f"<b>Teléfono:</b> {tercero.get('telefono', '')}",
                estilos["normal"],
            ),
        ],
        [
            Paragraph(
                f"<b>Correo:</b> {tercero.get('correo', '')}",
                estilos["normal"],
            ),
        ],
    ]

    tabla = Table(
        filas,
        colWidths=[
            510,
        ],
    )

    tabla.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    AZUL_CLARO,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    GRIS_BORDE,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.25,
                    GRIS_BORDE,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
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
            ],
        ),
    )

    return tabla
