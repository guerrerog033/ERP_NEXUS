from __future__ import annotations

from dataclasses import dataclass

from .text_field import TextField


@dataclass(slots=True)
class EmailField(TextField):

    widget: str = "text"

    lower: bool = True

    remove_multiple_spaces: bool = False

    def __post_init__(self):

        super().__post_init__()

        from .validators import Email

        self.validadores.append(
            Email()
        )