from __future__ import annotations

from types import SimpleNamespace

from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    ContextoFormato,
    _datos_empresa,
    formatos_combo,
    generar_html_desde_contexto,
)


def _detalles_para_formato(
    recibo,
    detalles,
) -> list:

    if not detalles:

        valor = float(
            recibo.valor_total or 0,
        )

        if valor <= 0:

            return []

        return [
            SimpleNamespace(
                producto_id=None,
                descripcion="Abono / anticipo sin factura",
                cantidad=1,
                precio_unitario=valor,
                impuesto_id=None,
                total_linea=valor,
            ),
        ]

    from aplicacion.base_datos.conexion import (
        SessionLocal,
    )
    from aplicacion.modulos.ventas.facturas.modelos import (
        FacturaVenta,
    )

    db = SessionLocal()

    try:

        adaptados = []

        for detalle in detalles:

            factura = (
                db.query(
                    FacturaVenta,
                )
                .filter(
                    FacturaVenta.id
                    == detalle.factura_venta_id,
                )
                .first()
            )

            numero = (
                factura.numero
                if factura is not None
                else str(
                    detalle.factura_venta_id,
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


def _datos_cliente_recibo(
    recibo,
    nombre_cliente: str,
    *,
    documento_cliente: str = "",
    correo_cliente: str = "",
) -> dict:

    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    cliente_id = getattr(
        recibo,
        "cliente_id",
        None,
    )

    cliente = (
        TerceroServicio.obtener_por_id(
            cliente_id,
        )
        if cliente_id
        else None
    )

    if cliente is None:

        return {
            "nombre": nombre_cliente,
            "nit": documento_cliente,
            "contacto": nombre_cliente,
            "direccion": "No aplica",
            "ciudad": "",
            "telefono": "",
            "correo": correo_cliente,
        }

    nit = str(
        cliente.numero_documento
        or "",
    ).strip()

    if getattr(
        cliente,
        "dv",
        None,
    ):

        nit = f"{nit}-{cliente.dv}"

    nombre = (
        cliente.razon_social
        or cliente.nombre_completo
        or nombre_cliente
    )

    contacto = (
        cliente.nombre_comercial
        or cliente.razon_social
        or cliente.nombre_completo
        or nombre_cliente
    )

    return {
        "nombre": nombre,
        "nit": nit or documento_cliente,
        "contacto": contacto,
        "direccion": str(
            cliente.direccion
            or "No aplica",
        ),
        "ciudad": str(
            cliente.ciudad or "",
        ),
        "telefono": str(
            cliente.telefono
            or cliente.celular
            or "",
        ),
        "correo": str(
            cliente.correo
            or correo_cliente
            or "",
        ),
    }


def _crear_contexto_recibo(
    recibo,
    nombre_cliente: str,
    *,
    documento_cliente: str = "",
    correo_cliente: str = "",
) -> ContextoFormato:

    total = float(
        recibo.valor_total or 0,
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
            recibo,
            "forma_pago",
            "",
        )
        or "",
    ).replace(
        "_",
        " ",
    ).title()

    return ContextoFormato(
        cotizacion=recibo,
        detalles=_detalles_para_formato(
            recibo,
            recibo.detalles or [],
        ),
        nombre_cliente=nombre_cliente,
        resumen=resumen,
        empresa=_datos_empresa(),
        cliente=_datos_cliente_recibo(
            recibo,
            nombre_cliente,
            documento_cliente=documento_cliente,
            correo_cliente=correo_cliente,
        ),
        fecha=(
            recibo.fecha.strftime(
                "%d/%m/%Y",
            )
            if recibo.fecha
            else ""
        ),
        observaciones=str(
            recibo.observaciones or "",
        ).strip(),
        etiqueta_documento="RECIBO DE CAJA",
        titulo_documento="Recibo de caja",
        info_adicional=(
            f"<p><strong>Forma de pago:</strong> "
            f"{forma_pago}</p>"
        ),
        mostrar_imagenes=False,
        etiqueta_contraparte="Recibimos de",
    )


def generar_html_recibo(
    recibo,
    *,
    nombre_cliente: str,
    documento_cliente: str = "",
    correo_cliente: str = "",
    formato: str | None = None,
) -> str:

    ctx = _crear_contexto_recibo(
        recibo,
        nombre_cliente,
        documento_cliente=documento_cliente,
        correo_cliente=correo_cliente,
    )

    return generar_html_desde_contexto(
        ctx,
        formato,
    )


__all__ = [
    "formatos_combo",
    "generar_html_recibo",
]
