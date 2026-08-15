from __future__ import annotations

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)
from aplicacion.reportes.comunes.reporte_tabular import (
    crear_reporte_tabular,
)


def crear_reporte_estado_cuenta_cxc(
    resultado: dict,
    *,
    nombre_pdf: str | None = None,
) -> ReporteDocumentoGenerico:

    from aplicacion.reportes.comunes.datos_contabilidad import (
        estado_cuenta_a_dto,
    )

    dto = estado_cuenta_a_dto(
        resultado,
        titulo="Estado de cuenta — Cliente (CxC)",
        subtitulo="Movimientos de cartera por cobrar",
    )

    tercero = str(
        resultado.get(
            "tercero",
            "",
        ),
    )

    return crear_reporte_tabular(
        titulo=dto["titulo"],
        numero=dto["numero"],
        subtitulo=dto["subtitulo"],
        columnas=dto["columnas"],
        filas=dto["filas"],
        pie=dto["pie"],
        nombre_pdf=(
            nombre_pdf
            or f"Estado cuenta CxC {tercero}.pdf"
        ),
    )


def crear_reporte_estado_cuenta_cxp(
    resultado: dict,
    *,
    nombre_pdf: str | None = None,
) -> ReporteDocumentoGenerico:

    from aplicacion.reportes.comunes.datos_contabilidad import (
        estado_cuenta_a_dto,
    )

    dto = estado_cuenta_a_dto(
        resultado,
        titulo="Estado de cuenta — Proveedor (CxP)",
        subtitulo="Movimientos de cartera por pagar",
    )

    tercero = str(
        resultado.get(
            "tercero",
            "",
        ),
    )

    return crear_reporte_tabular(
        titulo=dto["titulo"],
        numero=dto["numero"],
        subtitulo=dto["subtitulo"],
        columnas=dto["columnas"],
        filas=dto["filas"],
        pie=dto["pie"],
        nombre_pdf=(
            nombre_pdf
            or f"Estado cuenta CxP {tercero}.pdf"
        ),
    )
