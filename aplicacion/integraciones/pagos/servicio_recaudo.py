from __future__ import annotations

from aplicacion.base_datos.conexion import SessionLocal


class ServicioRecaudo:
    """Aplica pagos de pasarelas a cartera."""

    @classmethod
    def aplicar_pago(
        cls,
        *,
        referencia: str,
        valor: float,
        pasarela: str,
    ) -> dict:
        from aplicacion.modulos.ventas.facturas.modelos import (
            FacturaVenta,
        )

        db = SessionLocal()

        try:
            factura = (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.numero == referencia,
                )
                .first()
            )

            if factura is None:
                return {
                    "exito": False,
                    "mensaje": "Factura no encontrada.",
                }

            saldo = float(
                factura.saldo_pendiente
                or factura.total
                or 0,
            )

            if valor >= saldo:
                factura.estado_pago = "pagada"
                factura.saldo_pendiente = 0

            else:
                factura.saldo_pendiente = saldo - valor

            db.commit()

            return {
                "exito": True,
                "factura": factura.numero,
                "pasarela": pasarela,
                "valor": valor,
            }

        finally:
            db.close()

    @classmethod
    def enlace_multifactura(
        cls,
        *,
        factura_ids: list[int],
        pasarela: str = "bold",
    ) -> dict:
        from aplicacion.integraciones.pagos.pasarelas import (
            obtener_pasarela,
        )
        from aplicacion.modulos.ventas.facturas.modelos import (
            FacturaVenta,
        )

        db = SessionLocal()

        try:
            facturas = (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.id.in_(
                        factura_ids,
                    )
                )
                .all()
            )

            total = sum(
                float(
                    f.saldo_pendiente or f.total or 0,
                )
                for f in facturas
            )

            referencia = "-".join(
                f.numero for f in facturas[:3]
            )

        finally:
            db.close()

        return obtener_pasarela(
            pasarela,
        ).crear_enlace_pago(
            referencia=referencia,
            valor=total,
            descripcion="Pago múltiple cartera",
        )
