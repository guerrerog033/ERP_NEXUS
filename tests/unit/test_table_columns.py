from datetime import date
from decimal import Decimal

from aplicacion.framework.table.column_factories.decimal_factory import (
    DecimalColumnFactory,
)
from aplicacion.framework.table.column_factories.date_factory import (
    DateColumnFactory,
)
from aplicacion.framework.table.column_factories.check_factory import (
    CheckColumnFactory,
)
from aplicacion.framework.table.decimal_column import (
    DecimalColumn,
)
from aplicacion.framework.table.date_column import (
    DateColumn,
)
from aplicacion.framework.table.check_column import (
    CheckColumn,
)
from aplicacion.framework.utilidades.moneda import (
    formatear_decimal,
)


def test_formatear_decimal_colombiano():
    texto = formatear_decimal(
        Decimal(
            "1250000.5",
        ),
        decimales=2,
    )

    assert texto == "1.250.000,50"


def test_decimal_column_factory():
    factory = DecimalColumnFactory()
    columna = DecimalColumn(
        nombre="total",
        metadata={
            "prefijo": "$ ",
        },
    )

    item = factory.crear_item(
        46.74,
        columna,
    )

    assert item.text().startswith(
        "$ ",
    )
    assert "46,74" in item.text()


def test_date_column_factory():
    factory = DateColumnFactory()
    columna = DateColumn(
        nombre="fecha",
    )

    item = factory.crear_item(
        date(
            2026,
            8,
            10,
        ),
        columna,
    )

    assert item.text() == "10/08/2026"


def test_check_column_factory():
    factory = CheckColumnFactory()
    columna = CheckColumn(
        nombre="activo",
    )

    item = factory.crear_item(
        True,
        columna,
    )

    assert item.text() == "Sí"
