from aplicacion.framework.form import (
    FormDefinition,
    FieldGroup,
    TextField,
    EmailField,
    PhoneField,
    CheckField,
    ComboField,
)

from aplicacion.framework.form.form_layout import FormLayout

from aplicacion.maestros.empresas.empresas_table import (
    EmpresaTable,
)


class EmpresaDefinition(FormDefinition):

    titulo = "Empresas"

    descripcion = "Administración de empresas."

    table_definition = EmpresaTable


    layout = FormLayout(

        columnas=[

            [
                "Información General",
            ],

            [
                "Ubicación",
                "Contacto",
                "Estado",
            ],

        ],

        proporcion=(2, 1),

    )


    grupos = [

        # =====================================================
        # Información General
        # =====================================================

        FieldGroup(

            titulo="Información General",

            columnas=1,

            separacion=16,

            campos=[

                TextField(
                    nombre="nit",
                    titulo="NIT",
                    requerido=True,
                    longitud_maxima=20,
                    upper=True,
                ),

                TextField(
                    nombre="dv",
                    titulo="DV",
                    longitud_maxima=2,
                    upper=True,
                ),

                TextField(
                    nombre="razon_social",
                    titulo="Razón Social",
                    requerido=True,
                    longitud_maxima=200,
                    title=True,
                ),

                TextField(
                    nombre="nombre_comercial",
                    titulo="Nombre Comercial",
                    longitud_maxima=200,
                    title=True,
                ),

                TextField(
                    nombre="representante_legal",
                    titulo="Representante Legal",
                    longitud_maxima=200,
                    title=True,
                ),

                TextField(
                    nombre="actividad_economica",
                    titulo="Actividad Económica",
                    longitud_maxima=150,
                    title=True,
                ),


                ComboField(
                    nombre="regimen_tributario",
                    titulo="Régimen Tributario",
                    opciones=[

                        (
                            "Régimen Ordinario",
                            "Régimen Ordinario"
                        ),

                        (
                            "Régimen Simple",
                            "Régimen Simple"
                        ),

                    ],
                ),


                ComboField(
                    nombre="responsable_iva",
                    titulo="Responsable IVA",
                    opciones=[

                        (
                            "Responsable IVA",
                            True
                        ),

                        (
                            "No responsable IVA",
                            False
                        ),

                    ],
                ),


            ],

        ),



        # =====================================================
        # Ubicación
        # =====================================================

        FieldGroup(

            titulo="Ubicación",

            columnas=1,

            separacion=16,

            campos=[

                TextField(
                    nombre="direccion",
                    titulo="Dirección",
                    title=True,
                ),

                TextField(
                    nombre="pais",
                    titulo="País",
                    valor_inicial="Colombia",
                    title=True,
                ),

                TextField(
                    nombre="departamento",
                    titulo="Departamento",
                    title=True,
                ),

                TextField(
                    nombre="ciudad",
                    titulo="Ciudad",
                    title=True,
                ),

            ],

        ),



        # =====================================================
        # Contacto
        # =====================================================

        FieldGroup(

            titulo="Contacto",

            columnas=1,

            separacion=16,

            campos=[

                PhoneField(
                    nombre="telefono",
                    titulo="Teléfono",
                ),

                PhoneField(
                    nombre="celular",
                    titulo="Celular",
                ),

                EmailField(
                    nombre="correo",
                    titulo="Correo",
                ),

                TextField(
                    nombre="sitio_web",
                    titulo="Sitio Web",
                ),

            ],

        ),



        # =====================================================
        # Estado
        # =====================================================

        FieldGroup(

            titulo="Estado",

            columnas=1,

            separacion=16,

            campos=[

                CheckField(
                    nombre="activo",
                    titulo="Empresa Activa",
                    valor_inicial=True,
                ),

            ],

        ),

    ]
