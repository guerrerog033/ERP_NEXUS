from __future__ import annotations

from types import SimpleNamespace

from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    ContextoFormato,
    _datos_empresa,
    formatos_combo,
    generar_html_desde_contexto,
)


def _datos_proveedor(
    orden,
    nombre_proveedor: str,
) -> dict:

    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    proveedor_id = getattr(
        orden,
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

    if proveedor is None:

        return {
            "nombre": nombre_proveedor,
            "nit": "",
            "contacto": nombre_proveedor,
            "direccion": "No aplica",
            "ciudad": "",
            "telefono": "",
            "correo": "",
        }

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
            proveedor.correo or "",
        ),
    }


def _detalles_para_formato(
    detalles,
) -> list:

    return [
        SimpleNamespace(
            producto_id=getattr(
                detalle,
                "producto_id",
                None,
            ),
            descripcion=detalle.descripcion,
            cantidad=float(
                detalle.cantidad or 0,
            ),
            precio_unitario=float(
                detalle.costo_unitario or 0,
            ),
            impuesto_id=None,
            total_linea=float(
                detalle.total_linea or 0,
            ),
        )
        for detalle in detalles
    ]


def _crear_contexto_orden_compra(
    orden,
    detalles,
    nombre_proveedor: str,
) -> ContextoFormato:

    resumen = {
        "subtotal": float(
            orden.subtotal or 0,
        ),
        "retefuente": 0,
        "reteica": 0,
        "reteiva": 0,
        "iva": 0,
        "total": float(
            orden.total or 0,
        ),
    }

    return ContextoFormato(
        cotizacion=orden,
        detalles=_detalles_para_formato(
            detalles,
        ),
        nombre_cliente=nombre_proveedor,
        resumen=resumen,
        empresa=_datos_empresa(),
        cliente=_datos_proveedor(
            orden,
            nombre_proveedor,
        ),
        fecha=(
            orden.fecha.strftime(
                "%d/%m/%Y",
            )
            if orden.fecha
            else ""
        ),
        observaciones=str(
            orden.observaciones or "",
        ).strip(),
        etiqueta_documento="ORDEN DE COMPRA",
        titulo_documento="Orden de compra",
        info_adicional=(
            "<p>Condiciones de entrega y pago según acuerdo "
            "comercial con el proveedor.</p>"
        ),
        mostrar_imagenes=False,
        etiqueta_contraparte="Proveedor",
    )


def generar_html_orden_compra(
    orden,
    detalles,
    nombre_proveedor: str,
    *,
    documento_proveedor: str = "",
    formato: str | None = None,
) -> str:

    ctx = _crear_contexto_orden_compra(
        orden,
        detalles,
        nombre_proveedor,
    )

    if documento_proveedor and not ctx.cliente["nit"]:

        ctx.cliente["nit"] = documento_proveedor

    return generar_html_desde_contexto(
        ctx,
        formato,
    )


__all__ = [
    "formatos_combo",
    "generar_html_orden_compra",
]
