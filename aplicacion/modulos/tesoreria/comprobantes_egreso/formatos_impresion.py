from __future__ import annotations

from aplicacion.reportes.comunes.datos_documento import (
    comprobante_egreso_a_dto,
)
from aplicacion.reportes.comunes.html_documento import (
    html_comercial_desde_dto,
)


def generar_html_comprobante(
    comprobante,
    *,
    nombre_proveedor: str,
    documento_proveedor: str = "",
) -> str:

    dto = comprobante_egreso_a_dto(
        comprobante,
        nombre_proveedor=nombre_proveedor,
        documento_proveedor=documento_proveedor,
    )

    meta = (
        f"<div><strong>Forma de pago:</strong> "
        f"{comprobante.forma_pago}</div>"
    )

    if getattr(
        comprobante,
        "banco",
        None,
    ):

        meta += (
            f"<div><strong>Banco:</strong> "
            f"{comprobante.banco}</div>"
        )

    return html_comercial_desde_dto(
        dto,
        titulo_documento="COMPROBANTE DE EGRESO",
        contraparte_titulo="PAGADO A",
        meta_derecha=meta,
        info_adicional=(
            "<p>Elaboró ________  Revisó ________  "
            "Aprobó ________  Recibí ________</p>"
        ),
    )
