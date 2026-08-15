from __future__ import annotations

from PySide6.QtCore import QSettings

from aplicacion.framework.menu_manifest import (
    MODULO_PENDIENTE,
    etiqueta_modulo,
)


class NavegacionUsuario:

    def __init__(
        self,
        usuario_id: str | int,
    ):

        self._usuario_id = str(
            usuario_id,
        )

        self._settings = QSettings(
            "ERP_NEXUS",
            "Navegacion",
        )

    def _clave(
        self,
        sufijo: str,
    ) -> str:

        return (
            f"usuario/{self._usuario_id}/{sufijo}"
        )

    def favoritos(
        self,
    ) -> list[str]:

        valores = self._settings.value(
            self._clave(
                "favoritos",
            ),
            [],
        )

        if not isinstance(
            valores,
            list,
        ):

            return []

        return [
            str(
                item,
            )
            for item in valores
            if str(
                item,
            )
            not in (
                MODULO_PENDIENTE,
            )
        ]

    def es_favorito(
        self,
        modulo_id: str,
    ) -> bool:

        return (
            modulo_id
            in self.favoritos()
        )

    def alternar_favorito(
        self,
        modulo_id: str,
    ) -> bool:

        if modulo_id in (
            MODULO_PENDIENTE,
        ):

            return False

        favoritos = self.favoritos()

        if modulo_id in favoritos:

            favoritos.remove(
                modulo_id,
            )

            self._settings.setValue(
                self._clave(
                    "favoritos",
                ),
                favoritos,
            )

            return False

        favoritos.append(
            modulo_id,
        )

        self._settings.setValue(
            self._clave(
                "favoritos",
            ),
            favoritos,
        )

        return True

    def etiqueta(
        self,
        modulo_id: str,
    ) -> str:

        return etiqueta_modulo(
            modulo_id,
        )
