from __future__ import annotations

from .widget_accessor import WidgetAccessor


class IntegerAccessor(WidgetAccessor):

    def leer(
        self,
        widget,
        field,
    ):

        return widget.value()

    def escribir(
        self,
        widget,
        valor,
        field,
    ):

        widget.setValue(
            0 if valor is None else int(valor)
        )