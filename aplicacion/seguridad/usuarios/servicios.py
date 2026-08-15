from __future__ import annotations

from aplicacion.autenticacion.seguridad import (
    cifrar_password,
)
from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.nucleo.sesion import Sesion

from .repositorio import RepositorioUsuario


class ServicioUsuario(ServicioBase):

    repositorio = RepositorioUsuario

    @classmethod
    def validar(
        cls,
        datos,
        id_registro=None,
    ):

        usuario = str(
            datos.get(
                "usuario",
                "",
            ),
        ).strip().lower()

        nombre = str(
            datos.get(
                "nombre",
                "",
            ),
        ).strip()

        if not usuario:

            raise ValueError(
                "El usuario es obligatorio.",
            )

        if not nombre:

            raise ValueError(
                "El nombre es obligatorio.",
            )

        if cls.repositorio.existe_usuario(
            usuario,
            excluir_id=id_registro,
        ):

            raise ValueError(
                "Ya existe un usuario con ese login.",
            )

        password = str(
            datos.get(
                "password",
                "",
            )
            or "",
        ).strip()

        if id_registro is None:

            if len(password) < 6:

                raise ValueError(
                    "La contraseña debe tener al menos 6 caracteres.",
                )

            datos["password"] = cifrar_password(
                password,
            )

        elif password:

            if len(password) < 6:

                raise ValueError(
                    "La contraseña debe tener al menos 6 caracteres.",
                )

            datos["password"] = cifrar_password(
                password,
            )

        else:

            datos.pop(
                "password",
                None,
            )

        datos["usuario"] = usuario
        datos["nombre"] = nombre

        correo = str(
            datos.get(
                "correo",
                "",
            )
            or "",
        ).strip()

        datos["correo"] = correo or None

        rol_id = datos.get(
            "rol_id",
        )

        if not rol_id:

            raise ValueError(
                "Seleccione un rol.",
            )

        datos["rol_id"] = int(
            rol_id,
        )

        datos["activo"] = bool(
            datos.get(
                "activo",
                True,
            ),
        )

    @classmethod
    def eliminar(
        cls,
        id_registro,
    ):

        registro = cls.obtener_por_id(
            id_registro,
        )

        if registro is None:

            return False

        sesion = Sesion.usuario()

        if (
            sesion is not None
            and registro.id == sesion.id
        ):

            raise ValueError(
                "No puede eliminar su propio usuario.",
            )

        if (
            registro.rol
            and registro.rol.codigo == "admin"
            and cls.repositorio.contar_admins_activos(
                excluir_id=registro.id,
            ) < 1
            and registro.activo
        ):

            raise ValueError(
                "Debe existir al menos un administrador activo.",
            )

        return cls.repositorio.eliminar(
            id_registro,
        )

    @classmethod
    def buscar(
        cls,
        texto,
    ):

        texto = texto.strip()

        if not texto:

            return cls.obtener_todos()

        return cls.repositorio.buscar(
            texto,
        )

    @classmethod
    def opciones_roles(cls):

        from aplicacion.seguridad.roles.repositorio import (
            RepositorioRol,
        )

        roles = RepositorioRol.obtener_todos()

        return [
            (
                rol.nombre,
                rol.id,
            )
            for rol in roles
            if rol.activo
        ]
