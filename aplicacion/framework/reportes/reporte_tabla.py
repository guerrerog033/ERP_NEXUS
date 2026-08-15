from __future__ import annotations

from aplicacion.framework.reportes.estilos import (
    css_base,
)
from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)
from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    _datos_empresa,
)

def html_reporte_tabla(
    *,
    titulo: str,
    subtitulo: str = "",
    columnas: list[str],
    filas: list[list[str]],
    pie: str = "",
) -> str:

    encabezados = "".join(
        f"<th style='padding:6px 8px;text-align:left;"
        f"background:#e8eef5;border:1px solid #cbd5e1;'>"
        f"{col}</th>"
        for col in columnas
    )

    cuerpo = ""

    for fila in filas:

        celdas = "".join(
            f"<td style='padding:5px 8px;border:1px solid #cbd5e1;'>"
            f"{valor}</td>"
            for valor in fila
        )

        cuerpo += f"<tr>{celdas}</tr>"

    empresa = _datos_empresa()

    return f"""
    <!DOCTYPE html>
    <html><head><meta charset='utf-8'>
    <style>{css_base()}</style>
    </head><body>
    <h2 style='color:#1b4f8a;margin:0 0 4px 0;'>{titulo}</h2>
    <p class='texto-secundario'>{subtitulo}</p>
    <p class='texto-secundario'><strong>{empresa.get('nombre','')}</strong>
    · NIT {empresa.get('nit','')}</p>
    <table style='width:100%;margin-top:12px;border-collapse:collapse;'>
    <thead><tr>{encabezados}</tr></thead>
    <tbody>{cuerpo}</tbody>
    </table>
    <p style='margin-top:12px;'>{pie}</p>
    </body></html>
    """


def crear_reporte_tabla(
    *,
    titulo: str,
    numero: str,
    subtitulo: str,
    columnas: list[str],
    filas: list[list[str]],
    pie: str = "",
    nombre_pdf: str | None = None,
) -> ReporteDocumentoGenerico:

    from aplicacion.reportes.comunes.reporte_tabular import (
        crear_reporte_tabular,
    )

    return crear_reporte_tabular(
        titulo=titulo,
        numero=numero,
        subtitulo=subtitulo,
        columnas=columnas,
        filas=filas,
        pie=pie,
        nombre_pdf=nombre_pdf,
    )
