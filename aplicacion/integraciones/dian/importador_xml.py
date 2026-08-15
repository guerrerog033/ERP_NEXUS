from __future__ import annotations

import re
import shutil
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path


@dataclass
class LineaFacturaXml:

    descripcion: str
    cantidad: float
    precio_unitario: float
    porcentaje_iva: float = 0.0
    total_linea: float = 0.0
    codigo_producto: str = ""
    codigo_barras: str = ""
    referencia: str = ""


@dataclass
class FacturaXmlParseada:

    cufe: str = ""
    numero_proveedor: str = ""
    prefijo: str = ""
    consecutivo: str = ""
    fecha: date | None = None
    nit_proveedor: str = ""
    razon_social_proveedor: str = ""
    subtotal: float = 0.0
    iva: float = 0.0
    total: float = 0.0
    es_credito: bool = False
    fecha_vencimiento: date | None = None
    lineas: list[LineaFacturaXml] = field(
        default_factory=list,
    )
    ruta_xml_origen: str = ""


def _local(tag: str) -> str:

    if "}" in tag:

        return tag.rsplit("}", 1)[-1]

    return tag


def _texto(
    elemento: ET.Element | None,
) -> str:

    if elemento is None:

        return ""

    return (elemento.text or "").strip()


def _float(
    valor: str | None,
    default: float = 0.0,
) -> float:

    if not valor:

        return default

    try:

        return float(
            str(valor).replace(",", ""),
        )

    except ValueError:

        return default


def _buscar_raiz_factura(
    raiz: ET.Element,
) -> ET.Element:

    if _local(raiz.tag) == "Invoice":

        return raiz

    for elemento in raiz.iter():

        if _local(elemento.tag) == "Invoice":

            return elemento

    return raiz


def _primer_hijo(
    padre: ET.Element,
    nombre_local: str,
) -> ET.Element | None:

    for hijo in padre:

        if _local(hijo.tag) == nombre_local:

            return hijo

    return None


def _todos_hijos(
    padre: ET.Element,
    nombre_local: str,
) -> list[ET.Element]:

    return [
        hijo
        for hijo in padre
        if _local(hijo.tag) == nombre_local
    ]


def _extraer_proveedor(
    factura: ET.Element,
) -> tuple[str, str]:

    proveedor = _primer_hijo(
        factura,
        "AccountingSupplierParty",
    )

    if proveedor is None:

        return "", ""

    party = _primer_hijo(
        proveedor,
        "Party",
    )

    if party is None:

        return "", ""

    esquema = _primer_hijo(
        party,
        "PartyTaxScheme",
    )

    if esquema is None:

        esquema = party

    razon = _texto(
        _primer_hijo(
            esquema,
            "RegistrationName",
        )
    )

    company = _primer_hijo(
        esquema,
        "CompanyID",
    )

    nit = re.sub(
        r"\D",
        "",
        _texto(company),
    )

    if not razon:

        razon = _texto(
            _primer_hijo(
                party,
                "PartyName",
            )
        )

        nombre = _primer_hijo(
            _primer_hijo(
                party,
                "PartyName",
            )
            or party,
            "Name",
        )

        if nombre is not None:

            razon = _texto(nombre)

    return nit, razon


def _separar_numero_factura(
    numero: str,
) -> tuple[str, str]:

    numero = numero.strip()

    if not numero:

        return "", ""

    coincidencia = re.match(
        r"^([A-Za-z]+)(\d+)$",
        numero,
    )

    if coincidencia:

        return (
            coincidencia.group(1),
            coincidencia.group(2),
        )

    return "", numero


def _porcentaje_linea(
    linea: ET.Element,
) -> float:

    impuestos = _todos_hijos(
        linea,
        "TaxTotal",
    )

    for impuesto in impuestos:

        subtotal = _primer_hijo(
            impuesto,
            "TaxSubtotal",
        )

        if subtotal is None:

            continue

        categoria = _primer_hijo(
            subtotal,
            "TaxCategory",
        )

        if categoria is None:

            continue

        porcentaje = _primer_hijo(
            categoria,
            "Percent",
        )

        if porcentaje is not None:

            return _float(
                _texto(porcentaje),
            )

    return 0.0


