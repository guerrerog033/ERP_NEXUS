from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def a_decimal(
    valor,
) -> Decimal | None:

    if valor is None or valor == "":

        return None

    try:

        return Decimal(
            str(valor),
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):

        return None


def formatear_decimal(
    valor,
    *,
    decimales: int = 2,
    prefijo: str = "",
    sufijo: str = "",
    miles: str = ".",
    decimal: str = ",",
) -> str:

    numero = a_decimal(
        valor,
    )

    if numero is None:

        return ""

    cuantia = numero.quantize(
        Decimal(
            "1"
            if decimales <= 0
            else "0."
            + (
                "0"
                * decimales
            ),
        ),
        rounding=ROUND_HALF_UP,
    )

    signo = ""

    if cuantia < 0:

        signo = "-"

        cuantia = abs(
            cuantia,
        )

    partes = f"{cuantia:.{decimales}f}".split(
        ".",
    )

    entero = partes[0]
    fraccion = (
        partes[1]
        if len(partes) > 1
        else ""
    )

    entero_fmt = ""

    for indice, digito in enumerate(
        reversed(
            entero,
        ),
    ):

        if (
            indice
            and indice
            % 3
            == 0
        ):

            entero_fmt = (
                miles
                + entero_fmt
            )

        entero_fmt = (
            digito
            + entero_fmt
        )

    texto = entero_fmt

    if decimales > 0:

        texto += (
            decimal
            + fraccion.ljust(
                decimales,
                "0",
            )[:decimales]
        )

    return (
        f"{prefijo}{signo}{texto}{sufijo}"
    )
