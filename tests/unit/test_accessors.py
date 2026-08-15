from decimal import Decimal

from aplicacion.framework.form.accessors.decimal_accessor import (
    DecimalAccessor,
    _a_decimal,
)


class _SpinStub:

    def __init__(
        self,
        value: float,
    ):

        self._value = value

    def value(
        self,
    ) -> float:

        return self._value

    def setValue(
        self,
        value: float,
    ) -> None:

        self._value = value


def test_a_decimal_desde_float():
    assert _a_decimal(
        46.0,
    ) == Decimal(
        "46.0",
    )


def test_a_decimal_desde_none():
    assert _a_decimal(
        None,
    ) is None


def test_decimal_accessor_lee_decimal():
    accessor = DecimalAccessor()
    widget = _SpinStub(
        1250.5,
    )

    valor = accessor.leer(
        widget,
        None,
    )

    assert isinstance(
        valor,
        Decimal,
    )
    assert valor == Decimal(
        "1250.5",
    )


def test_decimal_accessor_escribe_desde_decimal():
    accessor = DecimalAccessor()
    widget = _SpinStub(
        0.0,
    )

    accessor.escribir(
        widget,
        Decimal(
            "54.74",
        ),
        None,
    )

    assert widget.value() == 54.74
