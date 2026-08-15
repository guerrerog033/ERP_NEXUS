from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .field import Field


@dataclass(slots=True)
class LookupField(Field):
    """
    Campo de búsqueda (Lookup).

    Solo describe el comportamiento del campo.

    No conoce:

        • Qt
        • LookupWidget
        • Widgets
    """

    widget: str = "lookup"

    datasource: type | None = None

    texto: str = ""

    permitir_vacio: bool = False

    # =====================================================
    # Inicialización
    # =====================================================

    def __post_init__(self):

        super().__post_init__()

        if self.datasource is None:

            raise RuntimeError(

                "LookupField requiere un datasource."

            )