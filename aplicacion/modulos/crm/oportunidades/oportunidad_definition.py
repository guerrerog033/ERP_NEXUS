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
from aplicacion.framework.datagrid.filtros import (
    LookupFilter,
)
from aplicacion.maestros.terceros.cliente_lookup import (
    ClienteLookup,
)

from aplicacion.modulos.crm.constantes import (
    ETAPAS_OPORTUNIDAD,
)


class OportunidadDefinition(FormDefinition):

    titulo = "Oportunidades"

    table_definition = TableDefinition(

        titulo="Oportunidades CRM",

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
                nombre="titulo",
                etiqueta="Título",
            ),

            Column(
                nombre="cliente_nombre",
                etiqueta="Cliente",
            ),

            StatusColumn(
                nombre="etapa",
                etiqueta="Etapa",
            ),

            DecimalColumn(
                nombre="valor_estimado",
                etiqueta="Valor",
            ),

            DecimalColumn(
                nombre="probabilidad",
                etiqueta="Prob. %",
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

        filtros=[

            LookupFilter(
                "cliente_id",
                etiqueta="Cliente",
                lookup=ClienteLookup,
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

        TextField(
            "titulo",
            titulo="Título",
            requerido=True,
            longitud_maxima=200,
        ),

        LookupField(
            nombre="cliente_id",
            titulo="Cliente",
            datasource=ClienteLookup,
        ),

        ComboField(
            "etapa",
            titulo="Etapa",
            requerido=True,
            opciones=ETAPAS_OPORTUNIDAD,
        ),

        DecimalField(
            "valor_estimado",
            titulo="Valor estimado",
        ),

        DecimalField(
            "probabilidad",
            titulo="Probabilidad (%)",
        ),

        DateField(
            "fecha_cierre_esperada",
            titulo="Fecha cierre esperada",
        ),

        TextField(
            "observaciones",
            titulo="Observaciones",
            longitud_maxima=500,
        ),

        CheckField(
            "activo",
            titulo="Activo",
            valor_inicial=True,
        ),

    ]
