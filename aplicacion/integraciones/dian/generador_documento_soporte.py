from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from aplicacion.nucleo.configuracion import Configuracion


NS = (
    'xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
    'xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" '
    'xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" '
    'xmlns:sts="dian:gov:co:facturaelectronica:Structures-2-1"'
)


@dataclass(slots=True)
class DatosEmisionDocumentoSoporte:

    xml: str
    cuds: str
    ruta_xml: str


class GeneradorDocumentoSoporte:

    TIPO_DOCUMENTO = "05"

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
    def _empresa(cls) -> tuple[str, str]:

        nit = str(
            Configuracion.obtener(
                "empresa",
                "nit",
            )
            or "",
        ).strip()

        razon = str(
            Configuracion.obtener(
                "empresa",
                "nombre",
            )
            or "Empresa",
        ).strip()

        return nit, razon

    @classmethod
    def _calcular_cuds(
        cls,
        *,
        numero: str,
        fecha,
        hora: datetime,
        nit_emisor: str,
        nit_adquiriente: str,
        total: float,
    ) -> str:

        cadena = "^".join(
            [
                numero,
                fecha.strftime("%Y-%m-%d"),
                hora.strftime("%H:%M:%S-05:00"),
                f"{float(total):.2f}",
                nit_emisor,
                nit_adquiriente,
                cls.TIPO_DOCUMENTO,
                cls._ambiente(),
            ],
        )

        return hashlib.sha384(
            cadena.encode("utf-8"),
        ).hexdigest()

    @classmethod
    def _carpeta_salida(cls) -> Path:

        ruta = Configuracion.obtener(
            "compras",
            "carpeta_xml_soporte",
        ) or "aplicacion/recursos/xml/documentos_soporte"

        carpeta = Path(ruta)
        carpeta.mkdir(
            parents=True,
            exist_ok=True,
        )

        return carpeta

    @classmethod
    def generar(
        cls,
        documento,
    ) -> DatosEmisionDocumentoSoporte:

        nit_empresa, razon_empresa = cls._empresa()

        if not nit_empresa:

            raise ValueError(
                "Configure el NIT de la empresa.",
            )

        nit_proveedor = str(
            documento.nit_proveedor or "",
        ).strip()

        ahora = datetime.now()

        cuds = cls._calcular_cuds(
            numero=documento.numero,
            fecha=documento.fecha,
            hora=ahora,
            nit_emisor=nit_proveedor,
            nit_adquiriente=nit_empresa,
            total=float(
                documento.total or 0,
            ),
        )

        lineas_xml = ""

        # DocumentoSoporteDetalle no tiene producto_id (línea de
        # texto libre, sin vínculo al catálogo), así que no hay
        # unidad de medida real que consultar por línea — se usa
        # "94" (unidad, UN/CEFACT) como en GeneradorXmlFactura._codigo_unidad.
        for indice, detalle in enumerate(
            documento.detalles,
            start=1,
        ):

            lineas_xml += f"""
  <cac:InvoiceLine>
    <cbc:ID>{indice}</cbc:ID>
    <cbc:InvoicedQuantity unitCode="94">{float(detalle.cantidad):.2f}</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount currencyID="COP">{float(detalle.total_linea):.2f}</cbc:LineExtensionAmount>
    <cac:Item>
      <cbc:Description>{escape(detalle.descripcion)}</cbc:Description>
    </cac:Item>
    <cac:Price>
      <cbc:PriceAmount currencyID="COP">{float(detalle.precio_unitario):.2f}</cbc:PriceAmount>
    </cac:Price>
  </cac:InvoiceLine>"""

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice {NS}>
  <cbc:UBLVersionID>UBL 2.1</cbc:UBLVersionID>
  <cbc:CustomizationID>10</cbc:CustomizationID>
  <cbc:ProfileID>DIAN 2.1: Documento Soporte en Adquisiciones</cbc:ProfileID>
  <cbc:ProfileExecutionID>{cls._ambiente()}</cbc:ProfileExecutionID>
  <cbc:ID>{escape(documento.numero)}</cbc:ID>
  <cbc:UUID schemeName="CUDS-SHA384">{escape(cuds)}</cbc:UUID>
  <cbc:IssueDate>{documento.fecha.strftime("%Y-%m-%d")}</cbc:IssueDate>
  <cbc:IssueTime>{ahora.strftime("%H:%M:%S-05:00")}</cbc:IssueTime>
  <cbc:InvoiceTypeCode>{cls.TIPO_DOCUMENTO}</cbc:InvoiceTypeCode>
  <cbc:DocumentCurrencyCode>COP</cbc:DocumentCurrencyCode>
  <cac:AccountingSupplierParty>
    <cac:Party>
      <cac:PartyTaxScheme>
        <cbc:RegistrationName>{escape(documento.razon_social_proveedor or "Proveedor")}</cbc:RegistrationName>
        <cbc:CompanyID>{escape(nit_proveedor)}</cbc:CompanyID>
      </cac:PartyTaxScheme>
    </cac:Party>
  </cac:AccountingSupplierParty>
  <cac:AccountingCustomerParty>
    <cac:Party>
      <cac:PartyTaxScheme>
        <cbc:RegistrationName>{escape(razon_empresa)}</cbc:RegistrationName>
        <cbc:CompanyID>{escape(nit_empresa)}</cbc:CompanyID>
      </cac:PartyTaxScheme>
    </cac:Party>
  </cac:AccountingCustomerParty>
  <cac:LegalMonetaryTotal>
    <cbc:LineExtensionAmount currencyID="COP">{float(documento.subtotal or 0):.2f}</cbc:LineExtensionAmount>
    <cbc:TaxInclusiveAmount currencyID="COP">{float(documento.total or 0):.2f}</cbc:TaxInclusiveAmount>
    <cbc:PayableAmount currencyID="COP">{float(documento.total or 0):.2f}</cbc:PayableAmount>
  </cac:LegalMonetaryTotal>
{lineas_xml}
</Invoice>"""

        carpeta = cls._carpeta_salida()
        ruta = carpeta / f"DS_{documento.numero}.xml"
        ruta.write_text(
            xml,
            encoding="utf-8",
        )

        return DatosEmisionDocumentoSoporte(
            xml=xml,
            cuds=cuds,
            ruta_xml=str(ruta),
        )
