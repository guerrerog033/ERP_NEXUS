from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from xml.etree import ElementTree as ET

from aplicacion.framework.documento.dv import DVCalculator
from aplicacion.integraciones.dian.cufe import calcular_cufe
from aplicacion.maestros.empresas.repositorio import (
    EmpresaRepositorio,
)
from aplicacion.maestros.impuestos.repositorio import (
    RepositorioImpuesto,
)
from aplicacion.maestros.productos.repositorio import (
    RepositorioProducto,
)
from aplicacion.maestros.terceros.repositorio import (
    TerceroRepositorio,
)
from aplicacion.maestros.unidades_medida.repositorio import (
    UnidadMedidaRepositorio,
)
from aplicacion.nucleo.configuracion import Configuracion


NS = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "sts": "dian:gov:co:facturaelectronica:Structures-2-1",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
}


def _registrar_ns() -> None:

    for prefijo, uri in NS.items():

        ET.register_namespace(
            prefijo,
            uri,
        )


@dataclass(slots=True)
class DatosEmision:

    xml: str
    cufe: str
    numero: str
    prefijo: str
    consecutivo: str
    ruta_xml: str


class GeneradorXmlFactura:

    @classmethod
    def _empresa(cls):

        nit_config = Configuracion.obtener(
            "empresa",
            "nit",
        )

        if nit_config:

            empresa = EmpresaRepositorio.obtener_por_nit(
                str(nit_config).strip(),
            )

            if empresa is not None:

                return empresa

        db = EmpresaRepositorio.obtener_sesion()

        try:

            return (
                db.query(
                    EmpresaRepositorio.modelo,
                )
                .filter(
                    EmpresaRepositorio.modelo.activo
                    == True,  # noqa: E712
                )
                .first()
            )

        finally:

            db.close()

    @classmethod
    def _ambiente_codigo(cls) -> str:

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

            return "1"

        return "2"

    @classmethod
    def _carpeta_salida(cls) -> Path:

        ruta = Configuracion.obtener(
            "dian",
            "carpeta_xml_venta",
        )

        if not ruta:

            ruta = "aplicacion/recursos/xml/facturas_venta"

        carpeta = Path(ruta)
        carpeta.mkdir(
            parents=True,
            exist_ok=True,
        )

        return carpeta

    @classmethod
    def _porcentaje_impuesto(
        cls,
        impuesto_id,
    ) -> float:

        if not impuesto_id:

            return 0.0

        impuesto = RepositorioImpuesto.obtener_por_id(
            impuesto_id,
        )

        if impuesto is None:

            return 0.0

        return float(
            impuesto.porcentaje or 0,
        )

    @classmethod
    def _codigo_unidad(
        cls,
        producto_id,
    ) -> str:
        """
        Código UN/CEFACT de unidad de medida para InvoicedQuantity.
        "94" (unidad) es el respaldo cuando el producto no tiene
        unidad de medida asignada o no está vinculado a un producto
        del catálogo.
        """

        if not producto_id:

            return "94"

        producto = RepositorioProducto.obtener_por_id(
            producto_id,
        )

        if producto is None or not producto.unidad_medida_id:

            return "94"

        # Se consulta por unidad_medida_id (escalar) en vez de
        # navegar producto.unidad_medida: la sesión que trajo
        # ``producto`` ya se cerró, así que la relación perezosa
        # lanzaría DetachedInstanceError.
        unidad = UnidadMedidaRepositorio.obtener_por_id(
            producto.unidad_medida_id,
        )

        if unidad is None or not unidad.codigo_dian:

            return "94"

        return unidad.codigo_dian

    @classmethod
    def generar(
        cls,
        factura,
    ) -> DatosEmision:

        _registrar_ns()

        empresa = cls._empresa()

        if empresa is None:

            raise ValueError(
                "Configure la empresa emisora "
                "en Maestros › Empresas.",
            )

        cliente = TerceroRepositorio.obtener_por_id(
            factura.cliente_id,
        )

        if cliente is None:

            raise ValueError(
                "No se encontró el cliente.",
            )

        prefijo = str(
            Configuracion.obtener(
                "dian",
                "prefijo_factura",
            )
            or "SETP",
        )

        consecutivo = str(
            factura.consecutivo_dian
            or factura.numero.split("-")[-1],
        )

        numero_dian = (
            f"{prefijo}{consecutivo}"
        )

        subtotal = float(
            factura.subtotal or 0,
        )

        iva = float(
            factura.iva or 0,
        )

        total = float(
            factura.total or 0,
        )

        total_bruto = round(
            subtotal + iva,
            2,
        )

        retenciones = (
            (
                getattr(
                    factura,
                    "retefuente_id",
                    None,
                ),
                float(
                    getattr(
                        factura,
                        "valor_retefuente",
                        0,
                    )
                    or 0,
                ),
                "06",
                "ReteRenta",
            ),
            (
                getattr(
                    factura,
                    "reteica_id",
                    None,
                ),
                float(
                    getattr(
                        factura,
                        "valor_reteica",
                        0,
                    )
                    or 0,
                ),
                "07",
                "ReteICA",
            ),
            (
                getattr(
                    factura,
                    "reteiva_id",
                    None,
                ),
                float(
                    getattr(
                        factura,
                        "valor_reteiva",
                        0,
                    )
                    or 0,
                ),
                "05",
                "ReteIVA",
            ),
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
            fecha=factura.fecha or date.today(),
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
            ambiente=cls._ambiente_codigo(),
        )

        root = ET.Element(
            "Invoice",
            {
                "xmlns": (
                    "urn:oasis:names:specification:"
                    "ubl:schema:xsd:Invoice-2"
                ),
                "xmlns:cac": NS["cac"],
                "xmlns:cbc": NS["cbc"],
                "xmlns:ext": NS["ext"],
                "xmlns:sts": NS["sts"],
                "xmlns:ds": NS["ds"],
            },
        )

        ext = ET.SubElement(
            root,
            f"{{{NS['ext']}}}UBLExtensions",
        )

        ubl_ext = ET.SubElement(
            ext,
            f"{{{NS['ext']}}}UBLExtension",
        )

        ext_content = ET.SubElement(
            ubl_ext,
            f"{{{NS['ext']}}}ExtensionContent",
        )

        dian_ext = ET.SubElement(
            ext_content,
            f"{{{NS['sts']}}}DianExtensions",
        )

        ET.SubElement(
            dian_ext,
            f"{{{NS['sts']}}}InvoiceControl",
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
        ).text = "DIAN 2.1: Factura Electrónica de Venta"

        ET.SubElement(
            root,
            f"{{{NS['cbc']}}}ProfileExecutionID",
        ).text = cls._ambiente_codigo()

        ET.SubElement(
            root,
            f"{{{NS['cbc']}}}ID",
        ).text = numero_dian

        ET.SubElement(
            root,
            f"{{{NS['cbc']}}}UUID",
            {
                "schemeName": "CUFE-SHA384",
                "schemeID": cls._ambiente_codigo(),
            },
        ).text = cufe

        ET.SubElement(
            root,
            f"{{{NS['cbc']}}}IssueDate",
        ).text = (
            factura.fecha or date.today()
        ).strftime("%Y-%m-%d")

        ET.SubElement(
            root,
            f"{{{NS['cbc']}}}IssueTime",
        ).text = datetime.now().strftime(
            "%H:%M:%S-05:00",
        )

        ET.SubElement(
            root,
            f"{{{NS['cbc']}}}InvoiceTypeCode",
        ).text = "01"

        ET.SubElement(
            root,
            f"{{{NS['cbc']}}}DocumentCurrencyCode",
        ).text = "COP"

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

        party_name_sup = ET.SubElement(
            party_sup,
            f"{{{NS['cac']}}}PartyName",
        )

        ET.SubElement(
            party_name_sup,
            f"{{{NS['cbc']}}}Name",
        ).text = (
            empresa.razon_social
        )

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

        party_name_cus = ET.SubElement(
            party_cus,
            f"{{{NS['cac']}}}PartyName",
        )

        ET.SubElement(
            party_name_cus,
            f"{{{NS['cbc']}}}Name",
        ).text = (
            cliente.razon_social
            or cliente.nombre_completo
            or nit_cliente
        )

        tax_total = ET.SubElement(
            root,
            f"{{{NS['cac']}}}TaxTotal",
        )

        ET.SubElement(
            tax_total,
            f"{{{NS['cbc']}}}TaxAmount",
            {"currencyID": "COP"},
        ).text = f"{iva:.2f}"

        for (
            impuesto_id,
            valor,
            codigo_dian,
            nombre_dian,
        ) in retenciones:

            if valor <= 0:

                continue

            wh_total = ET.SubElement(
                root,
                f"{{{NS['cac']}}}WithholdingTaxTotal",
            )

            ET.SubElement(
                wh_total,
                f"{{{NS['cbc']}}}TaxAmount",
                {"currencyID": "COP"},
            ).text = f"{valor:.2f}"

            wh_sub = ET.SubElement(
                wh_total,
                f"{{{NS['cac']}}}TaxSubtotal",
            )

            ET.SubElement(
                wh_sub,
                f"{{{NS['cbc']}}}TaxableAmount",
                {"currencyID": "COP"},
            ).text = f"{subtotal:.2f}"

            ET.SubElement(
                wh_sub,
                f"{{{NS['cbc']}}}TaxAmount",
                {"currencyID": "COP"},
            ).text = f"{valor:.2f}"

            wh_cat = ET.SubElement(
                wh_sub,
                f"{{{NS['cac']}}}TaxCategory",
            )

            wh_scheme = ET.SubElement(
                wh_cat,
                f"{{{NS['cac']}}}TaxScheme",
            )

            ET.SubElement(
                wh_scheme,
                f"{{{NS['cbc']}}}ID",
            ).text = codigo_dian

            ET.SubElement(
                wh_scheme,
                f"{{{NS['cbc']}}}Name",
            ).text = nombre_dian

            porcentaje = cls._porcentaje_impuesto(
                impuesto_id,
            )

            if porcentaje > 0:

                ET.SubElement(
                    wh_cat,
                    f"{{{NS['cbc']}}}Percent",
                ).text = f"{porcentaje:.2f}"

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
            factura.detalles,
            start=1,
        ):

            linea = ET.SubElement(
                root,
                f"{{{NS['cac']}}}InvoiceLine",
            )

            ET.SubElement(
                linea,
                f"{{{NS['cbc']}}}ID",
            ).text = str(indice)

            ET.SubElement(
                linea,
                f"{{{NS['cbc']}}}InvoicedQuantity",
                {
                    "unitCode": cls._codigo_unidad(
                        detalle.producto_id,
                    ),
                },
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

            price = ET.SubElement(
                linea,
                f"{{{NS['cac']}}}Price",
            )

            ET.SubElement(
                price,
                f"{{{NS['cbc']}}}PriceAmount",
                {"currencyID": "COP"},
            ).text = f"{float(detalle.precio_unitario):.2f}"

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

        return DatosEmision(
            xml=xml_texto,
            cufe=cufe,
            numero=numero_dian,
            prefijo=prefijo,
            consecutivo=consecutivo,
            ruta_xml=str(ruta),
        )
