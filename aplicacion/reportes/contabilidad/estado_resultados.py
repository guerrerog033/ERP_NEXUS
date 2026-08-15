from __future__ import annotations

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)
from aplicacion.reportes.comunes.reporte_tabular import (
    crear_reporte_tabular,
)


def crear_reporte_estado_resultados(
    resultado: dict,
    *,
    periodo: str,
    nombre_pdf: str | None = None,
) -> ReporteDocumentoGenerico:

    from aplicacion.reportes.comunes.datos_contabilidad import (
        estado_resultados_a_dto,
    )

    dto = estado_resultados_a_dto(
        resultado,
        periodo=periodo,
    )

    return crear_reporte_tabular(
        titulo=dto["titulo"],
        numero=dto["numero"],
        subtitulo=dto["subtitulo"],
        columnas=dto["columnas"],
        filas=dto["filas"],
        pie=dto.get(
            "pie",
            "",
        ),
        nombre_pdf=(
            nombre_pdf
            or f"Estado resultados {periodo}.pdf"
        ),
    )
