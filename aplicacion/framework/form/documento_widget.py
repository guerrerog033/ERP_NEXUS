from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QLineEdit,
)


class DocumentoWidget(QLineEdit):
    """
    Widget de documento conectado al DocumentoService unificado.
    """

    documentoChanged = Signal(str)

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(parent)

        self.context = None
        self.tipo_documento = ""
        self.resultado = None

        self.setMinimumHeight(36)

        self.editingFinished.connect(
            self._editing_finished,
        )

    def set_context(
        self,
        context,
    ) -> None:

        self.context = context

        if context is None:

            return

        combo = context.widget(
            "tipo_documento",
        )

        if not isinstance(
            combo,
            QComboBox,
        ):

            return

        self.tipo_documento = combo.currentText()
        combo.currentTextChanged.connect(
            self._tipo_documento_changed,
        )

    def _tipo_documento_changed(
        self,
        texto,
    ) -> None:

        self.tipo_documento = texto or ""

    def set_tipo_documento(
        self,
        tipo,
    ) -> None:

        self.tipo_documento = tipo or ""

    @property
    def documento_resultado(self):

        return self.resultado

    def _editing_finished(self) -> None:

        if not self.tipo_documento:

            self.resultado = None
            self.documentoChanged.emit(
                self.text(),
            )

            return

        if self.context is not None:
            self.resultado = self.context.consultar_documento(
                self.tipo_documento,
                self.text(),
            )
        else:
            from aplicacion.dominio.documentos.consulta import consultar

            self.resultado = consultar(
                self.tipo_documento,
                self.text(),
            )

        if self.context is not None:

            widget_dv = self.context.widget(
                "dv",
            )

            if (
                widget_dv is not None
                and hasattr(
                    widget_dv,
                    "setText",
                )
                and self.resultado is not None
            ):

                widget_dv.setText(
                    self.resultado.dv or "",
                )

        self.documentoChanged.emit(
            self.text(),
        )
