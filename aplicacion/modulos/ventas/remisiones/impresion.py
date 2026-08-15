from __future__ import annotations

from aplicacion.framework.reportes.impresion_util import (
    abrir_centro_impresion,
    exportar_pdf_dialogo,
)
from aplicacion.reportes.ventas.remision import (
    crear_reporte_remision,
)


def imprimir_remision(
    remision,
    detalles,
    nombre_cliente: str,
    *,
    parent=None,
    cliente=None,
) -> None:

    abrir_centro_impresion(
        crear_reporte_remision(
            remision,
            detalles,
            nombre_cliente,
            cliente=cliente,
        ),
        parent=parent,
        titulo=f"Centro de impresión — Remisión {remision.numero}",
    )


def exportar_pdf_remision(
    remision,
    detalles,
    nombre_cliente: str,
    *,
    parent=None,
    cliente=None,
) -> bool:

    return exportar_pdf_dialogo(
        crear_reporte_remision(
            remision,
            detalles,
            nombre_cliente,
            cliente=cliente,
        ),
        parent=parent,
    )
