from datetime import date

from aplicacion.framework.datagrid.filtros import (
    DateRangeFilter,
    LookupFilter,
    construir_filtros,
)
from aplicacion.framework.table.column_registry import (
    ColumnRegistry,
)
from aplicacion.framework.table.column import (
    Column,
)


def test_filtro_rango_fechas():

    definiciones = [
        DateRangeFilter(
            "fecha",
            etiqueta="Fecha",
        ),
    ]

    filtros = construir_filtros(
        definiciones,
        {
            "fecha": {
                "desde": date(
                    2026,
                    1,
                    1,
                ),
                "hasta": date(
                    2026,
                    1,
                    31,
                ),
            },
        },
    )

    assert len(
        filtros,
    ) == 2

    assert filtros[
        0
    ].operador == "gte"

    assert filtros[
        1
    ].operador == "lte"


def test_filtro_lookup_id():

    definiciones = [
        LookupFilter(
            "cliente_id",
            etiqueta="Cliente",
        ),
    ]

    filtros = construir_filtros(
        definiciones,
        {
            "cliente_id": "42",
        },
    )

    assert len(
        filtros,
    ) == 1

    assert filtros[
        0
    ].valor == 42


def test_column_registry_formatear_decimal():

    from decimal import Decimal

    columna = Column(
        "total",
        "Total",
        widget="decimal",
        metadata={
            "prefijo": "$ ",
        },
    )

    texto = ColumnRegistry.formatear_valor(
        "decimal",
        Decimal(
            "1234.50",
        ),
        columna,
    )

    assert "$" in texto

    assert "1.234" in texto or "1234" in texto
