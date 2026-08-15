from __future__ import annotations

from datetime import date, datetime

from aplicacion.framework.reportes.numero_letras import (
    numero_a_letras,
)
from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    _datos_cliente,
    _datos_empresa,
    _porcentaje_impuesto_id,
    _unidad_producto,
)
from aplicacion.nucleo.configuracion import Configuracion


def url_qr_dian(
    cufe: str,
) -> str:

    cufe_limpio = str(
        cufe or "",
    ).strip()

    if not cufe_limpio:

        return ""

    url_base = Configuracion.obtener(
        "dian",
        "url_catalogo_cufe",
    ) or (
        "https://catalogo-vpfe.dian.gov.co/document/searchqr"
    )

    separador = (
        "?"
        if "?"
        not in url_base
        else "&"
    )

    return (
        f"{url_base.rstrip('/')}"
        f"{separador}documentkey={cufe_limpio}"
    )


def empresa_reporte() -> dict:

    datos = _datos_empresa()

    return {
        **datos,
        "razon_social": (
            datos.get(
                "nombre",
                "",
            )
            or ""
        ),
    }


def _formatear_fecha(
    valor,
) -> str:

    if valor is None:

        return ""

    if isinstance(
        valor,
        datetime,
    ):

        return valor.strftime(
            "%d/%m/%Y %H:%M",
        )

    if isinstance(
        valor,
        date,
    ):

        return valor.strftime(
            "%d/%m/%Y",
        )

    return str(
        valor,
    )


def cliente_a_dto(
    documento,
    nombre_cliente: str,
) -> dict:

    datos = _datos_cliente(
        documento,
        nombre_cliente,
    )

    documento_cliente = str(
        datos.get(
            "nit",
            "",
        )
        or datos.get(
            "documento",
            "",
        )
        or "",
    ).strip()

    return {
        "nombre": (
            datos.get(
                "nombre",
            )
            or nombre_cliente
        ),
        "documento": documento_cliente,
        "direccion": datos.get(
            "direccion",
            "",
        )
        or "",
        "ciudad": datos.get(
            "ciudad",
            "",
        )
        or "",
        "telefono": datos.get(
            "telefono",
            "",
        )
        or "",
        "correo": datos.get(
            "correo",
            "",
        )
        or "",
    }


def _impuesto_linea(
    detalle,
    total_linea: float,
) -> float:

    impuesto_id = getattr(
        detalle,
        "impuesto_id",
        None,
    )

    porcentaje = _porcentaje_impuesto_id(
        impuesto_id,
    )

    if (
        porcentaje <= 0
        or total_linea <= 0
    ):

        return 0.0

    incluye_iva = bool(
        getattr(
            detalle,
            "precio_incluye_iva",
            False,
        ),
    )

    if incluye_iva:

        base = total_linea / (
            1
            + porcentaje / 100
        )

        return max(
            0.0,
            total_linea - base,
        )

    cantidad = float(
        getattr(
            detalle,
            "cantidad",
            0,
        )
        or 0,
    )

    precio = float(
        getattr(
            detalle,
            "precio_unitario",
            0,
        )
        or 0,
    )

    return cantidad * precio * (
        porcentaje / 100
    )


def items_desde_detalles(
    detalles,
) -> list[dict]:

    filas: list[dict] = []

    for indice, detalle in enumerate(
        detalles,
        start=1,
    ):

        cantidad = float(
            getattr(
                detalle,
                "cantidad",
                0,
            )
            or 0,
        )

        precio = float(
            getattr(
                detalle,
                "precio_unitario",
                0,
            )
            or 0,
        )

        total = float(
            getattr(
                detalle,
                "total_linea",
                0,
            )
            or cantidad * precio,
        )

        descuento = float(
            getattr(
                detalle,
                "descuento",
                0,
            )
            or getattr(
                detalle,
                "descuento_valor",
                0,
            )
            or 0,
        )

        filas.append(
            {
                "numero": indice,
                "descripcion": str(
                    getattr(
                        detalle,
                        "descripcion",
                        "",
                    )
                    or "",
                ),
                "cantidad": cantidad,
                "precio": precio,
                "descuento": descuento,
                "impuestos": _impuesto_linea(
                    detalle,
                    total,
                ),
                "total": total,
                "unidad": _unidad_producto(
                    getattr(
                        detalle,
                        "producto_id",
                        None,
                    ),
                ),
            },
        )

    return filas


