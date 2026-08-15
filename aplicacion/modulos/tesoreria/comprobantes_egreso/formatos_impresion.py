from __future__ import annotations

from types import SimpleNamespace

from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    ContextoFormato,
    _datos_empresa,
    formatos_combo,
    generar_html_desde_contexto,
)


def _detalles_para_formato(
    comprobante,
    detalles,
) -> list:

    if not detalles:

        valor = float(
            comprobante.valor_total or 0,
        )

        if valor <= 0:

            return []

        return [
            SimpleNamespace(
                producto_id=None,
                descripcion="Anticipo / abono sin factura",
                cantidad=1,
                precio_unitario=valor,
                impuesto_id=None,
                total_linea=valor,
            ),
        ]

    from aplicacion.base_datos.conexion import (
        SessionLocal,
    )
    from aplicacion.modulos.compras.facturas.modelos import (
        FacturaCompra,
    )

    db = SessionLocal()

    try:

        adaptados = []

        for detalle in detalles:

            factura = (
                db.query(
                    FacturaCompra,
                )
                .filter(
                    FacturaCompra.id
                    == detalle.factura_compra_id,
                )
                .first()
            )

            numero = (
                factura.numero
                if factura is not None
                else str(
                    detalle.factura_compra_id,
                )
            )

            valor = float(
                detalle.valor_aplicado or 0,
            )

            adaptados.append(
                SimpleNamespace(
                    producto_id=None,
                    descripcion=(
                        f"Abono a factura {numero}"
                    ),
                    cantidad=1,
                    precio_unitario=valor,
                    impuesto_id=None,
                    total_linea=valor,
                ),
            )

        return adaptados

    finally:

        db.close()


def _datos_proveedor_comprobante(
    comprobante,
    nombre_proveedor: str,
    *,
    documento_proveedor: str = "",
) -> dict:

    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    proveedor_id = getattr(
        comprobante,
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
            "nit": documento_proveedor,
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
        "nit": nit or documento_proveedor,
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


def _crear_contexto_comprobante(
    comprobante,
    nombre_proveedor: str,
    *,
    documento_proveedor: str = "",
) -> ContextoFormato:

    total = float(
        comprobante.valor_total or 0,
    )

    resumen = {
        "subtotal": total,
        "retefuente": 0,
        "reteica": 0,
        "reteiva": 0,
        "iva": 0,
        "total": total,
    }

    forma_pago = str(
        getattr(
            comprobante,
            "forma_pago",
            "",
        )
        or "",
    ).replace(
        "_",
        " ",
    ).title()

    return ContextoFormato(
        cotizacion=comprobante,
        detalles=_detalles_para_formato(
            comprobante,
            comprobante.detalles or [],
        ),
        nombre_cliente=nombre_proveedor,
        resumen=resumen,
        empresa=_datos_empresa(),
        cliente=_datos_proveedor_comprobante(
            comprobante,
            nombre_proveedor,
            documento_proveedor=documento_proveedor,
        ),
        fecha=(
            comprobante.fecha.strftime(
                "%d/%m/%Y",
            )
            if comprobante.fecha
            else ""
        ),
        observaciones=str(
            comprobante.observaciones or "",
        ).strip(),
        etiqueta_documento="COMPROBANTE DE EGRESO",
        titulo_documento="Comprobante de egreso",
        info_adicional=(
            f"<p><strong>Forma de pago:</strong> "
            f"{forma_pago}</p>"
            "<p>Elaboró ________  Revisó ________  "
            "Aprobó ________  Recibí ________</p>"
        ),
        mostrar_imagenes=False,
        etiqueta_contraparte="Pagado a",
    )


def generar_html_comprobante(
    comprobante,
    *,
    nombre_proveedor: str,
    documento_proveedor: str = "",
    formato: str | None = None,
) -> str:

    ctx = _crear_contexto_comprobante(
        comprobante,
        nombre_proveedor,
        documento_proveedor=documento_proveedor,
    )

    return generar_html_desde_contexto(
        ctx,
        formato,
    )


__all__ = [
    "formatos_combo",
    "generar_html_comprobante",
]
