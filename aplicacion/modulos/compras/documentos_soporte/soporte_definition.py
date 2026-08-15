from aplicacion.framework.form import FormDefinition
from aplicacion.framework.table import Column, TableDefinition
from aplicacion.framework.table.date_column import DateColumn
from aplicacion.framework.table.decimal_column import DecimalColumn
from aplicacion.framework.table.status_column import StatusColumn


class DocumentoSoporteDefinition(FormDefinition):

    titulo = "Documentos soporte"

    campos = ()

    table_definition = TableDefinition(
        titulo="Documentos soporte",
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
            StatusColumn(
                nombre="estado",
                etiqueta="Estado",
            ),
            StatusColumn(
                nombre="estado_dian",
                etiqueta="DIAN",
            ),
        ],
    )
