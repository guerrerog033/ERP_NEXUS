from __future__ import annotations

import base64
import re
from datetime import date, datetime, timedelta
from typing import Any
from urllib.parse import urljoin

import requests

from aplicacion.nucleo.configuracion import Configuracion

from .modelos_recepcion import (
    DocumentoRecibidoDian,
    ResultadoConexionRecepcion,
)


class ClienteRecepcionDian:
    """
    Cliente configurable para sincronizar facturas recibidas
    mediante API REST con token Bearer (Factus, Cifra, Wardian, etc.).
    """

    CAMPOS_CUFE = (
        "cufe",
        "CUFE",
        "document_key",
        "documentKey",
        "track_id",
        "trackId",
        "uuid",
        "UUID",
        "id",
    )

    CAMPOS_NUMERO = (
        "number",
        "numero",
        "document_number",
        "invoice_number",
        "ID",
    )

    CAMPOS_FECHA = (
        "issue_date",
        "fecha",
        "date",
        "IssueDate",
        "created_at",
    )

    CAMPOS_NIT = (
        "supplier_nit",
        "nit_emisor",
        "nit",
        "NIT",
        "sender_nit",
    )

    CAMPOS_RAZON = (
        "supplier_name",
        "razon_social",
        "razon_social_emisor",
        "name",
        "supplier",
    )

    CAMPOS_TOTAL = (
        "total",
        "payable_amount",
        "PayableAmount",
        "valor_total",
    )

    @classmethod
    def _config(cls) -> dict:

        config = (
            Configuracion.obtener(
                "dian",
                "recepcion_compras",
            )
            or {}
        )

        return dict(config)

    @classmethod
    def habilitado(cls) -> bool:

        config = cls._config()

        return bool(
            config.get(
                "habilitado",
                False,
            )
        )

    @classmethod
    def _timeout(cls) -> int:

        try:

            return int(
                Configuracion.obtener(
                    "dian",
                    "timeout_segundos",
                )
                or 60,
            )

        except (
            TypeError,
            ValueError,
        ):

            return 60

    @classmethod
    def _url_base(cls) -> str:

        config = cls._config()

        return str(
            config.get(
                "url_base",
                "",
            )
            or "",
        ).strip().rstrip("/")

    @classmethod
    def _endpoint(
        cls,
        clave: str,
        defecto: str,
    ) -> str:

        config = cls._config()

        endpoints = config.get(
            "endpoints",
        ) or {}

        return str(
            endpoints.get(
                clave,
                defecto,
            )
            or defecto,
        ).strip()

    @classmethod
    def _token_configurado(cls) -> str:

        config = cls._config()

        return str(
            config.get(
                "token",
                "",
            )
            or "",
        ).strip()

    @classmethod
    def _obtener_token_oauth(cls) -> str:

        config = cls._config()

        oauth = config.get(
            "oauth",
        ) or {}

        if not oauth.get(
            "habilitado",
            False,
        ):

            return ""

        url_token = str(
            oauth.get(
                "url_token",
                "",
            )
            or "",
        ).strip()

        client_id = str(
            oauth.get(
                "client_id",
                "",
            )
            or "",
        ).strip()

        client_secret = str(
            oauth.get(
                "client_secret",
                "",
            )
            or "",
        ).strip()

        if (
            not url_token
            or not client_id
        ):

            return ""

        try:

            respuesta = requests.post(
                url_token,
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
                headers={
                    "Accept": "application/json",
                },
                timeout=cls._timeout(),
            )

            respuesta.raise_for_status()

            datos = respuesta.json()

        except (
            requests.RequestException,
            ValueError,
        ):

            return ""

        return str(
            datos.get(
                "access_token",
            )
            or datos.get(
                "token",
            )
            or "",
        ).strip()

    @classmethod
    def _obtener_token(cls) -> str:

        token = cls._token_configurado()

        if token:

            return token

        return cls._obtener_token_oauth()

    @classmethod
    def _headers(cls) -> dict[str, str]:

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": (
                "ERP-NEXUS/1.0 "
                "(recepcion-compras)"
            ),
        }

        token = cls._obtener_token()

        if token:

            headers["Authorization"] = (
                f"Bearer {token}"
            )

        return headers

    @classmethod
    def _nit_receptor(cls) -> str:

        config = cls._config()

        nit = str(
            config.get(
                "nit_receptor",
                "",
            )
            or "",
        ).strip()

        if nit:

            return re.sub(
                r"\D",
                "",
                nit,
            )

        return re.sub(
            r"\D",
            "",
            str(
                Configuracion.obtener(
                    "empresa",
                    "nit",
                )
                or "",
            ),
        )

    @classmethod
    def _dias_consulta(cls) -> int:

        config = cls._config()

        try:

            return max(
                1,
                int(
                    config.get(
                        "dias_consulta",
                        30,
                    )
                    or 30,
                ),
            )

        except (
            TypeError,
            ValueError,
        ):

            return 30

    @classmethod
    def _pagina_tamano(cls) -> int:

        config = cls._config()

        try:

            return max(
                10,
                int(
                    config.get(
                        "pagina_tamano",
                        50,
                    )
                    or 50,
                ),
            )

        except (
            TypeError,
            ValueError,
        ):

            return 50

    @classmethod
    def _formatear_endpoint(
        cls,
        plantilla: str,
        **parametros: Any,
    ) -> str:

        valores = {
            clave: str(
                valor,
            )
            for clave, valor in parametros.items()
        }

        try:

            return plantilla.format(
                **valores,
            )

        except KeyError:

            return plantilla

    @classmethod
    def _url_completa(
        cls,
        ruta: str,
    ) -> str:

        if ruta.startswith(
            "http://",
        ) or ruta.startswith(
            "https://",
        ):

            return ruta

        base = cls._url_base()

        if not base:

            raise ValueError(
                "Configure dian.recepcion_compras.url_base "
                "en configuracion.json.",
            )

        return urljoin(
            f"{base}/",
            ruta.lstrip("/"),
        )

    @classmethod
    def _valor_campo(
        cls,
        registro: dict,
        campos: tuple[str, ...],
        defecto: str = "",
    ) -> str:

        for campo in campos:

            if campo not in registro:

                continue

            valor = registro.get(
                campo,
            )

            if valor is None:

                continue

            texto = str(
                valor,
            ).strip()

            if texto:

                return texto

        return defecto

    @classmethod
    def _parsear_fecha(
        cls,
        valor: str,
    ) -> date | None:

        if not valor:

            return None

        texto = str(
            valor,
        ).strip()[:10]

        for formato in (
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d-%m-%Y",
        ):

            try:

                return datetime.strptime(
                    texto,
                    formato,
                ).date()

            except ValueError:

                continue

        return None

    @classmethod
    def _parsear_documento(
        cls,
        registro: dict,
    ) -> DocumentoRecibidoDian | None:

        if not isinstance(
            registro,
            dict,
        ):

            return None

        cufe = cls._valor_campo(
            registro,
            cls.CAMPOS_CUFE,
        )

        track_id = (
            cufe
            or cls._valor_campo(
                registro,
                (
                    "track_id",
                    "trackId",
                    "id",
                ),
            )
        )

        if not track_id:

            return None

        fecha_texto = cls._valor_campo(
            registro,
            cls.CAMPOS_FECHA,
        )

        total_texto = cls._valor_campo(
            registro,
            cls.CAMPOS_TOTAL,
        )

        try:

            total = float(
                total_texto.replace(
                    ",",
                    "",
                )
                if total_texto
                else 0,
            )

        except ValueError:

            total = 0.0

        return DocumentoRecibidoDian(
            track_id=track_id,
            cufe=cufe or track_id,
            numero=cls._valor_campo(
                registro,
                cls.CAMPOS_NUMERO,
            ),
            fecha=cls._parsear_fecha(
                fecha_texto,
            ),
            nit_emisor=re.sub(
                r"\D",
                "",
                cls._valor_campo(
                    registro,
                    cls.CAMPOS_NIT,
                ),
            ),
            razon_social_emisor=cls._valor_campo(
                registro,
                cls.CAMPOS_RAZON,
            ),
            total=total,
            datos=registro,
        )

    @classmethod
    def _extraer_registros(
        cls,
        datos: Any,
    ) -> list[dict]:

        if isinstance(
            datos,
            list,
        ):

            return [
                item
                for item in datos
                if isinstance(
                    item,
                    dict,
                )
            ]

        if not isinstance(
            datos,
            dict,
        ):

            return []

        for clave in (
            "data",
            "documents",
            "documentos",
            "items",
            "results",
            "received",
            "facturas",
        ):

            valor = datos.get(
                clave,
            )

            if isinstance(
                valor,
                list,
            ):

                return [
                    item
                    for item in valor
                    if isinstance(
                        item,
                        dict,
                    )
                ]

        return []

    @classmethod
    def probar_conexion(cls) -> ResultadoConexionRecepcion:

        if not cls.habilitado():

            return ResultadoConexionRecepcion(
                error=(
                    "La recepción de compras DIAN "
                    "está deshabilitada."
                ),
            )

        if not cls._obtener_token():

            return ResultadoConexionRecepcion(
                error=(
                    "Configure el token Bearer en "
                    "dian.recepcion_compras.token."
                ),
            )

        if not cls._url_base():

            return ResultadoConexionRecepcion(
                error=(
                    "Configure la URL base del proveedor "
                    "de integración DIAN."
                ),
            )

        hoy = date.today()

        try:

            documentos = cls.listar_recibidos(
                fecha_desde=hoy
                - timedelta(
                    days=7,
                ),
                fecha_hasta=hoy,
                pagina=1,
            )

        except (
            ValueError,
            requests.RequestException,
        ) as error:

            return ResultadoConexionRecepcion(
                error=str(
                    error,
                ),
            )

        return ResultadoConexionRecepcion(
            exito=True,
            mensaje=(
                "Conexión exitosa. "
                f"Documentos consultables: {len(documentos)} "
                "(últimos 7 días)."
            ),
        )

    @classmethod
    def listar_recibidos(
        cls,
        *,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        pagina: int = 1,
    ) -> list[DocumentoRecibidoDian]:

        if not cls.habilitado():

            raise ValueError(
                "La recepción de compras DIAN "
                "está deshabilitada.",
            )

        if fecha_hasta is None:

            fecha_hasta = date.today()

        if fecha_desde is None:

            fecha_desde = (
                fecha_hasta
                - timedelta(
                    days=cls._dias_consulta(),
                )
            )

        plantilla = cls._endpoint(
            "listar_recibidos",
            (
                "/v1/documents/received?"
                "page={page}&per_page={per_page}"
                "&from={fecha_desde}&to={fecha_hasta}"
                "&receiver_nit={nit_receptor}"
            ),
        )

        ruta = cls._formatear_endpoint(
            plantilla,
            page=pagina,
            per_page=cls._pagina_tamano(),
            fecha_desde=fecha_desde.isoformat(),
            fecha_hasta=fecha_hasta.isoformat(),
            nit_receptor=cls._nit_receptor(),
        )

        url = cls._url_completa(
            ruta,
        )

        respuesta = requests.get(
            url,
            headers=cls._headers(),
            timeout=cls._timeout(),
        )

        respuesta.raise_for_status()

        try:

            datos = respuesta.json()

        except ValueError as error:

            raise ValueError(
                "La API no devolvió JSON válido."
            ) from error

        registros = cls._extraer_registros(
            datos,
        )

        documentos: list[DocumentoRecibidoDian] = []

        for registro in registros:

            documento = cls._parsear_documento(
                registro,
            )

            if documento is not None:

                documentos.append(
                    documento,
                )

        return documentos

    @classmethod
    def descargar_xml(
        cls,
        track_id: str,
    ) -> str:

        if not track_id:

            raise ValueError(
                "El identificador del documento es obligatorio.",
            )

        plantilla = cls._endpoint(
            "descargar_xml",
            "/v1/documents/{track_id}/xml",
        )

        ruta = cls._formatear_endpoint(
            plantilla,
            track_id=track_id,
        )

        url = cls._url_completa(
            ruta,
        )

        respuesta = requests.get(
            url,
            headers=cls._headers(),
            timeout=cls._timeout(),
        )

        respuesta.raise_for_status()

        contenido_tipo = str(
            respuesta.headers.get(
                "Content-Type",
                "",
            )
        ).lower()

        if (
            "xml" in contenido_tipo
            or respuesta.text.strip().startswith(
                "<?xml",
            )
            or respuesta.text.strip().startswith(
                "<Invoice",
            )
        ):

            return respuesta.text

        try:

            datos = respuesta.json()

        except ValueError as error:

            raise ValueError(
                "No se pudo interpretar el XML descargado."
            ) from error

        if isinstance(
            datos,
            dict,
        ):

            for clave in (
                "xml",
                "content",
                "document",
                "data",
                "file",
            ):

                valor = datos.get(
                    clave,
                )

                if isinstance(
                    valor,
                    str,
                ) and (
                    "<" in valor
                    or len(valor) > 100
                ):

                    if valor.strip().startswith(
                        "PD94",
                    ):

                        return base64.b64decode(
                            valor,
                        ).decode(
                            "utf-8",
                            errors="replace",
                        )

                    return valor

        raise ValueError(
            "La API no devolvió contenido XML reconocible.",
        )

    @classmethod
    def enviar_acuse_recibo(
        cls,
        *,
        cufe: str,
        numero_factura: str,
        nit_proveedor: str,
        xml_evento: str = "",
        codigo_evento: str = "030",
    ):

        from .modelos_recepcion import ResultadoEnvioEvento

        if not cls.habilitado():

            return ResultadoEnvioEvento(
                mensaje=(
                    "Recepción DIAN deshabilitada. "
                    "Acuse generado localmente."
                ),
            )

        plantilla = cls._endpoint(
            "enviar_acuse_recibo",
            "/v1/radian/events/{codigo_evento}",
        )

        ruta = cls._formatear_endpoint(
            plantilla,
            codigo_evento=codigo_evento,
            track_id=cufe,
            cufe=cufe,
        )

        url = cls._url_completa(
            ruta,
        )

        payload = {
            "cufe": cufe,
            "invoice_number": numero_factura,
            "supplier_nit": nit_proveedor,
            "event_code": codigo_evento,
            "receiver_nit": cls._nit_receptor(),
        }

        if xml_evento:

            payload["xml"] = xml_evento

        try:

            respuesta = requests.post(
                url,
                json=payload,
                headers=cls._headers(),
                timeout=cls._timeout(),
            )

            if respuesta.status_code in (
                404,
                405,
            ):

                return ResultadoEnvioEvento(
                    mensaje=(
                        "Acuse generado localmente. "
                        "Configure el endpoint "
                        "enviar_acuse_recibo en la API."
                    ),
                )

            respuesta.raise_for_status()

            try:

                datos = respuesta.json()

            except ValueError:

                datos = {
                    "respuesta": respuesta.text[:500],
                }

            mensaje = str(
                datos.get(
                    "message",
                )
                or datos.get(
                    "mensaje",
                )
                or "Acuse enviado a DIAN.",
            )

            exito = bool(
                datos.get(
                    "success",
                    True,
                )
                or datos.get(
                    "exito",
                    True,
                )
                or respuesta.ok,
            )

            return ResultadoEnvioEvento(
                exito=exito,
                mensaje=mensaje,
                datos=datos,
            )

        except requests.RequestException as error:

            return ResultadoEnvioEvento(
                mensaje=(
                    "Acuse generado localmente. "
                    "No se pudo enviar a la API."
                ),
                error=str(
                    error,
                ),
            )
