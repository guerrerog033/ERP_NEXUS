from __future__ import annotations

from aplicacion.framework.reportes.reporte_tabla import (
    html_reporte_tabla,
)


def generar_html_movimiento(
    movimientos,
    *,
    titulo: str,
    dto_fn,
) -> str:

    dto = dto_fn(
        movimientos,
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
                f"${float(item.get('costo', 0) or 0):,.2f}",
                f"${float(item.get('total', 0) or 0):,.2f}",
            ],
        )

    meta = [
        f"Número: {dto.get('numero', '')}",
        f"Fecha: {dto.get('fecha', '')}",
        f"Bodega: {dto.get('bodega', '')}",
    ]

    if dto.get(
        "referencia",
    ):

        meta.append(
            f"Referencia: {dto['referencia']}",
        )

    if dto.get(
        "tipo_ajuste",
    ):

        meta.append(
            f"Tipo: {dto['tipo_ajuste']}",
        )

    pie = dto.get(
        "observaciones",
        "",
    )

    return html_reporte_tabla(
        titulo=titulo,
        subtitulo=" · ".join(
            meta,
        ),
        columnas=[
            "#",
            "Código",
            "Descripción",
            "Cantidad",
            "Und",
            "Costo",
            "Total",
        ],
        filas=filas,
        pie=pie,
    )
