from __future__ import annotations

from datetime import date, timedelta

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.interfaz.kpis_inicio import (
    obtener_resumen_inicio,
)
from aplicacion.modulos.reportes.servicios import (
    ServicioReportes,
)


class ServicioPanelGerencial:

    @classmethod
    def _pipeline_periodo(
        cls,
        fecha_desde: date,
        fecha_hasta: date,
    ) -> dict:

        filas = ServicioReportes.pipeline_comercial(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )

        resumen = ServicioReportes.pipeline_comercial_resumen(
            filas,
        )

        total_cotizaciones = len(
            filas,
        )

        total_cobrado = float(
            resumen.get(
                "cobrado",
                {},
            ).get(
                "total",
                0,
            )
            or 0,
        )

        return {
            "periodo_desde": fecha_desde,
            "periodo_hasta": fecha_hasta,
            "cotizaciones": total_cotizaciones,
            "total_cotizado": float(
                ServicioReportes.totales_documentos(
                    filas,
                    "cotizacion_total",
                ),
            ),
            "total_cobrado": total_cobrado,
            "etapas": resumen,
        }

    @classmethod
    def _variacion_periodo_anterior(
        cls,
        fecha_desde: date,
        fecha_hasta: date,
        pipeline_actual: dict,
    ) -> dict:

        dias = (fecha_hasta - fecha_desde).days + 1

        anterior_hasta = fecha_desde - timedelta(days=1)
        anterior_desde = anterior_hasta - timedelta(days=dias - 1)

        pipeline_anterior = cls._pipeline_periodo(
            anterior_desde,
            anterior_hasta,
        )

        def _porcentaje(actual, anterior):

            if not anterior:

                return None

            return (actual - anterior) / anterior * 100

        return {
            "cotizado": _porcentaje(
                pipeline_actual["total_cotizado"],
                pipeline_anterior["total_cotizado"],
            ),
            "cobrado": _porcentaje(
                pipeline_actual["total_cobrado"],
                pipeline_anterior["total_cobrado"],
            ),
        }

    @classmethod
    def _top_productos_vendidos(
        cls,
        fecha_desde: date,
        fecha_hasta: date,
        *,
        limite: int = 5,
    ) -> list[dict]:

        from aplicacion.modulos.ventas.facturas.modelos import (
            FacturaVenta,
            FacturaVentaDetalle,
        )
        from aplicacion.maestros.productos.modelos import (
            Producto,
        )

        db = SessionLocal()

        try:
            facturas = (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.fecha >= fecha_desde,
                    FacturaVenta.fecha <= fecha_hasta,
                )
                .all()
            )

            ids_factura = [
                factura.id for factura in facturas
            ]

            if not ids_factura:

                return []

            detalles = (
                db.query(FacturaVentaDetalle)
                .filter(
                    FacturaVentaDetalle.factura_id.in_(
                        ids_factura,
                    ),
                    FacturaVentaDetalle.producto_id.isnot(
                        None,
                    ),
                )
                .all()
            )

            acumulado: dict[int, dict] = {}

            for detalle in detalles:

                fila = acumulado.setdefault(
                    detalle.producto_id,
                    {
                        "cantidad": 0.0,
                        "valor": 0.0,
                    },
                )

                fila["cantidad"] += float(
                    detalle.cantidad or 0,
                )
                fila["valor"] += float(
                    detalle.total_linea or 0,
                )

            if not acumulado:

                return []

            nombres = {
                producto.id: producto.nombre
                for producto in (
                    db.query(Producto)
                    .filter(
                        Producto.id.in_(
                            acumulado.keys(),
                        ),
                    )
                    .all()
                )
            }

        finally:
            db.close()

        filas = [
            {
                "producto_id": producto_id,
                "nombre": nombres.get(
                    producto_id,
                    f"Producto {producto_id}",
                ),
                "cantidad": datos["cantidad"],
                "valor": datos["valor"],
            }
            for producto_id, datos in acumulado.items()
        ]

        filas.sort(
            key=lambda fila: fila["valor"],
            reverse=True,
        )

        return filas[:limite]

    @classmethod
    def _serie_mensual(
        cls,
        *,
        meses: int = 6,
    ) -> list[dict]:

        from aplicacion.modulos.ventas.facturas.modelos import (
            FacturaVenta,
        )
        from aplicacion.modulos.compras.facturas.modelos import (
            FacturaCompra,
        )

        hoy = date.today()

        periodos = []
        anio, mes = hoy.year, hoy.month

        for _ in range(meses):

            periodos.append((anio, mes))

            mes -= 1

            if mes == 0:

                mes = 12
                anio -= 1

        periodos.reverse()

        db = SessionLocal()
        serie = []

        try:
            for anio, mes in periodos:

                inicio = date(anio, mes, 1)

                if mes == 12:

                    fin = date(
                        anio + 1,
                        1,
                        1,
                    ) - timedelta(days=1)

                else:

                    fin = date(
                        anio,
                        mes + 1,
                        1,
                    ) - timedelta(days=1)

                ventas = (
                    db.query(FacturaVenta)
                    .filter(
                        FacturaVenta.fecha >= inicio,
                        FacturaVenta.fecha <= fin,
                    )
                    .all()
                )

                compras = (
                    db.query(FacturaCompra)
                    .filter(
                        FacturaCompra.fecha >= inicio,
                        FacturaCompra.fecha <= fin,
                    )
                    .all()
                )

                serie.append(
                    {
                        "anio": anio,
                        "mes": mes,
                        "ventas": sum(
                            float(f.total or 0)
                            for f in ventas
                        ),
                        "compras": sum(
                            float(f.total or 0)
                            for f in compras
                        ),
                    }
                )

        finally:
            db.close()

        return serie

    @classmethod
    def resumen(
        cls,
        *,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> dict:
        base = obtener_resumen_inicio()
        hoy = date.today()

        if fecha_desde is None:

            fecha_desde = hoy.replace(
                day=1,
            )

        if fecha_hasta is None:

            fecha_hasta = hoy

        db = SessionLocal()

        try:
            from aplicacion.modulos.ventas.facturas.modelos import (
                FacturaVenta,
            )
            from aplicacion.modulos.compras.facturas.modelos import (
                FacturaCompra,
            )

            ventas_hoy = (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.fecha == hoy,
                )
                .all()
            )

            compras_hoy = (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.fecha == hoy,
                )
                .all()
            )

        finally:
            db.close()

        ventas_dia = sum(
            float(f.total or 0)
            for f in ventas_hoy
        )

        compras_dia = sum(
            float(f.total or 0)
            for f in compras_hoy
        )

        utilidad_est = ventas_dia - compras_dia

        pipeline = cls._pipeline_periodo(
            fecha_desde,
            fecha_hasta,
        )

        variacion = cls._variacion_periodo_anterior(
            fecha_desde,
            fecha_hasta,
            pipeline,
        )

        top_productos = cls._top_productos_vendidos(
            fecha_desde,
            fecha_hasta,
        )

        serie_mensual = cls._serie_mensual()

        return {
            "empresa": base.empresa_nombre,
            "ventas_dia": ventas_dia,
            "compras_dia": compras_dia,
            "utilidad_estimada": utilidad_est,
            "cxc_total": base.cxc_total,
            "cxp_total": base.cxp_total,
            "cxc_vencido": base.cxc_vencido,
            "cotizaciones_mes": base.cotizaciones_mes_total,
            "productos_activos": base.productos_activos,
            "top_productos": top_productos,
            "pipeline_periodo": pipeline,
            "variacion_periodo_anterior": variacion,
            "serie_mensual": serie_mensual,
            "periodo_desde": fecha_desde,
            "periodo_hasta": fecha_hasta,
        }
