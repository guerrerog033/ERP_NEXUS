from __future__ import annotations

from dataclasses import dataclass

from .column import Column


@dataclass(slots=True)
class CheckColumn(Column):
    """
    Columna booleana.
    """

    widget: str = "check"

    alineacion: str = "center"