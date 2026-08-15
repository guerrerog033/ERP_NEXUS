from __future__ import annotations

from dataclasses import dataclass

from .text_field import TextField


@dataclass(slots=True)
class TextAreaField(TextField):
    """
    Campo de texto multilínea.
    """

    widget: str = "textarea"

    alto: int = 110