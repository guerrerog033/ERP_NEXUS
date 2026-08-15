from __future__ import annotations

from aplicacion.framework.reportes.impresion_util import (
    abrir_centro_impresion,
    exportar_pdf_dialogo,
)
from aplicacion.reportes.ventas.pedido import (
    crear_reporte_pedido,
)


def imprimir_pedido(
    pedido,
    detalles,
    nombre_cliente: str,
    *,
    parent=None,
    cliente=None,
) -> None:

    abrir_centro_impresion(
        crear_reporte_pedido(
            pedido,
            detalles,
            nombre_cliente,
            cliente=cliente,
        ),
        parent=parent,
        titulo=f"Centro de impresión — Pedido {pedido.numero}",
    )


def exportar_pdf_pedido(
    pedido,
    detalles,
    nombre_cliente: str,
    *,
    parent=None,
    cliente=None,
) -> bool:

    return exportar_pdf_dialogo(
        crear_reporte_pedido(
            pedido,
            detalles,
            nombre_cliente,
            cliente=cliente,
        ),
        parent=parent,
    )
