from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class DataResult(Generic[T]):
    """
    Resultado estándar devuelto por cualquier DataSource.
    """

    registros: list[T] = field(default_factory=list)

    total: int = 0

    pagina: int = 1

    por_pagina: int = 0