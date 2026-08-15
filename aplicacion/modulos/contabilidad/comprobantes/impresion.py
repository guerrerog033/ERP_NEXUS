from __future__ import annotations

from aplicacion.framework.reportes.impresion_util import (
    abrir_centro_impresion,
    exportar_pdf_dialogo,
)
from aplicacion.reportes.contabilidad.comprobante_contable import (
    crear_reporte_comprobante_contable,
)


def imprimir_comprobante_contable(
    asiento,
    *,
    parent=None,
) -> None:

    abrir_centro_impresion(
        crear_reporte_comprobante_contable(
            asiento,
        ),
        parent=parent,
        titulo=(
            f"Centro de impresión — "
            f"Comprobante {asiento.numero}"
        ),
    )


def exportar_pdf_comprobante_contable(
    asiento,
    *,
    parent=None,
) -> bool:

    return exportar_pdf_dialogo(
        crear_reporte_comprobante_contable(
            asiento,
        ),
        parent=parent,
    )
