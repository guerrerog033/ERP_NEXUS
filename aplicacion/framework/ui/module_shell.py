from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class ModuleShellPage(QWidget):
    """
    Contenedor con título para módulos abiertos en pestañas.

    Distinto de framework.base.page.Page (layout de formularios/páginas).
    """

    def __init__(
        self,
        titulo: str = "",
        subtitulo: str = "",
    ):

        super().__init__()

        self.setObjectName(
            "PaginaModulo",
        )

        layout = QVBoxLayout(
            self,
        )

        layout.setContentsMargins(
            16,
            12,
            16,
            12,
        )

        panel = QFrame()
        panel.setObjectName(
            "PanelModulo",
        )

        panel_layout = QVBoxLayout(
            panel,
        )

        panel_layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        self.lbl_titulo = QLabel(
            titulo,
        )
        self.lbl_subtitulo = QLabel(
            subtitulo,
        )

        self.lbl_titulo.setObjectName(
            "PaginaModuloTitulo",
        )
        self.lbl_subtitulo.setObjectName(
            "PaginaModuloSubtitulo",
        )

        panel_layout.addWidget(
            self.lbl_titulo,
        )
        panel_layout.addWidget(
            self.lbl_subtitulo,
        )

        self.layout_contenido = QVBoxLayout()
        self.layout_contenido.setContentsMargins(
            0,
            8,
            0,
            0,
        )

        panel_layout.addLayout(
            self.layout_contenido,
            1,
        )

        layout.addWidget(
            panel,
            1,
        )

    def setContenido(
        self,
        widget,
    ) -> None:

        widget.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        self.layout_contenido.addWidget(
            widget,
            1,
        )
