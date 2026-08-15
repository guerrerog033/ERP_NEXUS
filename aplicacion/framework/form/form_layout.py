from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class FormLayout:
    """
    Describe la distribución lógica del formulario.

    No conoce:
        - PySide6
        - Widgets
        - FormBuilder

    Solo indica cómo organizar los grupos.
    """

    # =====================================================
    # Columnas
    # =====================================================

    columnas: list[list[str]] = field(
        default_factory=list
    )

    # =====================================================
    # Proporción entre columnas
    #
    # (1,1)
    # (2,1)
    # (3,2)
    # =====================================================

    proporcion: tuple[int, ...] = ()

    # =====================================================
    # Separación entre columnas
    # =====================================================

    separacion: int = 20

    # =====================================================
    # Márgenes del formulario
    # =====================================================

    margen: int = 10

    # =====================================================
    # Separación entre grupos
    # =====================================================

    separacion_grupos: int = 16