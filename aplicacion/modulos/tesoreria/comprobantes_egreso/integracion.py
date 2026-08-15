from __future__ import annotations

from aplicacion.modulos.contabilidad.servicios import (
    ServicioContabilidad,
)
from aplicacion.nucleo.configuracion import Configuracion

from .repositorio import RepositorioComprobanteEgreso
from .servicios import ServicioComprobanteEgreso


class IntegracionComprobanteEgreso:

    @classmethod
    def contabilizar(
        cls,
        id_registro: int,
    ):

        comprobante = (
            ServicioComprobanteEgreso.obtener_completo(
                id_registro,
            )
        )

        if comprobante is None:

            raise ValueError(
                "No se encontró el comprobante de egreso.",
            )

        if comprobante.contabilizado:

            raise ValueError(
                "El comprobante ya fue contabilizado.",
            )

        asiento = (
            ServicioContabilidad.registrar_comprobante_egreso(
                comprobante,
            )
        )

        if comprobante.detalles:

            lineas = [
                {
                    "factura_compra_id": detalle.factura_compra_id,
                    "valor_aplicado": detalle.valor_aplicado,
                }
                for detalle in comprobante.detalles
            ]

            ServicioComprobanteEgreso._validar_lineas(
                comprobante.proveedor_id,
                lineas,
            )

            RepositorioComprobanteEgreso.aplicar_pago_facturas(
                lineas,
            )

        return (
            RepositorioComprobanteEgreso.actualizar_contabilizacion(
                id_registro,
                asiento_id=asiento.id,
            )
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
