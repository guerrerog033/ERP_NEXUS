from __future__ import annotations

from pathlib import Path

from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from aplicacion.framework.reportes.pdf.estilos import (
    estilos_reportlab,
)


def _logo_imagen(
    ruta: str | None,
    *,
    ancho: float = 28 * mm,
):

    if not ruta:

        return Spacer(
            1,
            1,
        )

    archivo = Path(
        ruta,
    )

    if not archivo.is_file():

        return Spacer(
            1,
            1,
        )

    return Image(
        str(
            archivo,
        ),
        width=ancho,
        height=ancho * 0.45,
    )


def construir_encabezado_empresa(
    empresa: dict,
    *,
    titulo_documento: str,
    numero: str = "",
    estilos=None,
    incluir_logo: bool = True,
):

    if estilos is None:

        estilos = estilos_reportlab()

    razon = (
        empresa.get(
            "razon_social",
        )
        or empresa.get(
            "nombre",
            "",
        )
        or ""
    )

    nit = str(
        empresa.get(
            "nit",
            "",
        )
        or "",
    ).strip()

    dv = str(
        empresa.get(
            "dv",
            "",
        )
        or "",
    ).strip()

    nit_texto = nit

    if dv:

        nit_texto = f"{nit}-{dv}"

    bloque_empresa = [
        Paragraph(
            f"<b>{razon}</b>",
            estilos["titulo"],
        ),
        Paragraph(
            f"NIT: {nit_texto}",
            estilos["normal"],
        ),
        Paragraph(
            str(
                empresa.get(
                    "direccion",
                    "",
                )
                or "",
            ),
            estilos["normal"],
        ),
        Paragraph(
            (
                f"{empresa.get('telefono', '')}"
                f" · "
                f"{empresa.get('ciudad', '')}"
            ).strip(
                " · ",
            ),
            estilos["normal"],
        ),
        Paragraph(
            str(
                empresa.get(
                    "correo",
                    "",
                )
                or "",
            ),
            estilos["normal"],
        ),
    ]

    bloque_documento = [
        Paragraph(
            f"<b>{titulo_documento}</b>",
            estilos["titulo"],
        ),
    ]

    if numero:

        bloque_documento.append(
            Paragraph(
                f"<b>No. {numero}</b>",
                estilos["subtitulo"],
            ),
        )

    logo = (
        _logo_imagen(
            empresa.get(
                "logo",
            ),
        )
        if incluir_logo
        else Spacer(
            1,
            1,
        )
    )

    tabla = Table(
        [
            [
                [
                    logo,
                    Spacer(
                        1,
                        2 * mm,
                    ),
                    *bloque_empresa,
                ],
                bloque_documento,
            ],
        ],
        colWidths=[
            320,
            190,
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
        tabla,
        Spacer(
            1,
            4 * mm,
        ),
    ]


def construir_meta_documento(
    filas: list[
        tuple[
            str,
            str,
        ]
    ],
    *,
    estilos=None,
):

    if estilos is None:

        estilos = estilos_reportlab()

    if not filas:

        return []

    contenido = []

    for etiqueta, valor in filas:

        if not str(
            valor or "",
        ).strip():

            continue

        contenido.append(
            Paragraph(
                f"<b>{etiqueta}:</b> {valor}",
                estilos["normal"],
            ),
        )

    if not contenido:

        return []

    return [
        *contenido,
        Spacer(
            1,
            3 * mm,
        ),
    ]
