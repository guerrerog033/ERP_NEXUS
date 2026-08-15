from __future__ import annotations

from datetime import date

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.maestros.impuestos.modelos import Impuesto
from aplicacion.maestros.productos.modelos import (
    Producto,
    ProductoVariante,
)
from aplicacion.maestros.terceros.modelos import Tercero
from aplicacion.modulos.compras.facturas.modelos import (
    FacturaCompra,
)
from aplicacion.modulos.ventas.cotizaciones.modelos import (
    Cotizacion,
)
from aplicacion.modulos.ventas.facturas.modelos import (
    FacturaVenta,
)
from aplicacion.modulos.ventas.pedidos.modelos import (
    OrdenPedido,
)
from aplicacion.modulos.ventas.remisiones.modelos import (
    RemisionVenta,
)
from aplicacion.modulos.inventario.modelos import (
    Bodega,
    ExistenciaBodega,
)
from aplicacion.modulos.cartera.servicios import (
    ServicioCartera,
)


class ServicioReportes:

    @classmethod
    def ventas_por_periodo(
        cls,
        *,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[dict]:

        db = SessionLocal()

        try:

            consulta = (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.activo.is_(
                        True,
                    ),
                    FacturaVenta.contabilizado.is_(
                        True,
                    ),
                )
            )

            if fecha_desde is not None:

                consulta = consulta.filter(
                    FacturaVenta.fecha
                    >= fecha_desde,
                )

            if fecha_hasta is not None:

                consulta = consulta.filter(
                    FacturaVenta.fecha
                    <= fecha_hasta,
                )

            facturas = consulta.order_by(
                FacturaVenta.fecha.desc(),
                FacturaVenta.numero.desc(),
            ).all()

            cliente_ids = {
                factura.cliente_id
                for factura in facturas
            }

            clientes = {

                tercero.id: tercero

                for tercero in (
                    db.query(Tercero)
                    .filter(
                        Tercero.id.in_(
                            cliente_ids,
                        ),
                    )
                    .all()
                )

            } if cliente_ids else {}

            filas: list[dict] = []

            for factura in facturas:

                cliente = clientes.get(
                    factura.cliente_id,
                )

                nombre_cliente = ""

                if cliente is not None:

                    nombre_cliente = (
                        cliente.nombre_comercial
                        or cliente.razon_social
                        or cliente.nombre_completo
                        or ""
                    ).strip()

                filas.append(
                    {
                        "numero": factura.numero,
                        "fecha": factura.fecha,
                        "cliente": nombre_cliente,
                        "subtotal": float(
                            factura.subtotal or 0,
                        ),
                        "iva": float(
                            factura.iva or 0,
                        ),
                        "total": float(
                            factura.total or 0,
                        ),
                        "saldo": float(
                            factura.saldo_pendiente
                            or 0,
                        ),
                        "estado_pago": (
                            factura.estado_pago
                            or ""
                        ),
                    },
                )

            return filas

        finally:

            db.close()

    @classmethod
    def compras_por_periodo(
        cls,
        *,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[dict]:

        db = SessionLocal()

        try:

            consulta = (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.activo.is_(
                        True,
                    ),
                    FacturaCompra.contabilizado.is_(
                        True,
                    ),
                )
            )

            if fecha_desde is not None:

                consulta = consulta.filter(
                    FacturaCompra.fecha
                    >= fecha_desde,
                )

            if fecha_hasta is not None:

                consulta = consulta.filter(
                    FacturaCompra.fecha
                    <= fecha_hasta,
                )

            facturas = consulta.order_by(
                FacturaCompra.fecha.desc(),
                FacturaCompra.numero.desc(),
            ).all()

            filas: list[dict] = []

            for factura in facturas:

                filas.append(
                    {
                        "numero": factura.numero,
                        "fecha": factura.fecha,
                        "proveedor": (
                            factura.razon_social_proveedor
                            or ""
                        ),
                        "numero_proveedor": (
                            factura.numero_proveedor
                            or ""
                        ),
                        "subtotal": float(
                            factura.subtotal or 0,
                        ),
                        "iva": float(
                            factura.iva or 0,
                        ),
                        "total": float(
                            factura.total or 0,
                        ),
                        "saldo": float(
                            factura.saldo_pendiente
                            or 0,
                        ),
                        "estado_pago": (
                            factura.estado_pago
                            or ""
                        ),
                    },
                )

            return filas

        finally:

            db.close()

    @classmethod
    def existencias_inventario(
        cls,
        *,
        solo_con_stock: bool = False,
        bodega_id: int | None = None,
    ) -> list[dict]:

        db = SessionLocal()

        try:

            if bodega_id is not None:

                return cls._existencias_por_bodega(
                    db,
                    bodega_id=bodega_id,
                    solo_con_stock=solo_con_stock,
                )

            productos = (
                db.query(Producto)
                .filter(
                    Producto.activo.is_(
                        True,
                    ),
                    Producto.tipo != "servicio",
                )
                .order_by(
                    Producto.codigo,
                )
                .all()
            )

            producto_ids = [
                producto.id
                for producto in productos
            ]

            variantes_por_producto: dict[
                int,
                list[ProductoVariante],
            ] = {}

            if producto_ids:

                for variante in (
                    db.query(ProductoVariante)
                    .filter(
                        ProductoVariante.producto_id.in_(
                            producto_ids,
                        ),
                        ProductoVariante.activo.is_(
                            True,
                        ),
                    )
                    .order_by(
                        ProductoVariante.codigo,
                    )
                    .all()
                ):

                    variantes_por_producto.setdefault(
                        variante.producto_id,
                        [],
                    ).append(
                        variante,
                    )

            filas: list[dict] = []

            for producto in productos:

                variantes = variantes_por_producto.get(
                    producto.id,
                    [],
                )

                if variantes:

                    for variante in variantes:

                        existencia = float(
                            variante.existencia
                            or 0,
                        )

                        if (
                            solo_con_stock
                            and existencia <= 0
                        ):

                            continue

                        filas.append(
                            {
                                "codigo": (
                                    variante.codigo
                                ),
                                "producto": (
                                    producto.nombre
                                ),
                                "variante": (
                                    variante.talla
                                    or variante.color
                                    or ""
                                ),
                                "existencia": existencia,
                                "costo": float(
                                    variante.costo
                                    or producto.costo
                                    or 0,
                                ),
                            },
                        )

                    continue

                existencia = float(
                    producto.existencia or 0,
                )

                if (
                    solo_con_stock
                    and existencia <= 0
                ):

                    continue

                filas.append(
                    {
                        "codigo": producto.codigo,
                        "producto": producto.nombre,
                        "variante": "",
                        "existencia": existencia,
                        "costo": float(
                            producto.costo or 0,
                        ),
                    },
                )

            return filas

        finally:

            db.close()

    @classmethod
    def _existencias_por_bodega(
        cls,
        db,
        *,
        bodega_id: int,
        solo_con_stock: bool,
    ) -> list[dict]:

        bodega = (
            db.query(
                Bodega,
            )
            .filter(
                Bodega.id == bodega_id,
            )
            .first()
        )

        etiqueta_bodega = ""

        if bodega is not None:

            etiqueta_bodega = (
                f"{bodega.codigo} - {bodega.nombre}"
            )

        registros = (
            db.query(
                ExistenciaBodega,
            )
            .filter(
                ExistenciaBodega.bodega_id
                == bodega_id,
            )
            .all()
        )

        if not registros:

            return []

        producto_ids = {
            registro.producto_id
            for registro in registros
        }

        variante_ids = {
            registro.producto_variante_id
            for registro in registros
            if registro.producto_variante_id
        }

        productos = {

            producto.id: producto

            for producto in (
                db.query(
                    Producto,
                )
                .filter(
                    Producto.id.in_(
                        producto_ids,
                    ),
                )
                .all()
            )

        }

        variantes = {

            variante.id: variante

            for variante in (
                db.query(
                    ProductoVariante,
                )
                .filter(
                    ProductoVariante.id.in_(
                        variante_ids,
                    ),
                )
                .all()
            )

        } if variante_ids else {}

        filas: list[dict] = []

        for registro in registros:

            existencia = float(
                registro.cantidad or 0,
            )

            if (
                solo_con_stock
                and existencia <= 0
            ):

                continue

            producto = productos.get(
                registro.producto_id,
            )

            if producto is None:

                continue

            variante = variantes.get(
                registro.producto_variante_id,
            )

            if variante is not None:

                filas.append(
                    {
                        "codigo": variante.codigo,
                        "producto": producto.nombre,
                        "variante": (
                            variante.talla
                            or variante.color
                            or ""
                        ),
                        "bodega": etiqueta_bodega,
                        "existencia": existencia,
                        "costo": float(
                            variante.costo
                            or producto.costo
                            or 0,
                        ),
                    },
                )

                continue

            filas.append(
                {
                    "codigo": producto.codigo,
                    "producto": producto.nombre,
                    "variante": "",
                    "bodega": etiqueta_bodega,
                    "existencia": existencia,
                    "costo": float(
                        producto.costo or 0,
                    ),
                },
            )

        filas.sort(
            key=lambda fila: str(
                fila.get(
                    "codigo",
                    "",
                ),
            ),
        )

        return filas

    @classmethod
    def resumen_cartera(
        cls,
        *,
        referencia: date | None = None,
    ) -> list[dict]:

        resumen = ServicioCartera.resumen(
            referencia=referencia,
        )

        antiguedad = ServicioCartera.antiguedad(
            tipo="cxc",
            referencia=referencia,
        )

        filas = [
            {
                "concepto": "Total por cobrar",
                "valor": resumen["cxc_total"],
            },
            {
                "concepto": "Total por pagar",
                "valor": resumen["cxp_total"],
            },
            {
                "concepto": "CxC vencido",
                "valor": resumen["cxc_vencido"],
            },
            {
                "concepto": "CxP vencido",
                "valor": resumen["cxp_vencido"],
            },
            {
                "concepto": "Facturas CxC abiertas",
                "valor": resumen["facturas_cxc"],
            },
            {
                "concepto": "Facturas CxP abiertas",
                "valor": resumen["facturas_cxp"],
            },
        ]

        for bucket in antiguedad:

            filas.append(
                {
                    "concepto": (
                        f"CxC {bucket['rango']}"
                    ),
                    "valor": bucket["saldo"],
                },
            )

        return filas

    @classmethod
    def _fila_retenciones_documento(
        cls,
        *,
        numero: str,
        fecha,
        cliente_id: int,
        subtotal: float,
        total: float,
        retefuente_id,
        reteica_id,
        reteiva_id,
        impuestos: dict,
        clientes: dict,
        tipo: str = "Venta",
    ) -> dict | None:

        retenciones = []

        for tipo, impuesto_id in (
            (
                "Retefuente",
                retefuente_id,
            ),
            (
                "ReteICA",
                reteica_id,
            ),
            (
                "ReteIVA",
                reteiva_id,
            ),
        ):

            if not impuesto_id:

                continue

            impuesto = impuestos.get(
                impuesto_id,
            )

            if impuesto is None:

                continue

            retenciones.append(
                f"{tipo} {impuesto.nombre}",
            )

        if not retenciones:

            return None

        cliente = clientes.get(
            cliente_id,
        )

        nombre_cliente = ""

        if cliente is not None:

            nombre_cliente = (
                cliente.nombre_comercial
                or cliente.razon_social
                or cliente.nombre_completo
                or ""
            ).strip()

        return {
            "numero": numero,
            "fecha": fecha,
            "tipo": tipo,
            "cliente": nombre_cliente,
            "retenciones": ", ".join(
                retenciones,
            ),
            "base": float(
                subtotal or 0,
            ),
            "total": float(
                total or 0,
            ),
        }

    @classmethod
    def retenciones_aplicadas(
        cls,
        *,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[dict]:

        db = SessionLocal()

        try:

            consulta = (
                db.query(Cotizacion)
                .filter(
                    Cotizacion.activo.is_(
                        True,
                    ),
                )
            )

            if fecha_desde is not None:

                consulta = consulta.filter(
                    Cotizacion.fecha
                    >= fecha_desde,
                )

            if fecha_hasta is not None:

                consulta = consulta.filter(
                    Cotizacion.fecha
                    <= fecha_hasta,
                )

            cotizaciones = consulta.order_by(
                Cotizacion.fecha.desc(),
                Cotizacion.numero.desc(),
            ).all()

            consulta_facturas = (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.activo.is_(
                        True,
                    ),
                    FacturaVenta.estado.in_(
                        (
                            "emitida",
                            "generada",
                            "contabilizada",
                        ),
                    ),
                )
            )

            if fecha_desde is not None:

                consulta_facturas = consulta_facturas.filter(
                    FacturaVenta.fecha
                    >= fecha_desde,
                )

            if fecha_hasta is not None:

                consulta_facturas = consulta_facturas.filter(
                    FacturaVenta.fecha
                    <= fecha_hasta,
                )

            facturas = consulta_facturas.order_by(
                FacturaVenta.fecha.desc(),
                FacturaVenta.numero.desc(),
            ).all()

            consulta_compras = (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.activo.is_(
                        True,
                    ),
                    FacturaCompra.contabilizado.is_(
                        True,
                    ),
                )
            )

            if fecha_desde is not None:

                consulta_compras = consulta_compras.filter(
                    FacturaCompra.fecha
                    >= fecha_desde,
                )

            if fecha_hasta is not None:

                consulta_compras = consulta_compras.filter(
                    FacturaCompra.fecha
                    <= fecha_hasta,
                )

            facturas_compra = consulta_compras.order_by(
                FacturaCompra.fecha.desc(),
                FacturaCompra.numero.desc(),
            ).all()

            impuesto_ids = set()

            for cotizacion in cotizaciones:

                for campo in (
                    cotizacion.retefuente_id,
                    cotizacion.reteica_id,
                    cotizacion.reteiva_id,
                ):

                    if campo:

                        impuesto_ids.add(
                            campo,
                        )

            for factura in facturas:

                for campo in (
                    getattr(
                        factura,
                        "retefuente_id",
                        None,
                    ),
                    getattr(
                        factura,
                        "reteica_id",
                        None,
                    ),
                    getattr(
                        factura,
                        "reteiva_id",
                        None,
                    ),
                ):

                    if campo:

                        impuesto_ids.add(
                            campo,
                        )

            for factura in facturas_compra:

                for campo in (
                    getattr(
                        factura,
                        "retefuente_id",
                        None,
                    ),
                    getattr(
                        factura,
                        "reteica_id",
                        None,
                    ),
                    getattr(
                        factura,
                        "reteiva_id",
                        None,
                    ),
                ):

                    if campo:

                        impuesto_ids.add(
                            campo,
                        )

            impuestos = {

                impuesto.id: impuesto

                for impuesto in (
                    db.query(Impuesto)
                    .filter(
                        Impuesto.id.in_(
                            impuesto_ids,
                        ),
                    )
                    .all()
                )

            } if impuesto_ids else {}

            cliente_ids = {
                cotizacion.cliente_id
                for cotizacion in cotizaciones
            }

            cliente_ids.update(
                {
                    factura.cliente_id
                    for factura in facturas
                },
            )

            cliente_ids.update(
                {
                    factura.proveedor_id
                    for factura in facturas_compra
                    if factura.proveedor_id
                },
            )

            clientes = {

                tercero.id: tercero

                for tercero in (
                    db.query(Tercero)
                    .filter(
                        Tercero.id.in_(
                            cliente_ids,
                        ),
                    )
                    .all()
                )

            } if cliente_ids else {}

            filas: list[dict] = []

            for cotizacion in cotizaciones:

                fila = cls._fila_retenciones_documento(
                    numero=cotizacion.numero,
                    fecha=cotizacion.fecha,
                    cliente_id=cotizacion.cliente_id,
                    subtotal=float(
                        cotizacion.subtotal or 0,
                    ),
                    total=float(
                        cotizacion.total or 0,
                    ),
                    retefuente_id=cotizacion.retefuente_id,
                    reteica_id=cotizacion.reteica_id,
                    reteiva_id=cotizacion.reteiva_id,
                    impuestos=impuestos,
                    clientes=clientes,
                    tipo="Cotización",
                )

                if fila is not None:

                    filas.append(
                        fila,
                    )

            for factura in facturas:

                fila = cls._fila_retenciones_documento(
                    numero=factura.numero,
                    fecha=factura.fecha,
                    cliente_id=factura.cliente_id,
                    subtotal=float(
                        factura.subtotal or 0,
                    ),
                    total=float(
                        factura.total or 0,
                    ),
                    retefuente_id=getattr(
                        factura,
                        "retefuente_id",
                        None,
                    ),
                    reteica_id=getattr(
                        factura,
                        "reteica_id",
                        None,
                    ),
                    reteiva_id=getattr(
                        factura,
                        "reteiva_id",
                        None,
                    ),
                    impuestos=impuestos,
                    clientes=clientes,
                    tipo="Factura venta",
                )

                if fila is not None:

                    filas.append(
                        fila,
                    )

            for factura in facturas_compra:

                fila = cls._fila_retenciones_documento(
                    numero=factura.numero,
                    fecha=factura.fecha,
                    cliente_id=factura.proveedor_id,
                    subtotal=float(
                        factura.subtotal or 0,
                    ),
                    total=float(
                        factura.total or 0,
                    ),
                    retefuente_id=getattr(
                        factura,
                        "retefuente_id",
                        None,
                    ),
                    reteica_id=getattr(
                        factura,
                        "reteica_id",
                        None,
                    ),
                    reteiva_id=getattr(
                        factura,
                        "reteiva_id",
                        None,
                    ),
                    impuestos=impuestos,
                    clientes=clientes,
                    tipo="Factura compra",
                )

                if fila is not None:

                    filas.append(
                        fila,
                    )

            filas.sort(
                key=lambda fila: (
                    fila.get(
                        "fecha",
                    )
                    or date.min,
                    fila.get(
                        "numero",
                        "",
                    ),
                ),
                reverse=True,
            )

            return filas

        finally:

            db.close()

    @classmethod
    def _nombre_cliente_reporte(
        cls,
        tercero: Tercero | None,
    ) -> str:

        if tercero is None:

            return ""

        return (
            tercero.nombre_comercial
            or tercero.razon_social
            or tercero.nombre_completo
            or ""
        ).strip()

    @classmethod
    def _etapa_pipeline_comercial(
        cls,
        *,
        pedido: OrdenPedido | None,
        remision: RemisionVenta | None,
        factura: FacturaVenta | None,
    ) -> str:

        if factura is not None:

            saldo = float(
                factura.saldo_pendiente or 0,
            )

            total = float(
                factura.total or 0,
            )

            if (
                total > 0
                and saldo <= 0.01
            ):

                return "cobrado"

            return "factura"

        if remision is not None:

            return "remisión"

        if pedido is not None:

            return "pedido"

        return "cotización"

    @classmethod
    def pipeline_comercial(
        cls,
        *,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[dict]:

        db = SessionLocal()

        try:

            consulta = (
                db.query(
                    Cotizacion,
                )
                .filter(
                    Cotizacion.activo.is_(
                        True,
                    ),
                )
            )

            if fecha_desde is not None:

                consulta = consulta.filter(
                    Cotizacion.fecha
                    >= fecha_desde,
                )

            if fecha_hasta is not None:

                consulta = consulta.filter(
                    Cotizacion.fecha
                    <= fecha_hasta,
                )

            cotizaciones = consulta.order_by(
                Cotizacion.fecha.desc(),
                Cotizacion.numero.desc(),
            ).all()

            if not cotizaciones:

                return []

            cotizacion_ids = [
                cotizacion.id
                for cotizacion in cotizaciones
            ]

            cliente_ids = {
                cotizacion.cliente_id
                for cotizacion in cotizaciones
            }

            clientes = {

                tercero.id: tercero

                for tercero in (
                    db.query(
                        Tercero,
                    )
                    .filter(
                        Tercero.id.in_(
                            cliente_ids,
                        ),
                    )
                    .all()
                )

            } if cliente_ids else {}

            pedidos = {

                pedido.cotizacion_id: pedido

                for pedido in (
                    db.query(
                        OrdenPedido,
                    )
                    .filter(
                        OrdenPedido.cotizacion_id.in_(
                            cotizacion_ids,
                        ),
                        OrdenPedido.activo.is_(
                            True,
                        ),
                    )
                    .all()
                )

                if pedido.cotizacion_id
            }

            remisiones = {

                remision.cotizacion_id: remision

                for remision in (
                    db.query(
                        RemisionVenta,
                    )
                    .filter(
                        RemisionVenta.cotizacion_id.in_(
                            cotizacion_ids,
                        ),
                        RemisionVenta.activo.is_(
                            True,
                        ),
                    )
                    .all()
                )

                if remision.cotizacion_id
            }

            facturas = {

                factura.cotizacion_id: factura

                for factura in (
                    db.query(
                        FacturaVenta,
                    )
                    .filter(
                        FacturaVenta.cotizacion_id.in_(
                            cotizacion_ids,
                        ),
                        FacturaVenta.activo.is_(
                            True,
                        ),
                    )
                    .all()
                )

                if factura.cotizacion_id
            }

            filas: list[dict] = []

            for cotizacion in cotizaciones:

                pedido = pedidos.get(
                    cotizacion.id,
                )

                remision = remisiones.get(
                    cotizacion.id,
                )

                factura = facturas.get(
                    cotizacion.id,
                )

                valor_cobrado = 0.0
                saldo_pendiente = 0.0

                if factura is not None:

                    valor_cobrado = float(
                        factura.valor_pagado or 0,
                    )

                    saldo_pendiente = float(
                        factura.saldo_pendiente
                        or 0,
                    )

                filas.append(
                    {
                        "cotizacion_numero": (
                            cotizacion.numero
                        ),
                        "cotizacion_fecha": (
                            cotizacion.fecha
                        ),
                        "cliente": cls._nombre_cliente_reporte(
                            clientes.get(
                                cotizacion.cliente_id,
                            ),
                        ),
                        "cotizacion_estado": (
                            cotizacion.estado or ""
                        ),
                        "cotizacion_total": float(
                            cotizacion.total or 0,
                        ),
                        "pedido_numero": (
                            pedido.numero
                            if pedido
                            else ""
                        ),
                        "remision_numero": (
                            remision.numero
                            if remision
                            else ""
                        ),
                        "factura_numero": (
                            factura.numero
                            if factura
                            else ""
                        ),
                        "saldo_pendiente": (
                            saldo_pendiente
                        ),
                        "valor_cobrado": (
                            valor_cobrado
                        ),
                        "etapa_actual": cls._etapa_pipeline_comercial(
                            pedido=pedido,
                            remision=remision,
                            factura=factura,
                        ),
                    },
                )

            return filas

        finally:

            db.close()

    @classmethod
    def pipeline_comercial_resumen(
        cls,
        filas: list[dict],
    ) -> dict[str, dict[str, float | int]]:

        etapas = (
            "cotización",
            "pedido",
            "remisión",
            "factura",
            "cobrado",
        )

        resumen = {

            etapa: {
                "cantidad": 0,
                "total": 0.0,
            }

            for etapa in etapas

        }

        for fila in filas:

            etapa = str(
                fila.get(
                    "etapa_actual",
                    "",
                ),
            )

            if etapa not in resumen:

                continue

            resumen[etapa]["cantidad"] += 1
            resumen[etapa]["total"] += float(
                fila.get(
                    "cotizacion_total",
                    0,
                )
                or 0,
            )

        return resumen

    @classmethod
    def totales_documentos(
        cls,
        filas: list[dict],
        campo: str,
    ) -> float:

        return float(
            sum(
                float(
                    fila.get(
                        campo,
                        0,
                    )
                    or 0,
                )
                for fila in filas
            )
        )
