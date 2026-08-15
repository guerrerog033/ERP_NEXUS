from __future__ import annotations

from dataclasses import dataclass

from .field import Field


@dataclass(slots=True)
class CheckField(Field):
    """
    Campo booleano.

    Solo describe el campo.
    No conoce Qt.
    """

    widget: str = "check"

    texto: str = ""

    # =====================================================
    # Inicialización
    # =====================================================

    def __post_init__(self):

        super().__post_init__()

        if not self.texto:

            self.texto = self.titulo

    @property
    def etiqueta_visible(self):

        return False

    @property
    def ocupa_fila_completa(self):

        return True