def _descuento_documento(
    documento,
    subtotal: float,
    total: float,
) -> float:

    descuento = float(
        getattr(
            documento,
            "descuento_valor",
            0,
        )
        or 0,
    )

    if descuento > 0:

        return descuento

    impuestos = float(
        getattr(
            documento,
            "iva",
            0,
        )
        or 0,
    )

    if (
        subtotal > 0
        and total > 0
    ):

        calculado = subtotal + impuestos - total

        if calculado > 0:

            return calculado

    return 0.0


def _autorizacion_dian(
    documento,
) -> str:

    resolucion = Configuracion.obtener(
        "dian",
        "resolucion_numero",
    )

    if resolucion:

        return str(
            resolucion,
        )

    return str(
        getattr(
            documento,
            "consecutivo_dian",
            "",
        )
        or "",
    )


def factura_venta_a_dto(
    factura,
    detalles,
    nombre_cliente: str,
    *,
    electronica: bool = False,
) -> dict:

    subtotal = float(
        factura.subtotal or 0,
    )

    impuestos = float(
        factura.iva or 0,
    )

    total = float(
        factura.total or 0,
    )

    descuento = _descuento_documento(
        factura,
        subtotal,
        total,
    )

    fecha_generacion = _formatear_fecha(
        getattr(
            factura,
            "fecha_creacion",
            None,
        )
        or getattr(
            factura,
            "fecha",
            None,
        ),
    )

    if (
        getattr(
            factura,
            "fecha",
            None,
        )
        and not getattr(
            factura,
            "fecha_creacion",
            None,
        )
    ):

        fecha_generacion = _formatear_fecha(
            factura.fecha,
        )

    cufe = str(
        getattr(
            factura,
            "cufe",
            "",
        )
        or "",
    ).strip()

    return {
        "numero": str(
            factura.numero or "",
        ),
        "fecha_generacion": fecha_generacion,
        "fecha_vencimiento": _formatear_fecha(
            getattr(
                factura,
                "fecha_vencimiento",
                None,
            ),
        ),
        "forma_pago": str(
            getattr(
                factura,
                "estado_pago",
                "",
            )
            or "",
        ).replace(
            "_",
            " ",
        ).title(),
        "medio_pago": str(
            getattr(
                factura,
                "medio_pago",
                "",
            )
            or "",
        ),
        "subtotal": subtotal,
        "descuento": descuento,
        "impuestos": impuestos,
        "total": total,
        "total_letras": numero_a_letras(
            total,
        ),
        "cufe": cufe,
        "autorizacion": _autorizacion_dian(
            factura,
        ),
        "qr_url": url_qr_dian(
            cufe,
        )
        if electronica
        else "",
        "estado_dian": str(
            getattr(
                factura,
                "estado_dian",
                "",
            )
            or "",
        ),
        "cliente": cliente_a_dto(
            factura,
            nombre_cliente,
        ),
        "items": items_desde_detalles(
            detalles,
        ),
        "observaciones": str(
            getattr(
                factura,
                "observaciones",
                "",
            )
            or "",
        ).strip(),
    }


def cotizacion_a_dto(
    cotizacion,
    detalles,
    nombre_cliente: str,
) -> dict:

    subtotal = float(
        cotizacion.subtotal or 0,
    )

    total = float(
        cotizacion.total or 0,
    )

    impuestos = max(
        0.0,
        total - subtotal,
    )

    return {
        "numero": str(
            cotizacion.numero or "",
        ),
        "fecha": _formatear_fecha(
            getattr(
                cotizacion,
                "fecha",
                None,
            ),
        ),
        "fecha_vigencia": _formatear_fecha(
            getattr(
                cotizacion,
                "fecha_vigencia",
                None,
            ),
        ),
        "vendedor": str(
            getattr(
                cotizacion,
                "vendedor",
                "",
            )
            or "",
        ),
        "subtotal": subtotal,
        "descuento": _descuento_documento(
            cotizacion,
            subtotal,
            total,
        ),
        "impuestos": impuestos,
        "total": total,
        "total_letras": numero_a_letras(
            total,
        ),
        "cliente": cliente_a_dto(
            cotizacion,
            nombre_cliente,
        ),
        "items": items_desde_detalles(
            detalles,
        ),
        "observaciones": str(
            getattr(
                cotizacion,
                "observaciones",
                "",
            )
            or "",
        ).strip(),
    }


