from aplicacion.framework.form import (
    CheckField,
    FormDefinition,
    TextField,
)
from aplicacion.framework.table import (
    Column,
    TableDefinition,
)


class BodegaDefinition(FormDefinition):

    titulo = "Bodegas"

    table_definition = TableDefinition(

        titulo="Bodegas",

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
                nombre="activo",
                etiqueta="Activo",
            ),

        ],

    )

    campos = [

        TextField(
            nombre="codigo",
            titulo="Código",
            requerido=True,
            longitud_maxima=20,
            upper=True,
        ),

        TextField(
            nombre="nombre",
            titulo="Nombre",
            requerido=True,
            longitud_maxima=120,
            title=True,
        ),

        CheckField(
            nombre="activo",
            titulo="Activo",
            valor_inicial=True,
        ),

    ]
