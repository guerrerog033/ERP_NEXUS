from __future__ import annotations

from dataclasses import dataclass

from .column import Column


@dataclass(slots=True)
class StatusColumn(Column):
    """
    Columna de estado con badge semáforo en QTableView.
    """

    widget: str = "status"

    alineacion: str = "center"
