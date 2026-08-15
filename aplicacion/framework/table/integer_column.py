from __future__ import annotations

from dataclasses import dataclass

from .column import Column


@dataclass(slots=True)
class IntegerColumn(Column):
    """
    Columna numérica entera.
    """

    widget: str = "integer"

    minimo: int | None = None

    maximo: int | None = None

    alineacion: str = "right"