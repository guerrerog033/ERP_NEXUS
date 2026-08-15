from decimal import Decimal

from aplicacion.framework.utilidades.moneda import (
    a_decimal,
    formatear_decimal,
)


def test_a_decimal_desde_cadena():
    assert a_decimal(
        "54.74",
    ) == Decimal(
        "54.74",
    )


def test_formatear_con_prefijo():
    assert formatear_decimal(
        1000,
        prefijo="$ ",
        decimales=0,
    ) == "$ 1.000"
