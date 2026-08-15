from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

CodigoDocumento = Literal[
    "01_COTIZACION",
    "02_PEDIDO_VENTA",
    "03_REMISION",
    "04_FACTURA_VENTA",
    "05_NOTA_CREDITO",
    "06_NOTA_DEBITO",
    "07_RECIBO_CAJA",
    "08_SOLICITUD_COMPRA",
    "09_ORDEN_COMPRA",
    "10_RECEPCION_COMPRA",
    "11_FACTURA_COMPRA",
    "12_NOTA_CREDITO_COMPRA",
    "13_COMPROBANTE_EGRESO",
    "14_ENTRADA_INVENTARIO",
    "15_SALIDA_INVENTARIO",
    "16_AJUSTE_INVENTARIO",
    "17_TRASLADO_BODEGA",
    "18_KARDEX",
    "19_COMPROBANTE_CONTABLE",
    "20_LIBRO_DIARIO",
    "21_BALANCE_COMPROBACION",
    "22_ESTADO_SITUACION_FINANCIERA",
    "23_ESTADO_RESULTADOS",
    "24_RECIBO_CAJA_TESORERIA",
    "25_COMPROBANTE_EGRESO_TESORERIA",
    "26_MOVIMIENTO_BANCARIO",
]


@dataclass(
    frozen=True,
)
class EntradaCatalogo:

    codigo: str
    nombre: str
    modulo: str
    formato_pagina: str = "carta"
    soporta_reportlab: bool = True
    soporta_html: bool = True
    enfoque: str = "comercial"


CATALOGO_DOCUMENTOS: tuple[
    EntradaCatalogo,
    ...,
] = (
    EntradaCatalogo(
        "01_COTIZACION",
        "Cotización",
        "ventas.cotizacion",
        enfoque="comercial",
    ),
    EntradaCatalogo(
        "02_PEDIDO_VENTA",
        "Pedido de venta",
        "ventas.pedido",
        enfoque="comercial",
    ),
    EntradaCatalogo(
        "03_REMISION",
        "Remisión",
        "ventas.remision",
        enfoque="logistica",
    ),
    EntradaCatalogo(
        "04_FACTURA_VENTA",
        "Factura de venta",
        "ventas.factura",
        enfoque="comercial",
    ),
    EntradaCatalogo(
        "05_NOTA_CREDITO",
        "Nota crédito venta",
        "ventas.nota_credito",
        enfoque="comercial",
    ),
    EntradaCatalogo(
        "06_NOTA_DEBITO",
        "Nota débito venta",
        "ventas.nota_debito",
        enfoque="comercial",
    ),
    EntradaCatalogo(
        "07_RECIBO_CAJA",
        "Recibo de caja",
        "tesoreria.recibo_caja",
        enfoque="tesoreria",
    ),
    EntradaCatalogo(
        "08_SOLICITUD_COMPRA",
        "Solicitud de compra",
        "compras.solicitud",
        soporta_reportlab=False,
        enfoque="compras",
    ),
    EntradaCatalogo(
        "09_ORDEN_COMPRA",
        "Orden de compra",
        "compras.orden_compra",
        enfoque="compras",
    ),
    EntradaCatalogo(
        "10_RECEPCION_COMPRA",
        "Recepción de compra",
        "compras.recepcion",
        soporta_reportlab=False,
        enfoque="logistica",
    ),
    EntradaCatalogo(
        "11_FACTURA_COMPRA",
        "Factura de compra",
        "compras.factura",
        enfoque="compras",
    ),
    EntradaCatalogo(
        "12_NOTA_CREDITO_COMPRA",
        "Nota crédito compra",
        "compras.nota_credito",
        soporta_reportlab=False,
        enfoque="compras",
    ),
    EntradaCatalogo(
        "13_COMPROBANTE_EGRESO",
        "Comprobante de egreso",
        "tesoreria.comprobante_egreso",
        enfoque="tesoreria",
    ),
    EntradaCatalogo(
        "14_ENTRADA_INVENTARIO",
        "Entrada de inventario",
        "inventario.entrada",
        enfoque="inventario",
    ),
    EntradaCatalogo(
        "15_SALIDA_INVENTARIO",
        "Salida de inventario",
        "inventario.salida",
        enfoque="inventario",
    ),
    EntradaCatalogo(
        "16_AJUSTE_INVENTARIO",
        "Ajuste de inventario",
        "inventario.ajuste",
        enfoque="inventario",
    ),
    EntradaCatalogo(
        "17_TRASLADO_BODEGA",
        "Traslado entre bodegas",
        "inventario.traslado",
        enfoque="inventario",
    ),
    EntradaCatalogo(
        "18_KARDEX",
        "Kardex",
        "inventario.kardex",
        soporta_reportlab=False,
        enfoque="inventario",
    ),
    EntradaCatalogo(
        "19_COMPROBANTE_CONTABLE",
        "Comprobante contable",
        "contabilidad.comprobante",
        enfoque="contabilidad",
    ),
    EntradaCatalogo(
        "20_LIBRO_DIARIO",
        "Libro diario",
        "contabilidad.libro_diario",
        soporta_reportlab=False,
        enfoque="contabilidad",
    ),
    EntradaCatalogo(
        "21_BALANCE_COMPROBACION",
        "Balance de comprobación",
        "contabilidad.balance_prueba",
        soporta_reportlab=False,
        enfoque="contabilidad",
    ),
    EntradaCatalogo(
        "22_ESTADO_SITUACION_FINANCIERA",
        "Estado de situación financiera",
        "contabilidad.estado_situacion",
        soporta_reportlab=False,
        enfoque="contabilidad",
    ),
    EntradaCatalogo(
        "23_ESTADO_RESULTADOS",
        "Estado de resultados",
        "contabilidad.estado_resultados",
        soporta_reportlab=False,
        enfoque="contabilidad",
    ),
    EntradaCatalogo(
        "24_RECIBO_CAJA_TESORERIA",
        "Recibo de caja (tesorería)",
        "tesoreria.recibo_caja",
        enfoque="tesoreria",
    ),
    EntradaCatalogo(
        "25_COMPROBANTE_EGRESO_TESORERIA",
        "Comprobante de egreso (tesorería)",
        "tesoreria.comprobante_egreso",
        enfoque="tesoreria",
    ),
    EntradaCatalogo(
        "26_MOVIMIENTO_BANCARIO",
        "Movimiento bancario",
        "tesoreria.movimiento_bancario",
        soporta_reportlab=False,
        enfoque="tesoreria",
    ),
)

_INDICE = {
    entrada.codigo: entrada
    for entrada in CATALOGO_DOCUMENTOS
}


def obtener_entrada_catalogo(
    codigo: str,
) -> EntradaCatalogo | None:

    return _INDICE.get(
        codigo,
    )
