from __future__ import annotations

from datetime import date

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
            from aplicacion.maestros.productos.modelos import (
                Producto,
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

            top_productos = (
                db.query(Producto)
                .filter(
                    Producto.activo.is_(True),
                )
                .order_by(
                    Producto.existencia.desc(),
                )
                .limit(5)
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
            "top_productos": [
                {
                    "nombre": p.nombre,
                    "existencia": p.existencia,
                }
                for p in top_productos
            ],
            "pipeline_periodo": pipeline,
            "periodo_desde": fecha_desde,
            "periodo_hasta": fecha_hasta,
        }
