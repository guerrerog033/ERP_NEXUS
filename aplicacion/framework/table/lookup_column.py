from __future__ import annotations

from dataclasses import dataclass

from .column import Column


@dataclass(slots=True)
class LookupColumn(Column):
    """
    Columna de búsqueda.
    """

    widget: str = "lookup"

    descripcion: str = ""