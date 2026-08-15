from aplicacion.framework.form import (
    CheckField,
    ComboField,
    DecimalField,
    FieldGroup,
    FormDefinition,
    FormLayout,
    LookupField,
    TextAreaField,
    TextField,
)

from aplicacion.maestros.categorias.categoria_lookup import (
    CategoriaLookup,
)

from aplicacion.maestros.marcas.marca_lookup import (
    MarcaLookup,
)

from aplicacion.maestros.unidades_medida.unidad_medida_lookup import (
    UnidadMedidaLookup,
)

from aplicacion.maestros.productos.productos_table import (
    ProductoTable,
)


class ProductoDefinition(FormDefinition):

    titulo = "Productos"

    layout = FormLayout(
        columnas=[

            [
                "Identificación",
                "Precios",
            ],

            [
                "Impuestos",
                "Información adicional",
            ],

        ],

        proporcion=(1, 1),

        separacion=12,

        separacion_grupos=10,

    )

    table_definition = ProductoTable

    grupos = [

        FieldGroup(
            titulo="Identificación",
            campos=[

                TextField(
                    nombre="codigo",
                    titulo="Código",
                    requerido=True,
                    longitud_maxima=30,
                    upper=True,
                ),

                TextField(
                    nombre="codigo_barras",
                    titulo="Código de barras",
                    longitud_maxima=50,
                ),

                TextField(
                    nombre="nombre",
                    titulo="Nombre",
                    requerido=True,
                    longitud_maxima=200,
                    title=True,
                ),

                ComboField(
                    nombre="tipo",
                    titulo="Tipo",
                    requerido=True,
                    valor_inicial="producto",
                    opciones=[
                        ("Producto", "producto"),
                        ("Servicio", "servicio"),
                    ],
                ),

                LookupField(
                    nombre="unidad_medida_id",
                    titulo="Unidad de medida",
                    datasource=UnidadMedidaLookup,
                    permitir_vacio=False,
                ),

                LookupField(
                    nombre="categoria_id",
                    titulo="Categoría",
                    datasource=CategoriaLookup,
                    permitir_vacio=True,
                ),

                LookupField(
                    nombre="marca_id",
                    titulo="Marca",
                    datasource=MarcaLookup,
                    permitir_vacio=True,
                ),

            ],
        ),

        FieldGroup(
            titulo="Precios",
            campos=[

                DecimalField(
                    nombre="precio_venta",
                    titulo="Precio venta (lista predeterminada)",
                    decimales=2,
                    minimo=0,
                ),

                CheckField(
                    nombre="precio_incluye_iva",
                    titulo="Precio venta con IVA incluido",
                    valor_inicial=False,
                ),

                DecimalField(
                    nombre="costo",
                    titulo="Costo",
                    decimales=2,
                    minimo=0,
                ),

                DecimalField(
                    nombre="existencia",
                    titulo="Existencia (referencia)",
                    decimales=2,
                    minimo=0,
                    valor_inicial=0,
                    habilitado=False,
                    descripcion=(
                        "Referencia inicial sin variantes. "
                        "El stock real se obtiene del kardex."
                    ),
                ),

                DecimalField(
                    nombre="stock_minimo",
                    titulo="Stock mínimo",
                    decimales=2,
                    minimo=0,
                    valor_inicial=0,
                    descripcion=(
                        "Alerta de reposición; no modifica el kardex."
                    ),
                ),

            ],
        ),

        FieldGroup(
            titulo="Impuestos",
            campos=[

                ComboField(
                    nombre="impuesto_venta_id",
                    titulo="Impuesto venta",
                    opciones=[],
                ),

                ComboField(
                    nombre="impuesto_compra_id",
                    titulo="Impuesto compra",
                    opciones=[],
                ),

            ],
        ),

        FieldGroup(
            titulo="Información adicional",
            campos=[

                TextAreaField(
                    nombre="descripcion",
                    titulo="Descripción",
                    longitud_maxima=500,
                ),

                CheckField(
                    nombre="maneja_variantes",
                    titulo="Maneja variantes (talla, color, stock por variante)",
                    valor_inicial=False,
                ),

                CheckField(
                    nombre="es_kit",
                    titulo="Es un kit/combo (se compone de otros productos)",
                    valor_inicial=False,
                ),

                CheckField(
                    nombre="maneja_lote",
                    titulo="Controla existencia por lote",
                    valor_inicial=False,
                ),

                CheckField(
                    nombre="maneja_serie",
                    titulo="Controla existencia por número de serie",
                    valor_inicial=False,
                ),

                CheckField(
                    nombre="activo",
                    titulo="Activo",
                    valor_inicial=True,
                ),

            ],
        ),

    ]
