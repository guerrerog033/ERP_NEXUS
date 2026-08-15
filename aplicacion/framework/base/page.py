from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)


class Page(QWidget):
    """
    Clase base de todas las páginas del ERP.

    Toda pantalla del sistema debe heredar de Page.

    Responsabilidades:

        • Crear el layout principal.
        • Aplicar el estilo base.
        • Ofrecer utilidades para agregar widgets y layouts.

    No conoce:

        • Formularios
        • CRUD
        • SQLAlchemy
        • DataSources
    """

    titulo: str = ""

    icono: str = ""

    # =====================================================
    # Inicialización
    # =====================================================

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent
        )

        self._crear_ui()

    # =====================================================
    # Construcción
    # =====================================================

    def _crear_ui(self):

        self.setObjectName("Page")

        self.layout_principal = QVBoxLayout()

        self.layout_principal.setContentsMargins(
            10,
            8,
            10,
            8,
        )

        self.layout_principal.setSpacing(
            8,
        )

        self.setLayout(
            self.layout_principal
        )

    # =====================================================
    # Agregar widget
    # =====================================================

    def agregar_widget(
        self,
        widget,
        *,
        centrado=False,
        stretch=1,
    ):

        if centrado:

            self.layout_principal.addWidget(

                widget,

                alignment=Qt.AlignHCenter,

            )

        else:

            #
            # El widget ocupa todo el ancho.
            #

            self.layout_principal.addWidget(
                widget,
                stretch=stretch,
            )

    # =====================================================
    # Agregar layout
    # =====================================================

    def agregar_layout(
        self,
        layout,
    ):

        self.layout_principal.addLayout(
            layout,
            1,
        )

    # =====================================================
    # Separador
    # =====================================================

    def agregar_espacio(
        self,
        alto=20,
    ):

        self.layout_principal.addSpacing(
            alto
        )

    # =====================================================
    # Stretch
    # =====================================================

    def agregar_stretch(self):

        self.layout_principal.addStretch()

    # =====================================================
    # Método virtual
    # =====================================================

    def cargar(self):
        """
        Se ejecuta cuando la página
        es mostrada por primera vez.
        """

        pass