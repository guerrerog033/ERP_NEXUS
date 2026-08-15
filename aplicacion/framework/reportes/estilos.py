from __future__ import annotations

from aplicacion.recursos.estilos import colores


def css_base() -> str:

    return f"""
    @page {{
        margin: 12mm;
    }}
    body {{
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 10pt;
        color: {colores.TEXT};
        background: {colores.SURFACE};
        margin: 0;
        padding: 0;
        line-height: 1.35;
    }}
    h1, h2, h3 {{
        margin: 0;
        padding: 0;
        font-weight: 600;
    }}
    table {{
        border-collapse: collapse;
        width: 100%;
    }}
    .texto-secundario {{
        color: {colores.TEXT_SECONDARY};
        font-size: 9pt;
    }}
    .texto-derecha {{
        text-align: right;
    }}
    .texto-centro {{
        text-align: center;
    }}
    .negrita {{
        font-weight: 600;
    }}
    """
