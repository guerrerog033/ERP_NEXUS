from __future__ import annotations

from aplicacion.modulos.contabilidad.servicios import (
    ServicioContabilidad,
)
from aplicacion.nucleo.configuracion import Configuracion

from .repositorio import RepositorioReciboCaja
from .servicios import ServicioReciboCaja


class IntegracionReciboCaja:

    @classmethod
    def contabilizar(
        cls,
        id_registro: int,
    ):

        recibo = ServicioReciboCaja.obtener_completo(
            id_registro,
        )

        if recibo is None:

            raise ValueError(
                "No se encontró el recibo de caja.",
            )

        if recibo.contabilizado:

            raise ValueError(
                "El recibo ya fue contabilizado.",
            )

        asiento = ServicioContabilidad.registrar_recibo_caja(
            recibo,
        )

        if recibo.detalles:

            lineas = [
                {
                    "factura_venta_id": detalle.factura_venta_id,
                    "valor_aplicado": detalle.valor_aplicado,
                }
                for detalle in recibo.detalles
            ]

            ServicioReciboCaja._validar_lineas(
                recibo.cliente_id,
                lineas,
            )

            RepositorioReciboCaja.aplicar_pago_facturas(
                lineas,
            )

        return RepositorioReciboCaja.actualizar_contabilizacion(
            id_registro,
            asiento_id=asiento.id,
        )

    @classmethod
    def contabilizar_automatico(
        cls,
        id_registro: int,
    ):

        if not Configuracion.obtener(
            "tesoreria",
            "contabilizar_automatico",
        ):

            return None

        return cls.contabilizar(
            id_registro,
        )