def pedido_a_dto(
    pedido,
    detalles,
    nombre_cliente: str,
) -> dict:

    subtotal = float(
        pedido.subtotal or 0,
    )

    total = float(
        pedido.total or 0,
    )

    impuestos = max(
        0.0,
        total - subtotal,
    )

    return {
        "numero": str(
            pedido.numero or "",
        ),
        "fecha": _formatear_fecha(
            getattr(
                pedido,
                "fecha",
                None,
            ),
        ),
        "estado": str(
            getattr(
                pedido,
                "estado",
                "",
            )
            or "",
        ),
        "vendedor": str(
            getattr(
                pedido,
                "vendedor",
                "",
            )
            or "",
        ),
        "subtotal": subtotal,
        "descuento": _descuento_documento(
            pedido,
            subtotal,
            total,
        ),
        "impuestos": impuestos,
        "total": total,
        "total_letras": numero_a_letras(
            total,
        ),
        "cliente": cliente_a_dto(
            pedido,
            nombre_cliente,
        ),
        "items": items_desde_detalles(
            detalles,
        ),
        "observaciones": str(
            getattr(
                pedido,
                "observaciones",
                "",
            )
            or "",
        ).strip(),
    }


def remision_a_dto(
    remision,
    detalles,
    nombre_cliente: str,
) -> dict:

    cliente = cliente_a_dto(
        remision,
        nombre_cliente,
    )

    return {
        "numero": str(
            remision.numero or "",
        ),
        "fecha": _formatear_fecha(
            getattr(
                remision,
                "fecha",
                None,
            ),
        ),
        "estado": str(
            getattr(
                remision,
                "estado",
                "",
            )
            or "",
        ),
        "vendedor": str(
            getattr(
                remision,
                "vendedor",
                "",
            )
            or "",
        ),
        "pedido_numero": _pedido_numero_remision(
            remision,
        ),
        "direccion_entrega": str(
            cliente.get(
                "direccion",
                "",
            )
            or "",
        ),
        "transportador": "",
        "vehiculo": "",
        "cliente": cliente,
        "items": _items_remision_logistica(
            remision,
            detalles,
        ),
        "observaciones": str(
            getattr(
                remision,
                "observaciones",
                "",
            )
            or "",
        ).strip(),
    }


def _pedido_numero_remision(
    remision,
) -> str:

    pedido_id = getattr(
        remision,
        "pedido_id",
        None,
    )

    if (
        not pedido_id
        or not isinstance(
            pedido_id,
            int,
        )
    ):

        return ""

    from aplicacion.base_datos.conexion import (
        SessionLocal,
    )
    from aplicacion.modulos.ventas.pedidos.modelos import (
        OrdenPedido,
    )

    db = SessionLocal()

    try:

        pedido = (
            db.query(
                OrdenPedido,
            )
            .filter(
                OrdenPedido.id
                == pedido_id,
            )
            .first()
        )

        if pedido is None:

            return str(
                pedido_id,
            )

        return str(
            pedido.numero or "",
        )

    finally:

        db.close()


