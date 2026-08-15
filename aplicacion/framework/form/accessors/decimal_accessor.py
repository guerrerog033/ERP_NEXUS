from __future__ import annotations

from decimal import Decimal, InvalidOperation

from .widget_accessor import WidgetAccessor


def _a_decimal(
    valor,
) -> Decimal | None:

    if valor is None or valor == "":

        return None

    try:

        return Decimal(
            str(valor),
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):

        return None


class DecimalAccessor(WidgetAccessor):

    def leer(
        self,
        widget,
        field,
    ):

        return _a_decimal(
            widget.value(),
        )

    def escribir(
        self,
        widget,
        valor,
        field,
    ):

        decimal = _a_decimal(
            valor,
        )

        widget.setValue(
            0.0
            if decimal is None
            else float(
                decimal,
            ),
        )
