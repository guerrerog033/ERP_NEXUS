"""
Definición de listado de notas crédito de compra (mismo caso que las
guías electrónicas: se crean desde una factura de compra y se ven en
su vista de documento; el CRUD solo necesita la tabla).
"""

from __future__ import annotations

from aplicacion.framework.form import FormDefinition
from aplicacion.framework.table import Column, TableDefinition
from aplicacion.framework.table.date_column import DateColumn
from aplicacion.framework.table.decimal_column import DecimalColumn
from aplicacion.framework.table.status_column import StatusColumn


NotaCreditoCompraTable = TableDefinition(
    titulo="Notas crédito de compra",
    columnas=[
        Column(nombre="id", etiqueta="ID", visible=False),
        Column(nombre="numero", etiqueta="Número"),
        DateColumn(nombre="fecha", etiqueta="Fecha"),
        Column(nombre="proveedor_id", etiqueta="Proveedor"),
        Column(nombre="motivo", etiqueta="Motivo"),
        DecimalColumn(nombre="total", etiqueta="Total"),
        StatusColumn(nombre="estado", etiqueta="Estado"),
    ],
)


class NotaCreditoCompraDefinition(FormDefinition):

    titulo = "Notas crédito de compra"

    campos = ()

    table_definition = NotaCreditoCompraTable


class FormularioNotaCreditoCompraLista:
    """Solo aporta la definición para el listado."""

    definition = NotaCreditoCompraDefinition
