from aplicacion.framework.form import (
    CheckField,
    ComboField,
    DateField,
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
    TIPOS_CONTRATO,
)
from aplicacion.modulos.nomina.empleados.empleado_lookup import (
    EmpleadoLookup,
)


class ContratoDefinition(FormDefinition):

    titulo = "Contratos"

    table_definition = TableDefinition(

        titulo="Contratos históricos",

        columnas=[

            Column(
                nombre="id",
                etiqueta="ID",
                visible=False,
            ),

            Column(
                nombre="empleado_nombre",
                etiqueta="Empleado",
            ),

            Column(
                nombre="fecha_inicio",
                etiqueta="Inicio",
            ),

            Column(
                nombre="fecha_fin",
                etiqueta="Fin",
            ),

            DecimalColumn(
                nombre="salario",
                etiqueta="Salario",
            ),

            Column(
                nombre="tipo_contrato",
                etiqueta="Tipo",
            ),

            Column(
                nombre="cargo",
                etiqueta="Cargo",
            ),

            StatusColumn(
                nombre="vigente",
                etiqueta="Vigente",
                metadata={
                    "etiquetas_bool": {
                        True: "Vigente",
                        False: "Cerrado",
                    },
                    "colores": {
                        "vigente": ("#D1FAE5", "#065F46"),
                        "cerrado": ("#F3F4F6", "#374151"),
                    },
                },
            ),

        ],

    )

    campos = [

        LookupField(
            nombre="empleado_id",
            titulo="Empleado",
            datasource=EmpleadoLookup,
        ),

        DateField(
            "fecha_inicio",
            titulo="Fecha inicio",
            requerido=True,
        ),

        DateField(
            "fecha_fin",
            titulo="Fecha fin",
        ),

        DecimalField(
            "salario",
            titulo="Salario",
            requerido=True,
        ),

        ComboField(
            "tipo_contrato",
            titulo="Tipo de contrato",
            requerido=True,
            opciones=TIPOS_CONTRATO,
        ),

        TextField(
            "cargo",
            titulo="Cargo",
            longitud_maxima=120,
        ),

        TextField(
            "observaciones",
            titulo="Observaciones",
            longitud_maxima=500,
        ),

        CheckField(
            "vigente",
            titulo="Vigente",
            valor_inicial=True,
        ),

    ]
