from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from xml.sax.saxutils import escape

from aplicacion.nucleo.configuracion import Configuracion


CODIGO_ACUSE_RECIBO = "030"

EVENTOS_RADIAN: dict[str, str] = {
    "030": (
        "Acuse de recibo de factura electrónica de venta"
    ),
    "031": (
        "Recibo del bien y/o prestación del servicio"
    ),
    "032": "Aceptación expresa",
    "033": "Aceptación tácita",
    "034": "Reclamo de factura electrónica de venta",
    "035": "Recibo del bien y/o prestación del servicio",
    "036": "Aceptación expresa",
    "037": "Aceptación tácita",
    "038": "Reclamo de factura electrónica de venta",
    "039": "Evento RADIAN 039",
    "040": "Evento RADIAN 040",
    "041": "Evento RADIAN 041",
    "042": "Evento RADIAN 042",
    "043": "Evento RADIAN 043",
    "044": "Evento RADIAN 044",
    "045": "Evento RADIAN 045",
    "046": "Evento RADIAN 046",
    "047": "Evento RADIAN 047",
    "048": "Evento RADIAN 048",
    "049": "Evento RADIAN 049",
}

NS = (
    'xmlns="urn:oasis:names:specification:ubl:schema:xsd:ApplicationResponse-2" '
    'xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" '
    'xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" '
    'xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" '
    'xmlns:sts="dian:gov:co:facturaelectronica:Structures-2-1" '
    'xmlns:ds="http://www.w3.org/2000/09/xmldsig#"'
)


@dataclass(slots=True)
class DatosAcuseRecibo:

    xml: str
    cude: str
    numero_evento: str
    codigo_evento: str
    ruta_xml: str = ""


