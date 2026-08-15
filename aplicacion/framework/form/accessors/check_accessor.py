from __future__ import annotations

from .widget_accessor import WidgetAccessor


class CheckAccessor(WidgetAccessor):

    def leer(
        self,
        widget,
        field,
    ):

        return widget.isChecked()

    def escribir(
        self,
        widget,
        valor,
        field,
    ):

        widget.setChecked(
            bool(valor)
        )