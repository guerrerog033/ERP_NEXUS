from aplicacion.framework.form import (
    CheckField,
    ComboField,
    DecimalField,
    FormDefinition,
    TextField,
)

from aplicacion.maestros.impuestos.impuestos_table import (
    ImpuestoTable,
)


class ImpuestoDefinition(FormDefinition):

    titulo = "Impuestos"

    table_definition = ImpuestoTable

    campos = [

        TextField(
            nombre="codigo",
            titulo="Código",
            requerido=True,
            longitud_maxima=20,
            upper=True,
        ),

        TextField(
            nombre="nombre",
            titulo="Nombre",
            requerido=True,
            longitud_maxima=120,
            title=True,
        ),

        DecimalField(
            nombre="porcentaje",
            titulo="Porcentaje",
            decimales=2,
            minimo=0,
            maximo=100,
        ),

        ComboField(
            nombre="tipo",
            titulo="Tipo",
            valor_inicial="IVA",
            opciones=[
                ("IVA", "IVA"),
                ("Retención", "Retención"),
                ("Retefuente", "Retefuente"),
                ("ReteICA", "ReteICA"),
                ("INC", "INC"),
                ("Otro", "Otro"),
            ],
        ),

        CheckField(
            nombre="activo",
            titulo="Activo",
            valor_inicial=True,
        ),

    ]
