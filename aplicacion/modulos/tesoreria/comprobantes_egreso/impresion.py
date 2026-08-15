from __future__ import annotations

from aplicacion.framework.reportes.impresion_util import (
    abrir_centro_impresion,
    exportar_pdf_dialogo,
)
from aplicacion.reportes.tesoreria.comprobante_egreso import (
    crear_reporte_comprobante_egreso,
)


def imprimir_comprobante_egreso(
    comprobante,
    *,
    nombre_proveedor: str,
    documento_proveedor: str = "",
    parent=None,
) -> None:

    abrir_centro_impresion(
        crear_reporte_comprobante_egreso(
            comprobante,
            nombre_proveedor=nombre_proveedor,
            documento_proveedor=documento_proveedor,
        ),
        parent=parent,
        titulo=(
            f"Centro de impresión — "
            f"CE {comprobante.numero}"
        ),
    )


def exportar_pdf_comprobante_egreso(
    comprobante,
    *,
    nombre_proveedor: str,
    documento_proveedor: str = "",
    parent=None,
) -> bool:

    return exportar_pdf_dialogo(
        crear_reporte_comprobante_egreso(
            comprobante,
            nombre_proveedor=nombre_proveedor,
            documento_proveedor=documento_proveedor,
        ),
        parent=parent,
    )
