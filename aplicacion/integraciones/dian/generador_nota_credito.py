from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from xml.etree import ElementTree as ET

from aplicacion.framework.documento.dv import DVCalculator
from aplicacion.integraciones.dian.cufe import calcular_cufe
from aplicacion.integraciones.dian.generador_xml import (
    GeneradorXmlFactura,
    NS,
    _registrar_ns,
)
from aplicacion.maestros.terceros.repositorio import (
    TerceroRepositorio,
)
from aplicacion.nucleo.configuracion import Configuracion


@dataclass(slots=True)
class DatosEmisionNotaCredito:

    xml: str
    cufe: str
    numero: str
    prefijo: str
    consecutivo: str
    ruta_xml: str


class GeneradorNotaCreditoVenta:

    @classmethod
    def _carpeta_salida(cls) -> Path:

        ruta = Configuracion.obtener(
            "dian",
            "carpeta_xml_nota_credito",
        )

        if not ruta:

            ruta = (
                "aplicacion/recursos/xml/"
                "notas_credito_venta"
            )

        carpeta = Path(ruta)
        carpeta.mkdir(
            parents=True,
            exist_ok=True,
        )

        return carpeta

    @classmethod
    def generar(
        cls,
        nota,
    ) -> DatosEmisionNotaCredito:

        _registrar_ns()

        empresa = GeneradorXmlFactura._empresa()

        if empresa is None:

            raise ValueError(
                "Configure la empresa emisora "
                "en Maestros › Empresas.",
            )

        cliente = TerceroRepositorio.obtener_por_id(
            nota.cliente_id,
        )

        if cliente is None:

            raise ValueError(
                "No se encontró el cliente.",
            )

        prefijo = str(
            Configuracion.obtener(
                "dian",
                "prefijo_nota_credito",
            )
            or nota.prefijo
            or "NC",
        )

        consecutivo = str(
            nota.consecutivo_dian
            or nota.numero.split("-")[-1],
        )

        numero_dian = (
            f"{prefijo}{consecutivo}"
        )

        subtotal = float(
            nota.subtotal or 0,
        )

        iva = float(
            nota.iva or 0,
        )

        total = float(
            nota.total or 0,
        )

        total_bruto = round(
            subtotal + iva,
            2,
        )

        clave_tecnica = str(
            Configuracion.obtener(
                "dian",
                "software_pin",
            )
            or "75315f52-3988-4e7e-8749-2d633e49bfcc",
        )

        cufe = calcular_cufe(
            numero=numero_dian,
            fecha=nota.fecha or date.today(),
            valor_factura=subtotal,
            valor_iva=iva,
            valor_total=total,
            nit_emisor=str(
                empresa.nit,
            ).split("-")[0],
            nit_adquiriente=str(
                cliente.numero_documento
                or "",
            ).split("-")[0],
            clave_tecnica=clave_tecnica,
            ambiente=GeneradorXmlFactura._ambiente_codigo(),
        )

        root = ET.Element(
            "CreditNote",
            {
                "xmlns": (
                    "urn:oasis:names:specification:"
                    "ubl:schema:xsd:CreditNote-2"
                ),
                "xmlns:cac": NS["cac"],
                "xmlns:cbc": NS["cbc"],
                "xmlns:ext": NS["ext"],
                "xmlns:sts": NS["sts"],
                "xmlns:ds": NS["ds"],
            },
        )

        ET.SubElement(
            root,
            f"{{{NS['cbc']}}}UBLVersionID",
        ).text = "UBL 2.1"

        ET.SubElement(
            root,
            f"{{{NS['cbc']}}}CustomizationID",
        ).text = "10"

        ET.SubElement(
            root,
            f"{{{NS['cbc']}}}ProfileID",
        ).text = (
            "DIAN 2.1: Nota Crédito de Factura "
            "Electrónica de Venta"
        )

        ET.SubElement(
            root,
            f"{{{NS['cbc']}}}ProfileExecutionID",
        ).text = GeneradorXmlFactura._ambiente_codigo()

        ET.SubElement(
            root,
            f"{{{NS['cbc']}}}ID",
        ).text = numero_dian

        ET.SubElement(
            root,
            f"{{{NS['cbc']}}}UUID",
            {
                "schemeName": "CUDE-SHA384",
                "schemeID": (
                    GeneradorXmlFactura._ambiente_codigo()
                ),
            },
        ).text = cufe

        ET.SubElement(
            root,
            f"{{{NS['cbc']}}}IssueDate",
        ).text = (
            nota.fecha or date.today()
        ).strftime("%Y-%m-%d")

        ET.SubElement(
            root,
            f"{{{NS['cbc']}}}IssueTime",
        ).text = datetime.now().strftime(
            "%H:%M:%S-05:00",
        )

        ET.SubElement(
            root,
            f"{{{NS['cbc']}}}CreditNoteTypeCode",
        ).text = "91"

        ET.SubElement(
            root,
            f"{{{NS['cbc']}}}DocumentCurrencyCode",
        ).text = "COP"

        if nota.motivo:

            ET.SubElement(
                root,
                f"{{{NS['cbc']}}}Note",
            ).text = nota.motivo

        if nota.factura_cufe:

            billing = ET.SubElement(
                root,
                f"{{{NS['cac']}}}BillingReference",
            )

            invoice_ref = ET.SubElement(
                billing,
                f"{{{NS['cac']}}}InvoiceDocumentReference",
            )

            ET.SubElement(
                invoice_ref,
                f"{{{NS['cbc']}}}UUID",
            ).text = nota.factura_cufe

        supplier = ET.SubElement(
            root,
            f"{{{NS['cac']}}}AccountingSupplierParty",
        )

        party_sup = ET.SubElement(
            supplier,
            f"{{{NS['cac']}}}Party",
        )

        party_id_sup = ET.SubElement(
            party_sup,
            f"{{{NS['cac']}}}PartyIdentification",
        )

        nit_emisor = str(
            empresa.nit,
        ).split("-")[0]

        dv_emisor = (
            empresa.dv
            or DVCalculator.calcular(
                nit_emisor,
            )
        )

        ET.SubElement(
            party_id_sup,
            f"{{{NS['cbc']}}}ID",
            {
                "schemeID": str(
                    dv_emisor,
                ),
                "schemeName": "31",
            },
        ).text = nit_emisor

        customer = ET.SubElement(
            root,
            f"{{{NS['cac']}}}AccountingCustomerParty",
        )

        party_cus = ET.SubElement(
            customer,
            f"{{{NS['cac']}}}Party",
        )

        party_id_cus = ET.SubElement(
            party_cus,
            f"{{{NS['cac']}}}PartyIdentification",
        )

        nit_cliente = str(
            cliente.numero_documento
            or "",
        ).split("-")[0]

        dv_cliente = DVCalculator.calcular(
            nit_cliente,
        )

        ET.SubElement(
            party_id_cus,
            f"{{{NS['cbc']}}}ID",
            {
                "schemeID": str(
                    dv_cliente,
                ),
                "schemeName": "31",
            },
        ).text = nit_cliente

        tax_total = ET.SubElement(
            root,
            f"{{{NS['cac']}}}TaxTotal",
        )

        ET.SubElement(
            tax_total,
            f"{{{NS['cbc']}}}TaxAmount",
            {"currencyID": "COP"},
        ).text = f"{iva:.2f}"

        legal = ET.SubElement(
            root,
            f"{{{NS['cac']}}}LegalMonetaryTotal",
        )

        ET.SubElement(
            legal,
            f"{{{NS['cbc']}}}LineExtensionAmount",
            {"currencyID": "COP"},
        ).text = f"{subtotal:.2f}"

        ET.SubElement(
            legal,
            f"{{{NS['cbc']}}}TaxExclusiveAmount",
            {"currencyID": "COP"},
        ).text = f"{subtotal:.2f}"

        ET.SubElement(
            legal,
            f"{{{NS['cbc']}}}TaxInclusiveAmount",
            {"currencyID": "COP"},
        ).text = f"{total_bruto:.2f}"

        ET.SubElement(
            legal,
            f"{{{NS['cbc']}}}PayableAmount",
            {"currencyID": "COP"},
        ).text = f"{total:.2f}"

        for indice, detalle in enumerate(
            nota.detalles,
            start=1,
        ):

            linea = ET.SubElement(
                root,
                f"{{{NS['cac']}}}CreditNoteLine",
            )

            ET.SubElement(
                linea,
                f"{{{NS['cbc']}}}ID",
            ).text = str(indice)

            ET.SubElement(
                linea,
                f"{{{NS['cbc']}}}CreditedQuantity",
                {"unitCode": "EA"},
            ).text = f"{float(detalle.cantidad):.2f}"

            ET.SubElement(
                linea,
                f"{{{NS['cbc']}}}LineExtensionAmount",
                {"currencyID": "COP"},
            ).text = f"{float(detalle.total_linea):.2f}"

            item = ET.SubElement(
                linea,
                f"{{{NS['cac']}}}Item",
            )

            ET.SubElement(
                item,
                f"{{{NS['cbc']}}}Description",
            ).text = detalle.descripcion

        xml_bytes = ET.tostring(
            root,
            encoding="utf-8",
            xml_declaration=True,
        )

        xml_texto = xml_bytes.decode(
            "utf-8",
        )

        nombre = (
            f"{numero_dian}_{cufe[:16]}.xml"
        )

        ruta = cls._carpeta_salida() / nombre

        ruta.write_text(
            xml_texto,
            encoding="utf-8",
        )

        return DatosEmisionNotaCredito(
            xml=xml_texto,
            cufe=cufe,
            numero=numero_dian,
            prefijo=prefijo,
            consecutivo=consecutivo,
            ruta_xml=str(ruta),
        )
