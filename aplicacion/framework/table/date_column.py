from __future__ import annotations

from dataclasses import dataclass

from .column import Column


@dataclass(slots=True)
class DateColumn(Column):
    """
    Columna de fechas.
    """

    widget: str = "date"

    formato: str = "%d/%m/%Y"

    alineacion: str = "center"