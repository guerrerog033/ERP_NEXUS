from __future__ import annotations

from dataclasses import dataclass

from .text_field import TextField


@dataclass(slots=True)
class PasswordField(TextField):
    """
    Campo para contraseñas.
    """

    widget: str = "password"