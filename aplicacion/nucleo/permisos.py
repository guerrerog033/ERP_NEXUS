from __future__ import annotations

from aplicacion.framework.menu_ids import (
    MODULO_INICIO,
    MODULO_PENDIENTE,
    MODULOS_IDS,
)

class Permisos:

    _modulos_permitidos: set[str] = set()

    _acceso_total: bool = False

    _rol_codigo: str = ""

    _permisos_accion: dict[str, bool] = {}

    @classmethod
    def cargar_modulos(
        cls,
        modulos: list | None,
        *,
        rol_codigo: str = "",
    ) -> None:

        cls._rol_codigo = rol_codigo or ""

        cls._permisos_accion = {}

        if modulos is None:

            cls._acceso_total = True

            cls._modulos_permitidos = set(
                MODULOS_IDS,
            )

            return

        normalizados = [
            str(
                item,
            )
            for item in modulos
            if str(
                item,
            ).strip()
        ]

        if (
            "*" in normalizados
            or not normalizados
        ):

            cls._acceso_total = True

            cls._modulos_permitidos = set(
                MODULOS_IDS,
            )

            return

        cls._acceso_total = False

        cls._modulos_permitidos = {
            item
            for item in normalizados
            if item in MODULOS_IDS
        }

    @classmethod
    def cargar(
        cls,
        permisos: dict[str, bool],
    ) -> None:

        cls._permisos_accion = dict(
            permisos or {},
        )

    @classmethod
    def rol_codigo(
        cls,
    ) -> str:

        return cls._rol_codigo

    @classmethod
    def acceso_total(
        cls,
    ) -> bool:

        return cls._acceso_total

    @classmethod
    def puede_modulo(
        cls,
        modulo_id: str,
    ) -> bool:

        if modulo_id == MODULO_INICIO:

            return True

        if modulo_id in (
            MODULO_PENDIENTE,
            "",
        ):

            return False

        if modulo_id not in MODULOS_IDS:

            return False

        if modulo_id == "AdminLicencias":

            from aplicacion.licencias.admin.acceso import (
                panel_admin_visible,
            )

            return panel_admin_visible()

        if modulo_id in (
            "AdminUsuarios",
            "AdminRoles",
            "AdminAuditoria",
        ):

            return cls.puede_administrar_seguridad()

        from aplicacion.nucleo.licencia import (
            Licencia,
        )

        if not Licencia.puede_modulo(
            modulo_id,
        ):

            return False

        if cls._acceso_total:

            return True

        return (
            modulo_id
            in cls._modulos_permitidos
        )

    @classmethod
    def tiene(
        cls,
        permiso: str,
    ) -> bool:

        if cls._acceso_total:

            return True

        return cls._permisos_accion.get(
            permiso,
            False,
        )

    @classmethod
    def limpiar(
        cls,
    ) -> None:

        cls._modulos_permitidos = set()

        cls._acceso_total = False

        cls._rol_codigo = ""

        cls._permisos_accion = {}

    @classmethod
    def puede_administrar_seguridad(
        cls,
    ) -> bool:

        if cls._acceso_total:

            return True

        return cls._rol_codigo == "admin"