def _items_remision_logistica(
    remision,
    detalles,
) -> list[dict]:

    pedido_cantidades: dict[
        tuple,
        float,
    ] = {}

    pedido_id = getattr(
        remision,
        "pedido_id",
        None,
    )

    if pedido_id and isinstance(
        pedido_id,
        int,
    ):

        from aplicacion.base_datos.conexion import (
            SessionLocal,
        )
        from aplicacion.modulos.ventas.pedidos.modelos import (
            OrdenPedidoDetalle,
        )

        db = SessionLocal()

        try:

            for linea in (
                db.query(
                    OrdenPedidoDetalle,
                )
                .filter(
                    OrdenPedidoDetalle.pedido_id
                    == pedido_id,
                )
                .all()
            ):

                clave = (
                    getattr(
                        linea,
                        "producto_id",
                        None,
                    ),
                    getattr(
                        linea,
                        "producto_variante_id",
                        None,
                    ),
                )

                pedido_cantidades[
                    clave
                ] = float(
                    linea.cantidad
                    or 0,
                )

        finally:

            db.close()

    filas: list[dict] = []

    for indice, detalle in enumerate(
        detalles,
        start=1,
    ):

        cantidad_entregada = float(
            getattr(
                detalle,
                "cantidad",
                0,
            )
            or 0,
        )

        clave = (
            getattr(
                detalle,
                "producto_id",
                None,
            ),
            getattr(
                detalle,
                "producto_variante_id",
                None,
            ),
        )

        cantidad_solicitada = pedido_cantidades.get(
            clave,
            cantidad_entregada,
        )

        filas.append(
            {
                "numero": indice,
                "descripcion": str(
                    getattr(
                        detalle,
                        "descripcion",
                        "",
                    )
                    or "",
                ),
                "cantidad": cantidad_entregada,
                "cantidad_solicitada": cantidad_solicitada,
                "cantidad_entregada": cantidad_entregada,
                "unidad": _unidad_producto(
                    getattr(
                        detalle,
                        "producto_id",
                        None,
                    ),
                ),
            },
        )

    return filas


def guia_remision_electronica_a_dto(
    guia,
    detalles,
    nombre_cliente: str,
    *,
    electronica: bool = False,
    cude: str | None = None,
) -> dict:

    cude_val = str(
        cude
        or getattr(
            guia,
            "cude",
            "",
        )
        or "",
    ).strip()

    observaciones_partes: list[str] = []

    for etiqueta, atributo in (
        (
            "Remisión",
            "remision_numero",
        ),
        (
            "Origen",
            "direccion_origen",
        ),
        (
            "Destino",
            "direccion_destino",
        ),
        (
            "Conductor",
            "conductor",
        ),
        (
            "Vehículo",
            "vehiculo",
        ),
        (
            "Placa",
            "placa",
        ),
        (
            "Transportadora",
            "transportadora",
        ),
    ):

        valor = str(
            getattr(
                guia,
                atributo,
                "",
            )
            or "",
        ).strip()

        if valor:

            observaciones_partes.append(
                f"{etiqueta}: {valor}",
            )

    observaciones_base = str(
        getattr(
            guia,
            "observaciones",
            "",
        )
        or "",
    ).strip()

    if observaciones_base:

        observaciones_partes.append(
            observaciones_base,
        )

    dto = {
        "numero": str(
            guia.numero or "",
        ),
        "fecha": _formatear_fecha(
            getattr(
                guia,
                "fecha",
                None,
            ),
        ),
        "estado": str(
            getattr(
                guia,
                "estado",
                "",
            )
            or "",
        ),
        "vendedor": "",
        "cliente": cliente_a_dto(
            guia,
            nombre_cliente,
        ),
        "items": [
            {
                "numero": item[
                    "numero"
                ],
                "descripcion": item[
                    "descripcion"
                ],
                "cantidad": item[
                    "cantidad"
                ],
                "unidad": item.get(
                    "unidad",
                    "UND",
                ),
            }
            for item in items_desde_detalles(
                detalles,
            )
        ],
        "observaciones": "\n".join(
            observaciones_partes,
        ),
    }

    if electronica:

        dto.update(
            {
                "cude": cude_val,
                "cufe": cude_val,
                "qr_url": url_qr_dian(
                    cude_val,
                ),
                "autorizacion": _autorizacion_dian(
                    guia,
                ),
                "estado_dian": str(
                    getattr(
                        guia,
                        "estado_dian",
                        "",
                    )
                    or "",
                ),
            },
        )

    return dto


