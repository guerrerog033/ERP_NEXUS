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


def _campo(etiqueta: str, valor, estilos) -> Paragraph:

    return Paragraph(
        f"<b>{etiqueta}:</b> {str(valor or '').strip()}",
        estilos["normal"],
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

    ubicacion = " · ".join(
        parte
        for parte in (
            str(tercero.get("ciudad", "") or "").strip(),
            str(tercero.get("departamento", "") or "").strip(),
        )
        if parte
    )

    # Cabecera a todo el ancho + pares de campos en dos columnas
    # para no gastar media página en una sola columna.
    pares: list[tuple[str, str]] = [
        ("Nombre", tercero.get("nombre", "")),
        ("Documento", documento),
        ("Dirección", tercero.get("direccion", "")),
        ("Ciudad", ubicacion),
        ("Teléfono", tercero.get("telefono", "")),
        ("Correo", tercero.get("correo", "")),
    ]

    if str(tercero.get("regimen", "") or "").strip():

        pares.append(
            ("Régimen", tercero["regimen"]),
        )

    if str(tercero.get("responsabilidad_fiscal", "") or "").strip():

        pares.append(
            ("Resp. fiscal", tercero["responsabilidad_fiscal"]),
        )

    filas = [
        [
            Paragraph(
                f"<b>{titulo}</b>",
                estilos["normal"],
            ),
            "",
        ],
    ]

    for indice in range(0, len(pares), 2):

        izquierda = pares[indice]

        derecha = (
            pares[indice + 1]
            if indice + 1 < len(pares)
            else None
        )

        filas.append(
            [
                _campo(izquierda[0], izquierda[1], estilos),
                (
                    _campo(derecha[0], derecha[1], estilos)
                    if derecha is not None
                    else ""
                ),
            ],
        )

    tabla = Table(
        filas,
        colWidths=[
            255,
            255,
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
                    "SPAN",
                    (0, 0),
                    (-1, 0),
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
