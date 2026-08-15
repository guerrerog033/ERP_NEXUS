from __future__ import annotations

from aplicacion.maestros.impuestos.repositorio import (
    RepositorioImpuesto,
)


OPCIONES_IVA = (
    (
        "IVA19",
        "IVA 19%",
    ),
    (
        "IVA5",
        "IVA 5%",
    ),
    (
        "EXE0",
        "IVA 0%",
    ),
)

CODIGO_IVA_PREDETERMINADO = "IVA19"


def opciones_iva_combo() -> list[
    tuple[
        str,
        int,
    ]
]:

    opciones: list[
        tuple[
            str,
            int,
        ]
    ] = []

    for codigo, etiqueta in OPCIONES_IVA:

        impuesto = RepositorioImpuesto.obtener_por_codigo(
            codigo,
        )

        if impuesto is None:

            continue

        opciones.append(
            (
                etiqueta,
                impuesto.id,
            ),
        )

    return opciones


def id_iva_predeterminado():

    impuesto = RepositorioImpuesto.obtener_por_codigo(
        CODIGO_IVA_PREDETERMINADO,
    )

    if impuesto is None:

        return None

    return impuesto.id


def indice_por_codigo(
    codigo: str,
) -> int:

    codigo = str(
        codigo,
    ).strip().upper()

    for indice, (
        item_codigo,
        _etiqueta,
    ) in enumerate(
        OPCIONES_IVA,
    ):

        if item_codigo == codigo:

            return indice

    return 0
