from aplicacion.framework.form.documento_field import (
    DocumentoField,
)
from aplicacion.framework.form import (
    FormDefinition,
    FieldGroup,
    TextField,
    ComboField,
    CheckField,
    DecimalField,
    IntegerField,
    LookupField,
    PhoneField,
    FormLayout,
)

from aplicacion.maestros.listas_precio.lista_precio_lookup import (
    ListaPrecioLookup,
)

from aplicacion.maestros.terceros.constantes import (
    REGIMEN_IVA_OPCIONES,
    RESPONSABILIDAD_FISCAL,
)
from aplicacion.maestros.terceros.terceros_table import (
    TerceroTable,
)

class TerceroDefinition(FormDefinition):

    titulo = "Terceros"

    layout = FormLayout(

        columnas=[

            [
                "Información General",
                "Empresa",
                "Persona Natural",
            ],

            [
                "Ubicación",
                "Contacto",
                "Condiciones comerciales",
                "Información Tributaria",
                "Responsabilidad Fiscal *",
                "Estado",
            ],

        ],

        proporcion=(1, 1),

        separacion=12,

        separacion_grupos=8,

    )

    grupos = [

        FieldGroup(
            "Información General",
            [

                ComboField(
                    "tipo_documento",
                    titulo="Tipo Documento",
                    requerido_dian=True,
                    opciones=[
                        ("CC", "CC"),
                        ("CE", "CE"),
                        ("NIT", "NIT"),
                        ("TI", "TI"),
                        ("PAS", "PAS"),
                    ],
                ),

                DocumentoField(
                    "numero_documento",
                    titulo="Número Documento",
                    requerido=True,
                    requerido_dian=True,
                    longitud_maxima=30,
                ),

                TextField(
                    "dv",
                    titulo="DV",
                    requerido_dian=True,
                    longitud_maxima=2,
                    habilitado=False,
                ),

                ComboField(
                    "tipo_tercero",
                    titulo="Tipo de Tercero",
                    requerido=True,
                    opciones=[
                        ("Clientes", "Cliente"),
                        ("Proveedores", "Proveedor"),
                        ("Otros", "Otro"),
                    ],
                ),
            ],
        ),

        FieldGroup(
            "Empresa",
            [

                TextField(
                    "razon_social",
                    titulo="Razón Social",
                    requerido_dian=True,
                    longitud_maxima=200,
                ),

                TextField(
                    "nombre_comercial",
                    titulo="Nombre Comercial",
                    longitud_maxima=200,
                ),
            ],
        ),

        FieldGroup(
            "Persona Natural",
            [

                TextField(
                    "primer_nombre",
                    titulo="Primer Nombre",
                    requerido_dian=True,
                    longitud_maxima=100,
                ),

                TextField(
                    "segundo_nombre",
                    titulo="Segundo Nombre",
                    longitud_maxima=100,
                ),

                TextField(
                    "primer_apellido",
                    titulo="Primer Apellido",
                    requerido_dian=True,
                    longitud_maxima=100,
                ),

                TextField(
                    "segundo_apellido",
                    titulo="Segundo Apellido",
                    longitud_maxima=100,
                ),
            ],
        ),

        FieldGroup(
            "Ubicación",
            [

                TextField(
                    "direccion",
                    titulo="Dirección",
                    requerido_dian=True,
                    longitud_maxima=200,
                ),

                TextField(
                    "pais",
                    titulo="País",
                    requerido_dian=True,
                    longitud_maxima=100,
                ),

                TextField(
                    "departamento",
                    titulo="Departamento",
                    requerido_dian=True,
                    longitud_maxima=100,
                ),

                TextField(
                    "ciudad",
                    titulo="Ciudad",
                    requerido_dian=True,
                    longitud_maxima=100,
                ),
            ],
        ),

        FieldGroup(
            "Contacto",
            [

                PhoneField(
                    "telefono",
                    titulo="Teléfono",
                    longitud_maxima=30,
                ),

                PhoneField(
                    "celular",
                    titulo="Celular",
                    longitud_maxima=30,
                ),

                TextField(
                    "correo",
                    titulo="Correo",
                    requerido_dian=True,
                    longitud_maxima=150,
                    descripcion=(
                        "Formato: usuario@dominio.com"
                    ),
                ),
            ],
        ),

        FieldGroup(
            "Condiciones comerciales",
            [

                LookupField(
                    "lista_precio_id",
                    titulo="Lista de precios",
                    datasource=ListaPrecioLookup,
                    permitir_vacio=True,
                ),

                IntegerField(
                    "dias_credito",
                    titulo="Días de crédito",
                    minimo=0,
                    valor_inicial=0,
                    descripcion="0 = contado",
                ),

                DecimalField(
                    "cupo_credito",
                    titulo="Cupo de crédito",
                    decimales=0,
                    minimo=0,
                    valor_inicial=0,
                ),

                TextField(
                    "vendedor_asignado",
                    titulo="Vendedor asignado",
                    longitud_maxima=120,
                ),

                CheckField(
                    "exento_bloqueo_cartera",
                    titulo="Exento de bloqueo por cartera vencida",
                ),
            ],
        ),

        FieldGroup(
            "Información Tributaria",
            [

                ComboField(
                    "tipo_regimen_iva",
                    titulo="Tipo de régimen IVA",
                    requerido_dian=True,
                    permitir_vacio=True,
                    opciones=list(
                        REGIMEN_IVA_OPCIONES,
                    ),
                ),

                ComboField(
                    "retefuente_id",
                    titulo="Retefuente predeterminada",
                    permitir_vacio=True,
                    opciones=[],
                ),

                ComboField(
                    "reteica_id",
                    titulo="ReteICA predeterminada",
                    permitir_vacio=True,
                    opciones=[],
                ),

                ComboField(
                    "reteiva_id",
                    titulo="ReteIVA predeterminada",
                    permitir_vacio=True,
                    opciones=[],
                ),
            ],
        ),

        FieldGroup(
            "Responsabilidad Fiscal *",
            [

                CheckField(
                    nombre,
                    titulo=etiqueta,
                    valor_inicial=(
                        nombre == "resp_r99_pn"
                    ),
                )

                for nombre, etiqueta
                in RESPONSABILIDAD_FISCAL

            ],
        ),

        FieldGroup(
            "Estado",
            [

                CheckField(
                    "activo",
                    titulo="Tercero activo",
                    valor_inicial=True,
                ),
            ],
        ),
    ]

    table_definition = TerceroTable