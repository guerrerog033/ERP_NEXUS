from __future__ import annotations

from dataclasses import dataclass

from .field import Field


@dataclass(slots=True)
class IntegerField(Field):
    """
    Campo numérico entero.
    """

    widget: str = "integer"

    minimo: int = -(2**31)

    maximo: int = 2**31 - 1

    paso: int = 1