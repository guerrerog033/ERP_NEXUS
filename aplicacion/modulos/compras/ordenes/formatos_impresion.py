from __future__ import annotations

from aplicacion.framework.reportes.plantilla_comercial import (
    html_documento_comercial,
)
from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    _datos_empresa,
    _formatear_moneda,
)
from aplicacion.recursos.estilos import colores


def _filas_detalle(
    detalles,
) -> str:

    filas = ""

    for indice, detalle in enumerate(
        detalles,
        start=1,
    ):

        cantidad = float(
            detalle.cantidad or 0,
        )

        recibida = float(
            getattr(
                detalle,
                "cantidad_recibida",
                0,
            )
            or 0,
        )

        costo = float(
            detalle.costo_unitario or 0,
        )

        total = cantidad * costo

        filas += (
            f"<tr>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};'>"
            f"{indice}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};'>"
            f"{detalle.descripcion}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{cantidad:g}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{recibida:g}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{_formatear_moneda(costo)}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{_formatear_moneda(total)}</td>"
            f"</tr>"
        )

    return filas


def generar_html_orden_compra(
    orden,
    detalles,
    nombre_proveedor: str,
    *,
    documento_proveedor: str = "",
) -> str:

    empresa = _datos_empresa()

    return html_documento_comercial(
        empresa=empresa,
        titulo_documento="ORDEN DE COMPRA",
        numero_documento=str(
            orden.numero or "",
        ),
        fecha=orden.fecha.strftime(
            "%d/%m/%Y",
        ),
        estado=str(
            orden.estado or "",
        ),
        contraparte_titulo="PROVEEDOR",
        contraparte_nombre=nombre_proveedor,
        contraparte_documento=documento_proveedor,
        filas_tabla=_filas_detalle(
            detalles,
        ),
        subtotal=_formatear_moneda(
            float(
                orden.subtotal or 0,
            ),
        ),
        total=_formatear_moneda(
            float(
                orden.total or 0,
            ),
        ),
        observaciones=str(
            orden.observaciones
            or "",
        ).strip(),
        info_adicional=(
            "<p>Condiciones de entrega y pago según acuerdo "
            "comercial con el proveedor.</p>"
        ),
        notas_pie=str(
            empresa.get(
                "notas_pie",
                "",
            )
            or "",
        ),
        columnas_tabla=(
            "#",
            "Descripción",
            "Cant.",
            "Recibida",
            "Costo",
            "Total",
        ),
    )
