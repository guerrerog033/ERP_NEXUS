from aplicacion.framework.form import FormDefinition
from aplicacion.framework.table import Column, TableDefinition
from aplicacion.framework.table.status_column import StatusColumn


class ComprobanteDefinition(FormDefinition):

    titulo = "Comprobantes contables"

    table_definition = TableDefinition(

        titulo="Comprobantes contables",

        columnas=[

            Column(
                nombre="id",
                etiqueta="ID",
                visible=False,
            ),

            Column(
                nombre="numero",
                etiqueta="Número",
            ),

            Column(
                nombre="fecha",
                etiqueta="Fecha",
            ),

            Column(
                nombre="descripcion",
                etiqueta="Descripción",
            ),

            StatusColumn(
                nombre="origen",
                etiqueta="Origen",
            ),

            Column(
                nombre="total_debito",
                etiqueta="Débito",
            ),

            Column(
                nombre="total_credito",
                etiqueta="Crédito",
            ),

        ],

    )

    campos = []
