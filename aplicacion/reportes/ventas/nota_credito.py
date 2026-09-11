from __future__ import annotations

from pathlib import Path

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)


def _numero_factura_referencia(
    factura_id,
) -> str:

    if not factura_id:

        return ""

    from aplicacion.base_datos.conexion import (
        SessionLocal,
    )
    from aplicacion.modulos.ventas.facturas.modelos import (
        FacturaVenta,
    )

    db = SessionLocal()

    try:

        factura = (
            db.query(
                FacturaVenta,
            )
            .filter(
                FacturaVenta.id
                == factura_id,
            )
            .first()
        )

        if factura is None:

            return str(
                factura_id,
            )

        return str(
            factura.numero or "",
        )

    finally:

        db.close()


def _es_electronica(nota) -> bool:

    return bool(
        str(
            getattr(nota, "cufe", "") or "",
        ).strip(),
    )


def _codigo_formato_nota() -> str:

    from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
        normalizar_formato_codigo,
    )
    from aplicacion.modulos.ventas.cotizaciones.servicios import (
        ServicioCotizacion,
    )

    predeterminado = normalizar_formato_codigo(
        ServicioCotizacion.formato_predeterminado(),
    )

    if predeterminado in ServicioCotizacion.formatos_disponibles():

        return predeterminado

    return "estandar"


def generar_html_nota_venta(
    nota,
    detalles,
    nombre_cliente: str,
    *,
    tipo: str = "credito",
    factura_numero: str = "",
) -> str:
    """
    HTML de la nota (crédito o débito) usando el motor de formatos
    compartido — mismo aspecto que la factura — en vez del bloque
    suelto que se usaba en la vista previa.
    """

    from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
        generar_html_desde_contexto,
    )
    from aplicacion.reportes.comunes.datos_documento import (
        nota_credito_venta_a_dto,
        nota_debito_venta_a_dto,
    )
    from aplicacion.reportes.comunes.html_documento import (
        contexto_formato_desde_dto,
        dto_a_resumen_html,
    )

    es_debito = tipo == "debito"

    palabra = "débito" if es_debito else "crédito"

    referencia = (
        factura_numero
        or _numero_factura_referencia(
            getattr(
                nota,
                "factura_id",
                None,
            ),
        )
    )

    electronica = _es_electronica(nota)

    a_dto = (
        nota_debito_venta_a_dto
        if es_debito
        else nota_credito_venta_a_dto
    )

    dto = a_dto(
        nota,
        detalles,
        nombre_cliente,
        electronica=electronica,
        factura_numero=referencia,
    )

    info: list[str] = []

    if referencia:

        info.append(
            f"<p><b>Factura referencia:</b> {referencia}</p>",
        )

    if getattr(nota, "motivo", ""):

        info.append(
            f"<p><b>Motivo:</b> {nota.motivo}</p>",
        )

    if getattr(nota, "factura_cufe", ""):

        info.append(
            "<p><b>CUFE factura:</b> "
            f"<span style='font-size:9pt;'>{nota.factura_cufe}</span></p>",
        )

    if electronica:

        info.append(
            "<p><b>CUFE:</b> "
            f"<span style='font-size:9pt;'>{nota.cufe}</span></p>",
        )

    ctx = contexto_formato_desde_dto(
        dto,
        documento=nota,
        detalles=detalles,
        nombre_cliente=nombre_cliente,
        resumen=dto_a_resumen_html(dto),
        fecha=dto.get("fecha_generacion", ""),
        etiqueta_documento=f"NOTA {palabra.upper()}",
        titulo_documento=(
            f"Nota {palabra} electrónica"
            if electronica
            else f"Nota {palabra} de venta"
        ),
        info_adicional="".join(info),
        mostrar_imagenes=False,
    )

    return generar_html_desde_contexto(
        ctx,
        _codigo_formato_nota(),
    )


def generar_html_nota_credito_venta(
    nota,
    detalles,
    nombre_cliente: str,
    *,
    factura_numero: str = "",
) -> str:

    return generar_html_nota_venta(
        nota,
        detalles,
        nombre_cliente,
        tipo="credito",
        factura_numero=factura_numero,
    )


def _html_nota_credito_venta(
    nota,
    detalles,
    nombre_cliente: str,
    *,
    factura_numero: str = "",
) -> str:

    return generar_html_nota_credito_venta(
        nota,
        detalles,
        nombre_cliente,
        factura_numero=factura_numero,
    )


def _construir_pdf_nota_credito(
    nota,
    detalles,
    nombre_cliente: str,
    ruta: str | Path,
    *,
    factura_numero: str = "",
) -> Path:

    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
        nota_credito_venta_a_dto,
    )
    from aplicacion.reportes.ventas.pdf.nota_venta import (
        NotaVentaPDF,
    )

    cufe = str(
        getattr(
            nota,
            "cufe",
            "",
        )
        or "",
    ).strip()

    electronica = bool(
        cufe,
    )

    dto = nota_credito_venta_a_dto(
        nota,
        detalles,
        nombre_cliente,
        electronica=electronica,
        factura_numero=(
            factura_numero
            or _numero_factura_referencia(
                getattr(
                    nota,
                    "factura_id",
                    None,
                ),
            )
        ),
    )

    titulo = (
        "NOTA CRÉDITO ELECTRÓNICA"
        if electronica
        else "NOTA CRÉDITO DE VENTA"
    )

    return NotaVentaPDF(
        ruta,
        empresa_reporte(),
        dto,
        titulo=titulo,
        electronica=electronica,
    ).construir()


def crear_reporte_nota_credito_venta(
    nota,
    detalles,
    nombre_cliente: str,
    *,
    factura_numero: str = "",
) -> ReporteDocumentoGenerico:

    numero = str(
        nota.numero or "",
    )

    referencia = (
        factura_numero
        or _numero_factura_referencia(
            getattr(
                nota,
                "factura_id",
                None,
            ),
        )
    )

    return ReporteDocumentoGenerico(
        titulo="Nota crédito de venta",
        numero=numero,
        generar_html_fn=lambda: _html_nota_credito_venta(
            nota,
            detalles,
            nombre_cliente,
            factura_numero=referencia,
        ),
        nombre_pdf=f"Nota credito {numero}.pdf",
        construir_pdf_reportlab_fn=lambda ruta: _construir_pdf_nota_credito(
            nota,
            detalles,
            nombre_cliente,
            ruta,
            factura_numero=referencia,
        ),
    )
