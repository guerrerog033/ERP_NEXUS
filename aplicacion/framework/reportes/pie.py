from __future__ import annotations

from aplicacion.recursos.estilos import colores


def html_bloque_cliente(
    *,
    titulo: str,
    nombre: str,
    documento: str,
    direccion: str = "",
    telefono: str = "",
    correo: str = "",
    extra: str = "",
) -> str:

    return f"""
    <table style='margin:10px 0;border:1px solid {colores.BORDER};'>
      <tr>
        <td colspan='2' style='background:{colores.PRIMARY};color:white;
            padding:6px 10px;font-weight:600;font-size:9pt;'>
          {titulo}
        </td>
      </tr>
      <tr>
        <td style='padding:8px 10px;width:50%;vertical-align:top;'>
          <strong>{nombre}</strong><br/>
          <span class='texto-secundario'>NIT/CC: {documento or '—'}</span>
        </td>
        <td style='padding:8px 10px;width:50%;vertical-align:top;'>
          {direccion or '—'}<br/>
          Tel: {telefono or '—'}<br/>
          {correo or ''}
        </td>
      </tr>
      {extra}
    </table>
    """


def html_pie_legal(
    *,
    observaciones: str = "",
    notas_pie: str = "",
    info_electronica: str = "",
) -> str:

    bloques: list[str] = []

    if observaciones.strip():

        bloques.append(
            f"<p><strong>Observaciones:</strong> {observaciones}</p>",
        )

    if info_electronica.strip():

        bloques.append(
            info_electronica,
        )

    if notas_pie.strip():

        bloques.append(
            f"<p class='texto-secundario' style='font-size:8pt;'>"
            f"{notas_pie}</p>",
        )

    if not bloques:

        return ""

    return (
        f"<div style='margin-top:12px;padding-top:8px;"
        f"border-top:1px solid {colores.BORDER};'>"
        + "".join(
            bloques,
        )
        + "</div>"
    )
