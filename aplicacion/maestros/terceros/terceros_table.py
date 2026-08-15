from __future__ import annotations

from aplicacion.framework.table.column import Column
from aplicacion.framework.table.table_definition import (
    TableDefinition,
)
from aplicacion.framework.datagrid.filtros import (
    BooleanFilter,
    ComboFilter,
    TextFilter,
)


TerceroTable = TableDefinition(

    titulo="Terceros",

    columnas=[

        Column(
            "id",
            "ID",
            visible=False,
        ),

        Column(
            "numero_documento",
            "Documento",
        ),

        Column(
            "tipo_documento",
            "Tipo Doc.",
        ),

        Column(
            "tipo_tercero",
            "Clasificación",
        ),

        Column(
            "razon_social",
            "Razón Social",
        ),

        Column(
            "primer_nombre",
            "Primer Nombre",
        ),

        Column(
            "primer_apellido",
            "Primer Apellido",
        ),

        Column(
            "ciudad",
            "Ciudad",
        ),

        Column(
            "tipo_regimen_iva",
            "Régimen IVA",
        ),

        Column(
            "telefono",
            "Teléfono",
        ),

        Column(
            "activo",
            "Activo",
        ),

    ],

    filtros=[

        TextFilter(
            "numero_documento",
            etiqueta="Documento",
        ),

        ComboFilter(
            "tipo_documento",
            etiqueta="Tipo Doc.",
            opciones=[
                ("CC", "CC"),
                ("CE", "CE"),
                ("NIT", "NIT"),
                ("TI", "TI"),
                ("PAS", "PAS"),
            ],
        ),

        TextFilter(
            "ciudad",
            etiqueta="Ciudad",
        ),

        BooleanFilter(
            "activo",
            etiqueta="Activo",
        ),

    ],

)
