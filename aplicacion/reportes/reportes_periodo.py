from __future__ import annotations

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)
from aplicacion.reportes.comunes.reporte_tabular import (
    crear_reporte_tabular,
    filas_dict_a_tabla_pdf,
)


def crear_reporte_periodo(
    *,
    titulo: str,
    filas: list[dict],
    columnas: list[str],
    campos: list[str],
    periodo: str,
    pie: str = "",
    columnas_numericas: set[int] | None = None,
    formateadores: dict | None = None,
    nombre_pdf: str | None = None,
) -> ReporteDocumentoGenerico:

    filas_pdf = filas_dict_a_tabla_pdf(
        filas,
        campos,
        columnas_numericas=columnas_numericas,
        formateadores=formateadores,
    )

    return crear_reporte_tabular(
        titulo=titulo,
        numero=periodo,
        subtitulo="Consulta por periodo",
        columnas=columnas,
        filas=filas_pdf,
        pie=pie,
        nombre_pdf=(
            nombre_pdf
            or f"{titulo} {periodo}.pdf"
        ),
    )
