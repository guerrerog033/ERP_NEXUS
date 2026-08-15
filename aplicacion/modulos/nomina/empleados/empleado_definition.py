from aplicacion.framework.form import (
    CheckField,
    ComboField,
    DateField,
    DecimalField,
    FormDefinition,
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


class EmpleadoDefinition(FormDefinition):

    titulo = "Empleados"

    table_definition = TableDefinition(

        titulo="Empleados",

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
                nombre="numero_documento",
                etiqueta="Documento",
            ),

            Column(
                nombre="nombre_completo",
                etiqueta="Nombre",
            ),

            Column(
                nombre="cargo",
                etiqueta="Cargo",
            ),

            DecimalColumn(
                nombre="salario_basico",
                etiqueta="Salario",
            ),

            StatusColumn(
                nombre="activo",
                etiqueta="Activo",
                metadata={
                    "etiquetas_bool": {
                        True: "Activo",
                        False: "Inactivo",
                    },
                },
            ),

        ],

    )

    campos = [

        TextField(
            "codigo",
            titulo="Código",
            requerido=True,
            longitud_maxima=20,
            upper=True,
        ),

        ComboField(
            "tipo_documento",
            titulo="Tipo documento",
            requerido=True,
            opciones=[
                ("CC", "CC"),
                ("CE", "CE"),
                ("PA", "PA"),
                ("NIT", "NIT"),
            ],
        ),

        TextField(
            "numero_documento",
            titulo="Número documento",
            requerido=True,
            longitud_maxima=30,
        ),

        TextField(
            "primer_nombre",
            titulo="Primer nombre",
            requerido=True,
            longitud_maxima=100,
        ),

        TextField(
            "segundo_nombre",
            titulo="Segundo nombre",
            longitud_maxima=100,
        ),

        TextField(
            "primer_apellido",
            titulo="Primer apellido",
            requerido=True,
            longitud_maxima=100,
        ),

        TextField(
            "segundo_apellido",
            titulo="Segundo apellido",
            longitud_maxima=100,
        ),

        TextField(
            "cargo",
            titulo="Cargo",
            longitud_maxima=120,
        ),

        TextField(
            "area",
            titulo="Área",
            longitud_maxima=120,
        ),

        ComboField(
            "tipo_contrato",
            titulo="Tipo de contrato",
            requerido=True,
            opciones=TIPOS_CONTRATO,
        ),

        DecimalField(
            "salario_basico",
            titulo="Salario básico",
            requerido=True,
        ),

        DateField(
            "fecha_ingreso",
            titulo="Fecha de ingreso",
        ),

        TextField(
            "eps",
            titulo="EPS",
            longitud_maxima=120,
        ),

        TextField(
            "afp",
            titulo="Fondo de pensiones",
            longitud_maxima=120,
        ),

        TextField(
            "arl",
            titulo="ARL",
            longitud_maxima=120,
        ),

        TextField(
            "eps_codigo",
            titulo="Código EPS (PILA)",
            longitud_maxima=6,
        ),

        TextField(
            "afp_codigo",
            titulo="Código AFP (PILA)",
            longitud_maxima=6,
        ),

        TextField(
            "arl_codigo",
            titulo="Código ARL (PILA)",
            longitud_maxima=6,
        ),

        DecimalField(
            "auxilio_transporte",
            titulo="Auxilio de transporte",
        ),

        CheckField(
            "salario_integral",
            titulo="Salario integral",
            valor_inicial=False,
        ),

        ComboField(
            "clase_riesgo",
            titulo="Clase de riesgo ARL",
            opciones=[
                ("Clase I", "1"),
                ("Clase II", "2"),
                ("Clase III", "3"),
                ("Clase IV", "4"),
                ("Clase V", "5"),
            ],
        ),

        TextField(
            "departamento_codigo",
            titulo="Código departamento",
            longitud_maxima=2,
        ),

        TextField(
            "municipio_codigo",
            titulo="Código municipio",
            longitud_maxima=3,
        ),

        TextField(
            "email",
            titulo="Correo",
            longitud_maxima=120,
        ),

        TextField(
            "telefono",
            titulo="Teléfono",
            longitud_maxima=30,
        ),

        CheckField(
            "activo",
            titulo="Activo",
            valor_inicial=True,
        ),

    ]
