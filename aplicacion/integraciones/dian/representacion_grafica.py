from __future__ import annotations

import tempfile
from pathlib import Path


def _nombre_tercero(
    tercero_id,
) -> str:

    if not tercero_id:

        return ""

    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    tercero = TerceroServicio.obtener_por_id(
        tercero_id,
    )

    if tercero is None:

        return ""

    return (
        tercero.razon_social
        or tercero.nombre_completo
        or tercero.numero_documento
        or ""
    )


def _pdf_a_bytes(
    construir_fn,
) -> bytes:

    with tempfile.NamedTemporaryFile(
        suffix=".pdf",
        delete=False,
    ) as archivo:

        ruta = Path(
            archivo.name,
        )

    try:

        construir_fn(
            ruta,
        )

        return ruta.read_bytes()

    finally:

        ruta.unlink(
            missing_ok=True,
        )


def pdf_factura_electronica_venta(
    factura,
    *,
    cufe: str | None = None,
) -> bytes:

    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
        factura_venta_a_dto,
    )
    from aplicacion.reportes.ventas.pdf.factura_venta import (
        FacturaVentaPDF,
    )

    detalles = list(
        factura.detalles,
    )

    nombre_cliente = _nombre_tercero(
        getattr(
            factura,
            "cliente_id",
            None,
        ),
    )

    cufe_guardado = getattr(
        factura,
        "cufe",
        None,
    )

    if cufe:

        factura.cufe = cufe

    try:

        dto = factura_venta_a_dto(
            factura,
            detalles,
            nombre_cliente,
            electronica=True,
        )

    finally:

        if cufe:

            factura.cufe = cufe_guardado

    def _construir(
        ruta: Path,
    ) -> None:

        FacturaVentaPDF(
            ruta,
            empresa_reporte(),
            dto,
            titulo="FACTURA ELECTRÓNICA DE VENTA",
            electronica=True,
        ).construir()

    return _pdf_a_bytes(
        _construir,
    )


def pdf_nota_credito_venta(
    nota,
    *,
    cufe: str | None = None,
) -> bytes:

    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
        nota_credito_venta_a_dto,
    )
    from aplicacion.reportes.ventas.nota_credito import (
        _numero_factura_referencia,
    )
    from aplicacion.reportes.ventas.pdf.factura_venta import (
        FacturaVentaPDF,
    )

    detalles = list(
        nota.detalles,
    )

    nombre_cliente = _nombre_tercero(
        getattr(
            nota,
            "cliente_id",
            None,
        ),
    )

    referencia = _numero_factura_referencia(
        getattr(
            nota,
            "factura_id",
            None,
        ),
    )

    cufe_guardado = getattr(
        nota,
        "cufe",
        None,
    )

    if cufe:

        nota.cufe = cufe

    try:

        dto = nota_credito_venta_a_dto(
            nota,
            detalles,
            nombre_cliente,
            electronica=True,
            factura_numero=referencia,
        )

    finally:

        if cufe:

            nota.cufe = cufe_guardado

    def _construir(
        ruta: Path,
    ) -> None:

        FacturaVentaPDF(
            ruta,
            empresa_reporte(),
            dto,
            titulo="NOTA CRÉDITO ELECTRÓNICA",
            electronica=True,
        ).construir()

    return _pdf_a_bytes(
        _construir,
    )


def pdf_nota_debito_venta(
    nota,
    *,
    cufe: str | None = None,
) -> bytes:

    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
        nota_debito_venta_a_dto,
    )
    from aplicacion.reportes.ventas.nota_debito import (
        _numero_factura_referencia,
    )
    from aplicacion.reportes.ventas.pdf.factura_venta import (
        FacturaVentaPDF,
    )

    detalles = list(
        nota.detalles,
    )

    nombre_cliente = _nombre_tercero(
        getattr(
            nota,
            "cliente_id",
            None,
        ),
    )

    referencia = _numero_factura_referencia(
        getattr(
            nota,
            "factura_id",
            None,
        ),
    )

    cufe_guardado = getattr(
        nota,
        "cufe",
        None,
    )

    if cufe:

        nota.cufe = cufe

    try:

        dto = nota_debito_venta_a_dto(
            nota,
            detalles,
            nombre_cliente,
            electronica=True,
            factura_numero=referencia,
        )

    finally:

        if cufe:

            nota.cufe = cufe_guardado

    def _construir(
        ruta: Path,
    ) -> None:

        FacturaVentaPDF(
            ruta,
            empresa_reporte(),
            dto,
            titulo="NOTA DÉBITO ELECTRÓNICA",
            electronica=True,
        ).construir()

    return _pdf_a_bytes(
        _construir,
    )


