from __future__ import annotations

from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    ContextoFormato,
    generar_html_desde_contexto,
    normalizar_formato_codigo,
)
from aplicacion.modulos.ventas.cotizaciones.servicios import (
    ServicioCotizacion,
)
from aplicacion.reportes.comunes.datos_documento import (
    remision_a_dto,
)
from aplicacion.reportes.comunes.html_documento import (
    contexto_formato_desde_dto,
    filas_tabla_logistica_html,
)
from aplicacion.recursos.estilos import colores


def _formatear_moneda(
    valor: float,
) -> str:

    return f"${valor:,.2f}"


def _bloque_logistica(
    dto: dict,
) -> str:

    direccion = str(
        dto.get(
            "direccion_entrega",
            "",
        )
        or dto.get(
            "cliente",
            {},
        ).get(
            "direccion",
            "",
        )
        or "",
    )

    pedido = str(
        dto.get(
            "pedido_numero",
            "",
        )
        or "",
    ).strip()

    encabezado_pedido = ""

    if pedido:

        encabezado_pedido = (
            f"<p><strong>Pedido origen:</strong> {pedido}</p>"
        )

    tabla = (
        f"<table style='margin:8px 0;'>"
        f"<thead><tr>"
        f"<th>#</th><th>Producto</th>"
        f"<th>Solicitada</th><th>Entregada</th><th>Und.</th>"
        f"</tr></thead><tbody>"
        f"{filas_tabla_logistica_html(dto.get('items', []))}"
        f"</tbody></table>"
    )

    return (
        f"<div style='margin-top:12px;padding:10px;"
        f"border:1px solid {colores.BORDER};'>"
        f"<strong>Información logística</strong>"
        f"{encabezado_pedido}"
        f"<p><strong>Dirección de entrega:</strong> "
        f"{direccion or '—'}</p>"
        f"{tabla}"
        f"<p style='margin-top:12px;'>"
        f"Transportador: _____________________________<br/>"
        f"Vehículo: _________________________________<br/>"
        f"Recibe: ____________________________________<br/>"
        f"Documento: ________________________________</p>"
        f"<table width='100%'><tr>"
        f"<td>Firma quien entrega<br/><br/>________________</td>"
        f"<td>Firma quien recibe<br/><br/>________________</td>"
        f"</tr></table></div>"
    )


def _info_adicional_remision(
    dto: dict,
) -> str:

    return _bloque_logistica(
        dto,
    )


def _crear_contexto_remision(
    remision,
    detalles,
    nombre_cliente: str,
) -> ContextoFormato:

    dto = remision_a_dto(
        remision,
        detalles,
        nombre_cliente,
    )

    return contexto_formato_desde_dto(
        dto,
        documento=remision,
        detalles=detalles,
        nombre_cliente=nombre_cliente,
        resumen={
            "subtotal": float(
                dto.get(
                    "subtotal",
                    0,
                )
                or remision.subtotal
                or 0,
            ),
            "iva": 0.0,
            "total": float(
                dto.get(
                    "total",
                    0,
                )
                or remision.total
                or 0,
            ),
            "retefuente": 0.0,
            "reteica": 0.0,
            "reteiva": 0.0,
        },
        fecha=remision.fecha.strftime(
            "%d/%m/%Y",
        ),
        etiqueta_documento="REMISIÓN INTERNA",
        titulo_documento="Remisión interna",
        info_adicional=_info_adicional_remision(
            dto,
        ),
        mostrar_imagenes=False,
    )


def generar_html_remision(
    remision,
    detalles,
    nombre_cliente: str,
    *,
    formato: str | None = None,
) -> str:

    codigo = normalizar_formato_codigo(
        formato or "corporativo",
    )

    if codigo not in ServicioCotizacion.formatos_disponibles():

        codigo = "corporativo"

    ctx = _crear_contexto_remision(
        remision,
        detalles,
        nombre_cliente,
    )

    html = generar_html_desde_contexto(
        ctx,
        codigo,
    )

    total_ref = _formatear_moneda(
        float(
            remision.total or 0,
        ),
    )

    return html.replace(
        "</body></html>",
        (
            f"<p class='texto-secundario'>"
            f"Total referencia logística: {total_ref}</p>"
            "</body></html>"
        ),
    )
