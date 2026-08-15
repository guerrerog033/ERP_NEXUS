from __future__ import annotations

from aplicacion.framework.table import (
    Column,
    TableDefinition,
)
from aplicacion.framework.table.decimal_column import (
    DecimalColumn,
)


ImpuestoTable = TableDefinition(

    titulo="Impuestos",

    columnas=[

        Column(
            nombre="id",
            etiqueta="ID",
            visible=False,
        ),

        Column(
            nombre="codigo",
            etiqueta="Código",
        ),

        Column(
            nombre="nombre",
            etiqueta="Nombre",
        ),

        DecimalColumn(
            nombre="porcentaje",
            etiqueta="%",
        ),

        Column(
            nombre="tipo",
            etiqueta="Tipo",
        ),

        Column(
            nombre="activo",
            etiqueta="Activo",
        ),

    ],

)
