from __future__ import annotations

from typing import Callable

from .linea import calcular_linea


def calcular_totales_lineas(
    lineas: list[dict],
    resolver_porcentaje: Callable[[dict], float] | None = None,
    *,
    clave_cantidad: str = "cantidad",
    clave_precio: str = "precio_unitario",
    clave_impuesto: str = "impuesto_id",
    clave_incluye_iva: str = "precio_incluye_iva",
) -> tuple[float, float, float]:
    """
    Agrega subtotal, IVA y total de un listado de líneas.

    Si ``resolver_porcentaje`` es None, cada línea debe incluir
    ``porcentaje_impuesto`` numérico.
    """

    subtotal = 0.0
    total_con_iva = 0.0

    for linea in lineas:
        if resolver_porcentaje is not None:
            porcentaje = resolver_porcentaje(
                linea,
            )
        else:
            porcentaje = float(
                linea.get(
                    "porcentaje_impuesto",
                    0,
                )
                or 0,
            )

        subtotal_linea, total_linea = calcular_linea(
            linea.get(
                clave_cantidad,
                0,
            ),
            linea.get(
                clave_precio,
                0,
            ),
            porcentaje,
            precio_incluye_iva=bool(
                linea.get(
                    clave_incluye_iva,
                    False,
                ),
            ),
        )

        linea["total_linea"] = total_linea
        subtotal += subtotal_linea
        total_con_iva += total_linea

    iva = round(
        total_con_iva - subtotal,
        2,
    )

    return (
        round(
            subtotal,
            2,
        ),
        iva,
        round(
            total_con_iva,
            2,
        ),
    )
