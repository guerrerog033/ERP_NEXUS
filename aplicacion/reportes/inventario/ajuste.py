from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)

from aplicacion.reportes.inventario.entrada import (
    _construir_pdf_movimiento,
)


def crear_reporte_ajuste_inventario(
    movimiento,
    *,
    nombre_pdf: str | None = None,
) -> ReporteDocumentoGenerico:

    from aplicacion.reportes.comunes.datos_inventario import (
        ajuste_inventario_a_dto,
    )

    numero = getattr(
        movimiento,
        "id",
        "",
    )

    return ReporteDocumentoGenerico(
        titulo="Ajuste de inventario",
        numero=str(
            numero,
        ),
        generar_html_fn=lambda: __import__(
            "aplicacion.reportes.inventario.html_movimiento",
            fromlist=[
                "generar_html_movimiento",
            ],
        ).generar_html_movimiento(
            movimiento,
            titulo="Ajuste de inventario",
            dto_fn=ajuste_inventario_a_dto,
        ),
        nombre_pdf=(
            nombre_pdf
            or f"Ajuste inventario {numero}.pdf"
        ),
        construir_pdf_reportlab_fn=lambda ruta: _construir_pdf_movimiento(
            movimiento,
            ruta,
            titulo="AJUSTE DE INVENTARIO",
            dto_fn=ajuste_inventario_a_dto,
        ),
    )
