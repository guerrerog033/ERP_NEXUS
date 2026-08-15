from __future__ import annotations

from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    ContextoFormato,
    _datos_empresa,
    formatos_combo,
    generar_html_desde_contexto,
)


def _datos_proveedor(
    factura,
    nombre_proveedor: str,
    *,
    correo_proveedor: str = "",
) -> dict:

    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    proveedor_id = getattr(
        factura,
        "proveedor_id",
        None,
    )

    proveedor = (
        TerceroServicio.obtener_por_id(
            proveedor_id,
        )
        if proveedor_id
        else None
    )

    if proveedor is not None:

        nit = str(
            proveedor.numero_documento
            or "",
        ).strip()

        if getattr(
            proveedor,
            "dv",
            None,
        ):

            nit = f"{nit}-{proveedor.dv}"

        nombre = (
            proveedor.razon_social
            or proveedor.nombre_completo
            or nombre_proveedor
        )

        contacto = (
            proveedor.nombre_comercial
            or proveedor.razon_social
            or proveedor.nombre_completo
            or nombre_proveedor
        )

        return {
            "nombre": nombre,
            "nit": nit,
            "contacto": contacto,
            "direccion": str(
                proveedor.direccion
                or "No aplica",
            ),
            "ciudad": str(
                proveedor.ciudad or "",
            ),
            "telefono": str(
                proveedor.telefono
                or proveedor.celular
                or "",
            ),
            "correo": str(
                proveedor.correo
                or correo_proveedor
                or "",
            ),
        }

    nit = str(
        getattr(
            factura,
            "nit_proveedor",
            "",
        )
        or "",
    )

    nombre = (
        getattr(
            factura,
            "razon_social_proveedor",
            "",
        )
        or nombre_proveedor
    )

    return {
        "nombre": nombre,
        "nit": nit,
        "contacto": nombre,
        "direccion": "No aplica",
        "ciudad": "",
        "telefono": "",
        "correo": correo_proveedor,
    }


def _info_adicional_factura_compra(
    factura,
) -> str:

    partes: list[str] = []

    if factura.cufe:

        partes.append(
            f"<p><strong>CUFE:</strong> {factura.cufe}</p>",
        )

    if factura.numero_proveedor:

        partes.append(
            f"<p><strong>Factura proveedor:</strong> "
            f"{factura.numero_proveedor}</p>",
        )

    partes.append(
        f"<p>Origen: {factura.origen} · "
        f"Estado: {factura.estado}</p>",
    )

    return "".join(
        partes,
    )


def _crear_contexto_factura_compra(
    factura,
    detalles,
    nombre_proveedor: str,
    *,
    correo_proveedor: str = "",
) -> ContextoFormato:

    resumen = {
        "subtotal": float(
            factura.subtotal or 0,
        ),
        "retefuente": float(
            factura.valor_retefuente or 0,
        ),
        "reteica": float(
            factura.valor_reteica or 0,
        ),
        "reteiva": float(
            factura.valor_reteiva or 0,
        ),
        "iva": float(
            factura.iva or 0,
        ),
        "total": float(
            factura.total or 0,
        ),
    }

    return ContextoFormato(
        cotizacion=factura,
        detalles=list(
            detalles,
        ),
        nombre_cliente=nombre_proveedor,
        resumen=resumen,
        empresa=_datos_empresa(),
        cliente=_datos_proveedor(
            factura,
            nombre_proveedor,
            correo_proveedor=correo_proveedor,
        ),
        fecha=(
            factura.fecha.strftime(
                "%d/%m/%Y",
            )
            if factura.fecha
            else ""
        ),
        observaciones=str(
            factura.observaciones or "",
        ).strip(),
        etiqueta_documento="FACTURA DE COMPRA",
        titulo_documento="Factura de compra",
        info_adicional=_info_adicional_factura_compra(
            factura,
        ),
        mostrar_imagenes=False,
        etiqueta_contraparte="Proveedor",
    )


def generar_html_factura_compra(
    factura,
    detalles,
    nombre_proveedor: str,
    *,
    documento_proveedor: str = "",
    correo_proveedor: str = "",
    formato: str | None = None,
) -> str:

    ctx = _crear_contexto_factura_compra(
        factura,
        detalles,
        nombre_proveedor,
        correo_proveedor=correo_proveedor,
    )

    if documento_proveedor and not ctx.cliente["nit"]:

        ctx.cliente["nit"] = documento_proveedor

    return generar_html_desde_contexto(
        ctx,
        formato,
    )


__all__ = [
    "formatos_combo",
    "generar_html_factura_compra",
]
