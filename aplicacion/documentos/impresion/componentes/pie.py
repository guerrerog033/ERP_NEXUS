from __future__ import annotations

from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from aplicacion.documentos.impresion.componentes.qr import (
    qr_imagen,
)
from aplicacion.framework.reportes.pdf.estilos import (
    estilos_reportlab,
)


def construir_pie_electronico(
    documento: dict,
    *,
    estilos=None,
):

    if estilos is None:

        estilos = estilos_reportlab()

    cufe = str(
        documento.get(
            "cufe",
            "",
        )
        or "",
    ).strip()

    if (
        not cufe
        and not documento.get(
            "qr_url",
        )
    ):

        return []

    qr = qr_imagen(
        documento.get(
            "qr_url",
            cufe,
        ),
    )

    texto = [
        Paragraph(
            "<b>Información electrónica</b>",
            estilos["subtitulo"],
        ),
        Paragraph(
            f"<b>CUFE:</b> {cufe}",
            estilos["pequeno"],
        ),
    ]

    if documento.get(
        "estado_dian",
    ):

        texto.append(
            Paragraph(
                f"<b>Estado DIAN:</b> {documento['estado_dian']}",
                estilos["normal"],
            ),
        )

    if documento.get(
        "fecha_validacion_dian",
    ):

        texto.append(
            Paragraph(
                (
                    f"<b>Validación:</b> "
                    f"{documento['fecha_validacion_dian']}"
                ),
                estilos["normal"],
            ),
        )

    if documento.get(
        "autorizacion",
    ):

        texto.append(
            Paragraph(
                f"<b>Resolución:</b> {documento['autorizacion']}",
                estilos["normal"],
            ),
        )

    tabla = Table(
        [
            [
                qr,
                texto,
            ],
        ],
        colWidths=[
            90,
            420,
        ],
    )

    tabla.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
            ],
        ),
    )

    return [
        Spacer(
            1,
            6,
        ),
        tabla,
    ]


def construir_observaciones(
    texto: str,
    *,
    estilos=None,
):

    if not str(
        texto or "",
    ).strip():

        return []

    if estilos is None:

        estilos = estilos_reportlab()

    return [
        Paragraph(
            f"<b>Observaciones:</b> {texto}",
            estilos["normal"],
        ),
    ]
