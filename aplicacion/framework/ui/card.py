from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class Card(QFrame):
    """
    Contenedor visual reutilizable del ERP.
    """

    # =====================================================
    # Inicialización
    # =====================================================

    def __init__(
        self,
        titulo: str = "",
    ):

        super().__init__()

        self._crear_ui()

        if titulo:
            self.set_titulo(titulo)

    # =====================================================
    # Construcción
    # =====================================================

    def _crear_ui(self):

        self.setObjectName("card")

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        self.setStyleSheet("""
QFrame#card{

    background:#ffffff;

    border:1px solid #d8dee9;

    border-radius:12px;

}

QLabel#titulo{

    font-size:22px;

    font-weight:700;

    color:#1f2937;

    padding-bottom:16px;

    border:none;

}
""")

        self.layout_principal = QVBoxLayout(self)

        self.layout_principal.setContentsMargins(
            36,
            30,
            36,
            30,
        )

        self.layout_principal.setSpacing(24)

        self.lbl_titulo = QLabel()

        self.lbl_titulo.setObjectName(
            "titulo"
        )

        self.lbl_titulo.setAlignment(
            Qt.AlignCenter
        )

        self.lbl_titulo.hide()

        self.layout_principal.addWidget(
            self.lbl_titulo
        )

        self.contenido = QVBoxLayout()

        self.contenido.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.contenido.setSpacing(22)

        self.layout_principal.addLayout(
            self.contenido,
            1,
        )

    # =====================================================
    # Título
    # =====================================================

    def set_titulo(
        self,
        titulo: str,
    ):

        self.lbl_titulo.setText(
            titulo
        )

        self.lbl_titulo.setVisible(
            bool(titulo)
        )

    # =====================================================
    # Agregar widget
    # =====================================================

    def agregar_widget(
        self,
        widget: QWidget,
        *,
        centrado=False,
    ):

        if centrado:

            self.contenido.addWidget(
                widget,
                alignment=Qt.AlignHCenter,
            )

        else:

            self.contenido.addWidget(
                widget,
            )

    # =====================================================
    # Agregar layout
    # =====================================================

    def agregar_layout(
        self,
        layout,
        stretch=0,
    ):

        self.contenido.addLayout(
            layout,
            stretch,
        )

    # =====================================================
    # Espaciado
    # =====================================================

    def agregar_espacio(
        self,
        alto=20,
    ):

        self.contenido.addSpacing(
            alto
        )

    # =====================================================
    # Stretch
    # =====================================================

    def agregar_stretch(self):

        self.contenido.addStretch()