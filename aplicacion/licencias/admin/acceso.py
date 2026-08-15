from __future__ import annotations

from aplicacion.nucleo.configuracion import Configuracion


def panel_admin_habilitado() -> bool:

    return bool(
        Configuracion.obtener(
            "licencias",
            "panel_admin_habilitado",
        ),
    )


def panel_admin_visible() -> bool:

    if not panel_admin_habilitado():

        return False

    from aplicacion.nucleo.permisos import (
        Permisos,
    )

    if Permisos.acceso_total():

        return True

    return Permisos.rol_codigo() == "admin"
