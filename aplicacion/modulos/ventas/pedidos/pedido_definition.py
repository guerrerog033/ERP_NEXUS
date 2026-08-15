from aplicacion.framework.form import FormDefinition

from .pedidos_table import (
    PedidoTable,
)


class PedidoDefinition(FormDefinition):

    titulo = "Pedidos"

    campos = ()

    table_definition = PedidoTable