def _extraer_lineas(
    factura: ET.Element,
) -> list[LineaFacturaXml]:

    lineas: list[LineaFacturaXml] = []

    for linea_xml in _todos_hijos(
        factura,
        "InvoiceLine",
    ):

        cantidad_el = _primer_hijo(
            linea_xml,
            "InvoicedQuantity",
        )

        cantidad = _float(
            _texto(cantidad_el),
            1.0,
        )

        item = _primer_hijo(
            linea_xml,
            "Item",
        )

        descripcion = _texto(
            _primer_hijo(
                item,
                "Description",
            )
            if item is not None
            else None,
        )

        if not descripcion and item is not None:

            descripcion = _texto(
                _primer_hijo(
                    item,
                    "Name",
                )
            )

        codigo_producto = ""
        codigo_barras = ""
        referencia = ""

        if item is not None:
            vendedor_id = _primer_hijo(
                item,
                "SellersItemIdentification",
            )

            if vendedor_id is not None:
                codigo_producto = _texto(
                    _primer_hijo(
                        vendedor_id,
                        "ID",
                    )
                )

            estandar_id = _primer_hijo(
                item,
                "StandardItemIdentification",
            )

            if estandar_id is not None:
                codigo_barras = _texto(
                    _primer_hijo(
                        estandar_id,
                        "ID",
                    )
                )

            referencia = codigo_producto or codigo_barras

        precio = _primer_hijo(
            linea_xml,
            "Price",
        )

        precio_unitario = _float(
            _texto(
                _primer_hijo(
                    precio,
                    "PriceAmount",
                )
                if precio is not None
                else None,
            ),
        )

        if precio_unitario <= 0:

            extension = _float(
                _texto(
                    _primer_hijo(
                        linea_xml,
                        "LineExtensionAmount",
                    )
                ),
            )

            if cantidad > 0:

                precio_unitario = round(
                    extension / cantidad,
                    2,
                )

        porcentaje = _porcentaje_linea(
            linea_xml,
        )

        subtotal_linea = round(
            cantidad * precio_unitario,
            2,
        )

        total_linea = round(
            subtotal_linea
            * (
                1
                + porcentaje
                / 100
            ),
            2,
        )

        lineas.append(
            LineaFacturaXml(
                descripcion=descripcion
                or "Ítem sin descripción",
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                porcentaje_iva=porcentaje,
                total_linea=total_linea,
                codigo_producto=codigo_producto,
                codigo_barras=codigo_barras,
                referencia=referencia,
            ),
        )

    return lineas


def _extraer_totales(
    factura: ET.Element,
) -> tuple[float, float, float]:

    legal = _primer_hijo(
        factura,
        "LegalMonetaryTotal",
    )

    if legal is None:

        return 0.0, 0.0, 0.0

    subtotal = _float(
        _texto(
            _primer_hijo(
                legal,
                "LineExtensionAmount",
            )
            or _primer_hijo(
                legal,
                "TaxExclusiveAmount",
            )
        ),
    )

    total = _float(
        _texto(
            _primer_hijo(
                legal,
                "PayableAmount",
            )
            or _primer_hijo(
                legal,
                "TaxInclusiveAmount",
            )
        ),
    )

    iva = round(
        max(
            total - subtotal,
            0.0,
        ),
        2,
    )

    return subtotal, iva, total


