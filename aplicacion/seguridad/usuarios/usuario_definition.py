from __future__ import annotations

from aplicacion.framework.form import (
    CheckField,
    ComboField,
    FormDefinition,
    PasswordField,
    TextField,
)
from aplicacion.framework.table import (
    Column,
    TableDefinition,
)
from aplicacion.seguridad.usuarios.servicios import (
    ServicioUsuario,
)


class UsuarioDefinition(FormDefinition):

    titulo = "Usuarios"

    table_definition = TableDefinition(

        titulo="Usuarios",

        columnas=[

            Column(
                nombre="id",
                etiqueta="ID",
                visible=False,
            ),

            Column(
                nombre="usuario",
                etiqueta="Usuario",
            ),

            Column(
                nombre="nombre",
                etiqueta="Nombre",
            ),

            Column(
                nombre="correo",
                etiqueta="Correo",
            ),

            Column(
                nombre="rol_nombre",
                etiqueta="Rol",
            ),

            Column(
                nombre="activo",
                etiqueta="Activo",
            ),

        ],

    )

    campos = [

        TextField(
            nombre="usuario",
            titulo="Usuario",
            requerido=True,
            longitud_maxima=50,
        ),

        TextField(
            nombre="nombre",
            titulo="Nombre completo",
            requerido=True,
            longitud_maxima=150,
        ),

        TextField(
            nombre="correo",
            titulo="Correo",
            longitud_maxima=150,
        ),

        ComboField(
            nombre="rol_id",
            titulo="Rol",
            requerido=True,
            opciones=[],
        ),

        PasswordField(
            nombre="password",
            titulo="Contraseña",
            longitud_maxima=100,
        ),

        CheckField(
            nombre="activo",
            titulo="Activo",
            valor_inicial=True,
        ),

    ]

    @classmethod
    def campos_dinamicos(cls):

        definicion = cls()

        for campo in definicion.campos:

            if campo.nombre == "rol_id":

                campo.opciones = (
                    ServicioUsuario.opciones_roles()
                )

        return definicion.campos
