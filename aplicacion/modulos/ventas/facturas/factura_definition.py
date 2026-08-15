from aplicacion.framework.form import FormDefinition

from .facturas_table import (
    FacturaVentaTable,
)


class FacturaVentaDefinition(FormDefinition):

    titulo = "Facturas de venta"

    campos = ()

    table_definition = FacturaVentaTable