def documento_soporte_a_dto(
    documento,
    detalles,
    nombre_proveedor: str = "",
    *,
    documento_proveedor: str = "",
    correo_proveedor: str = "",
    cuds: str | None = None,
) -> dict:

    if not nombre_proveedor:

        nombre_proveedor = str(
            getattr(
                documento,
                "razon_social_proveedor",
                "",
            )
            or "",
        ).strip()

    if not documento_proveedor:

        documento_proveedor = str(
            getattr(
                documento,
                "nit_proveedor",
                "",
            )
            or "",
        ).strip()

    subtotal = float(
        documento.subtotal or 0,
    )

    impuestos = float(
        documento.iva or 0,
    )

    total = float(
        documento.total or 0,
    )

    cuds_val = str(
        cuds
        or getattr(
            documento,
            "cuds",
            "",
        )
        or "",
    ).strip()

    info_adicional: list[str] = []

    if cuds_val:

        info_adicional.append(
            f"CUDS: {cuds_val}",
        )

    info_adicional.append(
        (
            f"Estado: {getattr(documento, 'estado', '')} · "
            f"DIAN: {getattr(documento, 'estado_dian', '') or '—'}"
        ),
    )

    return {
        "numero": str(
            documento.numero or "",
        ),
        "fecha": _formatear_fecha(
            getattr(
                documento,
                "fecha",
                None,
            ),
        ),
        "estado": str(
            getattr(
                documento,
                "estado",
                "",
            )
            or "",
        ),
        "titulo_documento": (
            "DOCUMENTO SOPORTE ELECTRÓNICO"
        ),
        "subtotal": subtotal,
        "descuento": _descuento_documento(
            documento,
            subtotal,
            total,
        ),
        "impuestos": impuestos,
        "total": total,
        "total_letras": numero_a_letras(
            total,
        ),
        "proveedor": _proveedor_desde_documento(
            documento,
            nombre_proveedor,
            documento_proveedor=documento_proveedor,
            correo_proveedor=correo_proveedor,
        ),
        "items": items_compra_desde_detalles(
            detalles,
        ),
        "observaciones": str(
            getattr(
                documento,
                "observaciones",
                "",
            )
            or "",
        ).strip(),
        "info_adicional": info_adicional,
    }


def proveedor_a_dto(
    *,
    nombre: str,
    documento: str = "",
    direccion: str = "",
    ciudad: str = "",
    telefono: str = "",
    correo: str = "",
) -> dict:

    return {
        "nombre": nombre,
        "documento": documento,
        "direccion": direccion,
        "ciudad": ciudad,
        "telefono": telefono,
        "correo": correo,
    }


def items_compra_desde_detalles(
    detalles,
) -> list[dict]:

    filas: list[dict] = []

    for indice, detalle in enumerate(
        detalles,
        start=1,
    ):

        cantidad = float(
            getattr(
                detalle,
                "cantidad",
                0,
            )
            or 0,
        )

        precio = float(
            getattr(
                detalle,
                "precio_unitario",
                0,
            )
            or getattr(
                detalle,
                "costo_unitario",
                0,
            )
            or 0,
        )

        total = float(
            getattr(
                detalle,
                "total_linea",
                0,
            )
            or cantidad * precio,
        )

        filas.append(
            {
                "numero": indice,
                "descripcion": str(
                    getattr(
                        detalle,
                        "descripcion",
                        "",
                    )
                    or "",
                ),
                "cantidad": cantidad,
                "precio": precio,
                "descuento": 0.0,
                "impuestos": _impuesto_linea(
                    detalle,
                    total,
                ),
                "total": total,
            },
        )

    return filas


def items_orden_compra_desde_detalles(
    detalles,
) -> list[dict]:

    filas: list[dict] = []

    for indice, detalle in enumerate(
        detalles,
        start=1,
    ):

        cantidad = float(
            getattr(
                detalle,
                "cantidad",
                0,
            )
            or 0,
        )

        recibida = float(
            getattr(
                detalle,
                "cantidad_recibida",
                0,
            )
            or 0,
        )

        costo = float(
            getattr(
                detalle,
                "costo_unitario",
                0,
            )
            or 0,
        )

        total = float(
            getattr(
                detalle,
                "total_linea",
                0,
            )
            or cantidad * costo,
        )

        filas.append(
            {
                "numero": indice,
                "descripcion": str(
                    getattr(
                        detalle,
                        "descripcion",
                        "",
                    )
                    or "",
                ),
                "cantidad": cantidad,
                "recibida": recibida,
                "costo": costo,
                "total": total,
            },
        )

    return filas


