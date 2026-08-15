from __future__ import annotations

from pathlib import Path

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)
from aplicacion.modulos.ventas.pedidos.formatos_impresion import (
    generar_html_pedido,
)


def _construir_pdf_pedido(
    pedido,
    detalles,
    nombre_cliente: str,
    ruta: str | Path,
) -> Path:

    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
        pedido_a_dto,
    )
    from aplicacion.reportes.ventas.pdf.pedido import (
        PedidoVentaPDF,
    )

    dto = pedido_a_dto(
        pedido,
        detalles,
        nombre_cliente,
    )

    return PedidoVentaPDF(
        ruta,
        empresa_reporte(),
        dto,
    ).construir()


def crear_reporte_pedido(
    pedido,
    detalles,
    nombre_cliente: str,
    *,
    cliente=None,
    formato: str | None = None,
) -> ReporteDocumentoGenerico:

    numero = str(
        pedido.numero or "",
    )

    correo = ""
    telefono = ""

    if cliente is not None:

        correo = str(
            getattr(
                cliente,
                "correo",
                "",
            )
            or "",
        ).strip()

        telefono = str(
            getattr(
                cliente,
                "telefono",
                "",
            )
            or "",
        ).strip()

    return ReporteDocumentoGenerico(
        titulo="Pedido de venta",
        numero=numero,
        generar_html_fn=lambda: generar_html_pedido(
            pedido,
            detalles,
            nombre_cliente,
            formato=formato,
        ),
        nombre_pdf=f"Pedido {numero}.pdf",
        correo_destino=correo,
        telefono_destino=telefono,
        texto_whatsapp=(
            f"Pedido {numero} — "
            f"Total ${float(pedido.total or 0):,.0f}"
        ),
        construir_pdf_reportlab_fn=lambda ruta: _construir_pdf_pedido(
            pedido,
            detalles,
            nombre_cliente,
            ruta,
        ),
    )
