from __future__ import annotations

import calendar
from datetime import date, timedelta

PERIODICIDADES = (
    ("quincenal", "Quincenal"),
    ("mensual", "Mensual"),
    ("trimestral", "Trimestral"),
    ("anual", "Anual"),
)

_MESES_POR_PERIODICIDAD = {
    "mensual": 1,
    "trimestral": 3,
    "anual": 12,
}


def sumar_meses(
    fecha: date,
    meses: int,
) -> date:

    mes_total = fecha.month - 1 + meses

    anio = fecha.year + mes_total // 12

    mes = mes_total % 12 + 1

    ultimo_dia = calendar.monthrange(
        anio,
        mes,
    )[1]

    return date(
        anio,
        mes,
        min(fecha.day, ultimo_dia),
    )


def calcular_proxima_fecha(
    fecha_actual: date,
    periodicidad: str,
) -> date:

    if periodicidad == "quincenal":

        return fecha_actual + timedelta(days=15)

    meses = _MESES_POR_PERIODICIDAD.get(
        periodicidad,
    )

    if meses is None:

        raise ValueError(
            f"Periodicidad desconocida: '{periodicidad}'.",
        )

    return sumar_meses(
        fecha_actual,
        meses,
    )
