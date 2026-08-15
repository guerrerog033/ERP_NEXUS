from __future__ import annotations

from aplicacion.recursos.estilos import colores

from .estado_documento import (
    html_estado_documento,
)


def html_encabezado_documento(
    *,
    empresa: dict,
    titulo_documento: str,
    numero_documento: str,
    fecha: str,
    estado: str = "",
    qr_html: str = "",
    meta_derecha: str = "",
) -> str:

    logo = str(
        empresa.get(
            "logo_ruta",
            "",
        )
        or "",
    ).strip()

    logo_html = ""

    if logo:

        logo_html = (
            f"<img src='{logo}' alt='Logo' "
            "style='max-height:56px;max-width:180px;'/>"
        )

    else:

        logo_html = (
            f"<div style='font-size:18pt;font-weight:700;"
            f"color:{colores.PRIMARY};'>"
            f"{empresa.get('nombre', 'ERP NEXUS')}</div>"
        )

    badge = html_estado_documento(
        estado,
    )

    return f"""
    <table style='margin-bottom:10px;border-bottom:2px solid {colores.PRIMARY};'>
      <tr>
        <td style='width:34%;vertical-align:top;padding:8px 4px;'>
          {logo_html}
          <div class='texto-secundario' style='margin-top:6px;'>
            <strong>{empresa.get('nombre', '')}</strong><br/>
            NIT {empresa.get('nit', '')}<br/>
            {empresa.get('direccion', '')}<br/>
            {empresa.get('ciudad', '')} · {empresa.get('telefono', '')}<br/>
            {empresa.get('correo', '')}
          </div>
        </td>
        <td style='width:33%;vertical-align:top;text-align:center;padding:8px;'>
          {qr_html}
        </td>
        <td style='width:33%;vertical-align:top;text-align:right;padding:8px 4px;'>
          <div style='font-size:15pt;font-weight:700;color:{colores.PRIMARY};'>
            {titulo_documento}
          </div>
          <div style='font-size:13pt;font-weight:600;margin:4px 0;'>
            {numero_documento}
          </div>
          {badge}
          <div class='texto-secundario' style='margin-top:8px;'>
            <strong>Fecha:</strong> {fecha}
          </div>
          {meta_derecha}
        </td>
      </tr>
    </table>
    """
