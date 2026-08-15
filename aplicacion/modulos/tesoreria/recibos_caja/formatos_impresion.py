from __future__ import annotations

from aplicacion.reportes.comunes.datos_documento import (
    recibo_caja_a_dto,
)
from aplicacion.reportes.comunes.html_documento import (
    html_comercial_desde_dto,
)


def generar_html_recibo(
    recibo,
    *,
    nombre_cliente: str,
    documento_cliente: str = "",
    correo_cliente: str = "",
) -> str:

    dto = recibo_caja_a_dto(
        recibo,
        nombre_cliente=nombre_cliente,
        documento_cliente=documento_cliente,
        correo_cliente=correo_cliente,
    )

    meta = (
        f"<div><strong>Forma de pago:</strong> "
        f"{recibo.forma_pago}</div>"
    )

    return html_comercial_desde_dto(
        dto,
        titulo_documento="RECIBO DE CAJA",
        contraparte_titulo="RECIBIMOS DE",
        meta_derecha=meta,
    )
