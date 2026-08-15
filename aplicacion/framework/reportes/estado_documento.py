from __future__ import annotations

from aplicacion.recursos.estilos import colores


_ESTADOS = {
    "borrador": ("BORRADOR", colores.TEXT_SECONDARY, "#E5E7EB"),
    "generada": ("GENERADA", colores.INFO, "#DBEAFE"),
    "emitida": ("EMITIDA", colores.SUCCESS, "#D1FAE5"),
    "contabilizada": ("CONTABILIZADA", colores.PRIMARY, "#E0E7FF"),
    "aprobada": ("APROBADA", colores.SUCCESS, "#D1FAE5"),
    "pendiente": ("PENDIENTE", colores.WARNING, "#FEF3C7"),
    "despachada": ("DESPACHADA", colores.INFO, "#DBEAFE"),
    "pagada": ("PAGADA", colores.SUCCESS, "#D1FAE5"),
    "anulada": ("ANULADA", colores.DANGER, "#FEE2E2"),
    "cancelada": ("CANCELADA", colores.DANGER, "#FEE2E2"),
}


def html_estado_documento(
    estado: str,
) -> str:

    clave = str(
        estado or "",
    ).strip().lower()

    if not clave:

        return ""

    etiqueta, color_texto, color_fondo = _ESTADOS.get(
        clave,
        (
            clave.upper(),
            colores.TEXT,
            colores.SURFACE_ALT,
        ),
    )

    return (
        f"<span style='display:inline-block;padding:3px 10px;"
        f"border-radius:12px;font-size:8pt;font-weight:700;"
        f"color:{color_texto};background:{color_fondo};'>"
        f"{etiqueta}</span>"
    )