class GeneradorAcuseRecibo:
    """
    Genera ApplicationResponse RADIAN (030–049).
    """

    @classmethod
    def descripcion_evento(
        cls,
        codigo_evento: str,
    ) -> str:

        codigo = str(
            codigo_evento or CODIGO_ACUSE_RECIBO,
        ).zfill(3)[-3:]

        return EVENTOS_RADIAN.get(
            codigo,
            f"Evento RADIAN {codigo}",
        )

    @classmethod
    def _ambiente(cls) -> str:

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

            return "1"

        return "2"

    @classmethod
    def _empresa(cls) -> tuple[str, str, str]:

        nit = re.sub(
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

        razon = str(
            Configuracion.obtener(
                "empresa",
                "nombre",
            )
            or "Empresa",
        ).strip()

        correo = str(
            Configuracion.obtener(
                "empresa",
                "correo",
            )
            or "",
        ).strip()

        return nit, razon, correo

    @classmethod
    def _calcular_cude(
        cls,
        *,
        numero_evento: str,
        fecha: date,
        hora: datetime,
        codigo_evento: str,
        cufe_factura: str,
        nit_emisor_factura: str,
        nit_receptor: str,
        valor_total: float,
    ) -> str:

        codigo = str(
            codigo_evento or CODIGO_ACUSE_RECIBO,
        ).zfill(3)[-3:]

        cadena = "^".join(
            [
                numero_evento,
                fecha.strftime("%Y-%m-%d"),
                hora.strftime("%H:%M:%S-05:00"),
                codigo,
                cufe_factura,
                nit_emisor_factura,
                nit_receptor,
                f"{float(valor_total):.2f}",
                cls._ambiente(),
            ],
        )

        return hashlib.sha384(
            cadena.encode("utf-8"),
        ).hexdigest()

    @classmethod
    def generar(
        cls,
        *,
        cufe_factura: str,
        numero_factura: str,
        fecha_factura: date,
        nit_emisor: str,
        razon_emisor: str,
        valor_total: float,
        numero_evento: str | None = None,
        codigo_evento: str = CODIGO_ACUSE_RECIBO,
    ) -> DatosAcuseRecibo:

        codigo = str(
            codigo_evento or CODIGO_ACUSE_RECIBO,
        ).zfill(3)[-3:]

        if codigo not in EVENTOS_RADIAN:

            raise ValueError(
                f"Código de evento RADIAN no soportado: "
                f"{codigo}",
            )

        if not cufe_factura:

            raise ValueError(
                "La factura no tiene CUFE para generar evento.",
            )

        nit_receptor, razon_receptor, _correo_receptor = (
            cls._empresa()
        )

        if not nit_receptor:

            raise ValueError(
                "Configure el NIT de la empresa en configuración.",
            )

        nit_emisor_limpio = re.sub(
            r"\D",
            "",
            str(
                nit_emisor or "",
            ),
        )

        ahora = datetime.now()
        numero_evento = (
            numero_evento
            or ahora.strftime(
                "%Y%m%d%H%M%S",
            )
        )

        descripcion = cls.descripcion_evento(
            codigo,
        )

        cude = cls._calcular_cude(
            numero_evento=numero_evento,
            fecha=ahora.date(),
            hora=ahora,
            codigo_evento=codigo,
            cufe_factura=cufe_factura,
            nit_emisor_factura=nit_emisor_limpio,
            nit_receptor=nit_receptor,
            valor_total=valor_total,
        )

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ApplicationResponse {NS}>
  <cbc:UBLVersionID>UBL 2.1</cbc:UBLVersionID>
  <cbc:CustomizationID>1</cbc:CustomizationID>
  <cbc:ProfileID>DIAN 2.1: ApplicationResponse de Factura Electrónica</cbc:ProfileID>
  <cbc:ProfileExecutionID>{cls._ambiente()}</cbc:ProfileExecutionID>
  <cbc:ID>{escape(numero_evento)}</cbc:ID>
  <cbc:UUID schemeName="CUDE-SHA384">{escape(cude)}</cbc:UUID>
  <cbc:IssueDate>{ahora.strftime("%Y-%m-%d")}</cbc:IssueDate>
  <cbc:IssueTime>{ahora.strftime("%H:%M:%S-05:00")}</cbc:IssueTime>
  <cac:SenderParty>
    <cac:PartyTaxScheme>
      <cbc:RegistrationName>{escape(razon_receptor)}</cbc:RegistrationName>
      <cbc:CompanyID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)" schemeName="31">{escape(nit_receptor)}</cbc:CompanyID>
      <cac:TaxScheme>
        <cbc:ID>01</cbc:ID>
        <cbc:Name>IVA</cbc:Name>
      </cac:TaxScheme>
    </cac:PartyTaxScheme>
  </cac:SenderParty>
  <cac:ReceiverParty>
    <cac:PartyTaxScheme>
      <cbc:RegistrationName>{escape(razon_emisor or "Proveedor")}</cbc:RegistrationName>
      <cbc:CompanyID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)" schemeName="31">{escape(nit_emisor_limpio)}</cbc:CompanyID>
      <cac:TaxScheme>
        <cbc:ID>01</cbc:ID>
        <cbc:Name>IVA</cbc:Name>
      </cac:TaxScheme>
    </cac:PartyTaxScheme>
  </cac:ReceiverParty>
  <cac:DocumentResponse>
    <cac:Response>
      <cbc:ResponseCode>{escape(codigo)}</cbc:ResponseCode>
      <cbc:Description>{escape(descripcion)}</cbc:Description>
    </cac:Response>
    <cac:DocumentReference>
      <cbc:ID>{escape(numero_factura)}</cbc:ID>
      <cbc:UUID schemeName="CUFE-SHA384">{escape(cufe_factura)}</cbc:UUID>
      <cbc:IssueDate>{fecha_factura.strftime("%Y-%m-%d")}</cbc:IssueDate>
    </cac:DocumentReference>
  </cac:DocumentResponse>
</ApplicationResponse>"""

        return DatosAcuseRecibo(
            xml=xml,
            cude=cude,
            numero_evento=numero_evento,
            codigo_evento=codigo,
        )

    @classmethod
    def guardar_xml(
        cls,
        datos: DatosAcuseRecibo,
        *,
        cufe_factura: str,
    ) -> str:

        carpeta = Configuracion.obtener(
            "compras",
            "carpeta_acuse_xml",
        ) or Configuracion.obtener(
            "compras",
            "carpeta_xml",
        ) or "aplicacion/recursos/xml/facturas_compra"

        destino = Path(carpeta) / "acuses"
        destino.mkdir(
            parents=True,
            exist_ok=True,
        )

        codigo = str(
            datos.codigo_evento
            or CODIGO_ACUSE_RECIBO,
        ).zfill(3)[-3:]

        nombre = (
            f"AR{codigo}_{cufe_factura[:16]}_{datos.numero_evento}.xml"
        )

        ruta = destino / nombre
        ruta.write_text(
            datos.xml,
            encoding="utf-8",
        )

        return str(ruta)
