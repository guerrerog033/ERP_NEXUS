from __future__ import annotations

from dataclasses import dataclass, field

from .field import Field


@dataclass(slots=True)
class FieldGroup:
    """
    Agrupa campos relacionados dentro de un formulario.

    No conoce:

        • Qt
        • Widgets
        • SQLAlchemy

    Solo describe la organización lógica
    del formulario.
    """

    # ==================================================
    # Identificación
    # ==================================================

    titulo: str

    # ==================================================
    # Campos
    # ==================================================

    campos: list[Field] = field(
        default_factory=list
    )

    # ==================================================
    # Presentación
    # ==================================================

    icono: str = ""

    visible: bool = True

    colapsable: bool = False

    expandido: bool = True

    # ==================================================
    # Distribución
    # ==================================================

    columnas: int = 1

    separacion: int = 16

    # ==================================================
    # Buscar campo
    # ==================================================

    def buscar(
        self,
        nombre: str,
    ) -> Field | None:

        for campo in self.campos:

            if campo.nombre == nombre:

                return campo

        return None

    # ==================================================
    # Nombres
    # ==================================================

    def nombres(
        self,
    ) -> list[str]:

        return [

            campo.nombre

            for campo in self.campos

        ]

    # ==================================================
    # Iterador
    # ==================================================

    def __iter__(
        self,
    ):

        return iter(
            self.campos
        )