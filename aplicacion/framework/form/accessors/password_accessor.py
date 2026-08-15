from __future__ import annotations

from .widget_accessor import WidgetAccessor


class PasswordAccessor(WidgetAccessor):

    def leer(
        self,
        widget,
        field,
    ):

        return widget.text()

    def escribir(
        self,
        widget,
        valor,
        field,
    ):

        widget.setText(
            "" if valor is None else str(valor)
        )