from aplicacion.framework.form import (
    CheckField,
    ComboField,
    FormDefinition,
    TextField,
)
from aplicacion.framework.table import (
    Column,
    TableDefinition,
)
from aplicacion.framework.table.status_column import (
    StatusColumn,
)
from aplicacion.modulos.contabilidad.plan_cuentas.servicios import (
    TIPOS_CUENTA,
)


class PlanCuentaDefinition(FormDefinition):

    titulo = "Plan de cuentas"

    table_definition = TableDefinition(

        titulo="Plan de cuentas",

        columnas=[

            Column(
                nombre="id",
                etiqueta="ID",
                visible=False,
            ),

            Column(
                nombre="codigo",
                etiqueta="Código",
            ),

            Column(
                nombre="nombre",
                etiqueta="Nombre",
            ),

            Column(
                nombre="tipo",
                etiqueta="Tipo",
            ),

            StatusColumn(
                nombre="activo",
                etiqueta="Activo",
                metadata={
                    "etiquetas_bool": {
                        True: "Activa",
                        False: "Inactiva",
                    },
                },
            ),

        ],

    )

    campos = [

        TextField(
            nombre="codigo",
            titulo="Código",
            requerido=True,
            longitud_maxima=20,
        ),

        TextField(
            nombre="nombre",
            titulo="Nombre",
            requerido=True,
            longitud_maxima=200,
        ),

        ComboField(
            nombre="tipo",
            titulo="Tipo",
            requerido=True,
            opciones=TIPOS_CUENTA,
        ),

        CheckField(
            nombre="activo",
            titulo="Activa",
            valor_inicial=True,
        ),

    ]
