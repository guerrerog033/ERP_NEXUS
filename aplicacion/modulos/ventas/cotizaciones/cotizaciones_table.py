from __future__ import annotations

from aplicacion.framework.table import (
    Column,
    TableDefinition,
)
from aplicacion.framework.table.date_column import (
    DateColumn,
)
from aplicacion.framework.table.decimal_column import (
    DecimalColumn,
)
from aplicacion.framework.table.status_column import (
    StatusColumn,
)


CotizacionTable = TableDefinition(

    titulo="Cotizaciones",

    columnas=[

        Column(
            nombre="id",
            etiqueta="ID",
            visible=False,
        ),

        Column(
            nombre="numero",
            etiqueta="Número",
        ),

        DateColumn(
            nombre="fecha",
            etiqueta="Fecha",
        ),

        Column(
            nombre="cliente_id",
            etiqueta="Cliente",
        ),

        Column(
            nombre="formato_impresion",
            etiqueta="Formato",
        ),

        DecimalColumn(
            nombre="total",
            etiqueta="Total",
        ),

        StatusColumn(
            nombre="estado",
            etiqueta="Estado",
        ),

    ],

)
