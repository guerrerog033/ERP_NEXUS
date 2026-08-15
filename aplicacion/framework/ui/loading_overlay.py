from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from aplicacion.recursos.estilos.tema import habilitar_fondo_qss


class LoadingOverlay(QWidget):
    """Capa semitransparente sobre un contenedor mientras carga datos."""

    def __init__(
        self,
        parent: QWidget | None = None,
    ):
        super().__init__(
            parent,
        )

        self.setObjectName(
            "LoadingOverlay",
        )

        habilitar_fondo_qss(
            self,
        )

        self.setAttribute(
            Qt.WA_TransparentForMouseEvents,
            False,
        )

        layout = QVBoxLayout(
            self,
        )

        self.lbl_mensaje = QLabel(
            "Cargando...",
        )

        self.lbl_mensaje.setObjectName(
            "LoadingOverlayText",
        )

        self.lbl_mensaje.setAlignment(
            Qt.AlignCenter,
        )

        layout.addStretch()
        layout.addWidget(
            self.lbl_mensaje,
        )
        layout.addStretch()

        self.hide()

    def mostrar(
        self,
        mensaje: str = "Cargando...",
    ) -> None:
        self.lbl_mensaje.setText(
            mensaje,
        )

        if self.parentWidget() is not None:
            self.setGeometry(
                self.parentWidget().rect(),
            )

        self.raise_()
        self.show()

    def ocultar(
        self,
    ) -> None:
        self.hide()

    def resizeEvent(
        self,
        event,
    ) -> None:
        super().resizeEvent(
            event,
        )

        if self.parentWidget() is not None:
            self.setGeometry(
                self.parentWidget().rect(),
            )
