from __future__ import annotations

from dataclasses import dataclass

from .field import Field


@dataclass(slots=True)
class DateField(Field):
    """
    Campo para fechas.
    """

    widget: str = "date"

    mostrar_calendario: bool = True

    formato: str = "dd/MM/yyyy"