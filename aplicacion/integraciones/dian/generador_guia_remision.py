from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from aplicacion.nucleo.configuracion import Configuracion


NS = (
    'xmlns="urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2" '
    'xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" '
    'xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" '
    'xmlns:sts="dian:gov:co:facturaelectronica:Structures-2-1"'
)


@dataclass(slots=True)
class DatosEmisionGuiaRemision:

    xml: str
    cude: str
    ruta_xml: str


class GeneradorGuiaRemision:

    TIPO_DOCUMENTO = "009"

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
    def _empresa(cls) -> tuple[str, str, str, str, str]:

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

        direccion = str(
            Configuracion.obtener(
                "empresa",
                "direccion",
            )
            or "",
        ).strip()

        ciudad = str(
            Configuracion.obtener(
                "empresa",
                "ciudad",
            )
            or "",
        ).strip()

        departamento = str(
            Configuracion.obtener(
                "empresa",
                "departamento",
            )
            or "",
        ).strip()

        return nit, razon, direccion, ciudad, departamento

    @classmethod
    def _calcular_cude(
        cls,
        *,
        numero: str,
        fecha,
        hora: datetime,
        nit_emisor: str,
        nit_destinatario: str,
        total: float,
    ) -> str:

        cadena = "^".join(
            [
                numero,
                fecha.strftime("%Y-%m-%d"),
                hora.strftime("%H:%M:%S-05:00"),
                f"{float(total):.2f}",
                nit_emisor,
                nit_destinatario,
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
            "ventas",
            "carpeta_xml_guia_remision",
        ) or Configuracion.obtener(
            "dian",
            "carpeta_xml_guia_remision",
        ) or "aplicacion/recursos/xml/guias_remision"

        carpeta = Path(ruta)
        carpeta.mkdir(
            parents=True,
            exist_ok=True,
        )

        return carpeta

    @classmethod
    def generar(
        cls,
        guia,
        *,
        nit_cliente: str = "",
        razon_cliente: str = "",
    ) -> DatosEmisionGuiaRemision:

        nit_empresa, razon_empresa, dir_origen, ciudad_origen, depto_origen = (
            cls._empresa()
        )

        if not nit_empresa:

            raise ValueError(
                "Configure el NIT de la empresa.",
            )

        nit_cliente = str(
            nit_cliente or "",
        ).strip()

        ahora = datetime.now()

        cude = cls._calcular_cude(
            numero=guia.numero,
            fecha=guia.fecha,
            hora=ahora,
            nit_emisor=nit_empresa,
            nit_destinatario=nit_cliente or "222222222222",
            total=float(
                guia.total or 0,
            ),
        )

        origen = escape(
            guia.direccion_origen
            or dir_origen
            or razon_empresa,
        )

        destino = escape(
            guia.direccion_destino
            or razon_cliente
            or "Destino",
        )

        lineas_xml = ""

        for indice, detalle in enumerate(
            guia.detalles,
            start=1,
        ):

            lineas_xml += f"""
  <cac:DespatchLine>
    <cbc:ID>{indice}</cbc:ID>
    <cbc:DeliveredQuantity unitCode="EA">{float(detalle.cantidad):.2f}</cbc:DeliveredQuantity>
    <cac:Item>
      <cbc:Description>{escape(detalle.descripcion)}</cbc:Description>
    </cac:Item>
  </cac:DespatchLine>"""

        transporte = ""

        if (
            guia.conductor
            or guia.vehiculo
            or guia.transportadora
        ):

            transporte = f"""
  <cac:Shipment>
    <cbc:ID>{escape(guia.numero)}</cbc:ID>
    <cac:Delivery>
      <cac:DeliveryAddress>
        <cbc:StreetName>{destino}</cbc:StreetName>
        <cbc:CityName>{escape(guia.ciudad_destino or "")}</cbc:CityName>
        <cbc:CountrySubentity>{escape(guia.departamento_destino or "")}</cbc:CountrySubentity>
      </cac:DeliveryAddress>
    </cac:Delivery>
    <cac:TransportHandlingUnit>
      <cac:TransportEquipment>
        <cbc:ID>{escape(guia.placa or guia.vehiculo or "")}</cbc:ID>
      </cac:TransportEquipment>
    </cac:TransportHandlingUnit>
    <cac:DriverPerson>
      <cbc:FirstName>{escape(guia.conductor or "")}</cbc:FirstName>
    </cac:DriverPerson>
    <cbc:Information>{escape(guia.transportadora or "")}</cbc:Information>
  </cac:Shipment>"""

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<DespatchAdvice {NS}>
  <cbc:UBLVersionID>UBL 2.1</cbc:UBLVersionID>
  <cbc:CustomizationID>10</cbc:CustomizationID>
  <cbc:ProfileID>DIAN 2.1: Guía de Remisión Electrónica</cbc:ProfileID>
  <cbc:ProfileExecutionID>{cls._ambiente()}</cbc:ProfileExecutionID>
  <cbc:ID>{escape(guia.numero)}</cbc:ID>
  <cbc:UUID schemeName="CUDE-SHA384">{escape(cude)}</cbc:UUID>
  <cbc:IssueDate>{guia.fecha.strftime("%Y-%m-%d")}</cbc:IssueDate>
  <cbc:IssueTime>{ahora.strftime("%H:%M:%S-05:00")}</cbc:IssueTime>
  <cbc:DocumentCurrencyCode>COP</cbc:DocumentCurrencyCode>
  <cac:DespatchSupplierParty>
    <cac:Party>
      <cac:PartyName>
        <cbc:Name>{escape(razon_empresa)}</cbc:Name>
      </cac:PartyName>
      <cac:PhysicalLocation>
        <cac:Address>
          <cbc:StreetName>{origen}</cbc:StreetName>
          <cbc:CityName>{escape(guia.ciudad_origen or ciudad_origen)}</cbc:CityName>
          <cbc:CountrySubentity>{escape(guia.departamento_origen or depto_origen)}</cbc:CountrySubentity>
        </cac:Address>
      </cac:PhysicalLocation>
      <cac:PartyTaxScheme>
        <cbc:RegistrationName>{escape(razon_empresa)}</cbc:RegistrationName>
        <cbc:CompanyID>{escape(nit_empresa)}</cbc:CompanyID>
      </cac:PartyTaxScheme>
    </cac:Party>
  </cac:DespatchSupplierParty>
  <cac:DeliveryCustomerParty>
    <cac:Party>
      <cac:PartyName>
        <cbc:Name>{escape(razon_cliente or "Cliente")}</cbc:Name>
      </cac:PartyName>
      <cac:PartyTaxScheme>
        <cbc:RegistrationName>{escape(razon_cliente or "Cliente")}</cbc:RegistrationName>
        <cbc:CompanyID>{escape(nit_cliente or "222222222222")}</cbc:CompanyID>
      </cac:PartyTaxScheme>
    </cac:Party>
  </cac:DeliveryCustomerParty>
{transporte}
{lineas_xml}
</DespatchAdvice>"""

        carpeta = cls._carpeta_salida()
        ruta = carpeta / f"GRE_{guia.numero}.xml"
        ruta.write_text(
            xml,
            encoding="utf-8",
        )

        return DatosEmisionGuiaRemision(
            xml=xml,
            cude=cude,
            ruta_xml=str(ruta),
        )
