from aplicacion.framework.form import (
    CheckField,
    FormDefinition,
    TextField,
)

from aplicacion.maestros.listas_precio.listas_precio_table import (
    ListaPrecioTable,
)


class ListaPrecioDefinition(FormDefinition):

    titulo = "Listas de precio"

    table_definition = ListaPrecioTable

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
            nombre="predeterminada",
            titulo="Lista predeterminada",
            valor_inicial=False,
        ),

        CheckField(
            nombre="activo",
            titulo="Activo",
            valor_inicial=True,
        ),

    ]
