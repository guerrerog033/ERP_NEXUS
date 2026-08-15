from __future__ import annotations

from .widget_accessor import WidgetAccessor


class TextAreaAccessor(WidgetAccessor):

    def leer(
        self,
        widget,
        field,
    ):

        return widget.toPlainText()

    def escribir(
        self,
        widget,
        valor,
        field,
    ):

        widget.setPlainText(
            "" if valor is None else str(valor)
        )