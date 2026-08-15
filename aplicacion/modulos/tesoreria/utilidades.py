from __future__ import annotations


def calcular_estado_pago(
    total: float,
    valor_pagado: float,
) -> str:

    total = float(
        total or 0,
    )

    pagado = float(
        valor_pagado or 0,
    )

    if total <= 0:

        return "pagada"

    if pagado <= 0:

        return "pendiente"

    if pagado >= total - 0.01:

        return "pagada"

    return "parcial"


def saldo_factura(
    total: float,
    valor_pagado: float,
) -> float:

    return max(
        float(
            total or 0,
        )
        - float(
            valor_pagado or 0,
        ),
        0.0,
    )
