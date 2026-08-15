from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class CampoContenedor(QWidget):
    """Envuelve un control con etiqueta de error debajo."""

    def __init__(
        self,
        control,
    ):
        super().__init__()

        self.setObjectName(
            "CampoContenedor",
        )

        self.control = control

        layout = QVBoxLayout(
            self,
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(
            2,
        )

        self.lbl_error = QLabel()

        self.lbl_error.setObjectName(
            "CampoErrorLabel",
        )

        self.lbl_error.setVisible(
            False,
        )

        self.lbl_error.setWordWrap(
            True,
        )

        layout.addWidget(
            control,
        )

        layout.addWidget(
            self.lbl_error,
        )

    def marcar_error(
        self,
        mensaje: str,
    ) -> None:

        texto = str(
            mensaje or "",
        ).strip()

        self.lbl_error.setText(
            texto,
        )

        self.lbl_error.setVisible(
            bool(
                texto,
            ),
        )

        if hasattr(
            self.control,
            "setProperty",
        ):

            self.control.setProperty(
                "invalid",
                bool(
                    texto,
                ),
            )

            self.control.style().unpolish(
                self.control,
            )

            self.control.style().polish(
                self.control,
            )

    def limpiar_error(
        self,
    ) -> None:

        self.marcar_error(
            "",
        )
