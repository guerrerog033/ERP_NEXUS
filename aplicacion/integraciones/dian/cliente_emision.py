from __future__ import annotations

import base64
import zipfile
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path

import requests

from aplicacion.nucleo.configuracion import Configuracion


@dataclass(slots=True)
class ResultadoEmision:

    exito: bool = False
    estado: str = ""
    mensaje: str = ""
    track_id: str = ""
    error: str = ""
    ruta_zip: str = ""
    datos: dict = field(default_factory=dict)


class ClienteEmisionDian:

    @classmethod
    def _url_servicio(cls) -> str:

        ambiente = str(
            Configuracion.obtener(
                "dian",
                "ambiente_emision",
            )
            or "habilitacion",
        ).lower()

        if ambiente in (
            "produccion",
            "production",
        ):

            return (
                "https://vpfe.dian.gov.co"
                "/WcfDianCustomerServices.svc"
            )

        return (
            "https://vpfe-hab.dian.gov.co"
            "/WcfDianCustomerServices.svc"
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
    def _contenedor_incluye_pdf(cls) -> bool:

        valor = Configuracion.obtener(
            "dian",
            "contenedor_incluir_pdf",
        )

        if valor is None:

            return True

        if isinstance(
            valor,
            str,
        ):

            return valor.strip().lower() in (
                "1",
                "true",
                "si",
                "sí",
                "yes",
            )

        return bool(
            valor,
        )

    @classmethod
    def _crear_zip(
        cls,
        nombre_xml: str,
        contenido_xml: str,
        *,
        adjuntos: list[tuple[str, bytes]] | None = None,
    ) -> tuple[bytes, str]:

        buffer = BytesIO()

        with zipfile.ZipFile(
            buffer,
            "w",
            zipfile.ZIP_DEFLATED,
        ) as archivo:

            archivo.writestr(
                nombre_xml,
                contenido_xml,
            )

            for (
                nombre_adjunto,
                contenido_adjunto,
            ) in adjuntos or []:

                archivo.writestr(
                    nombre_adjunto,
                    contenido_adjunto,
                )

        nombre_zip = (
            f"{Path(nombre_xml).stem}.zip"
        )

        return buffer.getvalue(), nombre_zip

    @classmethod
    def _guardar_zip_local(
        cls,
        nombre_zip: str,
        contenido: bytes,
    ) -> str:

        carpeta = Configuracion.obtener(
            "dian",
            "carpeta_xml_venta",
        )

        if not carpeta:

            carpeta = "aplicacion/recursos/xml/facturas_venta"

        destino = Path(carpeta)
        destino.mkdir(
            parents=True,
            exist_ok=True,
        )

        ruta = destino / nombre_zip

        ruta.write_bytes(
            contenido,
        )

        return str(ruta)

    @classmethod
    def enviar(
        cls,
        *,
        nombre_xml: str,
        xml_firmado: str,
        test_set_id: str | None = None,
        adjuntos_contenedor: list[tuple[str, bytes]] | None = None,
    ) -> ResultadoEmision:

        if not Configuracion.obtener(
            "dian",
            "emision_habilitada",
        ):

            return ResultadoEmision(
                error=(
                    "La emisión DIAN está deshabilitada "
                    "en configuración."
                ),
            )

        zip_transmision, nombre_zip = cls._crear_zip(
            nombre_xml,
            xml_firmado,
        )

        adjuntos = (
            adjuntos_contenedor
            if cls._contenedor_incluye_pdf()
            else None
        )

        if adjuntos:

            zip_local, _ = cls._crear_zip(
                nombre_xml,
                xml_firmado,
                adjuntos=adjuntos,
            )

        else:

            zip_local = zip_transmision

        ruta_zip = cls._guardar_zip_local(
            nombre_zip,
            zip_local,
        )

        test_set = (
            test_set_id
            or Configuracion.obtener(
                "dian",
                "test_set_id",
            )
            or ""
        )

        contenido_b64 = base64.b64encode(
            zip_transmision,
        ).decode("ascii")

        envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
               xmlns:wcf="http://wcf.dian.colombia">
  <soap:Header/>
  <soap:Body>
    <wcf:SendTestSetAsync>
      <wcf:fileName>{nombre_zip}</wcf:fileName>
      <wcf:contentFile>{contenido_b64}</wcf:contentFile>
      <wcf:testSetId>{test_set}</wcf:testSetId>
    </wcf:SendTestSetAsync>
  </soap:Body>
</soap:Envelope>"""

        url = cls._url_servicio()

        try:

            respuesta = requests.post(
                url,
                data=envelope.encode("utf-8"),
                headers={
                    "Content-Type": (
                        "application/soap+xml; "
                        "charset=utf-8"
                    ),
                    "SOAPAction": (
                        "http://wcf.dian.colombia/"
                        "IWcfDianCustomerServices/"
                        "SendTestSetAsync"
                    ),
                },
                timeout=cls._timeout(),
            )

        except requests.RequestException as error:

            return ResultadoEmision(
                estado="pendiente_local",
                mensaje=(
                    "XML firmado y ZIP generados. "
                    "No se pudo contactar DIAN."
                ),
                ruta_zip=ruta_zip,
                error=str(error),
            )

        texto = respuesta.text

        if (
            "IsValid>true"
            in texto.replace(" ", "")
            or "Accepted"
            in texto
        ):

            return ResultadoEmision(
                exito=True,
                estado="aceptada",
                mensaje=(
                    "Documento enviado a DIAN "
                    "correctamente."
                ),
                ruta_zip=ruta_zip,
                datos={
                    "http_status": respuesta.status_code,
                    "respuesta": texto[:2000],
                },
            )

        if respuesta.ok:

            return ResultadoEmision(
                estado="enviada",
                mensaje=(
                    "DIAN respondió al envío. "
                    "Revise el estado en el portal."
                ),
                ruta_zip=ruta_zip,
                datos={
                    "http_status": respuesta.status_code,
                    "respuesta": texto[:2000],
                },
            )

        return ResultadoEmision(
            estado="rechazada",
            mensaje=(
                "DIAN rechazó o no procesó el envío."
            ),
            ruta_zip=ruta_zip,
            error=(
                f"HTTP {respuesta.status_code}"
            ),
            datos={
                "respuesta": texto[:2000],
            },
        )
