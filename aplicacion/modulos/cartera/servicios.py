from __future__ import annotations

from datetime import date

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.maestros.terceros.modelos import Tercero
from aplicacion.modulos.compras.facturas.modelos import (
    FacturaCompra,
)
from aplicacion.modulos.tesoreria.comprobantes_egreso.modelos import (
    ComprobanteEgreso,
    ComprobanteEgresoDetalle,
)
from aplicacion.modulos.tesoreria.recibos_caja.modelos import (
    ReciboCaja,
    ReciboCajaDetalle,
)
from aplicacion.modulos.ventas.facturas.modelos import (
    FacturaVenta,
)

from .utilidades import (
    BUCKETS_ANTIGUEDAD,
    bucket_antiguedad,
    dias_mora,
)


class ServicioCartera:

    @classmethod
    def _nombre_tercero(
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
    def resumen(
        cls,
        *,
        referencia: date | None = None,
    ) -> dict:

        hoy = referencia or date.today()

        db = SessionLocal()

        try:

            facturas_cxc = (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.contabilizado.is_(
                        True,
                    ),
                    FacturaVenta.activo.is_(
                        True,
                    ),
                    FacturaVenta.saldo_pendiente
                    > 0,
                )
                .all()
            )

            facturas_cxp = (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.contabilizado.is_(
                        True,
                    ),
                    FacturaCompra.activo.is_(
                        True,
                    ),
                    FacturaCompra.saldo_pendiente
                    > 0,
                )
                .all()
            )

        finally:

            db.close()

        cxc_total = sum(
            float(
                f.saldo_pendiente or 0,
            )
            for f in facturas_cxc
        )

        cxp_total = sum(
            float(
                f.saldo_pendiente or 0,
            )
            for f in facturas_cxp
        )

        cxc_vencido = sum(
            float(
                f.saldo_pendiente or 0,
            )
            for f in facturas_cxc
            if dias_mora(
                f.fecha_vencimiento,
                referencia=hoy,
            )
            > 0
        )

        cxp_vencido = sum(
            float(
                f.saldo_pendiente or 0,
            )
            for f in facturas_cxp
            if dias_mora(
                f.fecha_vencimiento,
                referencia=hoy,
            )
            > 0
        )

        return {
            "cxc_total": cxc_total,
            "cxp_total": cxp_total,
            "cxc_vencido": cxc_vencido,
            "cxp_vencido": cxp_vencido,
            "facturas_cxc": len(
                facturas_cxc,
            ),
            "facturas_cxp": len(
                facturas_cxp,
            ),
        }

    @classmethod
    def listar_cxc(
        cls,
        *,
        tercero_id: int | None = None,
        solo_vencidos: bool = False,
        referencia: date | None = None,
    ) -> list[dict]:

        hoy = referencia or date.today()

        db = SessionLocal()

        try:

            consulta = (
                db.query(
                    FacturaVenta,
                    Tercero,
                )
                .join(
                    Tercero,
                    Tercero.id
                    == FacturaVenta.cliente_id,
                )
                .filter(
                    FacturaVenta.contabilizado.is_(
                        True,
                    ),
                    FacturaVenta.activo.is_(
                        True,
                    ),
                    FacturaVenta.saldo_pendiente
                    > 0,
                )
            )

            if tercero_id is not None:

                consulta = consulta.filter(
                    FacturaVenta.cliente_id
                    == tercero_id,
                )

            registros = consulta.order_by(
                FacturaVenta.fecha_vencimiento,
                FacturaVenta.numero,
            ).all()

            filas: list[dict] = []

            for factura, tercero in registros:

                mora = dias_mora(
                    factura.fecha_vencimiento,
                    referencia=hoy,
                )

                if (
                    solo_vencidos
                    and mora <= 0
                ):

                    continue

                filas.append(
                    cls._fila_factura_cxc(
                        factura,
                        tercero,
                        mora,
                    ),
                )

            return filas

        finally:

            db.close()

    @classmethod
    def resumen_cliente_cxc(
        cls,
        tercero_id: int,
    ) -> dict:

        filas = cls.listar_cxc(
            tercero_id=tercero_id,
        )

        saldo_total = sum(
            float(
                fila["saldo"],
            )
            for fila in filas
        )

        saldo_vencido = sum(
            float(
                fila["saldo"],
            )
            for fila in filas
            if int(
                fila["dias_mora"],
            )
            > 0
        )

        return {
            "saldo_total": saldo_total,
            "saldo_vencido": saldo_vencido,
            "facturas_pendientes": len(
                filas,
            ),
            "filas": filas,
        }

    @classmethod
    def listar_cxp(
        cls,
        *,
        tercero_id: int | None = None,
        solo_vencidos: bool = False,
        referencia: date | None = None,
    ) -> list[dict]:

        hoy = referencia or date.today()

        db = SessionLocal()

        try:

            consulta = (
                db.query(
                    FacturaCompra,
                    Tercero,
                )
                .outerjoin(
                    Tercero,
                    Tercero.id
                    == FacturaCompra.proveedor_id,
                )
                .filter(
                    FacturaCompra.contabilizado.is_(
                        True,
                    ),
                    FacturaCompra.activo.is_(
                        True,
                    ),
                    FacturaCompra.saldo_pendiente
                    > 0,
                )
            )

            if tercero_id is not None:

                consulta = consulta.filter(
                    FacturaCompra.proveedor_id
                    == tercero_id,
                )

            registros = consulta.order_by(
                FacturaCompra.fecha_vencimiento,
                FacturaCompra.numero,
            ).all()

            filas: list[dict] = []

            for factura, tercero in registros:

                mora = dias_mora(
                    factura.fecha_vencimiento,
                    referencia=hoy,
                )

                if (
                    solo_vencidos
                    and mora <= 0
                ):

                    continue

                filas.append(
                    cls._fila_factura_cxp(
                        factura,
                        tercero,
                        mora,
                    ),
                )

            return filas

        finally:

            db.close()

    @classmethod
    def _fila_factura_cxc(
        cls,
        factura: FacturaVenta,
        tercero: Tercero | None,
        mora: int,
    ) -> dict:

        return {
            "id": factura.id,
            "numero": factura.numero,
            "tercero": cls._nombre_tercero(
                tercero,
            ),
            "fecha": factura.fecha,
            "fecha_vencimiento": (
                factura.fecha_vencimiento
            ),
            "total": float(
                factura.total or 0,
            ),
            "valor_pagado": float(
                factura.valor_pagado or 0,
            ),
            "saldo": float(
                factura.saldo_pendiente
                or 0,
            ),
            "estado_pago": (
                factura.estado_pago or ""
            ),
            "dias_mora": mora,
        }

    @classmethod
    def _fila_factura_cxp(
        cls,
        factura: FacturaCompra,
        tercero: Tercero | None,
        mora: int,
    ) -> dict:

        nombre = cls._nombre_tercero(
            tercero,
        )

        if not nombre:

            nombre = (
                factura.razon_social_proveedor
                or factura.nit_proveedor
                or ""
            )

        return {
            "id": factura.id,
            "numero": factura.numero,
            "tercero": nombre,
            "fecha": factura.fecha,
            "fecha_vencimiento": (
                factura.fecha_vencimiento
            ),
            "total": float(
                factura.total or 0,
            ),
            "valor_pagado": float(
                factura.valor_pagado or 0,
            ),
            "saldo": float(
                factura.saldo_pendiente
                or 0,
            ),
            "estado_pago": (
                factura.estado_pago or ""
            ),
            "dias_mora": mora,
        }

    @classmethod
    def antiguedad(
        cls,
        *,
        tipo: str,
        referencia: date | None = None,
    ) -> list[dict]:

        tipo = tipo.strip().lower()

        if tipo == "cxp":

            facturas = cls.listar_cxp(
                referencia=referencia,
            )

        else:

            facturas = cls.listar_cxc(
                referencia=referencia,
            )

        totales = {
            etiqueta: 0.0
            for etiqueta, _, _ in BUCKETS_ANTIGUEDAD
        }

        for fila in facturas:

            etiqueta = bucket_antiguedad(
                fila["dias_mora"],
            )

            totales[etiqueta] += fila[
                "saldo"
            ]

        return [
            {
                "rango": etiqueta,
                "saldo": totales[etiqueta],
            }
            for etiqueta, _, _ in BUCKETS_ANTIGUEDAD
        ]

    @classmethod
    def estado_cuenta_cxc(
        cls,
        tercero_id: int,
    ) -> dict:

        db = SessionLocal()

        try:

            tercero = (
                db.query(Tercero)
                .filter(
                    Tercero.id
                    == tercero_id,
                )
                .first()
            )

            if tercero is None:

                raise ValueError(
                    "Cliente no encontrado.",
                )

            facturas = (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.cliente_id
                    == tercero_id,
                    FacturaVenta.contabilizado.is_(
                        True,
                    ),
                    FacturaVenta.activo.is_(
                        True,
                    ),
                )
                .order_by(
                    FacturaVenta.fecha,
                    FacturaVenta.numero,
                )
                .all()
            )

            pagos = (
                db.query(
                    ReciboCaja,
                    ReciboCajaDetalle,
                    FacturaVenta,
                )
                .join(
                    ReciboCajaDetalle,
                    ReciboCajaDetalle.recibo_id
                    == ReciboCaja.id,
                )
                .join(
                    FacturaVenta,
                    FacturaVenta.id
                    == ReciboCajaDetalle.factura_venta_id,
                )
                .filter(
                    ReciboCaja.cliente_id
                    == tercero_id,
                    ReciboCaja.contabilizado.is_(
                        True,
                    ),
                    ReciboCaja.activo.is_(
                        True,
                    ),
                )
                .order_by(
                    ReciboCaja.fecha,
                    ReciboCaja.numero,
                )
                .all()
            )

        finally:

            db.close()

        movimientos: list[dict] = []

        for factura in facturas:

            movimientos.append(
                {
                    "fecha": factura.fecha,
                    "documento": factura.numero,
                    "tipo": "Factura",
                    "debito": float(
                        factura.total or 0,
                    ),
                    "credito": 0.0,
                    "referencia": (
                        f"Vence "
                        f"{factura.fecha_vencimiento or ''}"
                    ),
                },
            )

        for (
            recibo,
            detalle,
            factura,
        ) in pagos:

            movimientos.append(
                {
                    "fecha": recibo.fecha,
                    "documento": recibo.numero,
                    "tipo": "Recibo",
                    "debito": 0.0,
                    "credito": float(
                        detalle.valor_aplicado
                        or 0,
                    ),
                    "referencia": (
                        f"Factura "
                        f"{factura.numero}"
                    ),
                },
            )

        movimientos.sort(
            key=lambda item: (
                item["fecha"],
                item["documento"],
            ),
        )

        saldo = 0.0

        for movimiento in movimientos:

            saldo += (
                movimiento["debito"]
                - movimiento["credito"]
            )

            movimiento["saldo"] = saldo

        return {
            "tercero": cls._nombre_tercero(
                tercero,
            ),
            "movimientos": movimientos,
            "saldo_final": saldo,
        }

    @classmethod
    def estado_cuenta_cxp(
        cls,
        tercero_id: int,
    ) -> dict:

        db = SessionLocal()

        try:

            tercero = (
                db.query(Tercero)
                .filter(
                    Tercero.id
                    == tercero_id,
                )
                .first()
            )

            if tercero is None:

                raise ValueError(
                    "Proveedor no encontrado.",
                )

            facturas = (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.proveedor_id
                    == tercero_id,
                    FacturaCompra.contabilizado.is_(
                        True,
                    ),
                    FacturaCompra.activo.is_(
                        True,
                    ),
                )
                .order_by(
                    FacturaCompra.fecha,
                    FacturaCompra.numero,
                )
                .all()
            )

            pagos = (
                db.query(
                    ComprobanteEgreso,
                    ComprobanteEgresoDetalle,
                    FacturaCompra,
                )
                .join(
                    ComprobanteEgresoDetalle,
                    ComprobanteEgresoDetalle.comprobante_id
                    == ComprobanteEgreso.id,
                )
                .join(
                    FacturaCompra,
                    FacturaCompra.id
                    == ComprobanteEgresoDetalle.factura_compra_id,
                )
                .filter(
                    ComprobanteEgreso.proveedor_id
                    == tercero_id,
                    ComprobanteEgreso.contabilizado.is_(
                        True,
                    ),
                    ComprobanteEgreso.activo.is_(
                        True,
                    ),
                )
                .order_by(
                    ComprobanteEgreso.fecha,
                    ComprobanteEgreso.numero,
                )
                .all()
            )

        finally:

            db.close()

        movimientos: list[dict] = []

        for factura in facturas:

            movimientos.append(
                {
                    "fecha": factura.fecha,
                    "documento": factura.numero,
                    "tipo": "Factura compra",
                    "debito": float(
                        factura.total or 0,
                    ),
                    "credito": 0.0,
                    "referencia": (
                        f"Vence "
                        f"{factura.fecha_vencimiento or ''}"
                    ),
                },
            )

        for (
            egreso,
            detalle,
            factura,
        ) in pagos:

            movimientos.append(
                {
                    "fecha": egreso.fecha,
                    "documento": egreso.numero,
                    "tipo": "Egreso",
                    "debito": 0.0,
                    "credito": float(
                        detalle.valor_aplicado
                        or 0,
                    ),
                    "referencia": (
                        f"Factura "
                        f"{factura.numero}"
                    ),
                },
            )

        movimientos.sort(
            key=lambda item: (
                item["fecha"],
                item["documento"],
            ),
        )

        saldo = 0.0

        for movimiento in movimientos:

            saldo += (
                movimiento["debito"]
                - movimiento["credito"]
            )

            movimiento["saldo"] = saldo

        return {
            "tercero": cls._nombre_tercero(
                tercero,
            ),
            "movimientos": movimientos,
            "saldo_final": saldo,
        }

    @classmethod
    def asegurar_fecha_vencimiento_factura_venta(
        cls,
        factura: FacturaVenta,
        db,
    ) -> None:

        if factura.fecha_vencimiento is not None:

            return

        from aplicacion.modulos.cartera.utilidades import (
            calcular_fecha_vencimiento,
        )

        tercero = (
            db.query(Tercero)
            .filter(
                Tercero.id
                == factura.cliente_id,
            )
            .first()
        )

        factura.fecha_vencimiento = (
            calcular_fecha_vencimiento(
                factura.fecha,
                (
                    tercero.dias_credito
                    if tercero
                    else 0
                ),
            )
        )

    @classmethod
    def asegurar_fecha_vencimiento_factura_compra(
        cls,
        factura: FacturaCompra,
        db,
    ) -> None:

        if factura.fecha_vencimiento is not None:

            return

        from aplicacion.modulos.cartera.utilidades import (
            calcular_fecha_vencimiento,
        )

        tercero = None

        if factura.proveedor_id:

            tercero = (
                db.query(Tercero)
                .filter(
                    Tercero.id
                    == factura.proveedor_id,
                )
                .first()
            )

        factura.fecha_vencimiento = (
            calcular_fecha_vencimiento(
                factura.fecha,
                (
                    tercero.dias_credito
                    if tercero
                    else 0
                ),
            )
        )
