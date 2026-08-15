from __future__ import annotations

from aplicacion.framework.reportes.encabezado import (
    html_encabezado_documento,
)
from aplicacion.framework.reportes.estado_documento import (
    html_estado_documento,
)
from aplicacion.framework.reportes.estilos import (
    css_base,
)
from aplicacion.framework.reportes.pie import (
    html_bloque_cliente,
    html_pie_legal,
)
from aplicacion.framework.reportes.tabla import (
    html_tabla_lineas,
    html_totales,
)


def html_documento_comercial(
    *,
    empresa: dict,
    titulo_documento: str,
    numero_documento: str,
    fecha: str,
    estado: str = "",
    contraparte_titulo: str,
    contraparte_nombre: str,
    contraparte_documento: str = "",
    contraparte_direccion: str = "",
    contraparte_telefono: str = "",
    contraparte_correo: str = "",
    meta_derecha: str = "",
    filas_tabla: str,
    subtotal: str,
    iva: str = "",
    total: str,
    valor_letras: str = "",
    observaciones: str = "",
    info_adicional: str = "",
    notas_pie: str = "",
    columnas_tabla: tuple[str, ...] | None = None,
) -> str:

    encabezado = html_encabezado_documento(
        empresa=empresa,
        titulo_documento=titulo_documento,
        numero_documento=numero_documento,
        fecha=fecha,
        estado=estado,
        meta_derecha=meta_derecha,
    )

    bloque = html_bloque_cliente(
        titulo=contraparte_titulo,
        nombre=contraparte_nombre,
        documento=contraparte_documento,
        direccion=contraparte_direccion,
        telefono=contraparte_telefono,
        correo=contraparte_correo,
    )

    kwargs_tabla = {}

    if columnas_tabla:

        kwargs_tabla["columnas"] = columnas_tabla

    tabla = html_tabla_lineas(
        filas_tabla,
        **kwargs_tabla,
    )

    totales = html_totales(
        subtotal=subtotal,
        iva=iva or "$0.00",
        total=total,
        valor_letras=valor_letras,
    )

    pie = html_pie_legal(
        observaciones=observaciones,
        notas_pie=notas_pie,
        info_electronica=info_adicional,
    )

    badge = html_estado_documento(
        estado,
    )

    return f"""
    <!DOCTYPE html>
    <html><head><meta charset='utf-8'>
    <style>{css_base()}</style>
    </head><body>
    {encabezado}
    {bloque}
    {tabla}
    {totales}
    {pie}
    {badge}
    </body></html>
    """
