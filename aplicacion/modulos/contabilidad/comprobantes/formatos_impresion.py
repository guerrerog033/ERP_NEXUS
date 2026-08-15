from __future__ import annotations

from aplicacion.framework.reportes.plantilla_comercial import (
    html_documento_comercial,
)
from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    _datos_empresa,
    _formatear_moneda,
)
from aplicacion.recursos.estilos import colores


def generar_html_comprobante_contable(
    asiento,
) -> str:

    empresa = _datos_empresa()

    filas = ""

    for indice, detalle in enumerate(
        asiento.detalles,
        start=1,
    ):

        cuenta = (
            detalle.cuenta.codigo
            if detalle.cuenta
            else ""
        )

        nombre = (
            detalle.cuenta.nombre
            if detalle.cuenta
            else ""
        )

        filas += (
            f"<tr>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};'>"
            f"{indice}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};'>"
            f"{cuenta}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};'>"
            f"{nombre}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{float(detalle.debito or 0):,.2f}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{float(detalle.credito or 0):,.2f}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};'>"
            f"{detalle.descripcion or ''}</td>"
            f"</tr>"
        )

    info = (
        f"<p><strong>Origen:</strong> {asiento.origen}</p>"
        f"<p><strong>Descripción:</strong> "
        f"{asiento.descripcion or ''}</p>"
    )

    total_debito = float(
        asiento.total_debito or 0,
    )

    total_credito = float(
        asiento.total_credito or 0,
    )

    return html_documento_comercial(
        empresa=empresa,
        titulo_documento="COMPROBANTE CONTABLE",
        numero_documento=str(
            asiento.numero or "",
        ),
        fecha=str(
            asiento.fecha or "",
        ),
        estado="",
        contraparte_titulo="REFERENCIA",
        contraparte_nombre=str(
            asiento.origen or "",
        ),
        filas_tabla=filas,
        subtotal=_formatear_moneda(
            total_debito,
        ),
        total=_formatear_moneda(
            total_credito,
        ),
        info_adicional=info,
        columnas_tabla=(
            "#",
            "Código",
            "Cuenta",
            "Débito",
            "Crédito",
            "Detalle",
        ),
    )
