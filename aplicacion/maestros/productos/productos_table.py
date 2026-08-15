from __future__ import annotations

from aplicacion.framework.table import (
    Column,
    TableDefinition,
)
from aplicacion.framework.table.decimal_column import (
    DecimalColumn,
)


ProductoTable = TableDefinition(

    titulo="Productos",

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
            nombre="codigo_barras",
            etiqueta="Código barras",
        ),

        Column(
            nombre="nombre",
            etiqueta="Nombre",
        ),

        Column(
            nombre="tipo",
            etiqueta="Tipo",
        ),

        Column(
            nombre="unidad_medida",
            etiqueta="Unidad",
        ),

        DecimalColumn(
            nombre="precio_venta",
            etiqueta="Precio",
        ),

        DecimalColumn(
            nombre="existencia",
            etiqueta="Existencia (ref.)",
        ),

        DecimalColumn(
            nombre="stock_minimo",
            etiqueta="Stock mín.",
        ),

        Column(
            nombre="activo",
            etiqueta="Activo",
        ),

    ],

)
