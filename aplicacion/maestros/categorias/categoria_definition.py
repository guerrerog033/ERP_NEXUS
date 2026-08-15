from aplicacion.framework.form import (
    FormDefinition,
    TextField,
    TextAreaField,
    CheckField,
)

from aplicacion.maestros.categorias.categorias_table import (
    CategoriaTable,
)


class CategoriaDefinition(FormDefinition):

    titulo = "Categorías"

    table_definition = CategoriaTable

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