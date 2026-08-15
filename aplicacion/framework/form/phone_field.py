from __future__ import annotations

from dataclasses import dataclass

from .text_field import TextField


@dataclass(slots=True)
class PhoneField(TextField):
    """
    Campo para teléfonos.
    """

    widget: str = "phone"

    mascara: str = ""