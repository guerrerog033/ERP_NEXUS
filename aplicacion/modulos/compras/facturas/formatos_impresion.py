from __future__ import annotations

from aplicacion.framework.reportes.numero_letras import (
    numero_a_letras,
)
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

        precio = float(
            detalle.precio_unitario or 0,
        )

        total = float(
            detalle.total_linea
            or cantidad * precio,
        )

        filas += (
            f"<tr>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};'>"
            f"{indice}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};'>"
            f"{detalle.descripcion}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{cantidad:g}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{_formatear_moneda(precio)}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{_formatear_moneda(total)}</td>"
            f"</tr>"
        )

    return filas


def generar_html_factura_compra(
    factura,
    detalles,
    nombre_proveedor: str,
    *,
    documento_proveedor: str = "",
    correo_proveedor: str = "",
) -> str:

    empresa = _datos_empresa()

    info = ""

    if factura.cufe:

        info += (
            f"<p><strong>CUFE:</strong> {factura.cufe}</p>"
        )

    if factura.numero_proveedor:

        info += (
            f"<p><strong>Factura proveedor:</strong> "
            f"{factura.numero_proveedor}</p>"
        )

    info += (
        f"<p>Origen: {factura.origen} · "
        f"Estado: {factura.estado}</p>"
    )

    return html_documento_comercial(
        empresa=empresa,
        titulo_documento="FACTURA DE COMPRA",
        numero_documento=str(
            factura.numero or "",
        ),
        fecha=factura.fecha.strftime(
            "%d/%m/%Y",
        ),
        estado=str(
            factura.estado or "",
        ),
        contraparte_titulo="PROVEEDOR",
        contraparte_nombre=nombre_proveedor,
        contraparte_documento=documento_proveedor,
        contraparte_correo=correo_proveedor,
        filas_tabla=_filas_detalle(
            detalles,
        ),
        subtotal=_formatear_moneda(
            float(
                factura.subtotal or 0,
            ),
        ),
        iva=_formatear_moneda(
            float(
                factura.iva or 0,
            ),
        ),
        total=_formatear_moneda(
            float(
                factura.total or 0,
            ),
        ),
        valor_letras=numero_a_letras(
            float(
                factura.total or 0,
            ),
        ),
        observaciones=str(
            factura.observaciones
            or "",
        ).strip(),
        info_adicional=info,
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
            "Costo",
            "Total",
        ),
    )