def _proveedor_desde_documento(
    documento,
    nombre_proveedor: str,
    *,
    documento_proveedor: str = "",
    correo_proveedor: str = "",
) -> dict:

    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    proveedor_id = getattr(
        documento,
        "proveedor_id",
        None,
    )

    if proveedor_id:

        proveedor = TerceroServicio.obtener_por_id(
            proveedor_id,
        )

        if proveedor is not None:

            documento_txt = str(
                proveedor.numero_documento
                or "",
            ).strip()

            if getattr(
                proveedor,
                "dv",
                None,
            ):

                documento_txt = (
                    f"{documento_txt}-{proveedor.dv}"
                )

            nombre = (
                proveedor.razon_social
                or proveedor.nombre_completo
                or nombre_proveedor
            )

            return proveedor_a_dto(
                nombre=nombre,
                documento=documento_txt
                or documento_proveedor,
                direccion=str(
                    proveedor.direccion
                    or "",
                ),
                ciudad=str(
                    proveedor.ciudad
                    or "",
                ),
                telefono=str(
                    proveedor.telefono
                    or proveedor.celular
                    or "",
                ),
                correo=str(
                    proveedor.correo
                    or correo_proveedor
                    or "",
                ),
            )

    documento_txt = documento_proveedor

    if (
        not documento_txt
        and getattr(
            documento,
            "nit_proveedor",
            None,
        )
    ):

        documento_txt = str(
            documento.nit_proveedor,
        )

    return proveedor_a_dto(
        nombre=(
            getattr(
                documento,
                "razon_social_proveedor",
                None,
            )
            or nombre_proveedor
        ),
        documento=documento_txt,
        correo=correo_proveedor,
    )


def factura_compra_a_dto(
    factura,
    detalles,
    nombre_proveedor: str,
    *,
    documento_proveedor: str = "",
    correo_proveedor: str = "",
) -> dict:

    subtotal = float(
        factura.subtotal or 0,
    )

    impuestos = float(
        factura.iva or 0,
    )

    total = float(
        factura.total or 0,
    )

    info_adicional: list[str] = []

    cufe = str(
        getattr(
            factura,
            "cufe",
            "",
        )
        or "",
    ).strip()

    if cufe:

        info_adicional.append(
            f"CUFE: {cufe}",
        )

    numero_proveedor = str(
        getattr(
            factura,
            "numero_proveedor",
            "",
        )
        or "",
    ).strip()

    if numero_proveedor:

        info_adicional.append(
            f"Factura proveedor: {numero_proveedor}",
        )

    info_adicional.append(
        (
            f"Origen: {getattr(factura, 'origen', '')} · "
            f"Estado: {getattr(factura, 'estado', '')}"
        ),
    )

    return {
        "numero": str(
            factura.numero or "",
        ),
        "fecha": _formatear_fecha(
            getattr(
                factura,
                "fecha",
                None,
            ),
        ),
        "estado": str(
            getattr(
                factura,
                "estado",
                "",
            )
            or "",
        ),
        "subtotal": subtotal,
        "descuento": _descuento_documento(
            factura,
            subtotal,
            total,
        ),
        "impuestos": impuestos,
        "total": total,
        "total_letras": numero_a_letras(
            total,
        ),
        "proveedor": _proveedor_desde_documento(
            factura,
            nombre_proveedor,
            documento_proveedor=documento_proveedor,
            correo_proveedor=correo_proveedor,
        ),
        "items": items_compra_desde_detalles(
            detalles,
        ),
        "observaciones": str(
            getattr(
                factura,
                "observaciones",
                "",
            )
            or "",
        ).strip(),
        "info_adicional": info_adicional,
    }


def orden_compra_a_dto(
    orden,
    detalles,
    nombre_proveedor: str,
    *,
    documento_proveedor: str = "",
) -> dict:

    subtotal = float(
        orden.subtotal or 0,
    )

    total = float(
        orden.total or 0,
    )

    return {
        "numero": str(
            orden.numero or "",
        ),
        "fecha": _formatear_fecha(
            getattr(
                orden,
                "fecha",
                None,
            ),
        ),
        "estado": str(
            getattr(
                orden,
                "estado",
                "",
            )
            or "",
        ),
        "subtotal": subtotal,
        "total": total,
        "total_letras": numero_a_letras(
            total,
        ),
        "proveedor": _proveedor_desde_documento(
            orden,
            nombre_proveedor,
            documento_proveedor=documento_proveedor,
        ),
        "items": items_orden_compra_desde_detalles(
            detalles,
        ),
        "observaciones": str(
            getattr(
                orden,
                "observaciones",
                "",
            )
            or "",
        ).strip(),
    }


