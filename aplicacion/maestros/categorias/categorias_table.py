from __future__ import annotations

from aplicacion.framework.table import (
    Column,
    TableDefinition,
)


CategoriaTable = TableDefinition(

    titulo="Categorías",

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

        Column(
            nombre="descripcion",
            etiqueta="Descripción",
        ),

        Column(
            nombre="activo",
            etiqueta="Activo",
        ),

    ],

)
