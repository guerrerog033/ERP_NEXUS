from __future__ import annotations

from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.framework.menu_ids import MODULOS_IDS

from .repositorio import RepositorioRol


class ServicioRol(ServicioBase):

    repositorio = RepositorioRol

    ROLES_PROTEGIDOS = {
        "admin",
    }

    @classmethod
    def validar(
        cls,
        datos,
        id_registro=None,
    ):

        codigo = str(
            datos.get(
                "codigo",
                "",
            ),
        ).strip().lower()

        nombre = str(
            datos.get(
                "nombre",
                "",
            ),
        ).strip()

        if not codigo:

            raise ValueError(
                "El código es obligatorio.",
            )

        if not nombre:

            raise ValueError(
                "El nombre es obligatorio.",
            )

        if cls.repositorio.existe_codigo(
            codigo,
            excluir_id=id_registro,
        ):

            raise ValueError(
                "Ya existe un rol con ese código.",
            )

        modulos = datos.get(
            "modulos",
        )

        if modulos is None:

            modulos = []

        if not isinstance(
            modulos,
            list,
        ):

            raise ValueError(
                "Los módulos del rol no son válidos.",
            )

        if "*" in modulos:

            modulos = ["*"]

        else:

            modulos = [
                str(item)
                for item in modulos
                if str(item) in MODULOS_IDS
            ]

            if not modulos:

                raise ValueError(
                    "Seleccione al menos un módulo o acceso total.",
                )

        if (
            id_registro is not None
            and codigo in cls.ROLES_PROTEGIDOS
        ):

            registro = cls.obtener_por_id(
                id_registro,
            )

            if (
                registro
                and registro.codigo
                in cls.ROLES_PROTEGIDOS
                and modulos != ["*"]
            ):

                raise ValueError(
                    "El rol administrador debe conservar acceso total.",
                )

        datos["codigo"] = codigo
        datos["nombre"] = nombre
        datos["modulos"] = modulos
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

        if registro.codigo in cls.ROLES_PROTEGIDOS:

            raise ValueError(
                "No se puede eliminar un rol protegido del sistema.",
            )

        from aplicacion.seguridad.usuarios.repositorio import (
            RepositorioUsuario,
        )

        if RepositorioUsuario.contar_por_rol(
            registro.id,
        ) > 0:

            raise ValueError(
                "El rol tiene usuarios asignados.",
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
    def modulos_para_formulario(cls):

        from aplicacion.framework.menu_manifest import (
            MODULOS,
            etiqueta_modulo,
        )

        return [
            (
                etiqueta_modulo(
                    modulo_id,
                ),
                modulo_id,
            )
            for modulo_id in sorted(
                MODULOS.keys(),
            )
        ]

    @classmethod
    def resumen_modulos(
        cls,
        modulos,
    ) -> str:

        if not modulos:

            return "Sin módulos"

        if "*" in modulos:

            return "Acceso total"

        return f"{len(modulos)} módulo(s)"
