from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .field import Field


@dataclass(slots=True)
class ComboField(Field):

    widget: str = "combo"

    opciones: list[tuple[str, Any]] = field(
        default_factory=list
    )

    editable: bool = False

    permitir_vacio: bool = False

    ordenar: bool = False

    def __post_init__(self):

        super().__post_init__()

        if self.ordenar:

            self.opciones.sort(
                key=lambda opcion: opcion[0]
            )

    def agregar(
        self,
        texto: str,
        valor: Any,
    ):

        self.opciones.append(
            (
                texto,
                valor,
            )
        )

        if self.ordenar:

            self.opciones.sort(
                key=lambda opcion: opcion[0]
            )

    def obtener_opciones(
        self,
    ) -> list[tuple[str, Any]]:

        return list(
            self.opciones
        )