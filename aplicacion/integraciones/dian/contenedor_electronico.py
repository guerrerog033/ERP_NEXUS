from __future__ import annotations

from aplicacion.integraciones.dian.representacion_grafica import (
    adjunto_pdf_contenedor,
    pdf_documento_soporte,
    pdf_factura_electronica_venta,
    pdf_guia_remision_electronica,
    pdf_nomina_electronica,
    pdf_nota_credito_venta,
    pdf_nota_debito_venta,
)


def _adjuntos_pdf(
    nombre_xml: str,
    generador,
) -> list[tuple[str, bytes]] | None:

    try:

        pdf_bytes = generador()

    except Exception:

        return None

    if not pdf_bytes:

        return None

    return [
        adjunto_pdf_contenedor(
            nombre_xml,
            pdf_bytes,
        ),
    ]


def adjuntos_contenedor_factura_venta(
    factura,
    *,
    nombre_xml: str,
    cufe: str,
) -> list[tuple[str, bytes]] | None:

    return _adjuntos_pdf(
        nombre_xml,
        lambda: pdf_factura_electronica_venta(
            factura,
            cufe=cufe,
        ),
    )


def adjuntos_contenedor_nota_credito(
    nota,
    *,
    nombre_xml: str,
    cufe: str,
) -> list[tuple[str, bytes]] | None:

    return _adjuntos_pdf(
        nombre_xml,
        lambda: pdf_nota_credito_venta(
            nota,
            cufe=cufe,
        ),
    )


def adjuntos_contenedor_nota_debito(
    nota,
    *,
    nombre_xml: str,
    cufe: str,
) -> list[tuple[str, bytes]] | None:

    return _adjuntos_pdf(
        nombre_xml,
        lambda: pdf_nota_debito_venta(
            nota,
            cufe=cufe,
        ),
    )


def adjuntos_contenedor_guia_remision(
    guia,
    *,
    nombre_xml: str,
    cude: str,
) -> list[tuple[str, bytes]] | None:

    return _adjuntos_pdf(
        nombre_xml,
        lambda: pdf_guia_remision_electronica(
            guia,
            cude=cude,
        ),
    )


def adjuntos_contenedor_documento_soporte(
    documento,
    *,
    nombre_xml: str,
    cuds: str,
) -> list[tuple[str, bytes]] | None:

    return _adjuntos_pdf(
        nombre_xml,
        lambda: pdf_documento_soporte(
            documento,
            cuds=cuds,
        ),
    )


def adjuntos_contenedor_nomina_electronica(
    periodo,
    *,
    nombre_xml: str,
    cune: str,
    numero: str,
    totales: dict | None = None,
    trabajadores: list[dict] | None = None,
) -> list[tuple[str, bytes]] | None:

    return _adjuntos_pdf(
        nombre_xml,
        lambda: pdf_nomina_electronica(
            periodo,
            numero=numero,
            cune=cune,
            totales=totales,
            trabajadores=trabajadores,
        ),
    )
