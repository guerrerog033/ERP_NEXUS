from __future__ import annotations

from aplicacion.nucleo.permisos import Permisos


def panel_seguridad_visible() -> bool:

    return Permisos.puede_administrar_seguridad()
