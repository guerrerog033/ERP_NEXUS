from __future__ import annotations

from aplicacion.framework.reportes.impresion_util import (
    abrir_centro_impresion,
    exportar_pdf_dialogo,
)
from aplicacion.reportes.ventas.nota_debito import (
    crear_reporte_nota_debito_venta,
)


def imprimir_nota_debito_venta(
    nota,
    detalles,
    nombre_cliente: str,
    *,
    parent=None,
) -> None:

    abrir_centro_impresion(
        crear_reporte_nota_debito_venta(
            nota,
            detalles,
            nombre_cliente,
        ),
        parent=parent,
        titulo=(
            f"Centro de impresión — "
            f"Nota débito {nota.numero}"
        ),
    )


def exportar_pdf_nota_debito_venta(
    nota,
    detalles,
    nombre_cliente: str,
    *,
    parent=None,
) -> bool:

    return exportar_pdf_dialogo(
        crear_reporte_nota_debito_venta(
            nota,
            detalles,
            nombre_cliente,
        ),
        parent=parent,
    )
