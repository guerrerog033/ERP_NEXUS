from __future__ import annotations

import secrets
import threading
from datetime import datetime, timedelta

HORAS_VIGENCIA = 8


class ServicioSesionMovil:
    """
    Sesiones del portal móvil de empleados: viven en memoria del
    proceso del servidor (no en base de datos) — igual que el resto
    del servidor API, que es efímero y se reinicia con la app de
    escritorio. Un token de sesión (no una cookie) identifica al
    usuario autenticado en cada solicitud subsiguiente.
    """

    _sesiones: dict[str, dict] = {}
    _bloqueo = threading.Lock()

    @classmethod
    def iniciar_sesion(
        cls,
        usuario,
    ) -> str:

        token = secrets.token_urlsafe(24)

        with cls._bloqueo:

            cls._sesiones[token] = {
                "usuario_id": usuario.id,
                "nombre": (
                    usuario.nombre
                    or usuario.usuario
                ),
                "expira_en": (
                    datetime.now()
                    + timedelta(hours=HORAS_VIGENCIA)
                ),
            }

        return token

    @classmethod
    def obtener_sesion(
        cls,
        token: str,
    ) -> dict | None:

        if not token:

            return None

        with cls._bloqueo:

            sesion = cls._sesiones.get(token)

            if sesion is None:

                return None

            if sesion["expira_en"] < datetime.now():

                del cls._sesiones[token]

                return None

            return dict(sesion)

    @classmethod
    def cerrar_sesion(
        cls,
        token: str,
    ) -> None:

        with cls._bloqueo:

            cls._sesiones.pop(
                token,
                None,
            )
