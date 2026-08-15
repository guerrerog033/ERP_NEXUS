from __future__ import annotations

from aplicacion.framework.reportes.impresion_util import (
    abrir_centro_impresion,
    exportar_pdf_dialogo,
)
from aplicacion.reportes.tesoreria.recibo_caja import (
    crear_reporte_recibo_caja,
)


def imprimir_recibo_caja(
    recibo,
    *,
    nombre_cliente: str,
    documento_cliente: str = "",
    correo_cliente: str = "",
    telefono_cliente: str = "",
    parent=None,
) -> None:

    abrir_centro_impresion(
        crear_reporte_recibo_caja(
            recibo,
            nombre_cliente=nombre_cliente,
            documento_cliente=documento_cliente,
            correo_cliente=correo_cliente,
            telefono_cliente=telefono_cliente,
        ),
        parent=parent,
        titulo=(
            f"Centro de impresión — "
            f"Recibo {recibo.numero}"
        ),
    )


def exportar_pdf_recibo_caja(
    recibo,
    *,
    nombre_cliente: str,
    documento_cliente: str = "",
    correo_cliente: str = "",
    telefono_cliente: str = "",
    parent=None,
) -> bool:

    return exportar_pdf_dialogo(
        crear_reporte_recibo_caja(
            recibo,
            nombre_cliente=nombre_cliente,
            documento_cliente=documento_cliente,
            correo_cliente=correo_cliente,
            telefono_cliente=telefono_cliente,
        ),
        parent=parent,
    )
