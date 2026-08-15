from __future__ import annotations

from datetime import date, timedelta

from aplicacion.base_datos.conexion import SessionLocal


class ServicioInteligencia:
    """Centro de inteligencia empresarial (reglas + consultas)."""

    @classmethod
    def alertas(cls) -> list[dict]:
        alertas: list[dict] = []

        alertas.extend(
            cls._duplicados_cufe(),
        )
        alertas.extend(
            cls._cartera_vencida(),
        )
        alertas.extend(
            cls._bajo_inventario(),
        )
        alertas.extend(
            cls._facturas_pendientes_revision(),
        )

        return alertas

    @classmethod
    def consultar(cls, pregunta: str) -> dict:
        texto = str(
            pregunta or "",
        ).lower()

        if "cartera" in texto and "vencida" in texto:
            return cls._respuesta_cartera_vencida()

        if "ventas" in texto and "vendedor" in texto:
            return cls._respuesta_ventas_vendedor()

        if "utilidad" in texto or "margen" in texto:
            return cls._respuesta_margen()

        if "flujo" in texto or "caja" in texto:
            return cls._respuesta_flujo_caja()

        if "duplic" in texto:
            return {
                "titulo": "Facturas duplicadas",
                "items": cls._duplicados_cufe(),
            }

        return {
            "titulo": "Consulta",
            "texto": (
                "Puede preguntar por cartera vencida, "
                "ventas por vendedor, utilidad, flujo de "
                "caja o facturas duplicadas."
            ),
        }

    @classmethod
    def recomendar_cuenta_compra(
        cls,
        *,
        es_servicio: bool,
        es_inventariable: bool,
    ) -> str:
        if es_servicio or not es_inventariable:
            return "613501"

        return "143501"

    @classmethod
    def _duplicados_cufe(cls) -> list[dict]:
        from aplicacion.modulos.compras.facturas.modelos import (
            FacturaCompra,
        )

        db = SessionLocal()

        try:
            filas = (
                db.query(
                    FacturaCompra.cufe,
                )
                .filter(
                    FacturaCompra.cufe.isnot(None),
                    FacturaCompra.cufe != "",
                )
                .all()
            )

            vistos: dict[str, int] = {}
            duplicados = []

            for (cufe,) in filas:
                vistos[cufe] = vistos.get(cufe, 0) + 1

            for cufe, cantidad in vistos.items():
                if cantidad > 1:
                    duplicados.append(
                        {
                            "tipo": "duplicado_cufe",
                            "mensaje": (
                                f"CUFE repetido {cufe[:20]}… "
                                f"({cantidad} veces)"
                            ),
                            "severidad": "alta",
                        }
                    )

            return duplicados

        finally:
            db.close()

    @classmethod
    def _cartera_vencida(cls) -> list[dict]:
        from aplicacion.modulos.ventas.facturas.modelos import (
            FacturaVenta,
        )

        db = SessionLocal()
        hoy = date.today()

        try:
            cantidad = (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.estado_pago == "pendiente",
                    FacturaVenta.fecha_vencimiento < hoy,
                )
                .count()
            )

            if cantidad <= 0:
                return []

            return [
                {
                    "tipo": "cartera_vencida",
                    "mensaje": (
                        f"{cantidad} factura(s) de venta "
                        "vencida(s)."
                    ),
                    "severidad": "media",
                }
            ]

        finally:
            db.close()

    @classmethod
    def _bajo_inventario(cls) -> list[dict]:
        from aplicacion.maestros.productos.modelos import (
            Producto,
        )

        db = SessionLocal()

        try:
            productos = (
                db.query(Producto)
                .filter(
                    Producto.activo.is_(True),
                    Producto.existencia <= 0,
                )
                .count()
            )

            if productos <= 0:
                return []

            return [
                {
                    "tipo": "bajo_inventario",
                    "mensaje": (
                        f"{productos} producto(s) sin "
                        "existencia."
                    ),
                    "severidad": "media",
                }
            ]

        finally:
            db.close()

    @classmethod
    def _facturas_pendientes_revision(cls) -> list[dict]:
        from aplicacion.modulos.compras.facturas.modelos import (
            FacturaCompra,
        )

        db = SessionLocal()

        try:
            cantidad = (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.estado
                    == "pendiente_revision",
                )
                .count()
            )

            if cantidad <= 0:
                return []

            return [
                {
                    "tipo": "compras_revision",
                    "mensaje": (
                        f"{cantidad} factura(s) de compra "
                        "pendientes de revisión."
                    ),
                    "severidad": "baja",
                }
            ]

        finally:
            db.close()

    @classmethod
    def _respuesta_cartera_vencida(cls) -> dict:
        from aplicacion.modulos.ventas.facturas.modelos import (
            FacturaVenta,
        )

        db = SessionLocal()
        hoy = date.today()

        try:
            facturas = (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.estado_pago == "pendiente",
                    FacturaVenta.fecha_vencimiento < hoy,
                )
                .order_by(
                    FacturaVenta.fecha_vencimiento,
                )
                .limit(10)
                .all()
            )

            items = [
                {
                    "numero": f.numero,
                    "saldo": float(
                        f.saldo_pendiente or f.total or 0,
                    ),
                    "vencimiento": str(
                        f.fecha_vencimiento,
                    ),
                }
                for f in facturas
            ]

            return {
                "titulo": "Cartera vencida",
                "items": items,
            }

        finally:
            db.close()

    @classmethod
    def _respuesta_ventas_vendedor(cls) -> dict:
        from aplicacion.modulos.ventas.facturas.modelos import (
            FacturaVenta,
        )

        db = SessionLocal()
        inicio = date.today().replace(day=1)

        try:
            facturas = (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.fecha >= inicio,
                )
                .all()
            )

            totales: dict[str, float] = {}

            for factura in facturas:
                vendedor = (
                    factura.vendedor or "Sin asignar"
                )
                totales[vendedor] = totales.get(
                    vendedor,
                    0,
                ) + float(
                    factura.total or 0,
                )

            items = [
                {
                    "vendedor": nombre,
                    "total": round(valor, 0),
                }
                for nombre, valor in sorted(
                    totales.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            ]

            return {
                "titulo": "Ventas por vendedor (mes)",
                "items": items,
            }

        finally:
            db.close()

    @classmethod
    def _respuesta_margen(cls) -> dict:
        return {
            "titulo": "Utilidad estimada",
            "texto": (
                "Compare ventas del mes contra costo "
                "de ventas en reportes → Ventas e "
                "Impuestos para margen detallado."
            ),
        }

    @classmethod
    def _respuesta_flujo_caja(cls) -> dict:
        from aplicacion.modulos.tesoreria.centro_financiero.servicios import (
            ServicioCentroFinanciero,
        )

        resumen = ServicioCentroFinanciero.resumen()

        return {
            "titulo": "Flujo de caja proyectado",
            "items": [
                {
                    "concepto": "Recaudos esperados (7 días)",
                    "valor": resumen["recaudos_esperados"],
                },
                {
                    "concepto": "Pagos programados (7 días)",
                    "valor": resumen["pagos_programados"],
                },
                {
                    "concepto": "Disponibilidad estimada",
                    "valor": resumen["disponibilidad"],
                },
            ],
        }
