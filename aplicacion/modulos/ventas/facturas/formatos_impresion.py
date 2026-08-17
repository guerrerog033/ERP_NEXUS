from __future__ import annotations

from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    ContextoFormato,
    etiqueta_formato,
    formatos_combo,
    generar_html_desde_contexto,
    normalizar_formato_codigo,
)
from aplicacion.framework.reportes.reporte_base import (
    ReporteDocumentoBase,
)
from aplicacion.modulos.ventas.cotizaciones.servicios import (
    ServicioCotizacion,
)


def _info_adicional_factura(
    factura,
) -> str:

    partes: list[str] = []

    if getattr(
        factura,
        "estado_dian",
        None,
    ):

        partes.append(
            f"<p>Estado DIAN: {factura.estado_dian}</p>",
        )

    if getattr(
        factura,
        "cufe",
        None,
    ):

        partes.append(
            "<p><strong>CUFE:</strong> "
            f"<span style='font-size:9pt;'>"
            f"{factura.cufe}</span></p>",
        )

    moneda = getattr(
        factura,
        "moneda_referencia",
        None,
    )

    tasa = getattr(
        factura,
        "tasa_cambio_referencia",
        None,
    )

    if moneda and tasa:

        valor_referencia = float(
            factura.total or 0,
        ) / float(
            tasa,
        )

        partes.append(
            "<p>Valor de referencia: "
            f"{moneda} {valor_referencia:,.2f} "
            f"(TRM: ${float(tasa):,.2f} COP) — "
            "Los valores legales de esta factura están en "
            "pesos colombianos (COP).</p>",
        )

    return "".join(
        partes,
    )


def _crear_contexto_factura(
    factura,
    detalles,
    nombre_cliente: str,
) -> ContextoFormato:

    from aplicacion.reportes.comunes.datos_documento import (
        factura_venta_a_dto,
    )
    from aplicacion.reportes.comunes.html_documento import (
        contexto_formato_desde_dto,
        dto_a_resumen_html,
    )

    electronica = bool(
        str(
            getattr(
                factura,
                "cufe",
                "",
            )
            or "",
        ).strip(),
    )

    dto = factura_venta_a_dto(
        factura,
        detalles,
        nombre_cliente,
        electronica=electronica,
    )

    return contexto_formato_desde_dto(
        dto,
        documento=factura,
        detalles=detalles,
        nombre_cliente=nombre_cliente,
        resumen=dto_a_resumen_html(
            dto,
        ),
        fecha=factura.fecha.strftime(
            "%d/%m/%Y",
        ),
        etiqueta_documento="FACTURA",
        titulo_documento="Factura",
        info_adicional=_info_adicional_factura(
            factura,
        ),
        mostrar_imagenes=False,
    )


def formato_predeterminado_factura() -> str:

    return normalizar_formato_codigo(
        ServicioCotizacion.formato_predeterminado(),
    )


def _codigo_formato_factura(
    factura,
    formato: str | None = None,
) -> str:

    codigo = normalizar_formato_codigo(
        formato
        or getattr(
            factura,
            "formato_impresion",
            None,
        )
        or formato_predeterminado_factura(),
    )

    disponibles = ServicioCotizacion.formatos_disponibles()

    if codigo not in disponibles:

        codigo = formato_predeterminado_factura()

    return codigo


def generar_html_factura_venta(
    factura,
    detalles,
    nombre_cliente: str,
    *,
    formato: str | None = None,
) -> str:

    codigo = _codigo_formato_factura(
        factura,
        formato,
    )

    ctx = _crear_contexto_factura(
        factura,
        detalles,
        nombre_cliente,
    )

    if codigo == "electronica":

        from aplicacion.reportes.ventas.factura_electronica import (
            generar_html_factura_electronica,
        )

        ctx.info_adicional = ""

        return generar_html_factura_electronica(
            ctx,
        )

    return generar_html_desde_contexto(
        ctx,
        codigo,
    )


def crear_reporte_factura_venta(
    factura,
    detalles,
    nombre_cliente: str,
    *,
    formato: str | None = None,
) -> ReporteDocumentoBase:

    codigo = _codigo_formato_factura(
        factura,
        formato,
    )

    if codigo == "electronica":

        from aplicacion.reportes.ventas.factura_electronica import (
            ReporteFacturaElectronicaVenta,
        )

        ctx = _crear_contexto_factura(
            factura,
            detalles,
            nombre_cliente,
        )

        ctx.info_adicional = ""

        return ReporteFacturaElectronicaVenta(
            ctx,
        )

    from aplicacion.reportes.ventas.factura import (
        ReporteFacturaVenta,
    )

    return ReporteFacturaVenta(
        factura,
        detalles,
        nombre_cliente,
        formato=codigo,
    )
