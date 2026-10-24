"""
Definición de listado de guías de remisión electrónica.

El maestro no tiene formulario de captura (la guía se crea desde una
remisión y se ve en su vista de documento), pero el CRUD necesita una
``FormDefinition`` con ``table_definition`` para construir la lista.
Sin ella el módulo fallaba al abrir con "No existe formulario
configurado".
"""

from __future__ import annotations

from aplicacion.framework.form import FormDefinition
from aplicacion.framework.table import Column, TableDefinition
from aplicacion.framework.table.date_column import DateColumn
from aplicacion.framework.table.decimal_column import DecimalColumn
from aplicacion.framework.table.status_column import StatusColumn


GuiaRemisionTable = TableDefinition(
    titulo="Guías electrónicas",
    columnas=[
        Column(nombre="id", etiqueta="ID", visible=False),
        Column(nombre="numero", etiqueta="Número"),
        DateColumn(nombre="fecha", etiqueta="Fecha"),
        Column(nombre="remision_numero", etiqueta="Remisión"),
        Column(nombre="ciudad_destino", etiqueta="Destino"),
        Column(nombre="placa", etiqueta="Placa"),
        DecimalColumn(nombre="total", etiqueta="Total"),
        StatusColumn(nombre="estado", etiqueta="Estado"),
        Column(nombre="estado_dian", etiqueta="DIAN"),
    ],
)


class GuiaRemisionDefinition(FormDefinition):

    titulo = "Guías electrónicas"

    campos = ()

    table_definition = GuiaRemisionTable


class FormularioGuiaRemisionLista:
    """Solo aporta la definición para el listado."""

    definition = GuiaRemisionDefinition
