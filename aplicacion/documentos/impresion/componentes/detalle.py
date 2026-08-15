from __future__ import annotations

from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from aplicacion.framework.reportes.pdf.componentes import (
    bloque_totales,
    dinero,
    tabla_detalle,
)
from aplicacion.framework.reportes.pdf.estilos import (
    estilos_reportlab,
)


def construir_tabla_detalle(
    items: list[dict],
    *,
    estilos=None,
    incluir_codigo: bool = True,
):

    if estilos is None:

        estilos = estilos_reportlab()

    return tabla_detalle(
        items,
        estilos,
    )


def construir_bloque_totales(
    subtotal,
    descuento,
    impuestos,
    total,
    *,
    total_letras: str = "",
    estilos=None,
):

    if estilos is None:

        estilos = estilos_reportlab()

    bloque = [
        bloque_totales(
            subtotal,
            descuento,
            impuestos,
            total,
            estilos,
        ),
    ]

    if total_letras:

        bloque.extend(
            [
                Spacer(
                    1,
                    4,
                ),
                Paragraph(
                    f"<b>SON:</b> {total_letras}",
                    estilos["normal"],
                ),
            ],
        )

    return bloque


def construir_tabla_logistica(
    items: list[dict],
    *,
    estilos=None,
):

    if estilos is None:

        estilos = estilos_reportlab()

    encabezado = [
        "#",
        "DESCRIPCIÓN",
        "SOLICITADA",
        "ENTREGADA",
        "UNIDAD",
        "OBS.",
    ]

    filas = [
        encabezado,
    ]

    for indice, item in enumerate(
        items,
        start=1,
    ):

        filas.append(
            [
                str(
                    indice,
                ),
                str(
                    item.get(
                        "descripcion",
                        "",
                    )
                    or "",
                ),
                str(
                    item.get(
                        "cantidad",
                        item.get(
                            "cantidad_solicitada",
                            "",
                        ),
                    )
                    or "",
                ),
                str(
                    item.get(
                        "cantidad_entregada",
                        item.get(
                            "cantidad",
                            "",
                        ),
                    )
                    or "",
                ),
                str(
                    item.get(
                        "unidad",
                        "",
                    )
                    or "",
                ),
                str(
                    item.get(
                        "observacion",
                        "",
                    )
                    or "",
                ),
            ],
        )

    tabla = Table(
        filas,
        repeatRows=1,
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
                    "#1B4F8A",
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    "white",
                ),
            ],
        ),
    )

    return tabla


def construir_aplicacion_cartera(
    lineas: list[dict],
    *,
    estilos=None,
):

    if (
        not lineas
    ):

        return []

    if estilos is None:

        estilos = estilos_reportlab()

    encabezado = [
        "Documento",
        "Saldo anterior",
        "Aplicado",
        "Saldo restante",
    ]

    filas = [
        encabezado,
    ]

    for linea in lineas:

        filas.append(
            [
                str(
                    linea.get(
                        "documento",
                        "",
                    )
                    or "",
                ),
                dinero(
                    linea.get(
                        "saldo_anterior",
                        0,
                    ),
                ),
                dinero(
                    linea.get(
                        "valor_aplicado",
                        linea.get(
                            "valor",
                            0,
                        ),
                    ),
                ),
                dinero(
                    linea.get(
                        "saldo_restante",
                        0,
                    ),
                ),
            ],
        )

    tabla = Table(
        filas,
        repeatRows=1,
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
            ],
        ),
    )

    return [
        Paragraph(
            "<b>Aplicado a:</b>",
            estilos["normal"],
        ),
        tabla,
    ]