def _lineas_recibo_caja(
    detalles,
) -> list[dict]:

    from aplicacion.base_datos.conexion import (
        SessionLocal,
    )
    from aplicacion.modulos.ventas.facturas.modelos import (
        FacturaVenta,
    )

    db = SessionLocal()
    filas: list[dict] = []

    try:

        for indice, detalle in enumerate(
            detalles,
            start=1,
        ):

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
                if factura
                else str(
                    detalle.factura_venta_id,
                )
            )

            valor_aplicado = float(
                detalle.valor_aplicado
                or 0,
            )

            saldo_restante = float(
                getattr(
                    factura,
                    "saldo_pendiente",
                    0,
                )
                or 0,
            ) if factura else 0.0

            saldo_anterior = saldo_restante + valor_aplicado

            filas.append(
                {
                    "numero": indice,
                    "documento": f"Factura {numero}",
                    "valor": valor_aplicado,
                    "valor_aplicado": valor_aplicado,
                    "saldo_anterior": saldo_anterior,
                    "saldo_restante": saldo_restante,
                },
            )

    finally:

        db.close()

    return filas


def recibo_caja_a_dto(
    recibo,
    *,
    nombre_cliente: str,
    documento_cliente: str = "",
    correo_cliente: str = "",
) -> dict:

    total = float(
        recibo.valor_total or 0,
    )

    detalles = getattr(
        recibo,
        "detalles",
        [],
    ) or []

    return {
        "numero": str(
            recibo.numero or "",
        ),
        "fecha": _formatear_fecha(
            getattr(
                recibo,
                "fecha",
                None,
            ),
        ),
        "estado": str(
            getattr(
                recibo,
                "estado",
                "",
            )
            or "",
        ),
        "forma_pago": str(
            getattr(
                recibo,
                "forma_pago",
                "",
            )
            or "",
        ).replace(
            "_",
            " ",
        ).title(),
        "valor": total,
        "total_letras": numero_a_letras(
            total,
        ),
        "cliente": proveedor_a_dto(
            nombre=nombre_cliente,
            documento=documento_cliente,
            correo=correo_cliente,
        ),
        "lineas": _lineas_recibo_caja(
            detalles,
        ),
        "concepto": str(
            getattr(
                recibo,
                "observaciones",
                "",
            )
            or "",
        ).strip(),
        "observaciones": str(
            getattr(
                recibo,
                "observaciones",
                "",
            )
            or "",
        ).strip(),
    }


def _lineas_comprobante_egreso(
    detalles,
) -> list[dict]:

    from aplicacion.base_datos.conexion import (
        SessionLocal,
    )
    from aplicacion.modulos.compras.facturas.modelos import (
        FacturaCompra,
    )

    db = SessionLocal()
    filas: list[dict] = []

    try:

        for indice, detalle in enumerate(
            detalles,
            start=1,
        ):

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
                if factura
                else str(
                    detalle.factura_compra_id,
                )
            )

            valor_aplicado = float(
                detalle.valor_aplicado
                or 0,
            )

            saldo_restante = float(
                getattr(
                    factura,
                    "saldo_pendiente",
                    0,
                )
                or 0,
            ) if factura else 0.0

            saldo_anterior = saldo_restante + valor_aplicado

            filas.append(
                {
                    "numero": indice,
                    "documento": f"FC {numero}",
                    "valor": valor_aplicado,
                    "valor_aplicado": valor_aplicado,
                    "saldo_anterior": saldo_anterior,
                    "saldo_restante": saldo_restante,
                },
            )

    finally:

        db.close()

    return filas


def comprobante_egreso_a_dto(
    comprobante,
    *,
    nombre_proveedor: str,
    documento_proveedor: str = "",
) -> dict:

    total = float(
        comprobante.valor_total or 0,
    )

    detalles = getattr(
        comprobante,
        "detalles",
        [],
    ) or []

    return {
        "numero": str(
            comprobante.numero or "",
        ),
        "fecha": _formatear_fecha(
            getattr(
                comprobante,
                "fecha",
                None,
            ),
        ),
        "estado": str(
            getattr(
                comprobante,
                "estado",
                "",
            )
            or "",
        ),
        "forma_pago": str(
            getattr(
                comprobante,
                "forma_pago",
                "",
            )
            or "",
        ).replace(
            "_",
            " ",
        ).title(),
        "valor": total,
        "total_letras": numero_a_letras(
            total,
        ),
        "beneficiario": proveedor_a_dto(
            nombre=nombre_proveedor,
            documento=documento_proveedor,
        ),
        "lineas": _lineas_comprobante_egreso(
            detalles,
        ),
        "concepto": str(
            getattr(
                comprobante,
                "observaciones",
                "",
            )
            or "",
        ).strip(),
        "observaciones": str(
            getattr(
                comprobante,
                "observaciones",
                "",
            )
            or "",
        ).strip(),
    }


