from __future__ import annotations

from dataclasses import dataclass

from .field import Field


@dataclass(slots=True)
class DecimalField(Field):
    """
    Campo numérico decimal.
    """

    widget: str = "decimal"

    minimo: float = -999999999.99

    maximo: float = 999999999.99

    decimales: int = 2

    paso: float = 0.01

    sufijo: str = ""

    prefijo: str = ""