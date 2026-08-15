from aplicacion.comunes.controlador_base import ControladorBase

from .integracion import IntegracionNotaCreditoVenta
from .servicios import ServicioNotaCreditoVenta


class ControladorNotaCreditoVenta(ControladorBase):

    servicio = ServicioNotaCreditoVenta

    @classmethod
    def obtener_completa(
        cls,
        id_registro,
    ):

        return cls.servicio.obtener_completa(
            id_registro,
        )

    @classmethod
    def confirmar_generacion(
        cls,
        id_registro,
        *,
        emitir_dian: bool = False,
    ):

        return IntegracionNotaCreditoVenta.confirmar_generacion(
            id_registro,
            emitir_dian=emitir_dian,
        )

    @classmethod
    def emitir_electronica(
        cls,
        id_registro,
    ):

        return IntegracionNotaCreditoVenta.emitir_electronica(
            id_registro,
        )

    @classmethod
    def contabilizar(
        cls,
        id_registro,
    ):

        return IntegracionNotaCreditoVenta.contabilizar(
            id_registro,
        )

    @classmethod
    def guardar_completa(
        cls,
        cabecera,
        lineas,
        id_registro=None,
    ):

        return cls.servicio.guardar_completa(
            cabecera,
            lineas,
            id_registro,
        )

    @classmethod
    def crear_desde_factura(
        cls,
        factura_id: int,
        motivo: str | None = None,
    ):

        return cls.servicio.crear_desde_factura(
            factura_id,
            motivo,
        )
