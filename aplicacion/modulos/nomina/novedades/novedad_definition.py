from aplicacion.framework.form import (
    ComboField,
    DecimalField,
    FormDefinition,
    LookupField,
    TextField,
)
from aplicacion.framework.table import (
    Column,
    TableDefinition,
)
from aplicacion.framework.table.decimal_column import (
    DecimalColumn,
)
from aplicacion.framework.table.status_column import (
    StatusColumn,
)
from aplicacion.modulos.nomina.constantes import (
    TIPOS_NOVEDAD,
)
from aplicacion.modulos.nomina.empleados.empleado_lookup import (
    EmpleadoLookup,
)
from aplicacion.modulos.nomina.periodo_lookup import (
    PeriodoLookup,
)


class NovedadDefinition(FormDefinition):

    titulo = "Novedades"

    table_definition = TableDefinition(

        titulo="Novedades de nómina",

        columnas=[

            Column(
                nombre="id",
                etiqueta="ID",
                visible=False,
            ),

            Column(
                nombre="periodo_nombre",
                etiqueta="Periodo",
            ),

            Column(
                nombre="empleado_nombre",
                etiqueta="Empleado",
            ),

            StatusColumn(
                nombre="tipo",
                etiqueta="Tipo",
            ),

            DecimalColumn(
                nombre="cantidad",
                etiqueta="Cantidad",
            ),

            DecimalColumn(
                nombre="valor",
                etiqueta="Valor",
            ),

        ],

    )

    campos = [

        LookupField(
            nombre="periodo_id",
            titulo="Periodo",
            datasource=PeriodoLookup,
        ),

        LookupField(
            nombre="empleado_id",
            titulo="Empleado",
            datasource=EmpleadoLookup,
        ),

        ComboField(
            "tipo",
            titulo="Tipo de novedad",
            requerido=True,
            opciones=TIPOS_NOVEDAD,
        ),

        DecimalField(
            "cantidad",
            titulo="Cantidad (horas/días)",
        ),

        DecimalField(
            "valor",
            titulo="Valor",
        ),

        TextField(
            "observaciones",
            titulo="Observaciones",
            longitud_maxima=500,
        ),

    ]
