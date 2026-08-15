from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

import requests

from aplicacion.nucleo.configuracion import Configuracion


@dataclass(slots=True)
class ResultadoValidacionCufe:

    valido: bool = False
    cufe: str = ""
    estado: str = ""
    mensaje: str = ""
    error: str = ""
    datos: dict = field(default_factory=dict)


class ValidadorCufe:
    """
    Consulta el catálogo público DIAN para verificar un CUFE.
    No requiere certificado digital.
    """

    ESTADOS_VALIDOS = {
        "aceptada",
        "aceptado",
        "valid",
        "valido",
        "válido",
        "approved",
        "accepted",
    }

    @classmethod
    def _url_catalogo(cls) -> str:

        url = Configuracion.obtener(
            "dian",
            "url_catalogo_cufe",
        )

        if url:

            return str(url).rstrip("/")

        ambiente = str(
            Configuracion.obtener(
                "dian",
                "ambiente",
            )
            or "produccion",
        ).lower()

        if ambiente in (
            "habilitacion",
            "pruebas",
            "test",
        ):

            return (
                "https://catalogo-vpfe-hab.dian.gov.co"
                "/document/searchqr"
            )

        return (
            "https://catalogo-vpfe.dian.gov.co"
            "/document/searchqr"
        )

    @classmethod
    def _timeout(cls) -> int:

        try:

            return int(
                Configuracion.obtener(
                    "dian",
                    "timeout_segundos",
                )
                or 30,
            )

        except (
            TypeError,
            ValueError,
        ):

            return 30

    @classmethod
    def _normalizar_cufe(
        cls,
        cufe: str,
    ) -> str:

        return re.sub(
            r"\s+",
            "",
            str(cufe or "").strip(),
        )

    @classmethod
    def _parsear_json(
        cls,
        cuerpo: str,
    ) -> dict | None:

        texto = cuerpo.strip()

        if not texto.startswith(
            "{",
        ):

            return None

        try:

            return json.loads(
                texto,
            )

        except json.JSONDecodeError:

            return None

    @classmethod
    def _estado_desde_texto(
        cls,
        texto: str,
    ) -> tuple[bool, str, str]:

        texto_lower = texto.lower()

        if any(
            indicio in texto_lower
            for indicio in (
                "no se encontr",
                "no existe",
                "not found",
                "documento no",
                "invalid document",
            )
        ):

            return (
                False,
                "no_encontrado",
                "El CUFE no aparece en el catálogo DIAN.",
            )

        if any(
            palabra in texto_lower
            for palabra in cls.ESTADOS_VALIDOS
        ):

            return (
                True,
                "aceptada",
                "Documento encontrado y aceptado en DIAN.",
            )

        if any(
            palabra in texto_lower
            for palabra in (
                "rechaz",
                "anul",
                "invalid",
            )
        ):

            return (
                False,
                "rechazada",
                "El documento existe pero no está aceptado.",
            )

        if len(
            texto.strip(),
        ) > 100:

            return (
                True,
                "consultada",
                "DIAN respondió información para el CUFE.",
            )

        return (
            False,
            "desconocido",
            "No fue posible interpretar la respuesta DIAN.",
        )

    @classmethod
    def _interpretar_respuesta(
        cls,
        cufe: str,
        respuesta: requests.Response,
    ) -> ResultadoValidacionCufe:

        datos_json = cls._parsear_json(
            respuesta.text,
        )

        if isinstance(
            datos_json,
            dict,
        ):

            estado = str(
                datos_json.get(
                    "DocumentStatus",
                )
                or datos_json.get(
                    "Status",
                )
                or datos_json.get(
                    "status",
                )
                or "",
            )

            valido = bool(
                datos_json.get(
                    "Result",
                )
                or datos_json.get(
                    "Valid",
                )
                or estado.lower()
                in cls.ESTADOS_VALIDOS
            )

            mensaje = str(
                datos_json.get(
                    "Message",
                )
                or datos_json.get(
                    "mensaje",
                )
                or "",
            )

            if not mensaje:

                mensaje = (
                    "Documento validado en catálogo DIAN."
                    if valido
                    else "CUFE no validado en DIAN."
                )

            return ResultadoValidacionCufe(
                valido=valido,
                cufe=cufe,
                estado=estado
                or (
                    "aceptada"
                    if valido
                    else "rechazada"
                ),
                mensaje=mensaje,
                datos=datos_json,
            )

        valido, estado, mensaje = cls._estado_desde_texto(
            respuesta.text,
        )

        if respuesta.status_code == 404:

            return ResultadoValidacionCufe(
                valido=False,
                cufe=cufe,
                estado="no_encontrado",
                mensaje=(
                    "El CUFE no fue encontrado "
                    "en el catálogo DIAN."
                ),
            )

        if (
            respuesta.ok
            and valido
        ):

            return ResultadoValidacionCufe(
                valido=True,
                cufe=cufe,
                estado=estado,
                mensaje=mensaje,
            )

        if respuesta.ok:

            return ResultadoValidacionCufe(
                valido=valido,
                cufe=cufe,
                estado=estado,
                mensaje=mensaje,
                datos={
                    "http_status": respuesta.status_code,
                },
            )

        return ResultadoValidacionCufe(
            valido=False,
            cufe=cufe,
            estado="error_http",
            error=(
                f"DIAN respondió HTTP "
                f"{respuesta.status_code}."
            ),
            mensaje=mensaje,
        )

    @classmethod
    def validar(
        cls,
        cufe: str,
    ) -> ResultadoValidacionCufe:

        if not Configuracion.obtener(
            "dian",
            "validacion_cufe",
        ):

            return ResultadoValidacionCufe(
                cufe=cufe,
                error=(
                    "La validación CUFE está deshabilitada "
                    "en configuración."
                ),
            )

        cufe = cls._normalizar_cufe(
            cufe,
        )

        if len(cufe) < 64:

            return ResultadoValidacionCufe(
                cufe=cufe,
                error=(
                    "El CUFE debe tener al menos "
                    "64 caracteres."
                ),
            )

        url = (
            f"{cls._url_catalogo()}"
            f"?documentkey={cufe}"
        )

        try:

            respuesta = requests.get(
                url,
                timeout=cls._timeout(),
                headers={
                    "Accept": (
                        "application/json,"
                        "text/html,"
                        "*/*"
                    ),
                    "User-Agent": (
                        "ERP-NEXUS/1.0 "
                        "(validacion-cufe)"
                    ),
                },
            )

        except requests.RequestException as error:

            return ResultadoValidacionCufe(
                cufe=cufe,
                error=str(error),
                mensaje=(
                    "No se pudo contactar "
                    "el catálogo DIAN."
                ),
            )

        return cls._interpretar_respuesta(
            cufe,
            respuesta,
        )
