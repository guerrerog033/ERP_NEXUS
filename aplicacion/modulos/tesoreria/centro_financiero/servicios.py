from __future__ import annotations

from datetime import date, timedelta

from aplicacion.base_datos.conexion import SessionLocal


class ServicioCentroFinanciero:

    @classmethod
    def resumen(cls) -> dict:
        db = SessionLocal()
        hoy = date.today()
        limite = hoy + timedelta(days=7)

        try:
            from aplicacion.modulos.ventas.facturas.modelos import (
                FacturaVenta,
            )
            from aplicacion.modulos.compras.facturas.modelos import (
                FacturaCompra,
            )
            from aplicacion.modulos.tesoreria.cuentas_bancarias.modelos import (
                CuentaBancaria,
            )

            cxc_hoy = cls._sumar_pendientes(
                db,
                FacturaVenta,
                hoy,
                hoy,
            )

            cxp_hoy = cls._sumar_pendientes(
                db,
                FacturaCompra,
                hoy,
                hoy,
            )

            recaudos = cls._sumar_pendientes(
                db,
                FacturaVenta,
                hoy,
                limite,
            )

            pagos = cls._sumar_pendientes(
                db,
                FacturaCompra,
                hoy,
                limite,
            )

            saldos_bancos = (
                db.query(CuentaBancaria)
                .filter(
                    CuentaBancaria.activo.is_(True),
                )
                .all()
            )

            saldo_total = sum(
                float(c.saldo or 0)
                for c in saldos_bancos
            )

        finally:
            db.close()

        disponibilidad = saldo_total + recaudos - pagos

        sugerencias = []

        if pagos > recaudos and disponibilidad < 0:
            sugerencias.append(
                "El flujo proyectado indica déficit "
                "en los próximos 7 días."
            )

        if cxp_hoy > 0:
            sugerencias.append(
                f"Hay ${cxp_hoy:,.0f} por pagar hoy."
            )

        return {
            "saldo_bancos": saldo_total,
            "cxc_hoy": cxc_hoy,
            "cxp_hoy": cxp_hoy,
            "recaudos_esperados": recaudos,
            "pagos_programados": pagos,
            "disponibilidad": disponibilidad,
            "sugerencias": sugerencias,
        }

    @classmethod
    def _sumar_pendientes(
        cls,
        db,
        modelo,
        desde: date,
        hasta: date,
    ) -> float:
        consulta = (
            db.query(modelo)
            .filter(
                modelo.estado_pago == "pendiente",
            )
        )

        if hasattr(modelo, "fecha_vencimiento"):
            consulta = consulta.filter(
                modelo.fecha_vencimiento >= desde,
                modelo.fecha_vencimiento <= hasta,
            )

        total = 0.0

        for registro in consulta.all():
            total += float(
                getattr(
                    registro,
                    "saldo_pendiente",
                    None,
                )
                or registro.total
                or 0,
            )

        return total
