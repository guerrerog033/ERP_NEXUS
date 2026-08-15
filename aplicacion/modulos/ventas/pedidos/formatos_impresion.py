from __future__ import annotations

from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    generar_html_desde_contexto,
    normalizar_formato_codigo,
)
from aplicacion.modulos.ventas.cotizaciones.servicios import (
    ServicioCotizacion,
)
from aplicacion.reportes.comunes.datos_documento import (
    pedido_a_dto,
)
from aplicacion.reportes.comunes.html_documento import (
    contexto_formato_desde_dto,
)


def _info_adicional_pedido(
    pedido,
) -> str:

    partes: list[str] = [
        "<p><strong>Este documento no es una factura.</strong> "
        "Confirma productos, cantidades y condiciones del pedido.</p>",
    ]

    if getattr(
        pedido,
        "vendedor",
        None,
    ):

        partes.append(
            f"<p><strong>Vendedor:</strong> {pedido.vendedor}</p>",
        )

    if getattr(
        pedido,
        "cotizacion_id",
        None,
    ):

        partes.append(
            f"<p><strong>Cotización origen:</strong> "
            f"#{pedido.cotizacion_id}</p>",
        )

    return "".join(
        partes,
    )


def _crear_contexto_pedido(
    pedido,
    detalles,
    nombre_cliente: str,
):

    dto = pedido_a_dto(
        pedido,
        detalles,
        nombre_cliente,
    )

    return contexto_formato_desde_dto(
        dto,
        documento=pedido,
        detalles=detalles,
        nombre_cliente=nombre_cliente,
        fecha=pedido.fecha.strftime(
            "%d/%m/%Y",
        ),
        etiqueta_documento="PEDIDO DE VENTA",
        titulo_documento="Pedido de venta",
        info_adicional=_info_adicional_pedido(
            pedido,
        ),
        mostrar_imagenes=False,
    )


def generar_html_pedido(
    pedido,
    detalles,
    nombre_cliente: str,
    *,
    formato: str | None = None,
) -> str:

    codigo = normalizar_formato_codigo(
        formato or "moderno",
    )

    if codigo not in ServicioCotizacion.formatos_disponibles():

        codigo = "moderno"

    ctx = _crear_contexto_pedido(
        pedido,
        detalles,
        nombre_cliente,
    )

    return generar_html_desde_contexto(
        ctx,
        codigo,
    )
