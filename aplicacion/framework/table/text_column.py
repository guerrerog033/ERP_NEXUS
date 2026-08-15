from __future__ import annotations

from dataclasses import dataclass

from .column import Column


@dataclass(slots=True)
class TextColumn(Column):
    """
    Columna de texto.
    """

    widget: str = "text"

    longitud_maxima: int | None = None

    recortar: bool = False

    mayusculas: bool = False

    minusculas: bool = False

    capitalizar: bool = False