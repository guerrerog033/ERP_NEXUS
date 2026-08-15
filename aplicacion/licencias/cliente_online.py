from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import requests

from aplicacion.licencias.huella import obtener_huella_equipo
from aplicacion.nucleo.configuracion import Configuracion


@dataclass(slots=True)
class ResultadoValidacionOnline:

    valido: bool = False

    revocado: bool = False

    mensaje: str = ""

    edicion: str = ""

    max_usuarios: int = 0

    conexion_ok: bool = False


def _config_servidor() -> dict:

    config = (
        Configuracion.obtener(
            "licencias",
            "servidor_online",
        )
        or {}
    )

    return dict(config)


def servidor_online_habilitado() -> bool:

    config = _config_servidor()

    return bool(
        config.get(
            "habilitado",
            False,
        ),
    )


def _fallar_sin_conexion() -> bool:

    config = _config_servidor()

    return bool(
        config.get(
            "fallar_si_sin_conexion",
            False,
        ),
    )


def _timeout() -> int:

    config = _config_servidor()

    return int(
        config.get(
            "timeout_segundos",
            10,
        )
        or 10,
    )


def _headers() -> dict[str, str]:

    config = _config_servidor()

    token = str(
        config.get(
            "token_api",
            "",
        )
        or "",
    ).strip()

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if token:

        headers["Authorization"] = (
            f"Bearer {token}"
        )

    return headers


def _url(
    clave: str,
    defecto: str,
) -> str:

    config = _config_servidor()

    return str(
        config.get(
            clave,
            defecto,
        )
        or defecto,
    ).strip()


def _payload_base(
    serial: str,
) -> dict:

    return {
        "serial": serial,
        "huella_equipo": obtener_huella_equipo(),
        "producto": "ERP_NEXUS",
        "version": str(
            Configuracion.obtener(
                "erp",
                "version",
            )
            or "1.0.0",
        ),
        "fecha_consulta": datetime.utcnow().isoformat(),
    }


def _interpretar_respuesta(
    datos: dict,
) -> ResultadoValidacionOnline:

    revocado = bool(
        datos.get(
            "revocado",
            False,
        ),
    )

    valido = bool(
        datos.get(
            "valido",
            False,
        ),
    ) and not revocado

    return ResultadoValidacionOnline(

        valido=valido,

        revocado=revocado,

        mensaje=str(
            datos.get(
                "mensaje",
                "",
            )
            or "",
        ),

        edicion=str(
            datos.get(
                "edicion",
                "",
            )
            or "",
        ),

        max_usuarios=int(
            datos.get(
                "max_usuarios",
                0,
            )
            or 0,
        ),

        conexion_ok=True,

    )


class ClienteLicenciaOnline:

    @classmethod
    def validar_vigencia(
        cls,
        serial: str,
    ) -> ResultadoValidacionOnline:

        if not servidor_online_habilitado():

            return ResultadoValidacionOnline(

                valido=True,

                conexion_ok=True,

                mensaje="Validación online deshabilitada.",

            )

        url = _url(
            "url_validar",
            "",
        )

        if not url:

            if _fallar_sin_conexion():

                return ResultadoValidacionOnline(

                    valido=False,

                    mensaje=(
                        "No está configurada la URL "
                        "del servidor de licencias."
                    ),

                )

            return ResultadoValidacionOnline(

                valido=True,

                mensaje="Sin URL de validación.",

            )

        try:

            respuesta = requests.post(
                url,
                json=_payload_base(
                    serial,
                ),
                headers=_headers(),
                timeout=_timeout(),
            )

            respuesta.raise_for_status()

            return _interpretar_respuesta(
                respuesta.json(),
            )

        except requests.RequestException as error:

            if _fallar_sin_conexion():

                return ResultadoValidacionOnline(

                    valido=False,

                    mensaje=(
                        "No se pudo validar la licencia "
                        f"en línea: {error}"
                    ),

                )

            return ResultadoValidacionOnline(

                valido=True,

                conexion_ok=False,

                mensaje=(
                    "Servidor de licencias no disponible; "
                    "se usará validación local."
                ),

            )

    @classmethod
    def activar(
        cls,
        serial: str,
        *,
        titular: str = "",
        nit_cliente: str = "",
    ) -> ResultadoValidacionOnline:

        if not servidor_online_habilitado():

            return ResultadoValidacionOnline(

                valido=True,

                conexion_ok=True,

            )

        url = _url(
            "url_activar",
            "",
        )

        if not url:

            url = _url(
                "url_validar",
                "",
            )

        if not url:

            if _fallar_sin_conexion():

                return ResultadoValidacionOnline(

                    valido=False,

                    mensaje=(
                        "No está configurada la URL "
                        "de activación."
                    ),

                )

            return ResultadoValidacionOnline(
                valido=True,
            )

        payload = _payload_base(
            serial,
        )

        payload["titular"] = titular
        payload["nit_cliente"] = nit_cliente

        try:

            respuesta = requests.post(
                url,
                json=payload,
                headers=_headers(),
                timeout=_timeout(),
            )

            respuesta.raise_for_status()

            return _interpretar_respuesta(
                respuesta.json(),
            )

        except requests.RequestException as error:

            if _fallar_sin_conexion():

                return ResultadoValidacionOnline(

                    valido=False,

                    mensaje=(
                        "No se pudo activar la licencia "
                        f"en línea: {error}"
                    ),

                )

            return ResultadoValidacionOnline(

                valido=True,

                conexion_ok=False,

                mensaje=str(
                    error,
                ),

            )

    @classmethod
    def probar_conexion(cls) -> ResultadoValidacionOnline:

        if not servidor_online_habilitado():

            return ResultadoValidacionOnline(

                valido=False,

                mensaje="Validación online deshabilitada.",

            )

        url = _url(
            "url_validar",
            "",
        )

        if not url:

            return ResultadoValidacionOnline(

                valido=False,

                mensaje="URL de validación no configurada.",

            )

        try:

            respuesta = requests.post(
                url,
                json={
                    "prueba": True,
                    "producto": "ERP_NEXUS",
                },
                headers=_headers(),
                timeout=_timeout(),
            )

            respuesta.raise_for_status()

            return ResultadoValidacionOnline(

                valido=True,

                conexion_ok=True,

                mensaje="Conexión exitosa con el servidor.",

            )

        except requests.RequestException as error:

            return ResultadoValidacionOnline(

                valido=False,

                mensaje=str(
                    error,
                ),

            )
