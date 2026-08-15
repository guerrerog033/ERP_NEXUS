from __future__ import annotations

from dataclasses import dataclass

from .field import Field


@dataclass(slots=True)
class TextField(Field):
    """
    Campo de texto.

    Solo describe el comportamiento del campo.
    No conoce Qt ni crea widgets.
    """

    widget: str = "text"

    longitud_minima: int | None = None

    longitud_maxima: int | None = None

    trim: bool = True

    upper: bool = False

    lower: bool = False

    title: bool = False

    capitalize: bool = False

    remove_multiple_spaces: bool = True

    # =====================================================
    # Inicialización
    # =====================================================

    def __post_init__(self):

        super().__post_init__()

        from .validators import (
            Required,
            MinLength,
            MaxLength,
        )

        from .normalizers import (
            Trim,
            Upper,
            Lower,
            Title,
            Capitalize,
            RemoveMultipleSpaces,
        )

        if self.trim:
            self.normalizers.append(Trim())

        if self.upper:
            self.normalizers.append(Upper())

        if self.lower:
            self.normalizers.append(Lower())

        if self.title:
            self.normalizers.append(Title())

        if self.capitalize:
            self.normalizers.append(Capitalize())

        if self.remove_multiple_spaces:
            self.normalizers.append(
                RemoveMultipleSpaces()
            )

        if self.requerido:
            self.validadores.append(
                Required()
            )

        if self.longitud_minima is not None:
            self.validadores.append(
                MinLength(
                    self.longitud_minima
                )
            )

        if self.longitud_maxima is not None:
            self.validadores.append(
                MaxLength(
                    self.longitud_maxima
                )
            )