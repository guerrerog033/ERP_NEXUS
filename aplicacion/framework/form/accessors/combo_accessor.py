from __future__ import annotations

from .widget_accessor import WidgetAccessor


class ComboAccessor(WidgetAccessor):

    def leer(
        self,
        widget,
        field,
    ):

        return widget.currentData()

    def escribir(
        self,
        widget,
        valor,
        field,
    ):

        indice = widget.findData(
            valor
        )

        if indice >= 0:

            widget.setCurrentIndex(
                indice
            )