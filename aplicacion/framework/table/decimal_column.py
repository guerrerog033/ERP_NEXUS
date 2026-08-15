from __future__ import annotations

from dataclasses import dataclass

from .column import Column


@dataclass(slots=True)
class DecimalColumn(Column):
    """
    Columna numérica decimal.
    """

    widget: str = "decimal"

    decimales: int = 2

    alineacion: str = "right"

    formato: str = ""