from __future__ import annotations

from pathlib import Path

from aplicacion.comunes.qr_util import (
    generar_qr_data_uri,
)
from aplicacion.framework.reportes.encabezado import (
    html_encabezado_documento,
)
from aplicacion.framework.reportes.estilos import (
    css_base,
)
from aplicacion.framework.reportes.numero_letras import (
    numero_a_letras,
)
from aplicacion.framework.reportes.pie import (
    html_bloque_cliente,
    html_pie_legal,
)
from aplicacion.framework.reportes.reporte_base import (
    ReporteDocumentoBase,
)
from aplicacion.framework.reportes.tabla import (
    html_tabla_lineas,
    html_totales,
)
from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    ContextoFormato,
    _etiqueta_impuesto_porcentaje,
    _formatear_moneda,
    _unidad_producto,
)
from aplicacion.recursos.estilos import colores


def _url_qr_dian(
    cufe: str,
) -> str:

    cufe_limpio = str(
        cufe or "",
    ).strip()

    if not cufe_limpio:

        return ""

    return (
        "https://catalogo-vpfe.dian.gov.co/"
        f"document/searchqr?documentkey={cufe_limpio}"
    )


def _filas_detalle(
    ctx: ContextoFormato,
) -> str:

    filas: list[str] = []

    for indice, detalle in enumerate(
        ctx.detalles,
        start=1,
    ):

        cantidad = float(
            getattr(
                detalle,
                "cantidad",
                0,
            )
            or 0,
        )

        precio = float(
            getattr(
                detalle,
                "precio_unitario",
                0,
            )
            or 0,
        )

        total = float(
            getattr(
                detalle,
                "total_linea",
                0,
            )
            or cantidad * precio,
        )

        impuesto = _etiqueta_impuesto_porcentaje(
            getattr(
                detalle,
                "impuesto_id",
                None,
            ),
        )

        unidad = _unidad_producto(
            getattr(
                detalle,
                "producto_id",
                None,
            ),
        )

        descripcion = str(
            getattr(
                detalle,
                "descripcion",
                "",
            )
            or "",
        )

        filas.append(
            f"<tr>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};'>"
            f"{indice}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};'>"
            f"<strong>{descripcion}</strong><br/>"
            f"<span class='texto-secundario'>UM: {unidad}</span></td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{cantidad:g}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{_formatear_moneda(precio)}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:center;'>{impuesto}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{_formatear_moneda(total)}</td>"
            f"</tr>"
        )

    return "".join(
        filas,
    )


