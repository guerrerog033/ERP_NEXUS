from __future__ import annotations

from datetime import date, timedelta


BUCKETS_ANTIGUEDAD = (
    ("Al día", 0, 0),
    ("1 - 30 días", 1, 30),
    ("31 - 60 días", 31, 60),
    ("61 - 90 días", 61, 90),
    ("Más de 90 días", 91, None),
)


def calcular_fecha_vencimiento(
    fecha_emision: date | None,
    dias_credito: int | None,
    *,
    fecha_vencimiento: date | None = None,
) -> date | None:

    if fecha_vencimiento is not None:

        return fecha_vencimiento

    if fecha_emision is None:

        return None

    dias = int(
        dias_credito or 0,
    )

    if dias <= 0:

        return fecha_emision

    return fecha_emision + timedelta(
        days=dias,
    )


def dias_mora(
    fecha_vencimiento: date | None,
    *,
    referencia: date | None = None,
) -> int:

    if fecha_vencimiento is None:

        return 0

    hoy = referencia or date.today()

    delta = (
        hoy - fecha_vencimiento
    ).days

    return max(
        delta,
        0,
    )


def bucket_antiguedad(
    dias: int,
) -> str:

    if dias <= 0:

        return BUCKETS_ANTIGUEDAD[0][0]

    if dias <= 30:

        return BUCKETS_ANTIGUEDAD[1][0]

    if dias <= 60:

        return BUCKETS_ANTIGUEDAD[2][0]

    if dias <= 90:

        return BUCKETS_ANTIGUEDAD[3][0]

    return BUCKETS_ANTIGUEDAD[4][0]