def _observaciones_nota_venta(
    nota,
    *,
    factura_numero: str = "",
) -> str:

    partes: list[str] = []

    motivo = str(
        getattr(
            nota,
            "motivo",
            "",
        )
        or "",
    ).strip()

    if motivo:

        partes.append(
            f"Motivo: {motivo}",
        )

    referencia = str(
        factura_numero
        or getattr(
            nota,
            "factura_id",
            "",
        )
        or "",
    ).strip()

    if referencia:

        partes.append(
            f"Factura referencia: {referencia}",
        )

    cufe_factura = str(
        getattr(
            nota,
            "factura_cufe",
            "",
        )
        or "",
    ).strip()

    if cufe_factura:

        partes.append(
            f"CUFE factura: {cufe_factura}",
        )

    observaciones = str(
        getattr(
            nota,
            "observaciones",
            "",
        )
        or "",
    ).strip()

    if observaciones:

        partes.append(
            observaciones,
        )

    return "\n".join(
        partes,
    )


def _nota_venta_a_dto(
    nota,
    detalles,
    nombre_cliente: str,
    *,
    electronica: bool = False,
    factura_numero: str = "",
) -> dict:

    subtotal = float(
        nota.subtotal or 0,
    )

    impuestos = float(
        nota.iva or 0,
    )

    total = float(
        nota.total or 0,
    )

    descuento = _descuento_documento(
        nota,
        subtotal,
        total,
    )

    fecha_generacion = _formatear_fecha(
        getattr(
            nota,
            "fecha_creacion",
            None,
        )
        or getattr(
            nota,
            "fecha",
            None,
        ),
    )

    cufe = str(
        getattr(
            nota,
            "cufe",
            "",
        )
        or "",
    ).strip()

    return {
        "numero": str(
            nota.numero or "",
        ),
        "fecha_generacion": fecha_generacion,
        "fecha_vencimiento": "",
        "forma_pago": "",
        "medio_pago": "",
        "subtotal": subtotal,
        "descuento": descuento,
        "impuestos": impuestos,
        "total": total,
        "total_letras": numero_a_letras(
            total,
        ),
        "cufe": cufe,
        "autorizacion": _autorizacion_dian(
            nota,
        ),
        "qr_url": url_qr_dian(
            cufe,
        )
        if electronica
        else "",
        "estado_dian": str(
            getattr(
                nota,
                "estado_dian",
                "",
            )
            or "",
        ),
        "motivo": str(
            getattr(
                nota,
                "motivo",
                "",
            )
            or "",
        ).strip(),
        "factura_referencia": str(
            factura_numero
            or "",
        ).strip(),
        "factura_cufe": str(
            getattr(
                nota,
                "factura_cufe",
                "",
            )
            or "",
        ).strip(),
        "cliente": cliente_a_dto(
            nota,
            nombre_cliente,
        ),
        "items": items_desde_detalles(
            detalles,
        ),
        "observaciones": str(
            getattr(
                nota,
                "observaciones",
                "",
            )
            or "",
        ).strip(),
    }


def nota_credito_venta_a_dto(
    nota,
    detalles,
    nombre_cliente: str,
    *,
    electronica: bool = False,
    factura_numero: str = "",
) -> dict:

    return _nota_venta_a_dto(
        nota,
        detalles,
        nombre_cliente,
        electronica=electronica,
        factura_numero=factura_numero,
    )


def nota_debito_venta_a_dto(
    nota,
    detalles,
    nombre_cliente: str,
    *,
    electronica: bool = False,
    factura_numero: str = "",
) -> dict:

    return _nota_venta_a_dto(
        nota,
        detalles,
        nombre_cliente,
        electronica=electronica,
        factura_numero=factura_numero,
    )
