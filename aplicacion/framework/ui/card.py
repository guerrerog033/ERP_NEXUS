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

    background:#E8ECF1;

    border:1px solid #B8C2CE;

    border-radius:4px;

}

QLabel#titulo{

    font-size:15px;

    font-weight:700;

    color:#1e293b;

    padding-bottom:6px;

    border:none;

}
""")

        self.layout_principal = QVBoxLayout(self)

        self.layout_principal.setContentsMargins(
            18,
            14,
            18,
            14,
        )

        self.layout_principal.setSpacing(10)

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

        self.contenido.setSpacing(12)

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