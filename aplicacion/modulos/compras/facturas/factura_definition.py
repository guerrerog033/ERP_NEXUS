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


class FacturaCompraDefinition(FormDefinition):

    titulo = "Facturas de compra"

    campos = ()

    table_definition = TableDefinition(

        titulo="Facturas de compra",

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
                nombre="numero_proveedor",
                etiqueta="Factura prov.",
            ),

            Column(
                nombre="nit_proveedor",
                etiqueta="NIT",
            ),

            Column(
                nombre="razon_social_proveedor",
                etiqueta="Proveedor",
            ),

            DecimalColumn(
                nombre="total",
                etiqueta="Total",
            ),

            Column(
                nombre="origen",
                etiqueta="Origen",
            ),

            StatusColumn(
                nombre="estado",
                etiqueta="Estado",
            ),

            DecimalColumn(
                nombre="saldo_pendiente",
                etiqueta="Saldo",
            ),

            StatusColumn(
                nombre="estado_pago",
                etiqueta="Pago",
            ),

            DateColumn(
                nombre="fecha_vencimiento",
                etiqueta="Vencimiento",
            ),

        ],

    )
