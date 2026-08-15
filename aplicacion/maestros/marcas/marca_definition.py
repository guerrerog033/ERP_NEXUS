from aplicacion.framework.form import (
    FormDefinition,
    TextField,
    TextAreaField,
    CheckField,
)

from aplicacion.maestros.marcas.marcas_table import (
    MarcaTable,
)


class MarcaDefinition(FormDefinition):

    titulo = "Marcas"

    table_definition = MarcaTable

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

        TextAreaField(
            nombre="descripcion",
            titulo="Descripción",
            longitud_maxima=250,
        ),

        CheckField(
            nombre="activo",
            titulo="Activo",
            valor_inicial=True,
        ),

    ]