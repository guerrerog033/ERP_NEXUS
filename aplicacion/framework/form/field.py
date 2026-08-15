from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Field:
    """
    Clase base de todos los campos del FormEngine.

    Es completamente declarativa.

    No conoce:

        • Qt
        • SQLAlchemy
        • Widgets

    Solo describe el campo.
    """

    # =====================================================
    # Identificación
    # =====================================================

    nombre: str

    titulo: str = ""

    descripcion: str = ""

    # =====================================================
    # Presentación
    # =====================================================

    placeholder: str = ""

    tooltip: str = ""

    ancho: int | None = None

    alto: int | None = None

    stretch: int = 0

    # =====================================================
    # Comportamiento
    # =====================================================

    requerido: bool = False

    requerido_dian: bool = False

    visible: bool = True

    habilitado: bool = True

    solo_lectura: bool = False

    valor_inicial: Any = None

    # Widget utilizado por WidgetFactory

    widget: str = ""

    # =====================================================
    # Extensibilidad
    # =====================================================

    validadores: list[Any] = field(
        default_factory=list
    )

    normalizers: list[Any] = field(
        default_factory=list
    )

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

        if not self.titulo:

            self.titulo = (
                self.nombre
                .replace("_", " ")
                .title()
            )

    # =====================================================
    # Etiqueta
    # =====================================================

    @property
    def etiqueta(self):

        if self.requerido_dian:

            return (
                f"{self.titulo} *"
            )

        return self.titulo

    @property
    def etiqueta_html(self):

        if self.requerido_dian:

            return (
                f'{self.titulo} '
                f'<span style="color:#C62828">*</span>'
            )

        return self.titulo

    # =====================================================
    # Mostrar etiqueta
    # =====================================================

    @property
    def etiqueta_visible(self):

        return True

    @property
    def ocupa_fila_completa(self):

        """
        Si True, el Builder coloca el widget sin columna
        de etiqueta (p. ej. checkboxes).
        """

        return False

    # =====================================================
    # Metadata
    # =====================================================

    def meta(
        self,
        nombre: str,
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
        nombre: str,
        default=None,
    ):

        return self.atributos.get(
            nombre,
            default,
        )