def generar_html_factura_electronica(
    ctx: ContextoFormato,
) -> str:

    factura = ctx.cotizacion

    cufe = str(
        getattr(
            factura,
            "cufe",
            "",
        )
        or "",
    ).strip()

    qr_html = ""

    url_qr = _url_qr_dian(
        cufe,
    )

    if url_qr:

        qr = generar_qr_data_uri(
            url_qr,
            tamano=3,
        )

        qr_html = (
            f"<img src='{qr}' width='110' alt='QR DIAN'/>"
            "<div class='texto-secundario' style='font-size:8pt;"
            "margin-top:4px;'>Validar en DIAN</div>"
        )

    vencimiento = ""

    if getattr(
        factura,
        "fecha_vencimiento",
        None,
    ):

        vencimiento = (
            f"<div><strong>Vencimiento:</strong> "
            f"{factura.fecha_vencimiento.strftime('%d/%m/%Y')}</div>"
        )

    meta_derecha = vencimiento

    if getattr(
        factura,
        "estado_pago",
        "",
    ):

        meta_derecha += (
            f"<div><strong>Pago:</strong> "
            f"{factura.estado_pago}</div>"
        )

    encabezado = html_encabezado_documento(
        empresa=ctx.empresa,
        titulo_documento="FACTURA ELECTRÓNICA DE VENTA",
        numero_documento=str(
            getattr(
                factura,
                "numero",
                "",
            )
            or "",
        ),
        fecha=ctx.fecha,
        estado=str(
            getattr(
                factura,
                "estado",
                "",
            )
            or "",
        ),
        qr_html=qr_html,
        meta_derecha=meta_derecha,
    )

    cliente = html_bloque_cliente(
        titulo="CLIENTE",
        nombre=ctx.nombre_cliente,
        documento=str(
            ctx.cliente.get(
                "documento",
                "",
            )
            or "",
        ),
        direccion=str(
            ctx.cliente.get(
                "direccion",
                "",
            )
            or "",
        ),
        telefono=str(
            ctx.cliente.get(
                "telefono",
                "",
            )
            or "",
        ),
        correo=str(
            ctx.cliente.get(
                "correo",
                "",
            )
            or "",
        ),
    )

    tabla = html_tabla_lineas(
        _filas_detalle(
            ctx,
        ),
    )

    resumen = ctx.resumen

    totales = html_totales(
        subtotal=_formatear_moneda(
            float(
                resumen.get(
                    "subtotal",
                    0,
                )
                or 0,
            ),
        ),
        iva=_formatear_moneda(
            float(
                resumen.get(
                    "iva",
                    0,
                )
                or 0,
            ),
        ),
        retefuente=_formatear_moneda(
            float(
                resumen.get(
                    "retefuente",
                    0,
                )
                or 0,
            ),
        )
        if float(
            resumen.get(
                "retefuente",
                0,
            )
            or 0,
        )
        else "",
        reteica=_formatear_moneda(
            float(
                resumen.get(
                    "reteica",
                    0,
                )
                or 0,
            ),
        )
        if float(
            resumen.get(
                "reteica",
                0,
            )
            or 0,
        )
        else "",
        total=_formatear_moneda(
            float(
                resumen.get(
                    "total",
                    0,
                )
                or 0,
            ),
        ),
        valor_letras=numero_a_letras(
            float(
                resumen.get(
                    "total",
                    0,
                )
                or 0,
            ),
        ),
    )

    info_electronica = ""

    if cufe:

        info_electronica = (
            f"<p style='font-size:8pt;word-break:break-all;'>"
            f"<strong>CUFE:</strong> {cufe}</p>"
        )

    if getattr(
        factura,
        "estado_dian",
        None,
    ):

        info_electronica += (
            f"<p class='texto-secundario'>"
            f"<strong>Estado DIAN:</strong> "
            f"{factura.estado_dian}</p>"
        )

    pie = html_pie_legal(
        observaciones=ctx.observaciones,
        notas_pie=str(
            ctx.empresa.get(
                "notas_pie",
                "",
            )
            or "",
        ),
        info_electronica=info_electronica,
    )

    return f"""
    <!DOCTYPE html>
    <html><head><meta charset='utf-8'>
    <style>{css_base()}</style>
    </head><body>
    {encabezado}
    {cliente}
    {tabla}
    {totales}
    {pie}
    {ctx.info_adicional}
    </body></html>
    """


class ReporteFacturaElectronicaVenta(
    ReporteDocumentoBase,
):

    def __init__(
        self,
        ctx: ContextoFormato,
    ):

        self.ctx = ctx

    @property
    def titulo_documento(
        self,
    ) -> str:

        return "Factura electrónica"

    @property
    def numero_documento(
        self,
    ) -> str:

        return str(
            getattr(
                self.ctx.cotizacion,
                "numero",
                "",
            )
            or "",
        )

    def generar_html(
        self,
    ) -> str:

        return generar_html_factura_electronica(
            self.ctx,
        )

    def nombre_archivo_pdf(
        self,
    ) -> str:

        cliente = str(
            self.ctx.nombre_cliente or "",
        ).strip()

        base = (
            f"Factura {self.numero_documento}"
        )

        if cliente:

            return f"{base} {cliente}.pdf"

        return f"{base}.pdf"

    def soporta_pdf_reportlab(
        self,
    ) -> bool:

        return True

    def construir_pdf_reportlab(
        self,
        ruta: str | Path,
    ) -> Path:

        from aplicacion.reportes.comunes.datos_documento import (
            empresa_reporte,
            factura_venta_a_dto,
        )
        from aplicacion.reportes.ventas.pdf.factura_venta import (
            FacturaVentaPDF,
        )

        factura = self.ctx.cotizacion

        dto = factura_venta_a_dto(
            factura,
            self.ctx.detalles,
            self.ctx.nombre_cliente,
            electronica=True,
        )

        return FacturaVentaPDF(
            ruta,
            empresa_reporte(),
            dto,
            titulo="FACTURA ELECTRÓNICA DE VENTA",
            electronica=True,
        ).construir()
