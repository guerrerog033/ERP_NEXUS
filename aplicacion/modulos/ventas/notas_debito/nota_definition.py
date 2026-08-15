from aplicacion.framework.form import FormDefinition

from .notas_debito_table import (
    NotaDebitoVentaTable,
)


class NotaDebitoVentaDefinition(FormDefinition):

    titulo = "Notas débito de venta"

    campos = ()

    table_definition = NotaDebitoVentaTable
