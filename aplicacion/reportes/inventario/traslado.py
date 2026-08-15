from __future__ import annotations

from pathlib import Path

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)


def _construir_pdf_traslado(
    salida,
    entrada,
    ruta: str | Path,
) -> Path:

    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
    )
    from aplicacion.reportes.comunes.datos_inventario import (
        traslado_inventario_a_dto,
    )
    from aplicacion.reportes.inventario.pdf.traslado import (
        TrasladoInventarioPDF,
    )

    dto = traslado_inventario_a_dto(
        salida,
        entrada,
    )

    return TrasladoInventarioPDF(
        ruta,
        empresa_reporte(),
        dto,
    ).construir()


def generar_html_traslado(
    salida,
    entrada,
) -> str:

    from aplicacion.framework.reportes.reporte_tabla import (
        html_reporte_tabla,
    )
    from aplicacion.reportes.comunes.datos_inventario import (
        traslado_inventario_a_dto,
    )

    dto = traslado_inventario_a_dto(
        salida,
        entrada,
    )

    filas = []

    for item in dto.get(
        "items",
        [],
    ):

        filas.append(
            [
                str(
                    item.get(
                        "numero",
                        "",
                    ),
                ),
                str(
                    item.get(
                        "codigo",
                        "",
                    ),
                ),
                str(
                    item.get(
                        "descripcion",
                        "",
                    ),
                ),
                f"{float(item.get('cantidad', 0) or 0):,.2f}",
                str(
                    item.get(
                        "unidad",
                        "UND",
                    ),
                ),
            ],
        )

    return html_reporte_tabla(
        titulo="Traslado de inventario",
        subtitulo=(
            f"Número: {dto.get('numero', '')} · "
            f"Fecha: {dto.get('fecha', '')} · "
            f"Origen: {dto.get('bodega_origen', '')} · "
            f"Destino: {dto.get('bodega_destino', '')}"
        ),
        columnas=[
            "#",
            "Código",
            "Descripción",
            "Cantidad",
            "Und",
        ],
        filas=filas,
        pie=dto.get(
            "observaciones",
            "",
        ),
    )


def crear_reporte_traslado_inventario(
    salida,
    entrada,
    *,
    nombre_pdf: str | None = None,
) -> ReporteDocumentoGenerico:

    numero = getattr(
        salida,
        "id",
        "",
    )

    return ReporteDocumentoGenerico(
        titulo="Traslado de inventario",
        numero=str(
            numero,
        ),
        generar_html_fn=lambda: generar_html_traslado(
            salida,
            entrada,
        ),
        nombre_pdf=(
            nombre_pdf
            or f"Traslado inventario {numero}.pdf"
        ),
        construir_pdf_reportlab_fn=lambda ruta: _construir_pdf_traslado(
            salida,
            entrada,
            ruta,
        ),
    )
