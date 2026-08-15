from __future__ import annotations

from PySide6.QtCore import QDate

from .widget_accessor import WidgetAccessor


class DateAccessor(WidgetAccessor):

    def leer(
        self,
        widget,
        field,
    ):

        return widget.date()

    def escribir(
        self,
        widget,
        valor,
        field,
    ):

        if valor is None:

            widget.setDate(
                QDate.currentDate()
            )

            return

        widget.setDate(
            valor
        )