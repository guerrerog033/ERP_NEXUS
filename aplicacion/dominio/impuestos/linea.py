from __future__ import annotations


def calcular_linea(
    cantidad: float,
    precio: float,
    porcentaje_impuesto: float = 0.0,
    *,
    precio_incluye_iva: bool = False,
) -> tuple[float, float]:
    """
    Calcula subtotal e importe con impuesto de una línea.

    Retorna ``(subtotal, total_con_impuesto)`` redondeados a 2 decimales.
    """

    cantidad = float(
        cantidad or 0,
    )

    precio = float(
        precio or 0,
    )

    porcentaje = float(
        porcentaje_impuesto or 0,
    )

    bruto = cantidad * precio

    if precio_incluye_iva and porcentaje > 0:
        subtotal = bruto / (
            1 + porcentaje / 100
        )
        total_con_iva = bruto
    else:
        subtotal = bruto
        total_con_iva = subtotal * (
            1 + porcentaje / 100
        )

    return (
        round(
            subtotal,
            2,
        ),
        round(
            total_con_iva,
            2,
        ),
    )