def pdf_guia_remision_electronica(
    guia,
    *,
    cude: str | None = None,
) -> bytes:

    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
        guia_remision_electronica_a_dto,
    )
    from aplicacion.reportes.ventas.pdf.remision import (
        RemisionPDF,
    )

    detalles = list(
        guia.detalles,
    )

    nombre_cliente = _nombre_tercero(
        getattr(
            guia,
            "cliente_id",
            None,
        ),
    )

    cude_guardado = getattr(
        guia,
        "cude",
        None,
    )

    if cude:

        guia.cude = cude

    try:

        dto = guia_remision_electronica_a_dto(
            guia,
            detalles,
            nombre_cliente,
            electronica=True,
            cude=cude,
        )

    finally:

        if cude:

            guia.cude = cude_guardado

    def _construir(
        ruta: Path,
    ) -> None:

        RemisionPDF(
            ruta,
            empresa_reporte(),
            dto,
            titulo="GUÍA DE REMISIÓN ELECTRÓNICA",
            electronica=True,
            codigo_label="CUDE",
        ).construir()

    return _pdf_a_bytes(
        _construir,
    )


def pdf_documento_soporte(
    documento,
    *,
    cuds: str | None = None,
) -> bytes:

    from aplicacion.reportes.comunes.datos_documento import (
        documento_soporte_a_dto,
        empresa_reporte,
    )
    from aplicacion.reportes.compras.pdf.factura_compra import (
        FacturaCompraPDF,
    )

    detalles = list(
        documento.detalles,
    )

    nombre_proveedor = _nombre_tercero(
        getattr(
            documento,
            "proveedor_id",
            None,
        ),
    )

    if not nombre_proveedor:

        nombre_proveedor = str(
            getattr(
                documento,
                "razon_social_proveedor",
                "",
            )
            or "",
        ).strip()

    documento_proveedor = str(
        getattr(
            documento,
            "nit_proveedor",
            "",
        )
        or "",
    ).strip()

    cuds_guardado = getattr(
        documento,
        "cuds",
        None,
    )

    if cuds:

        documento.cuds = cuds

    try:

        dto = documento_soporte_a_dto(
            documento,
            detalles,
            nombre_proveedor,
            documento_proveedor=documento_proveedor,
            cuds=cuds,
        )

    finally:

        if cuds:

            documento.cuds = cuds_guardado

    def _construir(
        ruta: Path,
    ) -> None:

        FacturaCompraPDF(
            ruta,
            empresa_reporte(),
            dto,
        ).construir()

    return _pdf_a_bytes(
        _construir,
    )


def pdf_nomina_electronica(
    periodo,
    *,
    numero: str,
    cune: str | None = None,
    totales: dict | None = None,
    trabajadores: list[dict] | None = None,
) -> bytes:

    from aplicacion.modulos.nomina.servicios import (
        ServicioNomina,
    )
    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
    )
    from aplicacion.reportes.nomina.electronica import (
        nomina_electronica_a_dto,
    )
    from aplicacion.framework.reportes.pdf.tabla_reporte import (
        TablaReportePDF,
    )

    periodo_id = getattr(
        periodo,
        "id",
        None,
    )

    if totales is None:

        totales = ServicioNomina.totales_periodo(
            periodo_id,
        )

    if trabajadores is None:

        trabajadores = ServicioNomina.listar_resumen_periodo(
            periodo_id,
        )

    cune_guardado = getattr(
        periodo,
        "cune",
        None,
    )

    if cune:

        periodo.cune = cune

    try:

        dto = nomina_electronica_a_dto(
            numero=numero,
            periodo=str(
                getattr(
                    periodo,
                    "nombre",
                    "",
                )
                or f"{getattr(periodo, 'mes', ''):02d}/{getattr(periodo, 'anio', '')}",
            ),
            cune=cune or cune_guardado or "",
            totales=totales,
            trabajadores=trabajadores,
            estado_dian=str(
                getattr(
                    periodo,
                    "estado_dian",
                    "",
                )
                or "",
            ),
        )

    finally:

        if cune:

            periodo.cune = cune_guardado

    def _construir(
        ruta: Path,
    ) -> None:

        TablaReportePDF(
            ruta,
            empresa_reporte(),
            dto,
        ).construir()

    return _pdf_a_bytes(
        _construir,
    )


def adjunto_pdf_contenedor(
    nombre_xml: str,
    pdf_bytes: bytes,
) -> tuple[str, bytes]:

    nombre_pdf = (
        f"{Path(nombre_xml).stem}.pdf"
    )

    return (
        nombre_pdf,
        pdf_bytes,
    )
