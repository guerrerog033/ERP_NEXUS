from __future__ import annotations

from .widget_accessor import WidgetAccessor


class LookupAccessor(WidgetAccessor):

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
            valor
        )