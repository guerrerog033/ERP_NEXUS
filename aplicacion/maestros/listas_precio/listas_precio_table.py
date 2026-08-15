from __future__ import annotations

from aplicacion.framework.table import (
    Column,
    TableDefinition,
)


ListaPrecioTable = TableDefinition(

    titulo="Listas de precio",

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
            nombre="predeterminada",
            etiqueta="Predeterminada",
        ),

        Column(
            nombre="activo",
            etiqueta="Activo",
        ),

    ],

)
