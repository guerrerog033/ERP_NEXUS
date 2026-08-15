from __future__ import annotations

from sqlalchemy import Numeric


DINERO = Numeric(
    18,
    2,
)

CANTIDAD = Numeric(
    18,
    4,
)

PORCENTAJE = Numeric(
    8,
    4,
)

TASA = Numeric(
    18,
    6,
)

COORDENADA = Numeric(
    10,
    7,
)