def _extraer_forma_pago(
    factura: ET.Element,
    fecha_factura: date | None,
) -> tuple[bool, date | None]:

    es_credito = False
    fecha_vencimiento = None

    for medio in _todos_hijos(
        factura,
        "PaymentMeans",
    ):

        codigo = _texto(
            _primer_hijo(
                medio,
                "PaymentMeansCode",
            )
        )

        if codigo == "2":

            es_credito = True

        vencimiento = _texto(
            _primer_hijo(
                medio,
                "PaymentDueDate",
            )
        )

        if vencimiento:

            try:

                fecha_vencimiento = datetime.strptime(
                    vencimiento[:10],
                    "%Y-%m-%d",
                ).date()

            except ValueError:

                fecha_vencimiento = None

    for termino in _todos_hijos(
        factura,
        "PaymentTerms",
    ):

        vencimiento = _texto(
            _primer_hijo(
                termino,
                "PaymentDueDate",
            )
        )

        if not vencimiento:

            periodo = _primer_hijo(
                termino,
                "SettlementPeriod",
            )

            if periodo is not None:

                vencimiento = _texto(
                    _primer_hijo(
                        periodo,
                        "EndDate",
                    )
                )

        if vencimiento:

            try:

                fecha_venc = datetime.strptime(
                    vencimiento[:10],
                    "%Y-%m-%d",
                ).date()

                fecha_vencimiento = fecha_venc

                if (
                    fecha_factura is None
                    or fecha_venc > fecha_factura
                ):

                    es_credito = True

            except ValueError:

                pass

    return es_credito, fecha_vencimiento


def parsear_factura_xml(
    ruta: str | Path,
) -> FacturaXmlParseada:

    ruta = Path(ruta)

    if not ruta.is_file():

        raise FileNotFoundError(
            f"No se encontró el archivo XML: {ruta}",
        )

    contenido = ruta.read_text(
        encoding="utf-8",
        errors="replace",
    )

    parseada = parsear_factura_xml_texto(
        contenido,
    )

    parseada.ruta_xml_origen = str(
        ruta,
    )

    return parseada


def parsear_factura_xml_texto(
    contenido: str,
) -> FacturaXmlParseada:

    if not str(
        contenido or "",
    ).strip():

        raise ValueError(
            "El contenido XML está vacío.",
        )

    arbol = ET.ElementTree(
        ET.fromstring(
            contenido,
        ),
    )

    factura = _buscar_raiz_factura(
        arbol.getroot(),
    )

    cufe = _texto(
        _primer_hijo(
            factura,
            "UUID",
        )
    )

    numero_proveedor = _texto(
        _primer_hijo(
            factura,
            "ID",
        )
    )

    prefijo, consecutivo = _separar_numero_factura(
        numero_proveedor,
    )

    fecha_texto = _texto(
        _primer_hijo(
            factura,
            "IssueDate",
        )
    )

    fecha_valor = None

    if fecha_texto:

        try:

            fecha_valor = datetime.strptime(
                fecha_texto[:10],
                "%Y-%m-%d",
            ).date()

        except ValueError:

            fecha_valor = None

    nit, razon = _extraer_proveedor(
        factura,
    )

    es_credito, fecha_vencimiento = _extraer_forma_pago(
        factura,
        fecha_valor,
    )

    lineas = _extraer_lineas(
        factura,
    )

    subtotal, iva, total = _extraer_totales(
        factura,
    )

    if subtotal <= 0 and lineas:

        subtotal = round(
            sum(
                linea.cantidad
                * linea.precio_unitario
                for linea in lineas
            ),
            2,
        )

        total = round(
            sum(
                linea.total_linea
                for linea in lineas
            ),
            2,
        )

        iva = round(
            total - subtotal,
            2,
        )

    return FacturaXmlParseada(
        cufe=cufe,
        numero_proveedor=numero_proveedor,
        prefijo=prefijo,
        consecutivo=consecutivo,
        fecha=fecha_valor,
        nit_proveedor=nit,
        razon_social_proveedor=razon,
        subtotal=subtotal,
        iva=iva,
        total=total,
        es_credito=es_credito,
        fecha_vencimiento=fecha_vencimiento,
        lineas=lineas,
        ruta_xml_origen="",
    )


def copiar_xml_almacen(
    ruta_origen: str | Path,
    *,
    carpeta_destino: str | Path,
    cufe: str = "",
) -> str:

    origen = Path(ruta_origen)

    destino_dir = Path(carpeta_destino)
    destino_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    sufijo = cufe[:16] if cufe else origen.stem

    destino = destino_dir / f"{sufijo}_{origen.name}"

    contador = 1

    while destino.exists():

        destino = destino_dir / (
            f"{sufijo}_{contador}_{origen.name}"
        )

        contador += 1

    shutil.copy2(
        origen,
        destino,
    )

    return str(destino)
