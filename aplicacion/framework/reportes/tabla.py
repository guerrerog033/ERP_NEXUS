from __future__ import annotations

from aplicacion.recursos.estilos import colores


def html_tabla_lineas(
    filas_html: str,
    *,
    columnas: tuple[str, ...] = (
        "#",
        "Descripción",
        "Cant.",
        "Precio",
        "IVA",
        "Total",
    ),
) -> str:

    encabezados = "".join(
        f"<th style='padding:6px 8px;text-align:left;"
        f"background:{colores.SURFACE_ALT};"
        f"border:1px solid {colores.BORDER};font-size:9pt;'>"
        f"{titulo}</th>"
        for titulo in columnas
    )

    return f"""
    <table style='margin:8px 0;'>
      <thead><tr>{encabezados}</tr></thead>
      <tbody>{filas_html}</tbody>
    </table>
    """


def html_totales(
    *,
    subtotal: str,
    descuento: str = "",
    iva: str,
    retefuente: str = "",
    reteica: str = "",
    total: str,
    valor_letras: str = "",
) -> str:

    filas = [
        ("Subtotal", subtotal),
    ]

    if descuento:

        filas.append(
            (
                "Descuento",
                descuento,
            ),
        )

    filas.append(
        (
            "IVA",
            iva,
        ),
    )

    if retefuente:

        filas.append(
            (
                "Retefuente",
                retefuente,
            ),
        )

    if reteica:

        filas.append(
            (
                "ReteICA",
                reteica,
            ),
        )

    filas.append(
        (
            "TOTAL",
            total,
        ),
    )

    cuerpo = ""

    for etiqueta, valor in filas:

        negrita = "font-weight:700;" if etiqueta == "TOTAL" else ""

        fondo = (
            f"background:{colores.PRIMARY};color:white;"
            if etiqueta == "TOTAL"
            else ""
        )

        cuerpo += (
            f"<tr><td style='padding:5px 8px;text-align:right;"
            f"border:1px solid {colores.BORDER};{negrita}{fondo}'>"
            f"{etiqueta}</td>"
            f"<td style='padding:5px 8px;text-align:right;"
            f"border:1px solid {colores.BORDER};{negrita}{fondo}'>"
            f"{valor}</td></tr>"
        )

    letras = ""

    if valor_letras:

        letras = (
            f"<p style='margin-top:8px;font-style:italic;'>"
            f"<strong>SON:</strong> {valor_letras}</p>"
        )

    return f"""
    <table style='width:320px;margin-left:auto;margin-top:8px;'>
      {cuerpo}
    </table>
    {letras}
    """
