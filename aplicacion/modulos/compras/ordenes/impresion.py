from __future__ import annotations

from aplicacion.framework.reportes.impresion_util import (
    abrir_centro_impresion,
    exportar_pdf_dialogo,
)
from aplicacion.reportes.compras.orden_compra import (
    crear_reporte_orden_compra,
)


def imprimir_orden_compra(
    orden,
    detalles,
    nombre_proveedor: str,
    *,
    parent=None,
    proveedor=None,
) -> None:

    abrir_centro_impresion(
        crear_reporte_orden_compra(
            orden,
            detalles,
            nombre_proveedor,
            proveedor=proveedor,
        ),
        parent=parent,
        titulo=(
            f"Centro de impresión — OC {orden.numero}"
        ),
    )


def exportar_pdf_orden_compra(
    orden,
    detalles,
    nombre_proveedor: str,
    *,
    parent=None,
    proveedor=None,
) -> bool:

    return exportar_pdf_dialogo(
        crear_reporte_orden_compra(
            orden,
            detalles,
            nombre_proveedor,
            proveedor=proveedor,
        ),
        parent=parent,
    )
