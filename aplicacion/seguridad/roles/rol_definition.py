from aplicacion.framework.form import (
    CheckField,
    FormDefinition,
    TextField,
)
from aplicacion.framework.table import (
    Column,
    TableDefinition,
)


class RolDefinition(FormDefinition):

    titulo = "Roles"

    table_definition = TableDefinition(

        titulo="Roles",

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
                nombre="resumen_modulos",
                etiqueta="Módulos",
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
            longitud_maxima=30,
        ),

        TextField(
            nombre="nombre",
            titulo="Nombre",
            requerido=True,
            longitud_maxima=100,
        ),

        CheckField(
            nombre="activo",
            titulo="Activo",
            valor_inicial=True,
        ),

    ]
