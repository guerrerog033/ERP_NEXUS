from aplicacion.framework.form import (
    CheckField,
    ComboField,
    DateField,
    FormDefinition,
    LookupField,
    TextField,
)
from aplicacion.framework.table import (
    Column,
    TableDefinition,
)
from aplicacion.framework.table.status_column import (
    StatusColumn,
)

from aplicacion.modulos.crm.constantes import (
    TIPOS_ACTIVIDAD_CRM,
)
from aplicacion.modulos.crm.oportunidades.oportunidad_lookup import (
    OportunidadLookup,
)


class ActividadDefinition(FormDefinition):

    titulo = "Actividades"

    table_definition = TableDefinition(

        titulo="Actividades CRM",

        columnas=[

            Column(
                nombre="id",
                etiqueta="ID",
                visible=False,
            ),

            Column(
                nombre="oportunidad_codigo",
                etiqueta="Oportunidad",
            ),

            StatusColumn(
                nombre="tipo",
                etiqueta="Tipo",
            ),

            Column(
                nombre="titulo",
                etiqueta="Título",
            ),

            Column(
                nombre="fecha",
                etiqueta="Fecha",
            ),

            StatusColumn(
                nombre="completada",
                etiqueta="Completada",
                metadata={
                    "etiquetas_bool": {
                        True: "Completada",
                        False: "Pendiente",
                    },
                    "colores": {
                        "completada": ("#D1FAE5", "#065F46"),
                        "pendiente": ("#FEF3C7", "#92400E"),
                    },
                },
            ),

        ],

    )

    campos = [

        LookupField(
            nombre="oportunidad_id",
            titulo="Oportunidad",
            datasource=OportunidadLookup,
        ),

        ComboField(
            "tipo",
            titulo="Tipo",
            requerido=True,
            opciones=TIPOS_ACTIVIDAD_CRM,
        ),

        TextField(
            "titulo",
            titulo="Título",
            requerido=True,
            longitud_maxima=200,
        ),

        TextField(
            "descripcion",
            titulo="Descripción",
            longitud_maxima=500,
        ),

        DateField(
            "fecha",
            titulo="Fecha",
            requerido=True,
        ),

        CheckField(
            "completada",
            titulo="Completada",
            valor_inicial=False,
        ),

    ]
