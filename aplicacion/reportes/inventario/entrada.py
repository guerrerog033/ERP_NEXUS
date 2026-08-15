from __future__ import annotations

from pathlib import Path

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)


def _construir_pdf_movimiento(
    movimientos,
    ruta: str | Path,
    *,
    titulo: str,
    dto_fn,
) -> Path:

    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
    )
    from aplicacion.reportes.inventario.pdf.movimiento import (
        MovimientoInventarioPDF,
    )

    dto = dto_fn(
        movimientos,
    )

    return MovimientoInventarioPDF(
        ruta,
        empresa_reporte(),
        dto,
        titulo=titulo,
    ).construir()


def crear_reporte_entrada_inventario(
    movimientos,
    *,
    nombre_pdf: str | None = None,
) -> ReporteDocumentoGenerico:

    from aplicacion.reportes.comunes.datos_inventario import (
        entrada_inventario_a_dto,
    )

    if not isinstance(
        movimientos,
        list,
    ):

        movimientos = [
            movimientos,
        ]

    primero = movimientos[0]
    numero = getattr(
        primero,
        "id",
        "",
    )

    return ReporteDocumentoGenerico(
        titulo="Entrada de inventario",
        numero=str(
            numero,
        ),
        generar_html_fn=lambda: __import__(
            "aplicacion.reportes.inventario.html_movimiento",
            fromlist=[
                "generar_html_movimiento",
            ],
        ).generar_html_movimiento(
            movimientos,
            titulo="Entrada de inventario",
            dto_fn=entrada_inventario_a_dto,
        ),
        nombre_pdf=(
            nombre_pdf
            or f"Entrada inventario {numero}.pdf"
        ),
        construir_pdf_reportlab_fn=lambda ruta: _construir_pdf_movimiento(
            movimientos,
            ruta,
            titulo="ENTRADA DE INVENTARIO",
            dto_fn=entrada_inventario_a_dto,
        ),
    )
