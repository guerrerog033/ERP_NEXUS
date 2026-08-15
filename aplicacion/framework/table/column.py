from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Column:
    """
    Clase base de todas las columnas del TableEngine.

    Es completamente declarativa.

    No conoce:

        • Qt
        • SQLAlchemy
        • Widgets
    """

    # =====================================================
    # Identificación
    # =====================================================

    nombre: str

    etiqueta: str = ""

    descripcion: str = ""

    # =====================================================
    # Presentación
    # =====================================================

    ancho: int | None = None

    stretch: bool = False

    visible: bool = True

    alineacion: str = "left"

    # =====================================================
    # Comportamiento
    # =====================================================

    sortable: bool = True

    editable: bool = False

    widget: str = "text"

    # =====================================================
    # Extensibilidad
    # =====================================================

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    atributos: dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # Inicialización
    # =====================================================

    def __post_init__(self):

        if not self.etiqueta:

            self.etiqueta = (
                self.nombre
                .replace("_", " ")
                .title()
            )

    # =====================================================
    # Compatibilidad
    # =====================================================

    @property
    def titulo(self):

        return self.etiqueta

    @titulo.setter
    def titulo(
        self,
        valor,
    ):

        self.etiqueta = valor

    @property
    def encabezado(self):

        return self.etiqueta

    # =====================================================
    # Metadata
    # =====================================================

    def meta(
        self,
        nombre,
        default=None,
    ):

        return self.metadata.get(
            nombre,
            default,
        )

    # =====================================================
    # Atributos
    # =====================================================

    def atributo(
        self,
        nombre,
        default=None,
    ):

        return self.atributos.get(
            nombre,
            default,
        )