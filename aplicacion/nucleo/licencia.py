from __future__ import annotations

from datetime import datetime


from aplicacion.framework.menu_ids import (
    MODULO_INICIO,
    MODULO_PENDIENTE,
    MODULOS_IDS,
)

class Licencia:

    _habilitada: bool = False

    _acceso_total: bool = True

    _modulos_permitidos: set[str] = set()

    _edicion: str = ""

    _edicion_nombre: str = ""

    _serial: str = ""

    _titular: str = ""

    _max_usuarios: int = 0

    _fecha_vencimiento: datetime | None = None

    @classmethod
    def cargar_desarrollo(
        cls,
    ) -> None:

        cls._habilitada = False

        cls._acceso_total = True

        cls._modulos_permitidos = set(
            MODULOS_IDS,
        )

        cls._edicion = "desarrollo"

        cls._edicion_nombre = "Desarrollo"

        cls._serial = ""

        cls._titular = ""

        cls._max_usuarios = 999

        cls._fecha_vencimiento = None

    @classmethod
    def cargar(
        cls,
        *,
        modulos: list | None,
        edicion: str = "",
        edicion_nombre: str = "",
        serial: str = "",
        titular: str = "",
        max_usuarios: int = 0,
        fecha_vencimiento: datetime | None = None,
        habilitada: bool = True,
    ) -> None:

        cls._habilitada = habilitada

        cls._edicion = edicion or ""

        cls._edicion_nombre = (
            edicion_nombre or edicion
        )

        cls._serial = serial or ""

        cls._titular = titular or ""

        cls._max_usuarios = max_usuarios

        cls._fecha_vencimiento = (
            fecha_vencimiento
        )

        normalizados = [
            str(item)
            for item in (
                modulos or []
            )
            if str(item).strip()
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
    def habilitada(
        cls,
    ) -> bool:

        return cls._habilitada

    @classmethod
    def acceso_total(
        cls,
    ) -> bool:

        if not cls._habilitada:

            return True

        return cls._acceso_total

    @classmethod
    def edicion(
        cls,
    ) -> str:

        return cls._edicion

    @classmethod
    def edicion_nombre(
        cls,
    ) -> str:

        return cls._edicion_nombre

    @classmethod
    def serial(
        cls,
    ) -> str:

        return cls._serial

    @classmethod
    def titular(
        cls,
    ) -> str:

        return cls._titular

    @classmethod
    def max_usuarios(
        cls,
    ) -> int:

        return cls._max_usuarios

    @classmethod
    def fecha_vencimiento(
        cls,
    ) -> datetime | None:

        return cls._fecha_vencimiento

    @classmethod
    def puede_modulo(
        cls,
        modulo_id: str,
    ) -> bool:

        modulo_inicio, modulo_pendiente = (
            MODULO_INICIO,
            MODULO_PENDIENTE,
        )

        if modulo_id in (
            modulo_inicio,
            modulo_pendiente,
            "",
        ):

            return modulo_id == modulo_inicio

        if not cls._habilitada:

            return True

        if modulo_id not in MODULOS_IDS:

            return False

        if cls._acceso_total:

            return True

        return (
            modulo_id
            in cls._modulos_permitidos
        )

    @classmethod
    def limpiar(
        cls,
    ) -> None:

        cls._habilitada = False

        cls._acceso_total = False

        cls._modulos_permitidos = set()

        cls._edicion = ""

        cls._edicion_nombre = ""

        cls._serial = ""

        cls._titular = ""

        cls._max_usuarios = 0

        cls._fecha_vencimiento = None
