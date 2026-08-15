from aplicacion.framework.form import FormDefinition

from aplicacion.framework.table import (
    Column,
    TableDefinition,
)
from aplicacion.framework.table.date_column import (
    DateColumn,
)
from aplicacion.framework.table.decimal_column import (
    DecimalColumn,
)
from aplicacion.framework.table.status_column import (
    StatusColumn,
)


class ReciboCajaDefinition(FormDefinition):

    titulo = "Recibos de caja"

    campos = ()

    table_definition = TableDefinition(

        titulo="Recibos de caja",

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

            DateColumn(
                nombre="fecha",
                etiqueta="Fecha",
            ),

            Column(
                nombre="cliente_id",
                etiqueta="Cliente",
            ),

            DecimalColumn(
                nombre="valor_total",
                etiqueta="Valor",
            ),

            Column(
                nombre="forma_pago",
                etiqueta="Forma pago",
            ),

            StatusColumn(
                nombre="estado",
                etiqueta="Estado",
            ),

        ],

    )
