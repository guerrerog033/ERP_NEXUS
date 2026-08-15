from __future__ import annotations

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)
from aplicacion.reportes.comunes.reporte_tabular import (
    crear_reporte_tabular,
)


def crear_reporte_libro_mayor(
    resultado: dict,
    *,
    periodo: str,
    nombre_pdf: str | None = None,
) -> ReporteDocumentoGenerico:

    from aplicacion.reportes.comunes.datos_contabilidad import (
        libro_mayor_a_dto,
    )

    dto = libro_mayor_a_dto(
        resultado,
        periodo=periodo,
    )

    cuenta = resultado.get(
        "cuenta",
    )

    codigo = str(
        getattr(
            cuenta,
            "codigo",
            "",
        )
        or "cuenta",
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
            or f"Libro mayor {codigo} {periodo}.pdf"
        ),
    )
