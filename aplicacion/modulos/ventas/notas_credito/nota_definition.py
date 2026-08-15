from aplicacion.framework.form import FormDefinition

from .notas_credito_table import (
    NotaCreditoVentaTable,
)


class NotaCreditoVentaDefinition(FormDefinition):

    titulo = "Notas crédito de venta"

    campos = ()

    table_definition = NotaCreditoVentaTable
